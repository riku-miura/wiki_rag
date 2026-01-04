from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import uuid
import time
import threading

PORT = 3000
sessions = {}

class MockHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        if self.path == '/rag/build':
            content_len = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_len)
            data = json.loads(post_body)
            
            session_id = str(uuid.uuid4())
            sessions[session_id] = "processing"
            
            # Auto-ready after 2 seconds
            def set_ready():
                time.sleep(2)
                sessions[session_id] = "ready"
                print(f"Session {session_id} is now READY")
            threading.Thread(target=set_ready).start()

            self._send_json({
                "session_id": session_id,
                "status": "processing",
                "source_url": data.get('url')
            })

        elif self.path == '/chat/query':
            content_len = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_len)
            data = json.loads(post_body)
            
            self._send_json({
                "session_id": data.get('session_id'),
                "response": "This is a mocked response from the testing server. RAG flow works!",
                "metadata": { "model": "mock-model" }
            })
            
    def do_GET(self):
        if '/status' in self.path:
            # /rag/{id}/status
            parts = self.path.split('/')
            session_id = parts[2]
            status = sessions.get(session_id, "unknown")
            self._send_json({"status": status})
            
        elif '/history' in self.path:
            self._send_json({"history": []})

    def _send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

print(f"Starting Mock API on port {PORT}")
HTTPServer(('localhost', PORT), MockHandler).serve_forever()
