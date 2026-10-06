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
def get_all_apps():
    return {"apps": apps}

@app.route("/apps/<name>", methods=["GET"])
def get_app(name):
    for app in apps:
        if app["name"] == name:
            return app

    return {"error": "app not found"}, 404
    

@app.route("/apps", methods=["POST"])

def add_app():
    data = request.get_json()

    if not data:
        return {"nah bruh"}, 404

    if "name" not in data:
        return {"error": "name is required"}, 404
   
    for app in apps:
        if app["name"].lower() == data["name"].lower():
            return {"error": "nah twin ts cant slide"}, 409
    
    apps.append(data)
    return data, 201

@app.route("/apps/<name>", methods=["DELETE"])
def delete_app(name):
    for app in apps:
        if app["name"].lower() == name.lower():
            apps.remove(app)
            return {"message": "app deleted"}, 200
    return {"message": "not found bruh"}, 404


@app.route("/apps/<name>", methods=["PUT"])
def update_app(name):
    data = request.get_json()
    for app in apps:
        if app["name"] == name:
            app.update(data)
            return app, 200
    return {"error" : "app not found"}, 404


@app.route("/app")
def get_app_real():
    return "aye twin idek what im doing tbh, but ima do it"

if __name__ == "__main__":
    app.run(debug=True, port = 5001)