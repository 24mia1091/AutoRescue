@echo off
echo AutoRescue - Smart Accident Detection System
echo ============================================
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting AutoRescue server...
echo Server will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python app.py
pause
