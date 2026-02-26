from flask import Flask, render_template, request, jsonify
import requests
import os
import concurrent.futures
import re

app = Flask(__name__)

# Intelligence Keys
LEAK_TOKEN = "7128071523:0Lv2XEkN"
GEMINI_KEY = "AIzaSyAsIUu5qfLvxswYtZp8FTly6BOHYn27KIA"

def call_leakosint(query):
    try:
        url = "https://leakosintapi.com/"
        payload = {"token": LEAK_TOKEN, "request": query, "limit": 100, "lang": "en"}
        r = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=20)
        return {"source": "Leak-Database", "data": r.json().get("List")}
    except: return {"source": "Leak-Database", "data": "Uplink Timeout"}

def call_ip_forensics(ip):
    try:
        # Detailing: City, ISP, Proxy, VPN, Mobile status
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=66846719", timeout=15)
        return {"source": "IP-Forensics", "data": r.json()}
    except: return {"source": "IP-Forensics", "data": "Tracking Failed"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    target = request.form.get('query').strip()
    if not target: return jsonify({"status": "error", "msg": "No target provided"}), 400
    
    is_ip = re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", target)
    results = []

    # Parallel Scan: Sabhi APIs ek saath hit karengi
    with concurrent.futures.ThreadPoolExecutor() as executor:
        tasks = [executor.submit(call_leakosint, target)]
        if is_ip:
            tasks.append(executor.submit(call_ip_forensics, target))
        
        for task in concurrent.futures.as_completed(tasks):
            results.append(task.result())

    return jsonify({"status": "success", "results": results})

@app.route('/ask_rat', methods=['POST'])
def ask_rat():
    data = request.json
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    prompt = f"Identify criminal leads from this forensic data: {data.get('intel')}. User message: {data.get('msg')}. Respond as Cyber Rat Forensic AI."
    
    try:
        r = requests.post(api_url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=20)
        return jsonify({"reply": r.json()['candidates'][0]['content']['parts'][0]['text']})
    except:
        return jsonify({"reply": "Cyber Rat Neural Link: Signal Lost."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
