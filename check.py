import sys
import base64
import json
import requests

import time


def encode_image_to_base64(image_path):
    """Encode image to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def check_image_safety(base64_image):
    """Send the base64 image to the API and get the safety check result."""
    url = "http://api.t4wefan.pub:51317/check_safety"  # Update this to your actual server URL if different
    headers = {"Content-Type": "application/json"}
    data = {
        "image": base64_image
    }
    json_data = json.dumps(data)
    
    print("Starting request to check image safety...")  # 请求开始打印
    start_time = time.time()
    # print(start_time)

    response = requests.post(url, headers=headers, data=json_data)

    if response.status_code == 200:
        
        end_time = time.time()  # 记录结束时间
        print("Request completed in {:.2f} seconds.".format(end_time - start_time))
        
        return response.json()
    else:
        print("Failed to get a valid response. Status code:", response.status_code)
        return None


def main(image_path):
    """Main function to handle the image safety check."""
    base64_image = encode_image_to_base64(image_path)
    result = check_image_safety(base64_image)
    
    result = json.dumps(result, indent=4, ensure_ascii=False)

    if result:
        print("Response:", result)
    else:
        print("No valid response received.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    main(image_path)