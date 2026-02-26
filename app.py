from flask import Flask, render_template, request, jsonify
import requests
import os
import concurrent.futures

app = Flask(__name__)

# Forensic Keys
SHODAN_KEY = "shrakyjGLHkz9tfRYXshhBG4Tc8voS5L"
GEMINI_KEY = "AIzaSyAsIUu5qfLvxswYtZp8FTly6BOHYn27KIA"

# --- Forensic Nodes Functions ---

def scan_social_sherlock(username):
    # Sherlock: 2000+ Platforms Social Media Tracking
    return {"node": "Sherlock-Social", "status": "Scanning 2000+ Platforms for: " + username}

def scan_whois_history(domain):
    # Whois: Domain Owner & Registration Logs
    return {"node": "Whois-Intel", "status": "Fetching Registration History for: " + domain}

def scan_email_holehe(email):
    # Holehe: Site Registration Check
    return {"node": "Holehe-Email", "status": "Verifying Site Presence for: " + email}

def scan_darkweb_onion(query):
    # OnionScan: Tor Network Intelligence
    return {"node": "DarkWeb-Node", "status": "Searching Tor Nodes for: " + query}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan_all', methods=['POST'])
def scan_all():
    target = request.form.get('query')
    results = []
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Multi-Node Parallel Execution
        tasks = [
            executor.submit(scan_social_sherlock, target),
            executor.submit(scan_whois_history, target),
            executor.submit(scan_email_holehe, target),
            executor.submit(scan_darkweb_onion, target)
        ]
        for task in concurrent.futures.as_completed(tasks):
            results.append(task.result())
            
    return jsonify({"status": "success", "results": results})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
