
#!/bin/bash

# 啟動 Frontend
echo "🚀 Starting frontend..."
cd ..
source venv/bin/activate
cd bankhub
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
FRONTEND_PID=$!

trap "echo '🛑 Stopping...'; kill $FRONTEND_PID" INT

\
wait


# Trap: 當你 Ctrl+C 時自動 kill 掉 backend & frontend
trap "echo '🛑 Stopping...'; kill $BACKEND_PID " INT

# 等待兩個程序
wait
