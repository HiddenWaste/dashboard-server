from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime
import sqlite3
import os

# 1. Setup Flask to serve the React 'build' folder
app = Flask(__name__, 
            static_folder='dashboard-react-site/build', 
            template_folder='dashboard-react-site/build')

CORS(app) # Allow React (port 3000) to talk to Flask (port 5000)

DB_NAME = "minecraft_data.db"

# 2. Database Initialization
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS energy_logs 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                         timestamp TEXT, 
                         current_fe INTEGER, 
                         max_fe INTEGER, 
                         percent REAL)''')
        conn.commit()

init_db()

# Variable to hold the single latest entry for quick React fetching
last_cell_data_dict = {
    "current": 0,
    "max": 1,
    "percent": 0,
    "timestamp": "No data yet"
}

# 3. Route to serve the React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# 4. API: Receive data from Minecraft (ComputerCraft)
@app.route('/api/energy', methods=['POST'])
def receive_energy():
    global last_cell_data_dict
    data = request.get_json()
    
    current = data.get('current', 0)
    maximum = data.get('max', 1)
    percent = (current / maximum) * 100
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Save to SQLite
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT INTO energy_logs (timestamp, current_fe, max_fe, percent) VALUES (?, ?, ?, ?)",
                     (timestamp, current, maximum, percent))
        conn.commit()

    # Update latest data global for the React GET route
    last_cell_data_dict = {
        "current": current,
        "max": maximum,
        "percent": percent,
        "timestamp": timestamp
    }
    
    print(f"[*] Logged to SQL: {percent:.2f}% at {timestamp}")
    return jsonify({"status": "success"}), 200

# 5. API: Send latest data to React Dashboard
@app.route('/api/energy/latest', methods=['GET'])
def get_latest_energy():
    return jsonify(last_cell_data_dict)

if __name__ == '__main__':
    app.run(debug=True, port=5000)