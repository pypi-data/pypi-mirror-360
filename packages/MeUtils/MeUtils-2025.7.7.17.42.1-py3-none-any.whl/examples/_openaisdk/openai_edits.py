#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : openai_edits
# @Time         : 2025/6/23 16:51
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 

from meutils.pipe import *

from openai import OpenAI

client = OpenAI()

r = client.images.edit(
    model="4x-UltraSharp",
    prompt="",
    image=open("/Users/betterme/PycharmProjects/AI/MeUtils/examples/img.png", "rb"),
    response_format="url"
)


# import requests
#
# API_URL = "https://ai.gitee.com/v1/images/upscaling"
# API_TOKEN = "5PJFN89RSDN8CCR7CRGMKAOWTPTZO6PN4XVZV2FQ"
# headers = {
# 	"Content-Type": "application/json",
# 	"Authorization": f"Bearer {API_TOKEN}"
# }
#
# def query(payload):
# 	response = requests.post(API_URL, headers=headers, data=payload)
# 	return response.content
#
# output = query({
# 	"prompt": "变成一幅油画",
# 	"model": "AnimeSharp",
# 	"model_name": "4x-UltraSharp",
# 	"outscale": 4,
# 	"image_url": "https://juzhen-1318772386.cos.ap-guangzhou.myqcloud.com/mj/2025/05/07/25fc47e6-ed58-482b-bb14-a3df00d9b92c.png",
# 	"output_format": "png"
# })
#
# with open("output.png", "wb") as file:
# 	file.write(output)