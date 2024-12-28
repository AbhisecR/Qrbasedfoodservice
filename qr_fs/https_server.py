import http.server
import ssl

server_address = ('localhost', 4443)  # You can change the port if needed
httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
httpd.socket = ssl.wrap_socket(httpd.socket, certfile='cert.pem', keyfile='key.pem', server_side=True)

print("Serving on https://localhost:4443")
httpd.serve_forever()
