import datetime
import json
import logging
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS

from atlaz.codeGen.backend.start_gen import start_gen
from atlaz.codeGen.backend.directory_tree import handle_get_directory_tree
from atlaz.io_operations.file_mediator import handle_apply_changes, remove_explanation_file, remove_json_files
from atlaz.io_operations.file_utils import read_json
server_start_time = datetime.datetime.now().isoformat()
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
logging.basicConfig(level=logging.INFO)

@app.route('/send_data', methods=['POST'])
def send_data():
    data = request.json or {}
    api_key = data.get('api_key', '')
    llm_model = data.get('llm_model', '')
    llm_provider = data.get('llm_provider', '')
    message = data.get('message', '')
    selected_files = data.get('selected_files', [])
    if not api_key or not llm_model:
        return jsonify({"status": "error", "message": "API key and LLM model are required."}), 400
    if not message:
        return jsonify({"status": "error", "message": "Message is required."}), 400
    if not selected_files:
        return jsonify({"status": "error", "message": "At least one directory must be selected."}), 400
    logging.info(f"Received API Key: {api_key}")
    logging.info(f"Received LLM Model: {llm_model}")
    logging.info(f"Received LLM Provider: {llm_provider}")
    logging.info(f"Received Message: {message}")
    logging.info(f"Received Selected Directories: {selected_files}")
    try:
        final_response = start_gen(data)
        explanation = ""
        if final_response and "response" in final_response:
            explanation = final_response["response"].get("explanation", "")
        response = {
            "status": "success",
            "message": "Code generation initiated.",
            "llm_model_used": llm_model,
            "explanation": explanation
        }
        return jsonify(response)
    except Exception as e:
        logging.error(f"Error during code generation: {e}")
        return jsonify({"status": "error", "message": "An error occurred during code generation."}), 500

@app.route('/api/directory_tree', methods=['GET'])
def get_directory_tree():
    """
    Dynamically build and return a JSON representation of the directory
    where this server is launched, but store paths as relative to root_path.
    """
    return handle_get_directory_tree()

@app.route('/api/save_selection', methods=['POST'])
def save_selection():
    data = request.json or {}
    selected_paths = data.get('selectedPaths', [])
    print("Received selected file paths:", selected_paths)
    return jsonify({"status": "ok", "receivedCount": len(selected_paths)})

@app.route('/api/version', methods=['GET'])
def get_version():
    return jsonify({"version": server_start_time})

@app.route('/api/get_credentials', methods=['GET'])
def get_credentials():
    """
    Retrieve the saved credentials from ~/.atlaz
    """
    token_file = Path.home() / ".atlaz"
    if not token_file.exists():
        return jsonify({
            "api_key": "",
            "llm_provider": "openai",
            "model_choice": "gpt-4o"
        }), 200
    try:
        data =read_json(token_file)
        api_key = data.get("api_key", "")
        llm_provider = data.get("llm_provider", "openai")
        model_choice = data.get("model_choice", "gpt-4")
        return jsonify({
            "api_key": api_key,
            "llm_provider": llm_provider,
            "model_choice": model_choice
        }), 200
    except (json.JSONDecodeError, OSError) as e:
        logging.error(f"Error reading .atlaz file: {e}")
        return jsonify({
            "api_key": "",
            "llm_provider": "openai",
            "model_choice": "gpt-4"
        }), 500

@app.route('/api/apply_changes', methods=['POST'])
def apply_changes():
    """
    Reads atlaz/frontend/files.json (or wherever you write them),
    then copies each file's content to the original location in the repo.
    """
    return handle_apply_changes()

@app.route('/api/remove_files', methods=['POST'])
def delete_files():
    """
    """
    remove_explanation_file()
    remove_json_files()
    return {"status": "success"}

def main():
    app.run(debug=True, port=5050)


if __name__ == '__main__':
    main()
