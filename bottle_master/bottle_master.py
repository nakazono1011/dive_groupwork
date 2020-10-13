
import os
import csv

# bottle_masterを読み込みを辞書型を取得する
def bottle_master_dict():
    bottle_master_dict = {}
    # csvファイルを読み込む
    cwd_path = os.getcwd()
    file_path = os.path.join(cwd_path, 'bottle_master/bottle_master.csv')
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        for bottle_name, price in reader:
            bottle_master_dict[bottle_name] = int(price)

    return bottle_master_dict

# 学習データが格納されているディレクトリのパスとラベルの辞書を取得する
def bottle_label_dirpath():
    data_dir_path = []
    label_dict = {}
    label = 0
    # csvファイルを読み込む
    cwd_path = os.getcwd()
    file_path = os.path.join(cwd_path, 'bottle_master/bottle_master.csv')
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        for bottle_name, _ in reader:
            # pathの取得、リストへ
            path = os.path.join(cwd_path, 'shutter2image', bottle_name)
            data_dir_path.append(path)
            # ラベルを辞書へ記録
            label_dict[bottle_name] = label
            label += 1
    return data_dir_path, label_dict
