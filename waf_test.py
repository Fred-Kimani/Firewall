import requests
import time

BASE_URL = "http://localhost:5002/api/process"

def test_attack(name, payload, expected_status):
    response = requests.post(BASE_URL, json={"input": payload})
    status = response.status_code
    result = "PASS" if status == expected_status else "FAIL"
    print(f"[{result}] {name}: sent '{payload[:30]}...' got {status}")

def test_rate_limit():
    print("Testing rate limiting (anomaly detection)...")
    for i in range(22):
        response = requests.post(BASE_URL, json={"input": "normal input"})
        if i < 20 and response.status_code != 200:
            print(f"[FAIL] Request {i+1} expected 200, got {response.status_code}")
        elif i >= 20 and response.status_code != 429:
            print(f"[FAIL] Request {i+1} expected 429, got {response.status_code}")
    print("Rate limiting test done.\n")

def run_all_tests():
    print("Starting WAF test cases...\n")

    # SQL Injection tests
    test_attack("SQL Injection 1", "' OR '1'='1", 403)
    test_attack("SQL Injection 2", "UNION SELECT username, password FROM users", 403)
    test_attack("SQL Injection 3", "DROP TABLE users;", 403)

    # XSS tests
    test_attack("XSS 1", "<script>alert('XSS')</script>", 403)
    test_attack("XSS 2", "<img src=x onerror=alert(1)>", 403)
    test_attack("XSS 3", "javascript:alert('XSS')", 403)

    # Command Injection tests
    test_attack("Cmd Injection 1", "test; ls -la", 403)
    test_attack("Cmd Injection 2", "hello | whoami", 403)

    # Local File Inclusion (LFI) tests
    test_attack("LFI 1", "../etc/passwd", 403)
    test_attack("LFI 2", "../../etc/passwd", 403)

    # Remote File Inclusion (RFI) tests
    test_attack("RFI 1", "http://malicious.com/shell.txt", 403)
    test_attack("RFI 2", "file://etc/passwd", 403)

    # Path Traversal tests
    test_attack("Path Traversal 1", "../secret.txt", 403)
    test_attack("Path Traversal 2", "C:\\windows\\system32", 403)

    # User Agent blocking test
    headers = {"User-Agent": "sqlmap"}
    response = requests.post(BASE_URL, json={"input": "normal input"}, headers=headers)
    print(f"[{'PASS' if response.status_code == 403 else 'FAIL'}] User-Agent block test: got {response.status_code}")

    # Clean input test (should pass)
    test_attack("Clean Input", "Hello, this is safe input!", 200)

    # Rate limiting test (anomaly detection)
    test_rate_limit()

    print("All tests completed.")

if __name__ == "__main__":
    run_all_tests()

