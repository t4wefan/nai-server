print("initializing")

import asyncio,pathlib,uuid
from flask import Flask, request,jsonify
from loguru import logger
from os import environ as env
from api import API
import base64
import os
# import string
from novelai_api.ImagePreset import ImagePreset,ImageResolution,UCPreset,ImageModel,ImageSampler
from nai import *
import time

import random

request_count = 0
fallback_count = 0

last_request = None

# 使用的库 https://github.com/Aedial/novelai-api


def save_string_to_txt(input_string, output_folder='./txt'):
    # 创建输出文件夹（如果不存在）
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 提取文件名，前5个字符并去除标点符号
    file_name = ''.join(char for char in input_string[:5] if char.isalnum())
    
    # 构建文件路径
    file_path = os.path.join(output_folder, f'{file_name}.txt')

    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(input_string)

new_variables = {'NAI_USERNAME': NAI_USERNAME, 'NAI_PASSWORD': NAI_PASSWORD}
os.environ.update(new_variables)

save_dir = pathlib.Path("./sample_image")
save_dir.mkdir(exist_ok=True)

#sample_prompt = "luo tianyi,artist: {artist}, 1girl,solo,grey hair, green eyes, standing"
#preset_str = "[artist:ningen_mame],artist:ciloranko,[artist:sho_(sho_lwlw)],[[tianliang duohe fangdongye]],[artist:rhasta]},year 2023,  best quality, amazing quality, very aesthetic, absurdres, best quality, amazing quality, very aesthetic, absurdres"


# preset 还可以改其它的信息

print("starting server")


# async def wait_for_connection():
#     while True:
#         if connection_count > 0 :
#             print(f"waiting {connection_count} generation......")
#             time.sleep(3)
#         else :

#             break


# api_inst.api.proxy = nai_proxy


async def generate(sample_prompt,preset_str,uc_str):
    api_inst = API()
    preset = ImagePreset()
    # global preset
    
    
    preset.scale = 6.5
    preset.n_samples = 1
    
    random_res = random.choice([1152,1216])
    
    from fallback import check_potrait
    
    # if check_private(input_str=sample_prompt):
    #     # return_data = await async_get_private_image(prompt=sample_prompt,negative_prompt=uc_str)
    #     return return_data
        
    if check_potrait(input_str=sample_prompt):
        preset.resolution = (832, random_res)
        print("Size: potrait")
    else:
        preset.resolution = (random_res, 832)
        print("Size: landscape")
        from fallback import process_string
        sample_prompt = process_string(input_str=sample_prompt,remove_list=['landscape',])
    
        
    preset.uc_preset = UCPreset.Preset_Heavy 
    preset.quality_toggle = True
    preset.smea = True
    preset.uc = uc_str
    # preset.sampler = ImageSampler.k_euler

    
    async with api_inst as api_handler:
    
        # uuid_str = uuid.uuid1()
        
        api = api_handler.api
        
        prompt = preset_str + sample_prompt
        #save_address = save_dir / f"image_{uuid_str}.png" # 给生成的图片添加随机后缀
            
        
            
        logger.info(f"satrting generation")
        try:
            async for img in api.high_level.generate_image(prompt, ImageModel.Anime_v3, preset):
                # img = api.high_level.generate_image(prompt, ImageModel.Anime_v3, preset)
                # 如果你想要将图像保存到文件，请取消注释下面的行
                # save_address.write_bytes(img) 
                
                # 将图像转换为base64编码的字符串
                b64_str = base64.b64encode(img[1]).decode('utf-8')
                #connection_count = connection_count - 1
                logger.info(f"generation complete")
                return b64_str
            
            # 可以在这里做一些操作，比如打印base64字符串或者将其传递给其他函数
                
        except Exception as e:
            print(f"发生错误: {e}")
            global connection_count
            # connection_count = connection_count - 1
            logger.error(f"generation failed")
            if "Reached the rate limits for free Opus image generations" in str(e):
                return "rate_limit"
            elif "Concurrent generation requests are not allowed for free Opus generations" in str(e):
                return "concurrent_generation"
            elif "An error occured while generating the image" in str(e):
                return "500"
            else:
                return ''
    

app = Flask(__name__)

connection_count = 0 

