#!/bin/bash

# 啟動 Frontend
echo "🚀 Starting frontend..."
cd ..
source venv/bin/activate
cd bankhub
cd frontend
npm start &
FRONTEND_PID=$!

trap "echo '🛑 Stopping...'; kill $FRONTEND_PID" INT

\
wait
