import logging
from . import services
from rest_framework import serializers
from .models import Members, Shift, StaffShift, LeaveRequest, LeaveBalance, Wage


log = logging.getLogger(__name__)

VALID_POSITIONS = ['full', 'part']


class MemberSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get('request', None)
        if not request or not hasattr(request, 'user'):
            return

        user = request.user
        part_time_staff = Members.objects.filter(id=user.id, position_type='part').first()

        if not part_time_staff:
            self.fields.pop('part_time_rate', None)
    
    class Meta:
        model = Members
        fields = ['id', 'first_name', 'last_name', 'email', 'mobile',
                  'permanent_position', 'part_time_rate', 'position_type', 
                  'is_active', 'is_manager', 'is_superuser', 'password']
        read_only_fields = ['id', 'is_superuser']

    def validate(self, attrs):
        request = self.context['request']
        user = getattr(request, 'user', None)

        if user and user.email == 'manager@shift.com':
            log.warning(f"MemberSerializer.validate - demo account attempt to create user: {user.email}")
            raise serializers.ValidationError('Demo account cannot create new user')
        
        return attrs
    
    def create(self, validated_data):
        log.debug(f"MemberSerializer.create - requested by: {self.context['request'].user.email}")
        password = validated_data.pop('password', None)
        return services.create_member(validated_data, password)

    def update(self, instance, validated_data):
        log.debug(f"MemberSerializer.update - instance: {instance.email}, requested by: {self.context['request'].user.email}")
        password = validated_data.pop('password', None)
        requested_user = self.context['request'].user

        services.validate_deactivation(instance, requested_user, validated_data)
        services.apply_active_status_changes(instance, validated_data)
        services.apply_position_changes(instance, validated_data)
        
        return services.update_member(instance, validated_data, password)


class ShiftSerializer(serializers.ModelSerializer):
    daily_work_hours = serializers.SerializerMethodField()

    class Meta:
        model = Shift
        fields = ['id', 'shift_name', 'start_time', 'end_time', 
                  'daily_work_hours']
        read_only_fields = ['id']
        
    def get_daily_work_hours(self, obj):
        return round(obj.daily_work_hours(), 2)


class StaffShiftSerializer(serializers.ModelSerializer):
    staff_name = serializers.SerializerMethodField()
    alternative_staff_name = serializers.SerializerMethodField()
    shift_name = serializers.StringRelatedField()

    class Meta:
        model = StaffShift
        fields = ['id', "shift_date", "staff", "staff_name", "shift", "shift_name", 
                  "cover_shift", "alternative_staff", "alternative_staff_name"]
        read_only_fields = ['id']
        
    def get_shift_name(self, obj):
        return str(obj.shift)

    def get_staff_name(self, obj):
        return str(obj.staff)
    
    def get_alternative_staff_name(self, obj):
        return str(obj.alternative_staff)
        
    def to_representation(self, instance):
        rep = super().to_representation(instance)

        if not instance.cover_shift:
            rep.pop('cover_shift', None)
            rep.pop("alternative_staff", None)
            rep.pop('alternative_staff_name', None)

        return rep
    
    def validate(self, data):
        cover_shift = data.get('cover_shift')
        if cover_shift:
            alt_staff_id = data.get('alternative_staff')
            if not alt_staff_id:
                log.warning("StaffShiftSerializer.validate - cover_shift is True but alternative_staff is missing")
                raise serializers.ValidationError({'alternative_staff': 'alternative_staff is required'})
        
        return data


class LeaveRequestSerializer(serializers.ModelSerializer):
    staff = serializers.StringRelatedField()
    reviewed_by = serializers.StringRelatedField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get('request', None)
        if request:
            user = request.user
            if user.is_manager:
                pass
            else:
                self.fields.pop('reviewed_by', None)

    class Meta:
        model = LeaveRequest
        fields = ['id', 'staff', 'leave_type', 'start_date', 'end_date', 
                  'leave_hours', 'reason', 'status', 'requested_at', 
                  'reviewed_at', 'reviewed_by']
        read_only_fields = ['id']
        
    def validate(self, data):
        if self.instance and len(data) == 1 and 'status' in data:
            log.debug(f"LeaveRequestSerializer.validate - status-only update, skipping validation")
            return data
        
        user = self.context['request'].user
        log.debug(f"LeaveRequestSerializer.validate - user: {user.email}")
        services.validate_leave_request(data, user)
        return data
    
    def create(self, validated_data):
        user = self.context['request'].user
        log.debug(f"LeaveRequestSerializer.create - requested by: {user.email}")
        return services.create_leave_request(validated_data, user)
    
    def validate_status(self, value):
        valid_status = ['approved', 'rejected', 'canceled']
        if value not in valid_status:
            log.warning(f"LeaveRequestSerializer.validate_status - invalid status value: {value}")
            raise serializers.ValidationError("Invalid status value.")
        return value
    
    def update(self, instance, validated_data):
        user = self.context['request'].user
        log.debug(f"LeaveRequestSerializer.update - instance: {instance.id}, requested by: {user.email}")
        return services.update_leave_request(instance, validated_data, user)


class LeaveBalanceSerializer(serializers.ModelSerializer):
    staff = serializers.StringRelatedField()
    available_annual_leave_hours = serializers.SerializerMethodField()
    available_sick_leave_hours = serializers.SerializerMethodField()

    class Meta:
        model = LeaveBalance
        fields = ['staff', 'available_annual_leave_hours', 
                  'available_sick_leave_hours']

    def get_available_annual_leave_hours(self, obj):
        return str(obj.get_available_annual_leave_hours())

    def get_available_sick_leave_hours(self, obj):
        return str(obj.get_available_sick_leave_hours())


class WageSerializer(serializers.ModelSerializer):
    staff = serializers.StringRelatedField()
    shift = serializers.StringRelatedField()

    class Meta:
        model = Wage
        fields = ['id', 'staff', 'shift', 'pay_date', 'salary']
        read_only_fields = ['id']

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        if not instance.pay_date:
            rep.pop('pay_date', None)

        return rep
    
    # def get_shift_date_max(self, obj):
    #     return str(Wage.objects.aggregate(Max('shift_date'))['shift_date__max'] or '')

    # def get_shift_date_min(self, obj):
    #     return str(Wage.objects.aggregate(Min('shift_date'))['shift_date__min'] or '')