from flask import Flask, jsonify, request
from docker_manager import get_container, stop_container, start_container, get_containers
from docker_manager import validate_container

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

@app.route("/health/db", methods = ["GET"])
def database_health():

    conn = None

    try:
        conn = get_db_connection()

        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()
        if result:
            return {"status":"ok"},200
        return {"status": "unavailable"}, 503

    except psycopg2.OperationalError:
        return {"status" : "unavailable"}, 503

    finally:
        if conn is not None: 
            conn.close()

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

            if not app:
                return {"error": "App not found"}, 404

            if app.get("container_id"):
                docker_info, docker_status_code = get_container(
                    app["container_id"]
                )

                if docker_status_code == 200:
                    docker_status = docker_info["status"]
                    app["docker_status"] = docker_status

                    new_status = None

                    if docker_status == "running":
                        new_status = "running"
                    elif docker_status == "exited":
                        new_status = "stopped"

                    if new_status is not None and app["status"] != new_status:
                        cursor.execute(
                            "UPDATE apps SET status = %s WHERE id = %s",
                            (new_status, app["id"])
                        )

                        conn.commit()
                        app["status"] = new_status

                else:
                    app["docker_status"] = None
                    app["docker_error"] = docker_info["error"]

            return {"app": app}, 200

    finally:
        conn.close()

@app.route("/apps", methods=["POST"])

def add_app():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return {"error":"Invalid JSON information"}, 400
    if not isinstance(data.get("name"), str) or not data["name"].strip():
        return {"error": "name is required"}, 400

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
    
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return {"error" : "you already have an application with this name"}, 409
    except psycopg2.errors.CheckViolation:
        conn.rollback()
        return {"error" : "this is not proper twin"}, 400

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
                conn.commit() 
                return {"app" : updated_app}, 200
                
            else: 
                return {"error" : "the app does not exist"}, 404
    finally:
        conn.close()


@app.route("/containers/<name>", methods=["GET"])
def get_container_route(name):
    return get_container(name)

@app.route("/containers/<name>/start", methods=["POST"])
def start_container_route(name):
    return start_container(name)
    
@app.route ("/containers/<name>/stop", methods=["POST"])
def stop_container_route(name):
    return stop_container(name)

@app.route("/containers", methods=["GET"])
def get_containers_route():
    return get_containers()

@app.route("/app")
def get_app_real():
    return "aye twin idek what im doing tbh, but ima do it"

@app.route("/apps/<name>/container", methods = ["PUT"])
def link_container(name):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return {"error" : "Invalid JSON data"}, 400
    if "container_id" not in data:
        return {"error" : "container id is required"}, 400
    if not isinstance(data["container_id"], str):
        return {"error": "Container ID must be a string"}, 400   
    
    container_id = data["container_id"].strip()

    if not container_id:
        return {"error": "Container ID cannot be empty"}, 400

    docker_info, docker_status_code = validate_container(container_id)

    if docker_status_code != 200:
        return docker_info, docker_status_code
    
    container_id = docker_info["id"]
    docker_status = docker_info["status"]
    container_name = docker_info["id"]
    
    conn = get_db_connection()

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(
                "SELECT * FROM apps WHERE LOWER(name) = LOWER(%s)",
                (name,)
            )

            app = cursor.fetchone()

            if not app:
                return {"error": "App not found"}, 404

            new_status = app["status"]

            if docker_status == "running":
                new_status = "running"
            elif docker_status == "exited":
                new_status = "stopped"

            cursor.execute(
                "UPDATE apps SET container_id = %s, status = %s WHERE id = %s RETURNING *",
                (container_id, new_status, app["id"])
            )

            updated_app = cursor.fetchone()
            conn.commit()

            return {"app": updated_app}, 200

    finally:
        conn.close()

if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", "5001"))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    app.run(host=host, port=port, debug=debug)