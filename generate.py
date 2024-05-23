import requests
import json
import os
import base64
import argparse
import time
import uuid

def send_request_to_server(prompt, negative_prompt):
    
    url = 'https://api.draw.t4wefan.pub/sdapi/v1/txt2img'
    
    # 构建请求数据
    data = {
        'prompt': prompt,
        'negative_prompt': negative_prompt
    }
    
    print('Sending request to server...')
    start_time = time.time()
    response = requests.post(url, json=data)
    
    end_time = time.time()
    print(f"Generation time: {end_time-start_time}")
    
    if response.status_code == 200:
        result = response.json()
        print('Response from server received.')
        print(result["censor"])
        return result
    else:
        print(f'Failed to get response from server. Status code: {response.status_code}')
        print(f'Error message: {response.text}')
        return None

def save_images_from_response(response):
    images = response.get('images', [])
    
    if not images:
        print('No images found in the response.')
        return
    
    os.makedirs('generated_images', exist_ok=True)
    
    for idx, img_data in enumerate(images):
        
        image_id = str(uuid.uuid4())
        
        # img_filename = os.path.join('generated_images', f'image_{image_id}.png')
        img_filename = os.path.join('generated_images', f'image_{idx+1}.png')
        with open(img_filename, 'wb') as img_file:
            img_file.write(base64.b64decode(img_data))
        print(f'Saved image {img_filename}')

def main():
    parser = argparse.ArgumentParser(description='Generate images using a prompt')
    parser.add_argument('prompt', type=str, help='The prompt text')
    parser.add_argument('--uc', type=str, help='The negative prompt text', default='')

    args = parser.parse_args()
    
    prompt = args.prompt
    negative_prompt = args.uc
    
    result = send_request_to_server(prompt, negative_prompt)
    
    if result:
        save_images_from_response(result)
        print('Images saved successfully.')
    else:
        print('Failed to generate images.')

if __name__ == '__main__':
    main()