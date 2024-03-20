#!/usr/bin/env python3
# Copyright (c) 2022 oatsu
"""
USTから個人情報を削除する。
"""

from glob import glob

import utaupy


def clean_ustfile(path_ust) -> utaupy.ust.Ust:
    """Ustオブジェクトを作り直して、最低限の情報だけ引き継ぐ。
    """
    # 元のUSTファイルを読み取る
    ust = utaupy.ust.load(path_ust)
    # 出力用のUSTオブジェクトを作る
    new_ust = utaupy.ust.Ust()
    new_ust.tempo = ust.tempo
    new_ust.setting['Mode2'] = 'True'
    # 情報を削減しつつ新規オブジェクトを作る
    for note in ust.notes:
        new_note = utaupy.ust.Note()
        new_note.lyric = note.lyric
        new_note.length = note.length
        new_note.notenum = note.notenum
        new_note.tempo = note.tempo
        new_ust.notes.append(new_note)
    path_ust_bak = path_ust.replace('.ust', '.ust.bak')
    ust.write(path_ust_bak)
    new_ust.write(path_ust)


def main():
    path = input('USTファイルがあるフォルダを指定してください: ').strip('"')
    ust_files = glob(f'{path}/**/*.ust', recursive=True)
    for path_ust in ust_files:
        print(path_ust)
        clean_ustfile(path_ust)


if __name__ == "__main__":
    main()
