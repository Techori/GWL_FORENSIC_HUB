from flask import Flask, render_template, request, jsonify
import requests
import os
import concurrent.futures
import re

app = Flask(__name__)

# Core Forensic Keys
LEAK_TOKEN = "7128071523:0Lv2XEkN"
GEMINI_KEY = "AIzaSyAsIUu5qfLvxswYtZp8FTly6BOHYn27KIA"
SHODAN_KEY = "shrakyjGLHkz9tfRYXshhBG4Tc8voS5L"

def call_shodan(ip):
    try:
        url = f"https://api.shodan.io/shodan/host/{ip}?key={SHODAN_KEY}"
        r = requests.get(url, timeout=15)
        return {"source": "Shodan-Intelligence", "data": r.json()}
    except: return None

def call_leakosint(query):
    try:
        url = "https://leakosintapi.com/"
        payload = {"token": LEAK_TOKEN, "request": query, "limit": 100, "lang": "en"}
        r = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=15)
        return {"source": "Leak-Database", "data": r.json().get("List")}
    except: return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    target = request.form.get('query').strip()
    is_ip = re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", target)
    results = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(call_leakosint, target)]
        if is_ip:
            futures.append(executor.submit(call_shodan, target))
        
        for f in concurrent.futures.as_completed(futures):
            res = f.result()
            if res: results.append(res)

    return jsonify({"status": "success", "results": results})

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    prompt = f"Identify criminal leads from this data: {data.get('intel')}. User: {data.get('msg')}. Respond briefly as Cyber Rat Forensic AI."
    try:
        r = requests.post(api_url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=20)
        return jsonify({"reply": r.json()['candidates'][0]['content']['parts'][0]['text']})
    except:
        return jsonify({"reply": "Neural Link Error."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
