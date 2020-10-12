# bottle_masterを読み込みを辞書型を取得する
bottle_master_dict = {}
#　ファイルの内容を一行ずつ読み込む
with open('bottle_master.csv', 'r') as f:
    bottle_master = f.readlines()
    for bottle_name, price in bottle_master:
        bottle_master_dict[bottle_name] = price
return bottle_master_dict
