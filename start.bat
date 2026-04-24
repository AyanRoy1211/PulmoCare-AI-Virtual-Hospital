@echo off
echo Starting PulmoCare Backend...
cd backend
start "" /b ..\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
echo Backend started on port 8000.

echo Starting PulmoCare Frontend...
cd ..
start "" /b .\.venv\Scripts\python.exe -m streamlit run frontend\app.py
echo Frontend started.
