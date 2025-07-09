from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import re
import logging
import time
import os

app = Flask(__name__, static_folder="static")
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# Logging to file
LOG_FILE = 'waf.log'
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.WARNING,
    format='%(asctime)s - %(message)s'
)

request_tracker = {}
blocked_ips = {}

# 1) SQLi rules, with an extra pattern to catch "' OR '1'='1"
SQLI_RULES = [
    re.compile(r"'\s*OR\s*'\d'\s*=\s*'\d", re.IGNORECASE),
    re.compile(r"(\s*')\s*OR\s*'\d'\s*=\s*'\d'", re.IGNORECASE),
    re.compile(r"(\s*')\s*OR\s*(\d+)=(\d+)", re.IGNORECASE),
    re.compile(r"UNION\s+SELECT", re.IGNORECASE),
    re.compile(r"DROP\s+TABLE", re.IGNORECASE),
    re.compile(r"(--|\#|;)", re.IGNORECASE)
]

# 2) XSS
XSS_RULES = [
    re.compile(r"<script.*?>.*?</script>", re.IGNORECASE | re.DOTALL),
    re.compile(r"on\w+\s*=", re.IGNORECASE),
    re.compile(r"javascript\s*:", re.IGNORECASE),
    re.compile(r"<img[^>]+src=['\"]?javascript:", re.IGNORECASE),
    re.compile(r"<iframe.*?>", re.IGNORECASE)
]

# 3) Command Injection
CMD_INJECTION_RULES = [
    re.compile(r";\s*(ls|cat|pwd|whoami|echo)", re.IGNORECASE),
    re.compile(r"\|\s*(ls|cat|whoami)", re.IGNORECASE)
]

# 4) Local File Inclusion
LFI_RULES = [
    re.compile(r"\.\./", re.IGNORECASE),
    re.compile(r"/etc/passwd", re.IGNORECASE)
]

# 5) Remote File Inclusion / SSRF
RFI_RULES = [
    re.compile(r"https?://[^\s]+", re.IGNORECASE),
    re.compile(r"file://", re.IGNORECASE)
]

# 6) Path Traversal
PATH_TRAVERSAL_RULES = [
    re.compile(r"\.\./", re.IGNORECASE),
    re.compile(r"[a-zA-Z]:\\", re.IGNORECASE)
]

# 7) Malicious User-Agent
USER_AGENT_RULES = [
    re.compile(r"(sqlmap|nmap|nikto)", re.IGNORECASE)
]

# Rate-limiting parameters
ANOMALY_RATE_LIMIT = 20
BLOCK_DURATION = 300  # seconds
TIME_WINDOW = 60      # seconds

def check_for_attack(input_string, user_agent):
    for rule in SQLI_RULES:
        if rule.search(input_string):
            return True, f"SQLi-{SQLI_RULES.index(rule)}"
    for rule in XSS_RULES:
        if rule.search(input_string):
            return True, f"XSS-{XSS_RULES.index(rule)}"
    for rule in CMD_INJECTION_RULES:
        if rule.search(input_string):
            return True, f"CMD-{CMD_INJECTION_RULES.index(rule)}"
    for rule in LFI_RULES:
        if rule.search(input_string):
            return True, f"LFI-{LFI_RULES.index(rule)}"
    for rule in RFI_RULES:
        if rule.search(input_string):
            return True, f"RFI-{RFI_RULES.index(rule)}"
    for rule in PATH_TRAVERSAL_RULES:
        if rule.search(input_string):
            return True, f"PathTraversal-{PATH_TRAVERSAL_RULES.index(rule)}"
    for rule in USER_AGENT_RULES:
        if rule.search(user_agent):
            return True, f"UserAgent-{USER_AGENT_RULES.index(rule)}"
    return False, None

@app.route("/api/process", methods=["POST"])
def process_request():
    source_ip = request.remote_addr
    user_agent = request.headers.get("User-Agent", "")
    now = time.time()

    # Unblock if block time expired
    if source_ip in blocked_ips and now >= blocked_ips[source_ip]:
        del blocked_ips[source_ip]
        request_tracker.pop(source_ip, None)

    # Initialize or purge old timestamps
    request_tracker.setdefault(source_ip, [])
    request_tracker[source_ip] = [
        ts for ts in request_tracker[source_ip]
        if now - ts < TIME_WINDOW
    ]

    # Rate limit: only count successful requests (tracked below)
    if len(request_tracker[source_ip]) > ANOMALY_RATE_LIMIT:
        blocked_ips[source_ip] = now + BLOCK_DURATION
        logging.warning(f"ANOMALY - IP {source_ip} blocked for too many requests")
        return jsonify({"error": "Too Many Requests"}), 429

    # Parse input
    try:
        data = request.get_json(force=True)
        user_input = data.get("input", "")
    except:
        return jsonify({"error": "Invalid JSON"}), 400

    # Threat detection
    is_attack, rule = check_for_attack(user_input, user_agent)
    if is_attack:
        logging.warning(f"THREAT - IP: {source_ip} - Rule: {rule} - Payload: {user_input!r}")
        return jsonify({"error": "Forbidden", "rule": rule}), 403

    # Only now count this request for rate limiting
    request_tracker[source_ip].append(now)

    return jsonify({"message": "OK"}), 200

@app.route("/logs")
def logs_page():
    return send_from_directory(app.static_folder, "logs.html")


@app.route("/api/logs")
def get_logs():
    if not os.path.exists(LOG_FILE):
        return jsonify([])
    with open(LOG_FILE) as f:
        return jsonify([{"entry": line.strip()} for line in f])

if __name__ == '__main__':
    print("✅ Flask server running on http://localhost:5002")
    app.run(debug=True, port=5002)
