from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

DB_FILE = "database.json"

# تأكد من وجود قاعدة البيانات
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump({
            "activations": {},
            "stats": {
                "total_keys": 0,
                "active_keys": 0,
                "suspended_keys": 0,
                "inactive_keys": 0
            }
        }, f, indent=2)

@app.route('/')
def home():
    return jsonify({"status": "online", "message": "Ashraf Server"})

@app.route('/activate', methods=['POST'])
def activate():
    data = request.json
    key = data.get('key', '').upper()
    months = int(data.get('months', 1))
    
    with open(DB_FILE, 'r') as f:
        db = json.load(f)
    
    if months > 0:
        expiry = (datetime.now() + timedelta(days=months*30)).isoformat()
    else:
        expiry = "permanent"
    
    db['activations'][key] = {
        'status': 'active',
        'activated': datetime.now().isoformat(),
        'expiry': expiry,
        'months': months
    }
    
    # تحديث الإحصائيات
    total = len(db['activations'])
    active = sum(1 for k in db['activations'].values() if k['status'] == 'active')
    suspended = sum(1 for k in db['activations'].values() if k['status'] == 'suspended')
    inactive = total - active - suspended
    
    db['stats'] = {
        'total_keys': total,
        'active_keys': active,
        'suspended_keys': suspended,
        'inactive_keys': inactive
    }
    
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=2)
    
    return jsonify({'success': True, 'key': key})

@app.route('/deactivate', methods=['POST'])
def deactivate():
    data = request.json
    key = data.get('key', '').upper()
    
    with open(DB_FILE, 'r') as f:
        db = json.load(f)
    
    if key in db['activations']:
        db['activations'][key]['status'] = 'inactive'
        
        # تحديث الإحصائيات
        total = len(db['activations'])
        active = sum(1 for k in db['activations'].values() if k['status'] == 'active')
        suspended = sum(1 for k in db['activations'].values() if k['status'] == 'suspended')
        inactive = total - active - suspended
        
        db['stats'] = {
            'total_keys': total,
            'active_keys': active,
            'suspended_keys': suspended,
            'inactive_keys': inactive
        }
        
        with open(DB_FILE, 'w') as f:
            json.dump(db, f, indent=2)
        
        return jsonify({'success': True})
    
    return jsonify({'success': False})

@app.route('/suspend', methods=['POST'])
def suspend():
    data = request.json
    key = data.get('key', '').upper()
    hours = int(data.get('hours', 24))
    
    with open(DB_FILE, 'r') as f:
        db = json.load(f)
    
    if key in db['activations']:
        resume = (datetime.now() + timedelta(hours=hours)).isoformat()
        db['activations'][key]['status'] = 'suspended'
        db['activations'][key]['resume'] = resume
        
        # تحديث الإحصائيات
        total = len(db['activations'])
        active = sum(1 for k in db['activations'].values() if k['status'] == 'active')
        suspended = sum(1 for k in db['activations'].values() if k['status'] == 'suspended')
        inactive = total - active - suspended
        
        db['stats'] = {
            'total_keys': total,
            'active_keys': active,
            'suspended_keys': suspended,
            'inactive_keys': inactive
        }
        
        with open(DB_FILE, 'w') as f:
            json.dump(db, f, indent=2)
        
        return jsonify({'success': True, 'resume': resume})
    
    return jsonify({'success': False})

@app.route('/resume', methods=['POST'])
def resume():
    data = request.json
    key = data.get('key', '').upper()
    
    with open(DB_FILE, 'r') as f:
        db = json.load(f)
    
    if key in db['activations']:
        db['activations'][key]['status'] = 'active'
        
        # تحديث الإحصائيات
        total = len(db['activations'])
        active = sum(1 for k in db['activations'].values() if k['status'] == 'active')
        suspended = sum(1 for k in db['activations'].values() if k['status'] == 'suspended')
        inactive = total - active - suspended
        
        db['stats'] = {
            'total_keys': total,
            'active_keys': active,
            'suspended_keys': suspended,
            'inactive_keys': inactive
        }
        
        with open(DB_FILE, 'w') as f:
            json.dump(db, f, indent=2)
        
        return jsonify({'success': True})
    
    return jsonify({'success': False})

@app.route('/check/<key>', methods=['GET'])
def check(key):
    key = key.upper()
    
    with open(DB_FILE, 'r') as f:
        db = json.load(f)
    
    if key in db['activations']:
        return jsonify({
            'found': True,
            'status': db['activations'][key]['status'],
            'expiry': db['activations'][key].get('expiry', ''),
            'activated': db['activations'][key].get('activated', '')
        })
    
    return jsonify({'found': False})

@app.route('/stats', methods=['GET'])
def get_stats():
    with open(DB_FILE, 'r') as f:
        db = json.load(f)
    return jsonify(db['stats'])

if __name__ == '__main__':
    print('=' * 60)
    print('🔥 Ashraf Activation Server')
    print('=' * 60)
    print('✅ Database: database.json')
    print('🌐 Port: 5000')
    print('=' * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)