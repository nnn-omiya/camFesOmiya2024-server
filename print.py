from escpos.printer import Usb
from escpos import *

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import datetime
import sys

def errorprint():
    draw.text((10,350), "エラーが発生しました。\nエラーコード:"+args[2], font=fontB, fill=0)
    image.show()
    r_print()
    sys.exit()

def r_print():
    p = Usb(0x416, 0x5011, in_ep=0x87, out_ep=0x06)
    p.text("\n")
    p.image(image)
    p.cut()

args = sys.argv

t_delta = datetime.timedelta(hours=9)
JST = datetime.timezone(t_delta, 'JST')
now = datetime.datetime.now(JST)

#HOTTEA_TANKA = 2
STTEA_TANKA = 2
MILKTEA_TANKA = 2

total_price = 0

width = 400
height = 900

image = Image.new('1', (width, height), 255)

#フォント指定
fontSS = ImageFont.truetype('mplus-1m-regular.ttf', 11, encoding='unic')
fontS = ImageFont.truetype('mplus-1m-regular.ttf', 16, encoding='unic')
fontA = ImageFont.truetype('mplus-1m-regular.ttf', 24, encoding='unic')
fontAa = ImageFont.truetype('mplus-1m-regular.ttf', 28, encoding='unic')
fontB = ImageFont.truetype('mplus-1m-regular.ttf', 36, encoding='unic')#小計
fontC = ImageFont.truetype('mplus-1m-regular.ttf', 96, encoding='unic') #注文番号

#イノキャンロゴの表示
ic_logo = Image.open('logo.png')
draw = ImageDraw.Draw(image)
image.paste(ic_logo, (0, 0))

#店名表示
draw.text((10,260), "イノキャン紅茶 大宮キャンパス店", font=fontA, fill=0)
draw.text((10,290), now.strftime('%Y年%m月%d日%H:%M'), font=fontA, fill=0)

if (args[1] == "error"):
    errorprint()

#注文部表示
draw.text((10,310), "--------------------------------", font=fontA, fill=0)
if (int(args[2]) != 0):
    draw.text((10,350), "ｽﾄﾚｰﾄﾃｨｰ(ｱｲｽ)*{0: <3}  {1: >3,}ｶﾞﾘｵﾝ".format(int(args[2]),int(args[2])*STTEA_TANKA), font=fontAa, fill=0)

if (int(args[3]) != 0):
    draw.text((10,390), "ｽﾄﾚｰﾄﾃｨｰ(ﾎｯﾄ)*{0: <3}  {1: >3,}ｶﾞﾘｵﾝ".format(int(args[3]),int(args[3])*STTEA_TANKA), font=fontAa, fill=0)

if (int(args[4]) != 0):
    draw.text((10,430), "ﾐﾙｸﾃｨｰ(ｱｲｽ)*{0: <5}  {1: >3,}ｶﾞﾘｵﾝ".format(int(args[4]),int(args[4])*MILKTEA_TANKA), font=fontAa, fill=0)

if (int(args[5]) != 0):
    draw.text((10,470), "ﾐﾙｸﾃｨｰ(ﾎｯﾄ)*{0: <5}  {1: >3,}ｶﾞﾘｵﾝ".format(int(args[5]),int(args[5])*MILKTEA_TANKA), font=fontAa, fill=0)

#合計
total_price = (int(args[2])*STTEA_TANKA)+(int(args[3])*STTEA_TANKA)+(int(args[4])*MILKTEA_TANKA)+(int(args[5])*MILKTEA_TANKA)
draw.text((10,500), "--------------------------------", font=fontA, fill=0)
draw.text((40,560), "小計:{: >6,}ガリオン".format(total_price), font=fontB, fill=0)

#注文コードの表示
if (args[1] != "mobile"):
    #draw.rectangle((10, 640, 390, 760), fill=0)
    font = ImageFont.truetype('mplus-1m-regular.ttf', 48, encoding='unic')
    draw.text((30,640), "こちらはモニターに表示されます、お客様の\nご注文番号です。今しばらくお待ちください。 ", 0 , font=fontS)
    draw.text((110,680), args[1], 0 , font=fontC)
else:
    draw.text((30,640), "ご利用ありがとうございました。", 0 , font=fontS)

image.show()
r_print()