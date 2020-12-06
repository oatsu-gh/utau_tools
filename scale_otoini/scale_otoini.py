#! /usr/bin/env python3
# coding: utf-8
# Copyright (c) 2020 oatsu

"""
収録テンポだけを変えたとき用の oto.ini 改変ツール
"""

import utaupy as up  # THE SUSHI-WARE LICENSE
from tqdm import tqdm  # MIT License, MPL v2.0


def scale_otoiniobj(otoini: up.otoini.OtoIni, original_bpm, new_bpm):
    """
    テンポの倍率にしたがって、各種パラメーターの値に倍率を書ける。
    """
    ratio = original_bpm / new_bpm
    for oto in tqdm(otoini):
        oto.offset = oto.offset * ratio
        oto.overlap = oto.overlap * ratio
        oto.preutterance = oto.preutterance * ratio
        oto.consonant = oto.consonant * ratio
        oto.cutoff = oto.cutoff * ratio


def main():
    """
    パスを指定して処理を実行する
    """
    print('_____ξ・ヮ・) < scale_otoini v0.0.1 ________')
    print('Copyright (c) 2001-2020 Python Software Foundation')
    print('Copyright (c) 2020 oatsu')
    print('Copyright (c) 2013 noamraph')
    print('Copyright (c) 2015-2020 Casper da Costa-Luis')
    print('Copyright (c) 2016 Google Inc.')
    print()

    path_otoini = input('oto.ini ファイルを指定してください。\n>>> ').strip('"')
    original_bpm = int(input('もとのBPMを入力してください。\n>>> '))
    new_bpm = int(input('新しいBPMを入力してください。\n>>> '))

    print(f'すべての値を {original_bpm/new_bpm} 倍します。')
    otoini = up.otoini.load(path_otoini)
    scale_otoiniobj(otoini, original_bpm, new_bpm)
    otoini.write('oto_scaled.ini')
    input('完了しました。エンターキーを押すと終了します。')


if __name__ == '__main__':
    main()
