from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import requests
import sys
import os

arozRequestEndpoint = "http://localhost:8080/api/ajgi/interface"
serverPort = 8000

def getMime(filename):
    ext = filename.split(".").pop()
    if ext == "png" or ext == "jpg" or ext == "jpeg" or ext == "gif":
        return "image/" + ext
    elif ext == "html" or ext == "htm":
        return "text/" + ext
    
    return "application/" + ext
    
def resolveVirtualPath(path, token):
    # Create an AGI script to perform a specific operation on ArozOS
    # For example, this script get the user's desktop path on host file system
    script = ""
    script += 'var abspath = decodeAbsoluteVirtualPath("' + path + '");'
    script += 'sendResp(abspath);'
    
    # Put the script into the POST request payload
    payload = {'script':script}
    
    # Post the script with the token to ArozOS
    session = requests.Session()
    resp = session.post(arozRequestEndpoint + "?token=" + token, data = payload)
    print(resp.content.decode('UTF-8'))
    
    # Return as a simple JSON string (Replace \\ with / for Windows)
    return '"' + str(resp.content.decode('UTF-8')).replace("\\", "/") + '"'

class Router(BaseHTTPRequestHandler):
    def do_GET(self):
        # Get the request token and username from the request header
        username = self.headers.get('aouser') # This is the username of the requesting user
        token = self.headers.get('aotoken') # This is the token for requesting ArozOS for futher file operation / information
        
        print("Req: " + self.path + " by " + username)
        if self.path == "/":
            self.path = "/index.html"
        if self.path == "/api":
            # Demo for getting information from the ArozOS AGI gateway
            resp = resolveVirtualPath("user:/Desktop", token);
            self.send_response(200)
            self.send_header('Content-type',"application/json")
            self.end_headers()
            self.wfile.write(bytes(str(resp), "utf-8"))
            return
        if os.path.exists("web" + self.path):
            # Serve the file
            self.send_response(200)
            self.send_header('Content-type',getMime(self.path))
            self.end_headers()
            f = open("web" + self.path, 'rb')
            self.wfile.write(f.read())
            f.close()
            return
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.wfile.write(bytes("404 Not Found", "utf-8"))
            return
        return
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))

if __name__ == "__main__":
    # Parse the input from ArozOS
    # ArozOS will pass in port and parent calling endpoint and parsed by the start.sh / start.bat
    # print(sys.argv)
    if (len(sys.argv) > 1):
        serverPort = int(sys.argv[1][1:])
        arozRequestEndpoint = sys.argv[2]
    
    
    webServer = HTTPServer(("localhost", serverPort), Router)
    print("PyServer started http://%s:%s" % ("localhost", serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("PyServer stopped.")
