@echo off
echo Starting Dashboard System...

:: Start the Flask Backend
start "Flask Backend" cmd /k "python first-server.py"

:: Move to react folder and start frontend
cd dashboard-react-site
start "React Frontend" cmd /k "npm start"

echo Both servers are launching!
pause