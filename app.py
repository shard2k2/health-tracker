from flask import Flask, render_template, request, redirect, url_for
import json
from datetime import datetime

app = Flask(__name__)
DATA_FILE = "health_data.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

def classify_bp(systolic, diastolic):
    if systolic < 120 and diastolic < 80:
        return "Normal", "✓"
    elif systolic < 130 and diastolic < 80:
        return "Elevated", "⚠️"
    elif (130 <= systolic < 140) or (80 <= diastolic < 90):
        return "Stage 1 Hypertension", "⚠️⚠️"
    else:
        return "Stage 2 Hypertension", "⚠️⚠️⚠️"

@app.route('/')
def home():
    health_data = load_data()
    
    # Add BP classification to each entry
    for entry in health_data:
        status, symbol = classify_bp(entry['systolic'], entry['diastolic'])
        entry['status'] = status
        entry['symbol'] = symbol
    
    return render_template('index.html', entries=health_data)

@app.route('/add', methods=['GET', 'POST'])
def add_entry():
    if request.method == 'POST':
        weight = float(request.form['weight'])
        systolic = int(request.form['systolic'])
        diastolic = int(request.form['diastolic'])
        
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "weight": weight,
            "systolic": systolic,
            "diastolic": diastolic
        }
        
        health_data = load_data()
        health_data.append(entry)
        save_data(health_data)
        
        return redirect(url_for('home'))
    
    return render_template('add.html')

@app.route('/stats')
def statistics():
    health_data = load_data()
    
    if len(health_data) == 0:
        return render_template('stats.html', stats=None)
    
    # Calculate statistics
    starting_weight = health_data[0]['weight']
    current_weight = health_data[-1]['weight']
    weight_change = current_weight - starting_weight
    
    total_systolic = sum(entry['systolic'] for entry in health_data)
    total_diastolic = sum(entry['diastolic'] for entry in health_data)
    avg_systolic = total_systolic / len(health_data)
    avg_diastolic = total_diastolic / len(health_data)
    
    latest = health_data[-1]
    status, symbol = classify_bp(latest['systolic'], latest['diastolic'])
    
    stats = {
        'starting_weight': starting_weight,
        'current_weight': current_weight,
        'weight_change': weight_change,
        'avg_systolic': avg_systolic,
        'avg_diastolic': avg_diastolic,
        'latest_status': status,
        'latest_symbol': symbol,
        'entry_count': len(health_data)
    }
    
    return render_template('stats.html', stats=stats)

@app.route('/delete/<int:index>')
def delete_entry(index):
    health_data = load_data()
    
    if 0 <= index < len(health_data):
        health_data.pop(index)  # Remove the entry at that index
        save_data(health_data)
    
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)