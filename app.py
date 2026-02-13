from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

DB_FILE = "database.json"

def init_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({"activations": {}}, f)

@app.route('/')
def home():
    return jsonify({"status": "online", "message": "Ashraf Activation Server"})

@app.route('/check/<key>')
def check_key(key):
    init_db()
    key = key.upper()
    
    with open(DB_FILE, "r") as f:
        data = json.load(f)
    
    if key in data["activations"]:
        return jsonify({
            "found": True,
            "status": data["activations"][key]["status"],
            "expiry": data["activations"][key].get("expiry", ""),
            "activated": data["activations"][key].get("activated", "")
        })
    
    return jsonify({"found": False})

@app.route('/activate', methods=['POST'])
def activate_key():
    init_db()
    data = request.json
    key = data.get("key", "").upper()
    months = int(data.get("months", 0))
    
    with open(DB_FILE, "r") as f:
        db = json.load(f)
    
    if months > 0:
        expiry = (datetime.now() + timedelta(days=months*30)).isoformat()
    else:
        expiry = "permanent"
    
    db["activations"][key] = {
        "status": "active",
        "activated": datetime.now().isoformat(),
        "expiry": expiry,
        "months": months
    }
    
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)
    
    return jsonify({"success": True, "key": key})

@app.route('/deactivate', methods=['POST'])
def deactivate_key():
    init_db()
    data = request.json
    key = data.get("key", "").upper()
    
    with open(DB_FILE, "r") as f:
        db = json.load(f)
    
    if key in db["activations"]:
        db["activations"][key]["status"] = "inactive"
        
        with open(DB_FILE, "w") as f:
            json.dump(db, f, indent=2)
        
        return jsonify({"success": True})
    
    return jsonify({"success": False})

@app.route('/suspend', methods=['POST'])
def suspend_key():
    init_db()
    data = request.json
    key = data.get("key", "").upper()
    hours = int(data.get("hours", 24))
    
    with open(DB_FILE, "r") as f:
        db = json.load(f)
    
    if key in db["activations"]:
        resume = (datetime.now() + timedelta(hours=hours)).isoformat()
        db["activations"][key]["status"] = f"suspended_until_{resume}"
        db["activations"][key]["resume"] = resume
        
        with open(DB_FILE, "w") as f:
            json.dump(db, f, indent=2)
        
        return jsonify({"success": True, "resume": resume})
    
    return jsonify({"success": False})

@app.route('/resume', methods=['POST'])
def resume_key():
    init_db()
    data = request.json
    key = data.get("key", "").upper()
    
    with open(DB_FILE, "r") as f:
        db = json.load(f)
    
    if key in db["activations"]:
        db["activations"][key]["status"] = "active"
        
        with open(DB_FILE, "w") as f:
            json.dump(db, f, indent=2)
        
        return jsonify({"success": True})
    
    return jsonify({"success": False})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)