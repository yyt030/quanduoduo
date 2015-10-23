#!/usr/bin/env python
# coding: utf-8
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import string, random

fontPath = ""


# 获得随机五个字母
def getRandomChar():
    return [random.choice(string.letters) for _ in range(5)]


# 获得颜色
def getRandomColor():
    return (random.randint(30, 100), random.randint(30, 100), random.randint(30, 100))


# 获得验证码图片
def getCodePiture():
    width = 270
    height = 90
    bp = 1
    shadowcolor = 'green'
    bordercolor = (150, 150, 150)
    # 创建画布
    image = Image.new('RGB', (width, height), (255, 255, 255))
    font = ImageFont.truetype('msyh.ttc', 70)
    draw = ImageDraw.Draw(image)
    # 创建验证码对象
    code = getRandomChar()
    # 把验证码放到画布上
    for t in range(5):
        draw.text((40 * t + 10, 0), code[t], font=font, fill=getRandomColor())

        # draw.text((40 * t+10-bp, 0), code[t], font=font, fill=shadowcolor)
        # draw.text((40 * t+10+bp, 0), code[t], font=font, fill=shadowcolor)
        # draw.text((40 * t+10, 0-bp), code[t], font=font, fill=shadowcolor)
        # draw.text((40 * t+10, 0+bp), code[t], font=font, fill=shadowcolor)
    draw.line((0, 0) + (width - 2, 0), fill=bordercolor, width=2)
    draw.line((0, 0) + (0, height - 1), fill=bordercolor, width=2)
    draw.line((0, height - 1) + (width - 1, height - 1), fill=bordercolor, width=2)
    draw.line((width - 1, height - 1) + (width - 1, 0), fill=bordercolor, width=2)

    def create_points():
        '''''绘制干扰点'''
        # chance = min(100, max(0, int(1)))  # 大小限制在[0, 50]

        # for w in xrange(width):
        #     for h in xrange(height):
        #         tmp = random.randint(0, 50)
        #         if tmp > 50 - chance:
        #             draw.point((w, h), fill=getRandomColor())

        for i in range(0, 50):
            w = random.randint(0, width)
            h = random.randint(0, height)
            draw.point((w, h), fill=getRandomColor())

    # 随机画四条线
    for i in range(0, 4):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        draw.line((x1, y1) + (x2, y2), fill=bordercolor, width=1)
    # 填充噪点
    # for _ in range(random.randint(1500, 3000)):
    #     draw.point((random.randint(0, width), random.randint(0, height)), fill=getRandomColor())
    create_points()

    # # 模糊处理
    # image = image.filter(ImageFilter.BLUR)
    # 保存名字为验证码的图片
    # image.save("".join(code) + '.jpg', 'jpeg')
    return image, "".join([s for s in code]).lower()
