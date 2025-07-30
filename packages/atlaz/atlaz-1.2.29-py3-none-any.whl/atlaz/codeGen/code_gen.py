import logging
import json
import requests  # type: ignore
from pathlib import Path

from atlaz.codeGen.schema import CodeGenRequest, CodeGenResponse
from atlaz.io_operations.file_mediator import obtain_write_paths
from atlaz.io_operations.file_utils import write_json, write_txt

def code_gen_handler(client,
    instruction: str,
    directory_structure: str,
    file_contents: list = [],
    model_choice: str = 'gpt-4o',
    provider: str = "openai"
    ):
    url = f"{client.base_url}/api/raspberry"
    payload = {
        "file_contents": file_contents,
        "directory_structure": directory_structure,
        "instruction": instruction,
        "api_key": client.api_key,
        "provider": provider,
        "model_choice": model_choice,
    }
    CodeGenRequest(**payload)
    headers = {"Authorization": f"Bearer {client.auth_token}", "Content-Type": "application/json"}
    replacing_dir, created_dir, original_dir, files_json_path, frontend_dir = obtain_write_paths()
    explanation_file_path = frontend_dir / "explanation.txt"
    try:
        with requests.post(url, json=payload, headers=headers, stream=True) as response:
            response.raise_for_status()
            final_response = None
            for line in response.iter_lines():
                if line:
                    try:
                        decoded_line = line.decode("utf-8").strip()
                        if not decoded_line:
                            continue
                        data = json.loads(decoded_line)
                        CodeGenResponse(**data)
                        status = data.get("status")
                        if status == "completed":
                            final_response = data
                            break
                    except json.JSONDecodeError as e:
                        logging.error("Failed to parse JSON line: %s", e)
                        logging.debug("Line content: %s", decoded_line)
            print(f"{final_response=}")
            if final_response and final_response.get("response").get("structured_output"):
                files_to_serve = []
                for file_item in final_response["response"]["structured_output"]:
                    new_file_name = Path(file_item["name"]).name + ".txt"
                    new_file_content = file_item["content"]
                    file_info = {"name": new_file_name, "content": new_file_content}
                    full_file_path = file_item["name"]
                    if file_item["name"].startswith('replacing-'):
                        target_file = replacing_dir / new_file_name
                        file_info['type'] = 'replacing'
                    elif file_item["name"].startswith('created-'):
                        target_file = created_dir / new_file_name
                        file_info['type'] = 'created'
                    elif file_item["name"].startswith('original-'):
                        target_file = original_dir / new_file_name
                        file_info['type'] = 'original'
                    file_info['full_name'] = full_file_path
                    write_txt(new_file_content, target_file)
                    files_to_serve.append(file_info)
                write_json(files_to_serve, files_json_path)
                explanation = final_response.get("response").get("explanation", "")
                print(f"{explanation=}")
                if explanation:
                    write_txt(explanation, explanation_file_path)
                print("Files generated. Press Ctrl+C to stop the server.")
                return final_response
            else:
                raise ValueError("Server Error: Did not receive a 'completed' response.")
    except requests.RequestException as e:
        raise e