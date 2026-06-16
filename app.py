import uuid
import os
import json
import yaml
from flask import Flask, request, jsonify, render_template
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

# ---------------------------------------------------------
# Pfad für die persistente Datenspeicherung (Docker Volume)
# ---------------------------------------------------------
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DATA_FILE = os.path.join(DATA_DIR, "todo_storage.json")

# Standard-Beispieldaten, falls noch keine Datei existiert
todo_list_1_id = '1318d3d1-d979-47e1-a225-dab1751dbe75'
todo_list_2_id = '3062dc25-6b80-4315-bb1d-a7c86b014c65'
todo_list_3_id = '44b02e00-03bc-451d-8d01-0c67ea866fee'

DEFAULT_DATA = {
    "todo_lists": [
        {"id": todo_list_1_id, "name": "Einkaufsliste"},
        {"id": todo_list_2_id, "name": "Arbeit"},
        {"id": todo_list_3_id, "name": "Privat"},
    ],
    "todo_entries": [
        {"id": str(uuid.uuid4()), "name": "Milch", "description": "", "list_id": todo_list_1_id},
        {"id": str(uuid.uuid4()), "name": "Arbeitsblaetter ausdrucken", "description": "", "list_id": todo_list_2_id},
        {"id": str(uuid.uuid4()), "name": "Kinokarten kaufen", "description": "", "list_id": todo_list_3_id},
        {"id": str(uuid.uuid4()), "name": "Eier", "description": "", "list_id": todo_list_1_id}
    ]
}

def load_data():
    """Lädt die Daten aus der JSON-Datei oder erstellt die Standarddaten."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
        
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_DATA, f, indent=4, ensure_ascii=False)
        return DEFAULT_DATA
    
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_DATA

def save_data(data):
    """Speichert die Daten permanent in die JSON-Datei."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ---------------------------------------------------------
# CORS: Cross-Origin Resource Sharing
# ---------------------------------------------------------
@app.after_request
def apply_cors_header(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,DELETE,PATCH"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


# ---------------------------------------------------------
# OpenAPI JSON für Swagger
# ---------------------------------------------------------
@app.route("/openapi.json")
def openapi_json():
    yaml_path = os.path.join(os.path.dirname(__file__), "openapi.yaml")
    with open(yaml_path, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)
    return jsonify(spec)


# ---------------------------------------------------------
# HTML UI
# ---------------------------------------------------------
@app.route("/ui")
def ui():
    return render_template("ui.html")


# ---------------------------------------------------------
# API: Listen
# ---------------------------------------------------------
@app.route("/todo-lists", methods=["GET", "POST"])
def handle_lists():
    data_store = load_data()
    
    if request.method == "GET":
        return jsonify(data_store["todo_lists"]), 200

    if request.method == "POST":
        data = request.get_json()
        if not data or "name" not in data:
            return jsonify({"error": "Invalid request body"}), 400

        new_list = {
            "id": str(uuid.uuid4()),
            "name": data["name"]
        }
        data_store["todo_lists"].append(new_list)
        save_data(data_store)
        return jsonify(new_list), 201


# ---------------------------------------------------------
# API: Einträge einer Liste
# ---------------------------------------------------------
@app.route("/todo-lists/<list_id>", methods=["GET", "POST", "DELETE"])
def handle_single_list(list_id):
    data_store = load_data()

    list_item = next((l for l in data_store["todo_lists"] if l["id"] == list_id), None)
    if not list_item:
        return jsonify({"error": "List not found"}), 404

    if request.method == "GET":
        entries = [e for e in data_store["todo_entries"] if e["list_id"] == list_id]
        return jsonify(entries), 200

    if request.method == "POST":
        data = request.get_json()
        if not data or "name" not in data:
            return jsonify({"error": "Invalid request body"}), 400

        new_entry = {
            "id": str(uuid.uuid4()),
            "name": data["name"],
            "description": data.get("description", ""),
            "list_id": list_id
        }
        data_store["todo_entries"].append(new_entry)
        save_data(data_store)
        return jsonify(new_entry), 201

    if request.method == "DELETE":
        data_store["todo_lists"].remove(list_item)
        data_store["todo_entries"] = [e for e in data_store["todo_entries"] if e["list_id"] != list_id]
        save_data(data_store)
        return "", 204


# ---------------------------------------------------------
# API: Einzelner Eintrag
# ---------------------------------------------------------
@app.route("/todo-lists/entry/<entry_id>", methods=["PATCH", "DELETE"])
def handle_entry(entry_id):
    data_store = load_data()
    
    entry = next((e for e in data_store["todo_entries"] if e["id"] == entry_id), None)
    if not entry:
        return jsonify({"error": "Entry not found"}), 404

    if request.method == "PATCH":
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request body"}), 400

        if "name" in data:
            entry["name"] = data["name"]
        if "description" in data:
            entry["description"] = data["description"]

        save_data(data_store)
        return jsonify(entry), 200

    if request.method == "DELETE":
        data_store["todo_entries"].remove(entry)
        save_data(data_store)
        return "", 204


# ---------------------------------------------------------
# Swagger UI
# ---------------------------------------------------------
SWAGGER_URL = "/swagger"
API_URL = "/openapi.json"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Todo-Listen-Verwaltung"}
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


# ---------------------------------------------------------
# Server starten
# ---------------------------------------------------------
if __name__ == "__main__":
    # debug=True bleibt für lokale Tests aktiv, reloader deaktivieren reloader damit Flask im Docker-Container die JSON-Datei nicht blockiert.
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)