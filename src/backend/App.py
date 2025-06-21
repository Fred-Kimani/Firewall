"""from flask import Flask, request, jsonify"""
from flask import Flask, jsonify
from datetime import datetime
import random
import math
import re
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def Process1(sayi1, sayi2): return sayi1 + sayi2
def Process2(sayi1, sayi2): return sayi1 * sayi2
def Process3(sayi1, sayi2): return sayi1 / sayi2
def Process4(sayi1, sayi2): return sayi1 - sayi2
def Process5(sayi1): return abs(sayi1)
def Process6(sayi1): return round(sayi1)
def Process7(sayi1): return math.floor(sayi1)
def Process8(sayi1): return math.ceil(sayi1)
def Process9(s1, s2, s3): return max(s1, s2, s3)
def Process10(s1, s2, s3): return min(s1, s2, s3)
def Process11(s1, s2): return math.pow(s1, s2)
def Process12(s1): return math.sqrt(s1)
def Process13(s1): return math.cbrt(s1)  # Python 3.11+
def Process14(s1): return math.sin(s1)
def Process15(s1): return math.cos(s1)
def Process16(s1): return math.tan(s1)
def Process17(s1): return math.cos(s1) / math.sin(s1)
def Process18(s1): return math.asin(s1)
def Process19(s1): return math.acos(s1)
def Process20(s1): return math.atan(s1)
def Process21(s1, s2): return math.atan2(s2, s1)
def Process22(s1): return math.log(s1)
def Process23(s1): return math.log10(s1)
def Process24(s1): return math.exp(s1)
def Process25(): return random.random()
def Process26(): return math.floor(random.random() * 10)
def Process27(): return math.pi
def Process28(): return math.e
def Process29(): return math.log(2)
def Process30(): return math.sqrt(2)

"""def process():
    data = request.get_json()
    number = data.get("number")
    result = round(float(number) ** 0.5 , 6)
    
    return jsonify({"result": result, "message": f"Processed {number}"})
"""
@app.route("/api/test" , methods=["GET"])
def test_api():
    return jsonify({
        "status": "success",
        "message": "I came from Flask API",
        "value": round(math.pi, 5)
    })   


if __name__ == '__main__':
    app.run(debug = True, port=5002)
