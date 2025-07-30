# atlaz/client.py
import logging
import json
from typing import List
import requests  # type: ignore
from pathlib import Path
import getpass

from atlaz.codeGen.code_gen import code_gen_handler
from atlaz.graph.graph import build_graph_handler
from atlaz.frontend.livereload_server import start_dev_server
from atlaz.io_operations.file_mediator import load_files, remove_explanation_file, file_exists, remove_json_files
from atlaz.io_operations.file_utils import read_json, write_json
from atlaz.io_operations.directory_tree import build_directory_tree_string

class AtlazClient:
    def __init__(
        self,
        api_key: str = 'No API key yet',
        llm_provider: str = 'openai',
        model_choice: str = 'gpt-4',
        base_url: str = "https://atlaz-api.com"
    ):
        self.api_key = api_key
        self.llm_provider = llm_provider
        self.model_choice = model_choice
        self.models = ["raspberry"]
        self.auth_token = None
        self.token_file = Path.home() / ".atlaz"
        self.base_url = base_url
        print(f'{self.token_file.exists()=}')
        if file_exists(self.token_file):
            data = read_json(self.token_file)
            self.auth_token = data.get("auth_token")
            if "api_key" in data:
                self.api_key = data["api_key"]
            if "llm_provider" in data:
                self.llm_provider = data["llm_provider"]
            if "model_choice" in data:
                self.model_choice = data["model_choice"]
            logging.info(f"Loaded credentials: {self.api_key=}, {self.llm_provider=}, {self.model_choice=}")
        if not self.auth_token:
            self.authenticate()

    def _save_token(self, token: str):
        """
        Legacy method to save the token. We'll call _save_settings here
        so that we always keep the .atlaz file in sync.
        """
        self.auth_token = token
        self._save_settings()

    def _save_settings(self):
        """
        Write the current auth_token, api_key, llm_provider, and model_choice to ~/.atlaz
        """
        data_to_save = {
            "auth_token": self.auth_token,
            "api_key": self.api_key,
            "llm_provider": self.llm_provider,
            "model_choice": self.model_choice
        }
        logging.info(f"Setting credentials: {self.api_key=}, {self.llm_provider=}, {self.model_choice=}")
        logging.info(f"{self.token_file},{data_to_save=}")
        write_json(data_to_save, self.token_file)
        logging.info(f"Saved credentials to {self.token_file}")

    def set_credentials(self, api_key: str, llm_provider: str, model_choice: str):
        """
        Public method to set the user credentials (API key, provider, model)
        and persist them to .atlaz
        """
        logging.info(f"Setting credentials: {api_key=}, {llm_provider=}, {model_choice=}")
        self.api_key = api_key
        self.llm_provider = llm_provider
        self.model_choice = model_choice
        self._save_settings()

    def authenticate(self):
        print("=== Welcome to Atlaz! ===")
        while True:
            choice = input("Do you want to (1) Login or (2) Create an account? Enter 1 or 2: ").strip()
            if choice == '1':
                login_flag = True
                print("=== Login ===")
                break
            elif choice == '2':
                login_flag = False
                print("=== Create an Account ===")
                break
            else:
                print("Invalid choice. Please enter 1 to Login or 2 to Create an account.")
        email = input("Enter your email: ")
        while True:
            password = getpass.getpass("Enter your password: ")
            if not login_flag:
                password_confirm = getpass.getpass("Confirm your password: ")
                if password != password_confirm:
                    print("Passwords do not match. Please try again.")
                    continue
            break
        login_url = f"{self.base_url}/api/login"
        payload = {"email": email, "password": password, "login": login_flag}
        try:
            response = requests.post(login_url, json=payload)
            if response.status_code == 200:
                data = response.json()
                persistent_token = data.get("persistent_token")
                if persistent_token:
                    self._save_token(persistent_token)
                if not login_flag:
                    print("Account created successfully. You are now logged in.")
                else:
                    print("Logged in successfully.")
            else:
                action = "login" if login_flag else "create an account"
                print(f"Failed to {action}. Status Code: {response.status_code}")
                try:
                    error_message = response.json().get("error", response.text)
                    print(f"Error: {error_message}")
                except json.JSONDecodeError:
                    print(f"Response: {response.text}")
        except requests.RequestException as e:
            logging.error(f"Request failed: {e}")
            print("An error occurred while trying to authenticate.")

    def list_models(self):
        return {"data": [{"id": model} for model in self.models]}

    def generate_code_new(
        self,
        instruction: str,
        selected_files: List[str],
        model_choice: str = None,
        provider: str = None
    ):
        """
        We allow model_choice and provider overrides here. If the user
        doesn't supply them, we use what's in self.
        """
        if not model_choice:
            model_choice = self.model_choice
        if not provider:
            provider = self.llm_provider
        print('selected_files:', selected_files)
        file_contents = load_files(selected_files)
        directory_structure = build_directory_tree_string(selected_files)
        logging.info(f"{instruction=}, {directory_structure=}, {file_contents=}, {model_choice=}, {provider=}")
        if not self.auth_token:
            print("Re-authenticating...")
            self.authenticate()
            if not self.auth_token:
                print("Authentication failed.")
                return
        return code_gen_handler(
            self,
            instruction=instruction,
            directory_structure=directory_structure,
            file_contents=file_contents,
            model_choice=model_choice,
            provider=provider
        )

    def build_graph(self, source_text: str, customization: str = '', graph: dict= None):
        return build_graph_handler(self, source_text, customization, graph)
    
    def start_frontend(self):
        if not self.auth_token:
            print("Re-authenticating...")
            self.authenticate()
            if not self.auth_token:
                print("Authentication failed.")
                return
        remove_json_files()
        remove_explanation_file()
        start_dev_server(port=8000)
        try:
            while True:
                pass  # spin forever
        except KeyboardInterrupt:
            print("Shutting down.")
