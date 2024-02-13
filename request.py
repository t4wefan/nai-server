import requests

import base64
from PIL import Image
from io import BytesIO
import os

import uuid

def save_base64_image(base64_string, output_folder='./images'):
    # 检查输出文件夹是否存在，如果不存在，则创建
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    try:
        # 解码base64字符串
        image_data = base64.b64decode(base64_string)
        # 将字节数据转换为图像
        image = Image.open(BytesIO(image_data))
        
        # 生成UUID作为文件名
        file_name = str(uuid.uuid4())
        
        # 构建输出文件路径
        output_path = os.path.join(output_folder, f'{file_name}.png')
        
        # 保存图像到文件
        image.save(output_path)
        
        print(f'图像已保存到 {output_path}')
    except Exception as e:
        print(f'发生错误: {str(e)}')


url = 'http://127.0.0.1:9090/sdapi/v1/txt2img'

post_json = {
    "prompt":"nai 1girl,cat ears,anime style,white long hair,full body,loli,potrait,nai night scape,masterpiece,in classroom,white legwear,((sunny out side)), best quality,solo,momoko,cat ears,in seat,solo,morning,indoor,cinematic lighting, looking at window, long hair, sitting on school chair,school desk, hair ornament, hair flower, cute, white flower,light blue coat,white dress,cinematic lighting,white tail"
}

print("requesting")

return_json = requests.post(url,json=post_json).json()
image_b64 = return_json["images"][0]

save_base64_image(base64_string=image_b64)
print('image saved')
