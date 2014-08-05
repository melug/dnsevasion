import socket

from flask import Flask

app = Flask(__name__)

@app.route("/resolve/<domain>/A/")
def resolve(domain, methods=['POST', 'GET']):
    data = socket.gethostbyname(domain)
    return data

if __name__ == '__main__':
    app.run(host='0.0.0.0')

