from flask import Flask, jsonify, request

app = Flask(__name__)

apps = []

@app.route("/")
def home():
    return "TinyCloud API"

@app.route("/health")
def get_health():
    return jsonify({"status": "ok"})

@app.route("/apps", methods=["GET"])
def get_apps():
  return {"apps": apps}

@app.route("/apps", methods=["POST"])
def create_app():
  data = request.get_json()
  apps.append(data)
  return data, 201

@app.route("/app")
def get_app():
    return "aye twin idek what im doing tbh, but ima do it"

if __name__ == "__main__":
    app.run(debug=True, port = 5001)