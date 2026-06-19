# 使用官方 Python image
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 先複製 requirements 並安裝，利用 Docker cache 加速
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製整個專案
COPY . .

# 對外開放 8000 port
EXPOSE 8000

# 啟動指令
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]