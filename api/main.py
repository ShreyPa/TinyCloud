from flask import Flask, jsonify, request
import psycopg2
import psycopg2.extras
import os

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        database=os.getenv("DB_NAME", "tinycloud"),
        user=os.getenv("DB_USER", "tinycloud"),
        password=os.getenv("DB_PASSWORD")
    )
    return conn

app = Flask(__name__)

apps = []

@app.route("/db-test", methods=["GET"])
def db_test():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM apps;")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({"apps": rows})

@app.route("/")
def home():
    return "TinyCloud API"

@app.route("/health")
def get_health():
    return jsonify({"status": "ok"})

@app.route("/apps", methods=["GET"])
def get_all_apps():


    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM apps;")
            rows = cur.fetchall()

            return jsonify({"apps":rows})

    finally:
        conn.close()


@app.route("/apps/<name>", methods=["GET"])
def get_app(name):

    conn = get_db_connection()

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(
                "SELECT * FROM apps WHERE LOWER(name) = LOWER(%s)",
                (name,)
            )

            app = cursor.fetchone()

            if app:
                return {"app": app}, 200
            else:
                return {"error": "app not found"}, 404
    finally:
        conn.close()

@app.route("/apps", methods=["POST"])

def add_app():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return {"error":"Invalid JSON information"}, 400
    if not isinstance(data.get("name"), str) or not data["name"].strip():
        return {"error": "name is required"}, 400

    data = request.get_json()
    name = data["name"].strip()
    status = data.get("status", "stopped")

    conn = get_db_connection()

    try:
        with conn.cursor() as cursor:

            cursor.execute(
                "SELECT id FROM apps WHERE LOWER(name) = LOWER(%s)",
                (name,)
            )

            if cursor.fetchone():
                return {"error":"nah twin ts cant work like that"}, 409
    
            cursor.execute(
            "INSERT INTO apps (name, status) VALUES (%s, %s)",
            (name, status)
            )
            
            conn.commit()

        return {"name": name, "status": status}, 201

    finally:
        conn.close()

@app.route("/apps/<name>", methods=["DELETE"])
def delete_app(name):

    conn = get_db_connection()

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(
                "DELETE FROM apps WHERE LOWER(name) = LOWER(%s) RETURNING *",
                (name,)
            )

            app = cursor.fetchone()
            if app:
                conn.commit()
                return {"message": "app was successfully deleted"}, 200
            else:
                return {"error": "app not found"}, 404
    finally:
        conn.close()
        


    for app in apps:
        if app["name"].lower() == name.lower():
            apps.remove(app)
            return {"message": "app deleted"}, 200
    return {"message": "not found bruh"}, 404


@app.route("/apps/<name>", methods=["PUT"])
def update_app(name):

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return {"error" : "Invalid JSON body"}, 400
    if "status" not in data:
        return {"error" : "status is required to do update"}, 400

    status = data["status"]

    if status not in ["running", "stopped"]:
        return {"error" : "status must be either running or stopped"}, 400
    

    conn = get_db_connection()

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:

            cursor.execute("SELECT id FROM apps WHERE LOWER(name) = LOWER(%s)",
            (name,)
            )

            app = cursor.fetchone()
            if app:
                cursor.execute(
                "UPDATE apps SET status = %s WHERE LOWER(name) = LOWER(%s) RETURNING *",
                (status, name)
                )
                updated_app = cursor.fetchone()
                return {"app" : updated_app}, 200
                conn.commit() 
            else: 
                return {"error" : "the app does not exist"}, 404
    finally:
        conn.close()



@app.route("/app")
def get_app_real():
    return "aye twin idek what im doing tbh, but ima do it"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)