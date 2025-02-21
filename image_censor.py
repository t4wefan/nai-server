import requests
import time
import hashlib
import os
import base64
import io

from PIL import Image, ImageFilter
from datetime import datetime


img_url_base = "http://192.168.1.16:8097/temp"

classify_server = "http://192.168.1.43:3000/classify"

safety_checker = "http://192.168.1.43:51317/check_safety"


def save_base64_image(base64_str):
    # 解码base64字符串
    image_data = base64.b64decode(base64_str)
    
    # 获取当前时间，格式为：年-月-日_时-分-秒
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
    
    # 定义文件名和路径
    file_name = f"{current_time}.png"
    
    # 将解码后的数据写入文件
    with open(f"images/{file_name}", "wb") as file:
        file.write(image_data)


def is_nsfw(img_b64: str):
    start_time = time.time()  # Record the start time
    
    # Decode the Base64 string into binary data
    image_data = base64.b64decode(img_b64)
    
    # Store the binary data in a BytesIO object
    image_file = io.BytesIO(image_data)
    image_file.name = 'image.png'  # Set the file name
    
    # Create a multipart/form-data dictionary
    files = {'image': image_file}
    
    # Send a POST request
    response = requests.post(classify_server, files=files)
    
    response = response.json()
    
    result = {
        "is_nsfw": False,
        "raw_result": response
    }
    
    if response["porn"] > 0.7 or response["hentai"] > 0.9:
        result["is_nsfw"] = True
    
    end_time = time.time()  # Record the end time
    elapsed_time = end_time - start_time  # Calculate elapsed time
    
    print(f"classify time: {elapsed_time:.2f}")  # Print execution time in English
    
    return result

def is_nsfw_2(img_b64: str):
    start_time = time.time()  # Record the start time
    
    # Decode the Base64 string into binary data
    # image_data = base64.b64decode(img_b64)
    
    # Store the binary data in a BytesIO object
    # image_file = io.BytesIO(image_data)
    # image_file.name = 'image.png'  # Set the file name
    
    # Create a multipart/form-data dictionary
    files = {'image': img_b64}
    
    # Send a POST request
    response = requests.post(safety_checker,json=files)
    
    response = response.json()
    
    result = {
        "is_nsfw": False,
        "raw_result": response
    }
    
    for i in response["concept_scores"]:
        if i > 0.019:
            result["is_nsfw"]=True
            break
        
    end_time = time.time()  # Record the end time
    elapsed_time = end_time - start_time  # Calculate elapsed time
    
    print(f"classify time: {elapsed_time:.2f}")  # Print execution time in English
    
    return result


def apply_gaussian_blur(base64_str: str, radius=20):
    # 解码base64字符串为字节
    image_data = base64.b64decode(base64_str)
    
    # 将字节数据转换为图像
    image = Image.open(io.BytesIO(image_data))
    
    # 应用高斯模糊
    blurred_image = image.filter(ImageFilter.GaussianBlur(radius))
    
    # 将图像转换为字节数据
    buffered = io.BytesIO()
    blurred_image.save(buffered, format="PNG")
    blurred_image_bytes = buffered.getvalue()
    
    # 编码字节数据为base64字符串
    blurred_base64_str = base64.b64encode(blurred_image_bytes).decode('utf-8')
    
    return blurred_base64_str

def classify_pipeline(response: dict):
    image_b64 = response["images"][0]
    save_base64_image(image_b64)
    nsfw_status:dict = is_nsfw(image_b64)
    print(nsfw_status)
    if nsfw_status["is_nsfw"]:
        image_b64 = apply_gaussian_blur(image_b64)
    
    result_dict = response
    result_dict["images"][0] = image_b64
    result_dict["censor"] = nsfw_status
    return result_dict

def classify_pipeline_2(response: dict):
    image_b64 = response["images"][0]
    nsfw_status:dict = is_nsfw_2(image_b64)
    print(nsfw_status)
    if nsfw_status["is_nsfw"]:
        image_b64 = apply_gaussian_blur(image_b64)
    
    result_dict = response
    result_dict["images"][0] = image_b64
    result_dict["censor"] = nsfw_status
    return result_dict