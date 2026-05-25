import logging
from django.utils import timezone
from datetime import datetime
from rest_framework import serializers

from .models import Members, LeaveRequest

log = logging.getLogger(__name__)

VALID_POSITIONS = ['full', 'part']

""" Member Part """
# =====================================  Create Member =====================================
def create_member(validated_data, password=None):
    log.debug("create_member start")
    try:
        position_type = validated_data.get('position_type')
        log.debug(f"create_member position_type: {position_type}")

        if position_type in VALID_POSITIONS:
            validated_data['start_date'] = datetime.today().date()

        if not validated_data.get('username'):
            validated_data['username'] = validated_data.get('email')

        user = Members(**validated_data)
        if password:
            user.set_password(password)
        user.save()

        log.info(f"create_member finished - member created: {user.email}")
        return user
    except serializers.ValidationError:
        raise
    except Exception as e:
        log.error(f"create_member failed: {e}", exc_info=True)
        raise


# =====================================  Update Member =====================================
def validate_deactivation(instance, requested_user, validated_data):
    log.debug(f"validate_deactivation start - instance: {instance.email}, requested_user: {requested_user.email}")
    if validated_data.get('is_active') is False:
        if instance.is_superuser:
            log.warning(f"validate_deactivation - attempt to deactivate superuser: {instance.email}")
            raise serializers.ValidationError({"is_active": "Cannot deactivate admin accounts"})
        if instance.is_staff and instance == requested_user:
            log.warning(f"validate_deactivation - staff attempt to deactivate themselves: {instance.email}")
            raise serializers.ValidationError({"is_active": "Cannot deactivate yourself"})
        if instance.is_manager and instance == requested_user:
            log.warning(f"validate_deactivation - manager attempt to deactivate themselves: {instance.email}")
            raise serializers.ValidationError({"is_active": "Manager cannot deactivate themselves"})
    log.debug("validate_deactivation finished")

def apply_active_status_changes(instance, validated_data):
    log.debug(f"apply_active_status_changes start - instance: {instance.email}")
    if 'is_active' not in validated_data:
        log.debug("apply_active_status_changes - no is_active in validated_data, skipping")
        return

    is_active = validated_data.get('is_active')
    new_position = validated_data.get('position_type')
    log.debug(f"apply_active_status_changes - is_active: {is_active}, new_position: {new_position}")

    if not is_active and instance.is_active:
        validated_data['end_date'] = datetime.today().date()
        validated_data['start_date'] = None
        log.info(f"apply_active_status_changes - member deactivated: {instance.email}")
    else:
        validated_data['end_date'] = None
        if new_position in VALID_POSITIONS:
            validated_data['start_date'] = datetime.today().date()
        log.info(f"apply_active_status_changes - member reactivated: {instance.email}")

    log.debug("apply_active_status_changes finished")


def apply_position_changes(instance, validated_data):
    log.debug(f"apply_position_changes start - instance: {instance.email}")
    new_position = validated_data.get('position_type')
    current_position = instance.position_type
    log.debug(f"apply_position_changes - current: {current_position}, new: {new_position}")

    if current_position not in VALID_POSITIONS and new_position in VALID_POSITIONS:
        validated_data['start_date'] = datetime.today().date()
        log.info(f"apply_position_changes - {instance.email} changed to permanent/part-time")
    elif new_position and current_position in VALID_POSITIONS and new_position not in VALID_POSITIONS:
        validated_data['start_date'] = None
        log.info(f"apply_position_changes - {instance.email} changed to casual")

    log.debug("apply_position_changes finished")


def update_member(instance, validated_data, password=None):
    log.debug(f"update_member start - instance: {instance.email}")
    try:
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()

        log.info(f"update_member finished - member updated: {instance.email}")
        return instance
    except Exception as e:
        log.error(f"update_member failed - instance: {instance.email}: {e}", exc_info=True)
        raise


# ===================================== Validate LeaveRequest =====================================
def validate_leave_request(data, user):
    log.debug(f"validate_leave_request start - user: {user.email}")
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    leave_hours = data.get('leave_hours')
    reason = data.get('reason')

    if not start_date:
        raise serializers.ValidationError({'start_date': 'start_date is required'})
    if not end_date:
        raise serializers.ValidationError({'end_date': 'end_date is required'})
    if not leave_hours:
        raise serializers.ValidationError({'leave_hours': 'leave_hours is required'})
    elif leave_hours <= 0:
        raise serializers.ValidationError({'leave_hours': 'must greater than zero'})
    if not data.get('leave_type'):
        raise serializers.ValidationError({'leave_type': 'leave_type is required'})
    if start_date > end_date:
        raise serializers.ValidationError('start_date later than end_date')

    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    existing = LeaveRequest.objects.filter(
        staff=user,
        start_date=start_date,
        end_date=end_date,
        reason=reason,
        status__in=['pending', 'approved']
    )
    if existing.exists():
        log.warning(f"validate_leave_request - duplicate leave request detected for user: {user.email}")
        raise serializers.ValidationError('An existing leave request matches this period.')

    log.debug("validate_leave_request finished")


# ===================================== Create LeaveRequest =====================================
def create_leave_request(validated_data, user):
    log.debug(f"create_leave_request start - user: {user.email}")
    try:
        validated_data['staff'] = user
        validated_data['status'] = 'pending'
        leave_request = LeaveRequest.objects.create(**validated_data)

        log.info(f"create_leave_request finished - leave request created for user: {user.email}")
        return leave_request
    except Exception as e:
        log.error(f"create_leave_request failed - user: {user.email}: {e}", exc_info=True)
        raise


# ===================================== Update LeaveRequest =====================================
def update_leave_request(instance, validated_data, user):
    log.debug(f"update_leave_request start - instance: {instance.id}, user: {user.email}")
    review_status = ['approved', 'rejected']
    current_status = instance.status
    new_status = validated_data.get('status')
    log.debug(f"update_leave_request - current_status: {current_status}, new_status: {new_status}")

    if not new_status:
        raise serializers.ValidationError("status is required")

    if current_status == 'pending' and new_status in review_status:
        if not user.is_staff:
            log.warning(f"update_leave_request - non-manager attempt to review leave request: {user.email}")
            raise serializers.ValidationError("Only manager can review leave requests.")
        if instance.staff == user:
            log.warning(f"update_leave_request - staff attempt to review own leave request: {user.email}")
            raise serializers.ValidationError("You cannot review your own leave request.")

    if current_status == 'approved' and new_status != 'canceled':
        log.warning(f"update_leave_request - invalid status transition: {current_status} -> {new_status}")
        raise serializers.ValidationError("Approved requests can only be canceled.")

    try:
        instance.status = new_status
        instance.reviewed_by = user
        instance.reviewed_at = timezone.now()
        instance.save()

        log.info(f"update_leave_request finished - leave request {instance.id} updated to '{new_status}' by {user.email}")
        return instance
    except Exception as e:
        log.error(f"update_leave_request failed - instance: {instance.id}: {e}", exc_info=True)
        raise