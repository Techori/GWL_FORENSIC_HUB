from flask import Flask, render_template, request, jsonify
import requests
import os
import concurrent.futures

app = Flask(__name__)

# Forensic Assets Integration
SHODAN_KEY = "shrakyjglhkz9tfryxshhbg4tc8vos5l"
LEAK_TOKEN = "7128071523:0Lv2XEkN"
GEMINI_KEY = "AIzaSyAsIUu5qfLvxswYtZp8FTly6BOHYn27KIA"

def get_shodan_data(ip):
    try:
        # Direct API hit to Shodan nodes
        url = f"https://api.shodan.io/shodan/host/{ip}?key={SHODAN_KEY}"
        r = requests.get(url, timeout=10)
        return r.json()
    except:
        return {"error": "Shodan Node Timeout"}

def get_ip_geo(ip):
    try:
        # Geolocation & ISP tracking
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        return r.json()
    except:
        return {"error": "Geo-Node Error"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    target = request.form.get('query')
    results = {}
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        shodan_task = executor.submit(get_shodan_data, target)
        geo_task = executor.submit(get_ip_geo, target)
        
        results['shodan'] = shodan_task.result()
        results['geo'] = geo_task.result()
        
    return jsonify({"status": "success", "results": results})

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    # Gemini Neural Link for profiling
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    prompt = f"Analyze this IP forensic data and identify vulnerabilities or criminal leads: {data.get('intel')}. Respond as Cyber Rat AI."
    
    try:
        r = requests.post(api_url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=15)
        return jsonify({"reply": r.json()['candidates'][0]['content']['parts'][0]['text']})
    except:
        return jsonify({"reply": "Neural Link Refused."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
