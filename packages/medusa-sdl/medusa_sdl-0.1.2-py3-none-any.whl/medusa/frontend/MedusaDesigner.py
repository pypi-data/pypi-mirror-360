import os
from pathlib import Path
import threading
import tempfile
import json
import webbrowser
import requests
import time
from flask import Flask, request, send_from_directory, jsonify
from typing import Optional, Callable, Dict, Tuple, Union
from importlib.resources import files

from ..utils.FileHandling import load_json


class MedusaDesigner:
    """
    Launches a local HTTP server to serve the MedusaDesigner frontend and
    captures the designed graph as JSON at the specified output_path.
    """
    def __init__(self, port: int = 5000, output_path: str = None, template: Dict = None):
        # Determine static folder within the package
        # import pkg_resources
        # static_folder = pkg_resources.resource_filename(__name__, 'static')
        # static_folder = os.path.join(os.path.dirname(__file__), "static")
        self.static_folder = Path(files(__package__))/"static"
        self.port = port
        
        self._update_output(output_path=output_path)
        self._load_template(template=template)

        # Flask app serving static files and POST endpoint
        self._ready = threading.Event()
        self._exit_requested = threading.Event()
        self._server_thread = None
        self.app = Flask(__name__, static_folder=self.static_folder, static_url_path='')
        self._setup_routes()

    def _load_template(self, template: Dict):
        if template is None:
            template = load_json(self.static_folder/"default_design.json")
        self.template = template

    def _update_output(self, output_path: Union[Path, str]):
        if output_path is None:
            output_path = tempfile.mktemp(suffix='.json', prefix='medusa_design_')
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)

    def _setup_routes(self):
        @self.app.route('/')
        def index():
            # Serve the main HTML
            return send_from_directory(self.app.static_folder, 'index.html')
        
        @self.app.route('/template')
        def get_template():
            return jsonify(self.template)

        @self.app.route('/<path:filename>')
        def static_files(filename):
            # Serve JS, CSS, icons, etc.
            return send_from_directory(self.app.static_folder, filename)

        @self.app.route('/submit', methods=['POST'])
        def submit_graph():
            # Receive the JSON payload and write to file
            data = request.get_json(force=True)
            with open(self.output_path, 'w') as f:
                json.dump(data, f, indent=2)

            # # Shut down the Flask server
            # shutdown = request.environ.get('werkzeug.server.shutdown')
            # if shutdown:
            #     shutdown()
            shutdown: Optional[Callable] = request.environ.get('werkzeug.server.shutdown')
            if callable(shutdown):
                shutdown()

            # signal the main thread and return
            self._ready.set()
            return {'status': 'ok'}       

        @self.app.route('/exit', methods=['POST'])
        def handle_exit():
            # shutdown_func = request.environ.get('werkzeug.server.shutdown')
            self._exit_requested.set()
            self._ready.set()
            return jsonify({'status': 'exiting...'}) 

        @self.app.route('/shutdown', methods=['POST'])
        def shutdown():
            func = request.environ.get('werkzeug.server.shutdown')
            if func:
                func()
            return 'Server shutting down...'

    def shutdown_server(self):
        if self._server_thread and self._server_thread._is_alive():
            requests.post(f"http://localhost:{self.port}/shutdown")
            self._server_thread.join(timeout = 2)

    def new_design(self) -> str:
        """
        Starts the server in a background thread, opens the browser to the UI,
        waits until the JSON is saved, then returns the path to the JSON file.
        """
        self._server_thread = threading.Thread(
            target=self.app.run,
            kwargs={
                'port': self.port,
                'debug': False,
                'use_reloader': False
            },
            daemon=True
        )
        self._server_thread.start()
        time.sleep(0.5)

        # Open the browser to the UI
        webbrowser.open(f'http://localhost:{self.port}')

        # Block here until /submit has been called
        self._ready.wait()
        self._server_thread.join()

        self.shutdown_server()

        if self._exit_requested.is_set():
            return None

        return self.output_path
    
