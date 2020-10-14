#!/usr/bin/env python
#! -*- coding: utf-8 -*-
from keras.preprocessing import image
from keras.models import load_model
from keras.preprocessing.image import img_to_array
import pygame.mixer
import numpy as np
import picamera
from PIL import Image
from time import sleep, perf_counter

from translate import *
from bottle_master import bottle_master
from shutter2image import shutter2image
import os
import datetime
import argparse

parser = argparse.ArgumentParser(description='model_path')
# modelが保存されているpathを引数で指定してください
parser.add_argument('--model_path', default=None, help="path to saved_model")
# デフォルトで引数を指定しない場合はmodelがloadされ予測が実行されます debugを行う場合はFalse
parser.add_argument('--predict_mode', default=True, help="model is loaded and prediction is excuted.")
# 画像を保存するかどうか、保存する場合はpathを指定
parser.add_argument('--image_save', default=None, help="input path if you want to save images.")

if __name__ == '__main__':
    # 引数を読み込み
    args = parser.parse_args()
    # predictモードの場合
    if args.predict_mode == True and args.model_path is None:
        print('--model_pathを指定してください')
    else:
        #画像を保存する場合、ディレクトリを作成
        if args.image_save:
            try:
                os.makedirs(args.image_save, exist_ok=True)
            except:
                print('読み取った画像を保存するpathが正しく指定されていません')

        # モデル+重みを読込み
        if args.predict_mode is True:
            self_model = load_model(args.model_path)

        #商品価格等の情報をbottle_masterから読み込み
        name_price_dict = bottle_master.bottle_master_dict()
        _, label_dict = bottle_master.bottle_label_dirpath()
        bottle_label = {}
        for key, value in label_dict.items():
            bottle_label[value] = key

        language_dict = {'k':'Kinyarwanda', 'e':'English', 'f':'French', 'j':'Japanese'}
        while True:
            money_sum = 0
            print('which language? Please select a language and input a key!!')
            language = input('Kinyarwanda :「k」,English :「e」,French :「f」,Japanese :「j]')
            if language not in ['k', 'e', 'f', 'j']:
                print('Please input correctly')
                pass
            else:
                print('Language_mode : {}'.format(language_dict[language]))

                while True:
                    # 「商品を置いてenterを押してください」
                    scene = "scan_start"
                    input(translate_language(language, scene))

                    # 時間を図る
                    time_start = perf_counter()

                    # 写真撮影した日時でファイル名を作成
                    dt_now = datetime.datetime.now()
                    file_name = 'checked' + '_' + dt_now.strftime('%Y%m%d%H%M%S') + '.jpg'

                    # 画像をsaveするpathを作成
                    if args.image_save:
                        save_path = os.path.join(args.image_save, file_name)
                    else:
                        save_path = os.path.join(os.getcwd(), file_name)

                    # 写真撮影してjpgをディレクトリへ保管
                    # ローカルデバッグ
                    shutter2image.shutter(save_path)

                    # # 音声再生
                    # pygame.mixer.music.play(1)
                    # sleep(1)
                    # # 再生の終了
                    # pygame.mixer.music.stop()

                    # 画像をモデルの入力用に加工

                    img = Image.open(save_path)
                    # ローカルデバッグ
                    # img = Image.open('/Users/ikeda/Desktop/IMG_0819.jpg')
                    # 画像保存のpathが指定されていない場合は消去
                    if args.image_save == None:
                        os.remove(save_path)

                    #img = Image.open("./0.jpg")
                    img = img.resize((224, 224))
                    img_array = img_to_array(img)
                    img_array = img_array.astype('float32')/255.0
                    img_array = img_array.reshape((1,224,224,3))

                    # predict_modeによって分岐
                    # modelが読み込まれてなく、流れのみ再現
                    if args.predict_mode == 'False':
                        # 時間計測
                        time_end = perf_counter()
                        # 商品を読み取るまで {}[s] 経過しました
                        scene = "time"
                        print(translate_language(language, scene).format(time_end-time_start))
                        
                        # 商品 : not predict が読み取られました
                        scene = "read_message"
                        print(translate_language(language, scene).format(img_array.shape))
                        
                        print('img_array_shape : {}'.format(img_array.shape))

                        while True:
                            # 読み取られた商品が正しい場合は「y」、誤っていた場合は「n」を押してください
                            scene = "correct?"
                            key = input(translate_language(language, scene))

                            if key != 'y' and key != 'n':
                                # 正しく入力されていません
                                scene = "input_error"
                                print(translate_language(language, scene))
                            else:
                                break

                        if key == 'y':
                            money_sum += 100
                            # 小計
                            scene = "subtotal"
                            print(translate_language(language, scene).format(money_sum))

                            while True:
                                # 続けて商品をスキャンする場合は「y」、会計する場合は「f」、\n キャンセルする商品がある場合は「ｘ」を押して下さい。
                                scene = "continue?"
                                key = input(translate_language(language, scene))
                                if key != 'y' and key != 'f':
                                    # 正しく入力されていません
                                    scene = "input_error"
                                    print(translate_language(language, scene))
                                else:
                                    break
                            if key == 'f':
                                # 合計
                                scene = "total"
                                print(translate_language(language, scene).format(money_sum))
                                
                                # ありがとうございました
                                scene = "thanks"
                                print(translate_language(language, scene))
                                print()
                                break
                            elif key == 'n':
                                # 次の商品を指定の位置に置いてください。
                                scene = "next"
                                print(translate_language(language, scene))


                    # 読み込んだmodelでpridictを実行
                    else:
                        img_pred = self_model.predict(img_array)
                        print("debug:",img_pred)
                        name = bottle_label[np.argmax(img_pred)]

                        # 時間計測
                        time_end = perf_counter()
                        # 商品を読み取るまで {}[s] 経過しました
                        scene = "time"
                        print(translate_language(language, scene).format(time_end-time_start))

                        # 商品 : {} 値段 : {} が読み取られました'
                        scene = "read_message"
                        print(translate_language(language, scene).format(name, name_price_dict[name]))

                        while True:
                            # 読み取られた商品が正しい場合は「y」、誤っていた場合は「n」を押してください
                            scene = "correct?"
                            key = input(translate_language(language, scene))
                            if key != 'y' and key != 'n':
                                # 正しく入力されていません
                                scene = "input_error"
                                print(translate_language(language, scene))
                            else:
                                break

                        if key == 'y':
                            money_sum += name_price_dict[name]
                            # 小計
                            scene = "subtotal"
                            print(translate_language(language, scene).format(money_sum))

                            while True:
                                # 続けて商品をスキャンする場合は「y」、会計する場合は「f」、\n キャンセルする商品がある場合は「ｘ」を押して下さい。
                                scene = "continue?"
                                key = input(translate_language(language, scene))
                                if key != 'y' and key != 'f':
                                    # 正しく入力されていません
                                    scene = "input_error"
                                    print(translate_language(language, scene)) 
                                else:
                                    break

                            if key == 'f':
                                # 合計
                                scene = "total"
                                print(translate_language(language, scene).format(money_sum))
                                
                                # ありがとうございました
                                scene = "thanks"
                                print(translate_language(language, scene))
                                print()
                                break
                            elif key == 'n':
                                # 次の商品を指定の位置に置いてください。
                                scene = "next"
                                print(translate_language(language, scene))
