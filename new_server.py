from flask import Flask, request,jsonify
from loguru import logger

import threading

app = Flask(__name__)

lock = threading.Lock()

@app.route('/sdapi/v1/txt2img', methods=['POST'])
async def txt2img():
    lock.acquire()
    logger.info()