from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import logging
from datetime import datetime
import time


app = Flask(__name__)
# Connect to the frontend
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})


logging.basicConfig(filename='waf.log', level=logging.WARNING, format='%(asctime)s - %(message)s')

# --- For Anomaly Detection (Rate Limiting) ---
request_tracker = {}
blocked_ips = {}  


#Block Sql Injections
SQLI_RULES = [
    re.compile(r"(\s*')\s*OR\s*'\d'\s*=\s*'\d'", re.IGNORECASE),
    re.compile(r"(\s*')\s*OR\s*(\d+)=(\d+)", re.IGNORECASE),
    re.compile(r"UNION\s+SELECT", re.IGNORECASE),
    re.compile(r"DROP\s+TABLE", re.IGNORECASE),
    re.compile(r"(--|\#|;)", re.IGNORECASE)
]
#Protect from XSS
XSS_RULES = [
    re.compile(r"<script.*?>.*?</script>", re.IGNORECASE | re.DOTALL),
    # THIS IS THE FIXED RULE for onerror, onload, etc.
    re.compile(r"on\w+\s*=", re.IGNORECASE),
    re.compile(r"javascript\s*:", re.IGNORECASE)
]

def check_for_attack(input_string):
    for rule in SQLI_RULES:
        if rule.search(input_string):
            return True, f"SQLI-Rule-{SQLI_RULES.index(rule)}"
    for rule in XSS_RULES:
        if rule.search(input_string):
            return True, f"XSS-Rule-{XSS_RULES.index(rule)}"
    return False, None

#API endpoint

@app.route("/api/process", methods=["POST"])
def process_request():
    source_ip = request.remote_addr
    current_time = time.time()

    # --- Anomaly Detection Logic ---
    # First, check if the IP is in the blocked list
    if source_ip in blocked_ips:
        if current_time < blocked_ips[source_ip]:
            return jsonify({"error": "Too Many Requests", "message": "Your IP is temporarily blocked."}), 429
        else:
            # The block time is over, so unblock them
            del blocked_ips[source_ip]
            del request_tracker[source_ip]

    # Keep track of requests for this IP
    if source_ip not in request_tracker:
        request_tracker[source_ip] = []
    
    # Remove old requests from the list that are outside the time window

    TIME_WINDOW = 60  
    request_tracker[source_ip] = [ts for ts in request_tracker[source_ip] if current_time - ts < TIME_WINDOW]

    # This logic blocks on the 21st request
    BLOCK_DURATION = 300
    REQUEST_LIMIT = 20

    if len(request_tracker[source_ip]) >= REQUEST_LIMIT:
        blocked_ips[source_ip] = current_time + BLOCK_DURATION
        logging.warning(f"ANOMALY DETECTED - IP: {source_ip} blocked for rate limiting.")
        return jsonify({"error": "Too Many Requests", "message": "Rate limit exceeded. Your IP is blocked."}), 429
    
    # Add the current request to the tracker
    request_tracker[source_ip].append(current_time)

    # --- Security Check Logic ---
    try:
        data = request.get_json()
        user_input = data['input']
        
        # Check the input with my security function
        is_attack, rule_name = check_for_attack(user_input)

        if is_attack:
            # If it is an attack, log it and block it
            logging.warning(f"THREAT DETECTED - IP: {source_ip} - Rule: {rule_name} - Payload: \"{user_input}\"")
            return jsonify({"error": "Forbidden", "message": "Malicious request blocked by WAF."}), 403
        
        # If it is not an attack, send success message
        return jsonify({"message": f"Request processed successfully. Input was: '{user_input}'"}), 200

    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002)