@app.route('/sdapi/v1/txt2img', methods=['POST'])
async def txt2img():
    global connection_count 
    
    while True:
        if connection_count > 0 :
            #print(f"waiting {connection_count} generation......")
            await asyncio.sleep(3)
        else :

            break
    
    # global last_request
    
    # if last_request == None:
    #     last_request = time.time()
    
    # time_diff = time.time() - last_request
    # if time_diff < 3:
    #     print(f"sleeping for {time_diff}")
    #     time.sleep(time_diff)
    
    # time.sleep(1)
    # 获取请求的 JSON 数据
    request_json = request.get_json()

    # 如果请求中没有 JSON 数据，返回错误响应
    if request_json is None:
        return jsonify({"error": "No JSON data provided"}), 400

    # 将 JSON 数据转换为字典
    data_dict = request_json
    
    # 这里可以对字典进行进一步处理
    sample_prompt = data_dict["prompt"]
    if "preset" in data_dict:
        preset_str = data_dict["preset"]
    else:
        preset_str = ''
    
    if "negative_prompt" in data_dict:
        n_prompt = data_dict['negative_prompt']
    else:
        n_prompt = ''
        
    uc_str = n_prompt + "weibo_username" 

    connection_count = connection_count + 1
    print(data_dict)
    
    if "enable_hr" in data_dict:
        print("\033[33mSource: outsider request \033[0m")
    else:
        print("\033[32mSource: insider request \033[0m")
    
    from fallback import check_private
    
    if check_private(input_str=sample_prompt):
        b64_str = ''
    
    else:
        try:
            # api_inst = API()
            b64_str = await generate(sample_prompt=sample_prompt,preset_str=preset_str,uc_str=uc_str)
        except Exception:
            print(Exception)
            b64_str = ''
            failed_reason = ''
        
    if b64_str == "rate_limit":
        failed_reason = "rate_limit"
        b64_str = ''
    elif b64_str == "concurrent_generation":
        failed_reason = "concurrent_generation"
        b64_str = ''
    elif b64_str == "500":
        failed_reason = "500"
        b64_str = ''
    elif b64_str == '':
        failed_reason = ''
        b64_str = ''
    
    if check_private(input_str=sample_prompt):
        failed_reason = 'private_generation'
    
    retry_count = 0 
    max_retry_count = 3
    
    while b64_str == '':
        # if retry_count >= max_retry_count or failed_reason == "rate_limit" or failed_reason == '':
            # print(f"request error,trying fallback ({retry_count})")
            # from fallback import async_get_sd_image
            # json_sd = await async_get_sd_image(prompt=sample_prompt,negative_prompt=n_prompt)
            # connection_count = connection_count - 1
            # return jsonify(json_sd)
        
        # elif failed_reason == "private_generation":
        #     # print(f"request error,trying fallback ({retry_count})")
        #     from fallback import async_get_private_image
        #     json_sd = await async_get_private_image(prompt=sample_prompt,negative_prompt=n_prompt)
        #     connection_count = connection_count - 1
        #     return jsonify(json_sd)
        
        if retry_count >= max_retry_count:
            b64_str = ''

        elif failed_reason == '500':
            try:
                failed_reason == ''
                print(f"request error,trying agian in 3s ({retry_count})")
                await asyncio.sleep(3)
                b64_str = await generate(sample_prompt=sample_prompt,preset_str=preset_str,uc_str=uc_str)
                if b64_str == "rate_limit":
                    retry_count = retry_count + 1
                    failed_reason = "rate_limit"
                    b64_str = ''
                elif b64_str == "concurrent_generation":
                    retry_count = retry_count + 1
                    failed_reason = "concurrent_generation"
                    b64_str = ''
                elif b64_str == "500":
                    retry_count = retry_count + 1
                    failed_reason = "500"
                    b64_str = ''
                elif b64_str == '':
                    retry_count = retry_count + 1
                    failed_reason = ''
                    b64_str = ''
            except:
                retry_count = retry_count + 1
                b64_str = ''
        
        elif failed_reason == 'concurrent_generation' and retry_count == 0:
            try:
                failed_reason == ''
                print(f"request error,trying agian in 16s ({retry_count})")
                await asyncio.sleep(16)
                b64_str = await generate(sample_prompt=sample_prompt,preset_str=preset_str,uc_str=uc_str)
                if b64_str == "rate_limit":
                    retry_count = retry_count + 1
                    failed_reason = "rate_limit"
                    b64_str = ''
                elif b64_str == "concurrent_generation":
                    retry_count = retry_count + 1
                    failed_reason = "concurrent_generation"
                    b64_str = ''
                elif b64_str == "500":
                    retry_count = retry_count + 1
                    failed_reason = "500"
                    b64_str = ''
                elif b64_str == '':
                    retry_count = retry_count + 1
                    failed_reason = ''
                    b64_str = ''
            except:
                retry_count = retry_count + 1
                b64_str = ''
        
        else:
            try:
                print(f"request error,trying agian in 8s ({retry_count})")
                await asyncio.sleep(8)
                b64_str = await generate(sample_prompt=sample_prompt,preset_str=preset_str,uc_str=uc_str)
                if b64_str == "rate_limit":
                    failed_reason = "rate_limit"
                    retry_count = retry_count + 1
                    b64_str = ''
                elif b64_str == "concurrent_generation":
                    failed_reason = "concurrent_generation"
                    retry_count = retry_count + 1
                    b64_str = ''
                elif b64_str == "500":
                    failed_reason = "500"
                    retry_count = retry_count + 1
                    b64_str = ''
                elif b64_str == '':
                    failed_reason = ''
                    retry_count = retry_count + 1
                    b64_str = ''
            except:
                retry_count = retry_count + 1
                b64_str = ''

    connection_count = connection_count -1
    return_data = {"images":[b64_str],"info":{"prompt":''}}
    
    
    last_request = time.time()
    
    # preset.negative_prompt = "weibo_username" 
    return jsonify(return_data)

    
    
if __name__ == '__main__':
    # 启动 Flask 应用程序，监听 0.0.0.0:7860
    app.run(host='0.0.0.0', port=9090)
