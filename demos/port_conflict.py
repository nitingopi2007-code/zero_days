from http.server import HTTPServer, SimpleHTTPRequestHandler
HTTPServer(("", 80), SimpleHTTPRequestHandler).serve_forever()
