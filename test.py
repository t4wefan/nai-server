import requests

json = {
    "prompt":"1girl"
}

data = requests.post("http://192.168.1.85:9090/sdapi/v1/txt2img",json=json)

# struct:dict = data.content

print(data)