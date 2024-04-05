from flask import Flask, request
import requests
import json
import os
from datetime import datetime

import time

app = Flask(__name__)
os.makedirs('requests', exist_ok=True)

connection_count = 0

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/sdapi/v1/txt2img', methods=['GET', 'POST'])


def forward():
    global connection_count
    while connection_count > 1:
        time.sleep(0.1)

    connection_count = connection_count +1
    
    if request.method in ['POST']:
        data = request.get_json(force=True) if request.data else request.form.to_dict()

        if not os.path.exists('preset/index.json'):
            with open('preset/index.json', 'w') as f:
                json.dump({'prompt': '', 'negative_prompt': '', 'steps': '', 'width': '', 'height': '', 'batch_size': 1, 'sampler_index': 'Euler'}, f)

        with open('preset/index.json') as f:
            preset = json.load(f)

        # Change batch_size to 1 if exists
        if 'batch_size' in data:
            data['batch_size'] = 1

        post_data:dict = {"source":"outsider",
                          "enable_hr":True}
        # post_data['prompt']= data
        
        
        if 'prompt' in data :
            post_data['prompt'] =  preset['prompt'] + data['prompt']

        # if 'negative_prompt' in data :
        #     post_data['negative_prompt'] = preset['negative_prompt']

        print('--------- START OF REQUEST DATA ---------')
        print(json.dumps(post_data, indent=4))
        print('---------- END OF REQUEST DATA ----------')

        url = f'https://api.rryth.com:42421'
        print(f"URL for the request made to the server: {url}")

        req_id = datetime.now().strftime('%Y%m%d%H%M%S')
        with open(f'requests/{req_id}.json', 'w') as f:
                json.dump(post_data, f)

        response = requests.request(request.method, url, json=post_data, timeout=2000,headers={'api': 'LCM' })
        connection_count = connection_count - 1 
        return response.content, response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7871)