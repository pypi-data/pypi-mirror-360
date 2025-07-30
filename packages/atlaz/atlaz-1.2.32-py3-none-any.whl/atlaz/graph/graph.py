import json
import logging
import requests
from atlaz.graph.schema.user_graph_model import Graph
from atlaz.graph.render import create_graph
from atlaz.graph.transformations.cytoscape import transform_to_cytoscape

def visualize(graph: dict, filename: str = "output_graph"):
    graph = Graph(**graph)
    nodes, edges, clusters = transform_to_cytoscape(graph)
    create_graph(nodes, edges, clusters, filename)

def build_graph_handler(client, source_text: str, customization: str = '', graph: dict= None):
    if "raspberry" not in client.models:
            raise ValueError("Model 'raspberry' is not available.")
    if not client.auth_token:
        print("Re-authenticating...")
        client.authenticate()
        if not client.auth_token:
            print("Authentication failed.")
            return
    url = f"{client.base_url}/models/raspberry-preview"
    payload = {
        "text": source_text,
        "openai_api_key": client.api_key,
        "customization": customization,
        "graph": graph
    }
    headers = {
        "Authorization": f"Bearer {client.auth_token}",
        "Content-Type": "application/json"
    }
    print(f"Building graph for text: {payload}")
    try:
        with requests.post(url, json=payload, headers=headers, stream=True) as response:
            response.raise_for_status()
            final_response = None
            for line in response.iter_lines():
                if line:
                    try:
                        decoded_line = line.decode('utf-8').strip()
                        if not decoded_line:
                            continue
                        data = json.loads(decoded_line)
                        status = data.get("status")
                        if status == "completed":
                            final_response = data
                            break
                    except json.JSONDecodeError as e:
                        logging.error("Failed to parse JSON line: %s", e)
                        logging.debug("Line content: %s", decoded_line)
            if final_response:
                return final_response
            else:
                raise ValueError("Server Error: Did not receive a completed response. You can only use GEMINI api keys right now. Can also be because of too much context, try to reduce the chunk.")
    except requests.HTTPError as e:
        raise e from None
    except requests.Timeout:
        raise e from None
    except requests.RequestException as e:
        raise e from None