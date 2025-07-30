import os
import threading
from livereload import Server
from importlib import resources

def start_dev_server(port=8000, open_browser=True):
    """
    Start a Livereload server in a background thread so we don't block
    the rest of the code from continuing.
    """
    server = Server()
    frontend_pkg = resources.files("atlaz.frontend")
    index_html = frontend_pkg / "index.html"
    frontend_dir = str(frontend_pkg)
    frontend_dir = os.path.dirname(__file__)
    server.watch(os.path.join(frontend_dir, "*.html"))
    server.watch(os.path.join(frontend_dir, "styles", "*.css"))
    server.watch(os.path.join(frontend_dir, "scripts", "*.js"))
    server.watch(os.path.join(frontend_dir, "files.json"))
    server.watch(os.path.join(frontend_dir, "explanation.txt"))
    def run_server():
        delay = 1 if open_browser else None
        server.serve(root=frontend_dir, port=port, open_url_delay=delay, default_filename=index_html.name)
    t = threading.Thread(target=run_server, daemon=True)
    t.start()