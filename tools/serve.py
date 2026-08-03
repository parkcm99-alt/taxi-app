import os, http.server, socketserver
os.chdir("/Users/parkyoungsun/Desktop/taxi-app")
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("127.0.0.1", 8765), http.server.SimpleHTTPRequestHandler) as h:
    print("serving on http://127.0.0.1:8765")
    h.serve_forever()
