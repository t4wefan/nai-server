from flask import Flask, request,jsonify
from loguru import logger

import threading

from new_utils import generate_image

app = Flask(__name__)

lock = threading.Lock()

@app.route('/sdapi/v1/txt2img', methods=['POST'])
def txt2img():
    logger.info("new request received")
    lock.acquire()
    logger.info("generating image")
    
    request_json = request.get_json()

    # 如果请求中没有 JSON 数据，返回错误响应
    if request_json is None:
        return jsonify({"error": "No JSON data provided"}), 400

    # 将 JSON 数据转换为字典
    data_dict = request_json
    
    # 这里可以对字典进行进一步处理
    sample_prompt = data_dict["prompt"]
   
    if "negative_prompt" in data_dict:
        n_prompt = data_dict['negative_prompt']
    else:
        n_prompt = ''
        
    uc_str = n_prompt + "weibo_username" 

    
    print(data_dict)
    
    if "enable_hr" in data_dict:
        print("\033[33mSource: outsider request \033[0m")
    else:
        print("\033[32mSource: insider request \033[0m")
        
    try:
        # api_inst = API()
        return_data = generate_image(prompt=sample_prompt,negative_prompt=uc_str,resolution=[832,1216])
        lock.release()
        
    except:
        return_data = generate_image(prompt=sample_prompt,negative_prompt=uc_str,resolution=[832,1216])
        lock.release()
        
    finally:
        return return_data
    

if __name__ == '__main__':
    # 启动 Flask 应用
    app.run(host='0.0.0.0', port=9090)
