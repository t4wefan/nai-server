import requests
import time
import asyncio
from loguru import logger

def process_string(input_str, remove_list):
    # 将中文逗号替换为英文逗号
    input_str = input_str.replace('，', ',')
    
    # 根据英文逗号拆分字符串
    split_list = input_str.split(',')
    
    
    # 移除在remove_list中出现的元素
    new_list = split_list
    for i in remove_list:
        for j in split_list:
            if i in j:
                new_list.remove(j)
    # new_list = [item for item in split_list if item not in remove_list]
    
    # 将剩余的元素使用英文逗号连接
    result_str = ','.join(new_list)
    
    return result_str

def check_potrait(input_str):
    # 将中文逗号替换为英文逗号
    input_str = input_str.replace('，', ',')
    
    # 根据英文逗号拆分字符串
    split_list = input_str.split(',')
        
    # 移除在remove_list中出现的元素
    new_list = split_list
    for i in new_list:
        if "landscape" in i:
            return False
        else:
            new_list = new_list
    return True

def check_private(input_str):
    # 将中文逗号替换为英文逗号
    input_str = input_str.replace('，', ',')
    
    # 根据英文逗号拆分字符串
    split_list = input_str.split(',')
        
    # 移除在remove_list中出现的元素
    new_list = split_list
    for i in new_list:
        if "lnkasjckd" in i:
            return True
        else:
            new_list = new_list
    return False


def get_sd_image(prompt,negative_prompt):
    
    RED = '\033[91m'
    GREEN = '\033[92m'
    END = '\033[0m'
    
    url = "http://192.168.1.6:7872/sdapi/v1/txt2img"
    
    black_list = ["artist","（","(","{","masterp","nsfw","nud"]
    
    
    post_json = {
        "prompt" : "best quality,amazing quality,very aesthetic,absurdres" + process_string(str(prompt),remove_list=black_list) ,
        "sampler_index": "DPM++ 2M",
        "enable_hr": False,
        "batch_size": 1,
        "negative_prompt": '''((easynegv2)), nsfw, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry,lowres,worst quality,low quality,hand with more than 5 fingers,hand with less than 4 fingers,ad anatomy,bad hands,mutated hands and fingers,extra legs,extra arms,interlocked fingers,duplicate,cropped,text,jpeg artifacts,signature,watermark,username,blurry,artist name,trademark,title,muscular,sd character,multiple view,Reference sheet,long body,malformed limbs,multiple breasts,cloned face,malformed,mutated,bad anatomy,disfigured,bad proportions,duplicate,bad feet,artist name,extra limbs,ugly,fused anus,text font ui,missing limb,nsfw''' + str(negative_prompt),
        "cfg_scale": 5,
        "steps": 20,
        "width": 720,
        "height": 1040,
        "denoising_strength": 0.7,
    }
    
    print("requesting")
    print(post_json)
    response =  requests.post(url,json=post_json,timeout=1000000)
    
    return_code = response.status_code
    if return_code == 200:
        return_json = response.json()
        image_b64 = return_json["images"][0]
        #save_base64_image(base64_string=image_b64,file_name=file_name,output_folder=output_dir)
        return return_json
    
    
def get_private_image(prompt,negative_prompt):
    
    RED = '\033[91m'
    GREEN = '\033[92m'
    END = '\033[0m'
    logger.info(GREEN + f'using private generation' + END)
    url = "http://192.168.1.43:19093/sdapi/v1/txt2img"
    
    black_list = ["lnkasjckd"]
    
    
    post_json = {
        "prompt" : process_string(str(prompt),remove_list=black_list) ,
        "sampler_index": "Euler",
        "negative_prompt":  str(negative_prompt),
        
    }
    if check_potrait(input_str=prompt):
        # preset.resolution = (832, random_res)
        print("Size: potrait")
    else:
        # preset.resolution = (random_res, 832)
        print("Size: landscape")
        
    
    print("requesting")
    print(post_json)
    response =  requests.post(url,json=post_json,timeout=1000000)
    
    return_code = response.status_code
    if return_code == 200:
        return_json = response.json()
        image_b64 = return_json["images"][0]
        #save_base64_image(base64_string=image_b64,file_name=file_name,output_folder=output_dir)
        logger.info(f"generation complete")
        return return_json
     
        
def async_get_sd_image(prompt,negative_prompt):
    loop = asyncio.get_running_loop()

    # 使用 run_in_executor 调用同步函数
    # None 表示使用默认的线程池执行器
    result = loop.run_in_executor(None, get_sd_image, prompt,negative_prompt)
    return result

def async_get_private_image(prompt,negative_prompt):
    loop = asyncio.get_running_loop()

    # 使用 run_in_executor 调用同步函数
    # None 表示使用默认的线程池执行器
    result = loop.run_in_executor(None, get_private_image, prompt,negative_prompt)
    return result

ver = 111
