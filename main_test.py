#!/usr/bin/env python
#! -*- coding: utf-8 -*-
from keras.preprocessing import image
from keras.models import load_model
from keras.preprocessing.image import img_to_array
import pygame.mixer
import numpy as np
import picamera
from PIL import Image
from time import sleep

from bottle_master import bottle_master
from shutter2image import shutter2image
import os
import datetime
import argparse

parser = argparse.ArgumentParser(description='model_path')
parser.add_argument('--model_path', default=None, help="path to saved_model")
parser.add_argument('--debug_without_model', default=False, help="not_predict")

# def shutter():
#     photofile = open(photo_filename, 'wb')
#     print(photofile)
#
#     # pi camera 用のライブラリーを使用して、画像を取得
#     with picamera.PiCamera() as camera:
#         #camera.resolution = (640,480)
#         camera.resolution = (300,400)
#         camera.start_preview()
#         sleep(1.000)
#         camera.capture(photofile)

if __name__ == '__main__':
    #モデルが保存されているパスを読み込み
    args = parser.parse_args()
    if args.model_path is None:
        print('--model_pathを指定してください')
    else:
        #画像を保存するディレクトリを作成
        os.makedirs('check_image', exist_ok)
        # モデル+重みを読込み
        self_model = load_model(args.model_path)

        #商品価格
        name_price_dict = bottle_master.bottle_master_dict()
        _, label_dict = bottle_master.get_bottle_label_dirpath()
        bottle_label = {}
        for key, value in label_dict:
            bottle_label[value] = key

        # 音声ファイル初期化
        # pygame.mixer.init()
        # pygame.mixer.music.load("Cash_Register-Beep01-1.mp3")

        # # 正解ラベル
        # label = ['cocacola-peach', 'ilohas', 'kuchidoke-momo', 'o-iocha', 'pocari-sweat']
        # # 商品価格
        # money = {'cocacola-peach':110, 'ilohas':120, 'kuchidoke-momo':130, 'o-iocha':140, 'pocari-sweat':150}

        while True:
            money_sum = 0
            while True:
                key = input('商品を指定の位置に設置し「Enter」を押して下さい')
                dt_now = datetime.datetime.now()
                file_name = 'check' + '_' + dt_now.strftime('%Y%m%d%H%M%S') + '.jpg'
                save_path = os.path.join('check_image', file_name)
                # 写真撮影
                shutter2image.shutter(save_path)

                # # 音声再生
                # pygame.mixer.music.play(1)
                # sleep(1)
                # # 再生の終了
                # pygame.mixer.music.stop()

                # 画像をモデルの入力用に加工
                img = Image.open(save_path)
                #img = Image.open("./0.jpg")
                img = img.resize((224, 224))
                img_array = img_to_array(img)
                img_array = img_array.astype('float32')/255.0
                img_array = img_array.reshape((1,224,224,3))

                if args.debug_without_model is False:
                    print('商品が読み取られました')
                    print('array_shape : {}'.format(img_array.shape))
                    key = input('読み取られた商品が正しい場合は「y」、誤っていた場合は「n」を押してください')
                    if key == 'y':
                        money_sum += 100
                        print("小計", money_sum)
                        key = input('続けて商品をスキャンする場合は「y」,会計する場合は「Enter」を押して下さい')
                        if key != 'y':
                            print('合計 : {}'.format(money_sum))
                            break
                    elif key == 'n':
                        print('商品を指定の位置に置き直してください')
                else:
                    # predict
                    img_pred = self_model.predict(img_array)
                    print("debug:",img_pred)
                    name = bottle_label[np.argmax(img_pred)]
                    print('商品 : {} 値段 : {} が読み取られました'.format(name, name_price_dict[name]))
                    key = input('読み取られた商品が正しい場合は「y」、誤っていた場合は「n」を押してください')
                    if key == 'y':
                        money_sum += name_price_dict[name]
                        print("小計", money_sum)
                        key = input('続けて商品をスキャンする場合は「y」,会計する場合は「Enter」を押して下さい')
                        if key != 'y':
                            print('合計 : {}'.format(money_sum))
                            break
                    elif key == 'n':
                        print('商品を指定の位置に置き直してください')
