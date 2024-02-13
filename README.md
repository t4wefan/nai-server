# NAI-server

## 填`nai.py`

```python
NAI_USERNAME = "**********@qq.com"
NAI_PASSWORD = "************"

nai_proxy = "http://127.0.0.1:7890" # 根据自己的梯子改
```

## 装依赖

```bash
pip install -r requirements.txt
```

## server启动

```bash
python server.py
```

## 请求用法

示例用py请求

``` python
import requests

url = 'http://your.server.address/sdapi/v1/txt2img'

post_json = {
    "prompt":"enter your prompt here"
}

return_json = requests.post(url,json=post_json).json
image_b64 = return_json["images"][0]

```
