#!/usr/bin/env python3
# Copyright (c) 2021 oatsu
"""
「x K」な音素があるか、ある場合は連続音パターンがそろっているか検索する。
"""

import utaupy as up


def bool_aru_nai(true_false):
    """
    bool地に応じて標準出力する
    """
    if true_false is True:
        return 'ある'
    if true_false is False:
        return '無'
    raise ValueError


def check_alias_patten(otoini: up.otoini.OtoIni, keyword):
    """
    原音設定のエイリアスに対してキーワード検索する
    """
    all_aliases = [oto.alias for oto in otoini]

    for x in ['-', 'a', 'i', 'u', 'e', 'o', 'n']:
        target_alias = keyword.replace('x', x, 1)
        target_alias_ga_aru = any(target_alias in alias for alias in all_aliases)
        print(f'{target_alias}: {bool_aru_nai(target_alias_ga_aru)}')


def main(path_config):
    """
    oto.iniファイルをロードして関数に渡す
    """
    try:
        with open(path_config, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except KeyError:
        with open(path_config, 'r', encoding='cp932') as f:
            lines = f.readlines()
    lines = [line.strip(' 　\r\n\t') for line in lines]
    patterns = [line for line in lines if line != '']

    path_otoini = input('oto.ini ファイルを D&D で指定してください。\n>>> ').strip('"')
    otoini = up.otoini.load(path_otoini)
    for patten in patterns:
        print()
        print(f'"{patten}" のパターンを満たすエイリアスを検索します。')
        check_alias_patten(otoini, patten)


if __name__ == '__main__':
    print('-------------------------------------------------')
    print('oto.ini内に「a K」があるとき\n'
          '「- K」「i K」「u K」「e K」「o K」「n K」\n'
          'があるか検索して欠けてる場合表示してくれる、\n'
          'みたいなことができるやつ (Ver.0.1.0)')
    print('-------------------------------------------------')
    while True:
        main('config.txt')
        print()
