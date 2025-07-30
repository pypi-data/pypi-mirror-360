import os
from pathlib import Path
from flask import jsonify

from atlaz.io_operations.directory_tree import build_directory_tree_json, make_paths_relative

def handle_get_directory_tree():
    root_path = Path.cwd()
    ignore_items = {'__pycache__', 'node_modules', '.git', '.venv', 'venv', 'build', 'dist', 'atlaz.egg-info','atlaz_overview.txt', 'LICENSE', 'MANIFEST.in'}
    
    # Original default unmarked items
    default_unmarked = ['.gitignore', 'docker-compose.yml', '__pycache__', 'x_deploy.md', 'tests', 'setup.cfg', 'prompts', 'old_files', 'pyproject.toml', 'requirements.txt', 'setup.cfg', 'prompts', 'start_servers.py', 'overview.py', 'overview_test.py', 'testing2.py']
    
    # Get all items in the root directory
    tree_json = build_directory_tree_json(root_path, ignore=ignore_items, max_depth=20)
    tree_json_relative = make_paths_relative(tree_json, root_path)
    
    # Add all root-level items to default_unmarked
    for item in tree_json_relative:
        item_path = item['path']
        # Check if the item is directly in the root (no directory separators)
        if '/' not in item_path and '\\' not in item_path:
            if item_path not in default_unmarked:
                default_unmarked.append(item_path)
    
    return jsonify({
        "tree": tree_json_relative,
        "default_unmarked": default_unmarked
    })