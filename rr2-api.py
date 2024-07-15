from flask import Flask, request, send_from_directory
import requests
import json
import os
from datetime import datetime

import time

from image_censor import is_nsfw,classify_pipeline_2,classify_pipeline

app = Flask(__name__)
os.makedirs('requests', exist_ok=True)
os.makedirs('temp', exist_ok=True)  # 确保temp目录存在

connection_count = 0
pending_count = 0 

@app.route('/sdapi/v1/txt2img', methods=['GET', 'POST'])
def forward():
    start_time = time.time()
    if request.method in ['POST']:
        data = request.get_json(force=True) if request.data else request.form.to_dict()

        if not os.path.exists('preset/index.json'):
            with open('preset/index.json', 'w') as f:
                json.dump({'prompt': '<lora:jimaXLANI31lokrV43P1:1>', 'negative_prompt': '', 'steps': '', 'width': 832, 'height': 1216, 'batch_size': 1, 'sampler_index': 'Euler'}, f)

        with open('preset/index.json') as f:
            preset = json.load(f)

        post_data:dict = {"source":"outsider", "enable_hr":False,"steps":20,'width': preset["width"], 'height': preset["height"],'sampler_index': preset["sampler_index"],}
        
        if 'prompt' in data :
            post_data['prompt'] =  preset['prompt'] + data['prompt']

        if 'negative_prompt' in data :
            post_data['negative_prompt'] = preset['negative_prompt']

        print('--------- START OF REQUEST DATA ---------')
        print(json.dumps(post_data, indent=4))
        print('---------- END OF REQUEST DATA ----------')

        url = f'http://192.168.1.6:7870/sdapi/v1/txt2img'
        print(f"URL for the request made to the server: {url}")

        req_id = datetime.now().strftime('%Y%m%d%H%M%S')
        with open(f'requests/{req_id}.json', 'w') as f:
                json.dump(post_data, f)

        response = requests.request(request.method, url, json=post_data, timeout=2000)
                
        
        
        end_time = time.time()
        print(f"total request time: {end_time-start_time}")
        if response.status_code == 200:
            result_dict = classify_pipeline(response.json())
            return result_dict, response.status_code
        else:
            return response.content, response.status_code



@app.route('/temp/<path:filename>', methods=['GET'])
def serve_temp_file(filename):
    """
    Serve a file from the temp directory.
    """
    try:
        return send_from_directory('temp', filename)
    except FileNotFoundError:
        return {"error": "File not found"}, 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7871)