from flask import Flask, request, Response
import requests

app = Flask(__name__)

DEFAULT_TARGET_URL = 'https://api.novelai.net'
SPECIAL_TARGET_URL = 'https://image.novelai.net'
SPECIAL_PATH = '/ai/generate-image'

domain1 = "api.novelai.net"
domain2 = "image.novelai.net"

proxies = {
    "http":"http://127.0.0.1:7890",
    "https":"http://127.0.0.1:7890"
}

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy(path):
    if path == SPECIAL_PATH.strip('/'):
        target_url = SPECIAL_TARGET_URL
        headers = dict(request.headers)
        headers["Host"] = domain2
        
    else:
        target_url = DEFAULT_TARGET_URL
        headers = dict(request.headers)
        headers["Host"] = domain1
        
    request.headers["Host"]

    if request.method == 'GET':
        resp = requests.get(f'{target_url}/{path}', params=request.args,proxies=proxies,headers=headers)
    elif request.method == 'POST':
        print(request.json)
        print(headers)
        resp = requests.post(f'{target_url}/{path}', json=request.json,proxies=proxies,headers=headers)
        
    elif request.method == 'PUT':
        resp = requests.put(f'{target_url}/{path}', json=request.json,proxies=proxies,headers=headers)
    elif request.method == 'DELETE':
        resp = requests.delete(f'{target_url}/{path}',)
    elif request.method == 'PATCH':
        resp = requests.patch(f'{target_url}/{path}', json=request.json,proxies=proxies,headers=headers)
    else:
        return 'Unsupported HTTP method', 405

    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    return_headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
    print(return_headers)
    response = Response(resp.content, resp.status_code, return_headers)
    return response


if __name__ == '__main__':
    app.run(host="0.0.0.0")