import os
import threading
import tempfile
import json
import webbrowser
from flask import Flask, request, send_from_directory


class MedusaDesigner:
    """
    Launches a local HTTP server to serve the MedusaDesigner frontend and
    captures the designed graph as JSON at the specified output_path.
    """
    def __init__(self, port: int = 5000, output_path: str = None):
        # Determine static folder within the package
        import pkg_resources
        static_folder = pkg_resources.resource_filename(__name__, 'static')

        self.port = port
        # If no output_path specified, create a temporary file
        self.output_path = output_path or os.path.abspath(
            tempfile.mktemp(suffix='.json', prefix='medusa_design_')
        )

        # Flask app serving static files and POST endpoint
        self._ready = threading.Event()
        self.app = Flask(__name__, static_folder=static_folder, static_url_path='')
        self._setup_routes()

    def _setup_routes(self):
        @self.app.route('/')
        def index():
            # Serve the main HTML
            return send_from_directory(self.app.static_folder, 'index.html')

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

            # signal the main thread and return
            self._ready.set()
            return {'status': 'ok'}            

    def new_design(self) -> str:
        """
        Starts the server in a background thread, opens the browser to the UI,
        waits until the JSON is saved, then returns the path to the JSON file.
        """
        # # Start Flask in a thread (disable reloader)
        # server_thread = threading.Thread(
        #     target=self.app.run,
        #     kwargs={
        #         'port': self.port,
        #         'debug': False,
        #         'use_reloader': False
        #     },
        #     daemon=True
        # )
        # server_thread.start()

        # # Open default browser
        # webbrowser.open(f'http://localhost:{self.port}')

        # # Wait until the JSON file is created
        # import time
        # while not os.path.exists(self.output_path):
        #     time.sleep(0.1)

        # # Optionally join thread (server has been shut down)
        # server_thread.join()
        # return self.output_path
        # Start Flask in a daemon thread
        threading.Thread(
            target=self.app.run,
            kwargs={
                'port': self.port,
                'debug': False,
                'use_reloader': False
            },
            daemon=True
        ).start()

        # Open the browser to the UI
        webbrowser.open(f'http://localhost:{self.port}')

        # Block here until /submit has been called
        self._ready.wait()
        return self.output_path
