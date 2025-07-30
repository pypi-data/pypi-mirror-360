#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : openai_siliconflow
# @Time         : 2024/6/26 10:42
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :
import os

from meutils.pipe import *
from openai import OpenAI
from openai import OpenAI, APIStatusError

client = OpenAI(
    base_url=os.getenv("FFIRE_BASE_URL"),
    api_key=os.getenv("FFIRE_API_KEY")
)

completion = client.chat.completions.create(
    model="deepseek-r1",
    # model="deepseek-reasoner",
    messages=[
        {"role": "user", "content": 'hi'}
    ],
    # top_p=0.7,
    top_p=None,
    temperature=None,
    # stream=True,
    max_tokens=1000
)
