#coding=utf-8
#!/usr/bin/python
# -*- coding:utf-8 -*-
# @author  : 刘立军
# @time    : 2025-01-03
# @Description: 生成和验证图形验证码。
# @version : V0.5

from PIL import Image, ImageDraw, ImageFont
from random import randint, choices
from datetime import datetime

def _generate_captcha_text(length=5):
    return ''.join(choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=length))

# 生成验证码
def generate_captcha():
    # 生成唯一ID作为验证码标识
    captcha_id = f"{int(datetime.now().timestamp() * 1000)}{randint(1000, 9999)}"
    captcha_text = _generate_captcha_text()
    captcha_image = _generate_captcha_image(captcha_text)
    return captcha_id,captcha_text,captcha_image

# 创建随机颜色
def _random_color():
    """
        生成随机颜色
        :return:
        """
    return randint(150, 235), randint(150, 235), randint(150, 235)

def _generate_captcha_image(captcha_text):
    
    image_width, image_height = 150, 40
    font_size: int = 25
    mode: str = 'RGB'
    character_length = len(captcha_text)

    # 创建一个白色背景的图像
    image = Image.new(mode, (image_width, image_height), 'white')
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=font_size)

    # 绘制验证码文字
    for i, char in enumerate(captcha_text):
        x = 5 + i * (image_width-5)/(character_length)
        y = randint(-5, 5)
        draw.text((x, y), text=char, font=font, fill=_random_color())

    # 添加干扰线
    for _ in range(10):  
        start = (randint(0, image_width), randint(0, image_height))
        end = (randint(0, image_width), randint(0, image_height))
        draw.line([start, end], fill=_random_color(), width=1)

    # 写干扰点
    for _ in range(150):        
        draw.point([randint(0, image_width), randint(0, image_height)], fill=_random_color())

    for _ in range(10):
        # 写干扰圆圈
        x = randint(0, image_width)
        y = randint(0, image_height)
        radius = randint(2, 4)
        draw.arc((x-radius, y-radius, x + radius, y + radius), 0, 360, fill=_random_color())

    return image


if __name__ == "__main__":
    c_id,c_text,c_imge = generate_captcha()
    print(c_id,c_text)