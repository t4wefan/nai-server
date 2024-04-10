import requests

from api import *
import random

import io
import zipfile

import base64


def generate_image(prompt: str,negative_prompt: str,resolution: list[int,int]) -> dict["images:":list[str]]:
  
  api = API()
  
  headers = {'Authorization': f'Bearer {sync_login()}' }
  # print(headers)
  
  seed:int = random.randint(11111111,99999999)
  
  generate_template = {
    "input": f"{prompt}, best quality, amazing quality, very aesthetic, absurdres",
    "model": "nai-diffusion-3",
    "action": "generate",
    "parameters": {
      "legacy": False,
      "n_samples": 1,
      "steps": 28,
      "scale": 6.5,
      "uncond_scale": 1.0,
      "controlnet_strength": 1.0,
      "add_original_image": False,
      "cfg_rescale": 0.0,
      "noise_schedule": "native",
      "width": resolution[0],
      "height": resolution[1],
      "seed": seed,
      "extra_noise_seed": seed,
      "negative_prompt": f"{negative_prompt},nsfw, lowres, error, fewer, extra, missing, worst quality, jpeg artifacts, bad quality, watermark, unfinished, displeasing, chromatic aberration, signature, extra digits, artistic error, username, scan, [abstract], weibo_username",
      "sampler": "k_euler",
      "sm": True,
      "sm_dyn": False,
      "dynamic_thresholding": True,
      "qualityToggle": True,
      "ucPreset": 4
    }
  }
  
  print("posting data")

  try:
    post_data = requests.post(url="https://image.novelai.net/ai/generate-image",json=generate_template,headers=headers)
  except:
    raise ConnectionError("can not access novelai")
  
  data_byte:bytearray =  post_data.content
  code = post_data.status_code
  
  if code == 200:
    try:
  
  
      byte_stream = io.BytesIO(data_byte)
      
      with zipfile.ZipFile(byte_stream, 'r') as zip_ref:
        # 提取zip文件中的image_0.png
        data = zip_ref.read('image_0.png')
        
      # with open("image.png","wb") as f:
      #   f.write(data)
        
      b64_str = base64.b64encode(data)
      b64_str = b64_str.decode('utf-8')
      
      return {"images":[b64_str]}
    
    except:
      raise ConnectionError("can not process data")
  
  else:
    raise ConnectionError("error occured")
  


async def async_generate_image(prompt: str,negative_prompt: str,resolution: list[int,int]) -> dict["images:":list[str]]:
  
  api = API()
  
  token = await login()
    
  headers = {'Authorization': f'Bearer {token}' }
  print(headers)
  
  seed:int = random.randint(11111111,99999999)
  
  generate_template = {
    "input": f"{prompt}, best quality, amazing quality, very aesthetic, absurdres",
    "model": "nai-diffusion-3",
    "action": "generate",
    "parameters": {
      "legacy": False,
      "n_samples": 1,
      "steps": 28,
      "scale": 6.5,
      "uncond_scale": 1.0,
      "controlnet_strength": 1.0,
      "add_original_image": False,
      "cfg_rescale": 0.0,
      "noise_schedule": "native",
      "width": resolution[0],
      "height": resolution[1],
      "seed": seed,
      "extra_noise_seed": seed,
      "negative_prompt": f"{negative_prompt},nsfw, lowres, error, fewer, extra, missing, worst quality, jpeg artifacts, bad quality, watermark, unfinished, displeasing, chromatic aberration, signature, extra digits, artistic error, username, scan, [abstract], weibo_username",
      "sampler": "k_dpmpp_2s_ancestral",
      "sm": True,
      "sm_dyn": False,
      "dynamic_thresholding": True,
      "qualityToggle": True,
      "ucPreset": 4
    }
  }
  
  print("posting data")
  
  post_data = requests.post(url="https://image.novelai.net/ai/generate-image",json=generate_template,headers=headers)
  
  data_byte:bytearray =  post_data.content
  code = post_data.status_code
  
  if code == 200:
    try:
  
      byte_stream = io.BytesIO(data_byte)
      
      with zipfile.ZipFile(byte_stream, 'r') as zip_ref:
        # 提取zip文件中的image_0.png
        data = zip_ref.read('image_0.png')
        
      # with open("image.png","wb") as f:
      #   f.write(data)
        
      b64_str = base64.b64encode(data)
      b64_str = b64_str.decode('utf-8')
      
      return {"images":[b64_str]}
    except:
      return ConnectionError
  else:
    return ConnectionError

if __name__ == "__main__":
  print(generate_image(prompt="1girl",negative_prompt="",resolution=[832,1216]))
