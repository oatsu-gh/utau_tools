#!/usr/bin/env python3
# Copyright (c) 2022 oatsu
"""
USTファイルのノート部分の情報をCSVに変換する。
ファイル名も記録する。
"""
from glob import glob
from os.path import basename, isdir, join

import pandas
import utaupy


def note2dict(note):
    """
    utaupy.ust.Note を 通常のdictに変換する。
    このとき、テンポを確実に埋め込む。
    """
    d = note.data
    d['Tempo'] = note.tempo
    d['TimeSignatures'] = note.timesignatures
    return d


def note2dict_detailed(note) -> pandas.DataFrame:
    """PBS, PBW, PBY を合わせて [(時刻,高さ), ...] のリストにする。
    """
    df = pandas.DataFrame()
    # USTのノートのピッチ情報を取得する
    if all(key in note for key in ['PBS', 'PBY', 'PBM']):
        pbs = note.pbs
        pby = note.pby
        pbw = note.pby
        # ピッチ点のノート開始位置に対する相対時刻を計算
        offset = pbs[0]
        times = [offset] + list(map(lambda x: x + offset, pbw))
        # ピッチ点の高さを計算
        if len(pbs) == 1:
            heights = [0] + pby
        else:
            heights = [pbs[1]] + pby
        # 点数が一致していることを確認
        assert len(times) == len(heights), f'{len(times)} {len(heights)}'
        df['Pitch_Time'] = times
        df['Pitch_Height'] = heights

    for k, v in note2dict(note).items():
        df[k] = v

    return df


def ust2df(path_ust_in):
    """
    USTファイルを指定して、CSVファイルに変換して出力する。
    """
    # ustファイルを読み取る
    ust = utaupy.ust.load(path_ust_in)
    # ustに辞書のリストに変換する
    df = pandas.concat(map(note2dict_detailed, ust.notes))
    # 辞書のリストをdataframeに変換する
    # USTファイル名のカラムを追加する
    df['FileName'] = basename(path_ust_in)

    return df


def main():
    """
    フォルダかファイルを指定して一括変換する。
    フォルダを指定した場合は複数のUSTを単一ファイルにまとめて結果とする。
    """
    # 各種パスを指定
    ust_dir = input('Select a directory or a UST file: ').strip('"')
    ust_files = glob(join(ust_dir, '*.ust')) if isdir(ust_dir) else [ust_dir]
    # USTを一括処理して単一のDataFrameにする
    df_concat = pandas.concat(map(ust2df, ust_files))
    # CSV出力
    df_concat.to_csv('./pitches_utf8.csv', encoding='utf-8')
    df_concat.to_csv('./pitches_sjis.csv', encoding='cp932')


if __name__ == '__main__':
    main()
