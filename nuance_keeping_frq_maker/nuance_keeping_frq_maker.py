#!/usr/bin/env python3
# Copyright (c) 2024 oatsu
"""
UTAU音源の周波数表のうち、oto.ini における子音部分のニュアンスを残す。
"""

import math
import shutil
import sys
from datetime import datetime
from glob import glob
from os import makedirs
from os.path import basename, dirname, isdir, isfile, join

import numpy as np
import utaupy
from pandas import DataFrame
from tqdm import tqdm

if isfile(join(dirname(__file__), 'frq.py')):
    sys.path.append(dirname(__file__))
    from frq import Frq
else:
    from PyUtauCli.voicebank.frq import Frq

FLAGNAME = '_should_be_flatten_flag'
INTERP_METHOD = 'akima'
INTERP_ORDER = 2

def backup_frq_files(dirpath):
    """指定したフォルダ内にあるfrqファイルをバックアップする"""

    # 現在の時刻を取得
    now = datetime.now()
    # YYYYMMDDHHHHMMSS 形式で時刻を表示
    formatted_time = now.strftime("%Y%m%d_%H%M%S")
    frq_files = glob(f'{dirpath}/*.frq')
    # バックアップフォルダを作る
    backup_dir = join(dirpath,'_BackupFrq', formatted_time)
    makedirs(backup_dir, exist_ok=True)
    # バックアップファイルを作成
    for path in tqdm(frq_files):
        shutil.copy2(path, join(backup_dir, basename(path)))

def frqobj_to_dataframe(frq: Frq) -> DataFrame:
    """PyUtauCli.voicebank.frq.Frq をpandas.DataFrame に変換する"""
    df = DataFrame()
    df['t'] = frq.t
    # 何らかの周波数生成ソフトだとベースラインが0Hzではなくて55Hzなので、それを除外するようにする。
    df['f0'] = [f0 if f0 > 55 else 0 for f0 in frq.f0]
    df['amp'] = frq.amp
    df['f0_avg'] = frq.f0_avg
    df['_log_f0'] = [math.log10(max(1,v)) for v in df['f0']]
    df['_should_be_flatten_flag'] = False
    df['_dummy'] = np.nan
    return df


def analyze_otoini(otoini_path) -> dict:
    """
    各WAVファイルに対して、オーバーラップから子音部の範囲の絶対時刻時刻を返す。

    形式: {周波数表ファイル名: (オーバーラップ時刻, 子音部時刻), (オーバーラップ時刻, 子音部時刻), ...}
    具体例: {'_あいうえお.frq': [(100, 200), (500, 800)]}
    """
    # 原音設定ファイルを読み込む
    otoini = utaupy.otoini.load(otoini_path)
    #[(frqファイル, 平坦化の開始時刻, 終了時刻), ... ]
    l = [(
        oto.filename.replace('.wav', '_wav.frq'),
        (oto.offset + oto.overlap) / 1000,
        (oto.offset + oto.consonant) / 1000
        ) for oto in tqdm(otoini)]
    return l

def set_f0_edit_flag(df, t_start, t_end) -> None:
    """
    各f0点に対して、編集が必要かどうかを判別する。
    補間に使うため、編集すべき範囲内だったとしても f0 = 0Hz な点から近い両側2点は残す必要がある。
    """
    # 対象の点が編集すべき範囲に入っているかどうかを判定
    df[FLAGNAME] = [
        (flag is True) or (t_start < t < t_end and f0!=0)
        for (flag, t, f0)
        in zip(df[FLAGNAME], df['t'], df['f0'])
    ]
    # 直後の点またはその次の点の f0が0Hzであれば、もとのF0データを保持する
    # df[FLAGNAME] = [
    #     all((f0_next != 0, f0_nextnext != 0, flag))
    #     for flag, f0_next, f0_nextnext
    #     in zip(df[FLAGNAME][:-2], df['f0'][1:-1], df['f0'][2:])
    # ] + df[FLAGNAME][-2:].to_list()

    # # 直前の点またはその前の点の f0が0Hzであれば、もとのF0データを保持する
    # df[FLAGNAME] = df[FLAGNAME][:2].to_list() + [
    #     all((f0_prev != 0, f0_prevprev != 0, flag))
    #     for flag, f0_prev, f0_prevprev
    #     in zip(df[FLAGNAME][2:], df['f0'][1:-1], df['f0'][0:-2])
    # ]
    return None

def main():
    """全体の処理をする"""
    dir_in = input('編集したい周波数表ファイル(frq)と 対応する原音設定ファイル(oto.ini) の両方があるフォルダを指定してください。\n>>> ').strip('"')
    assert isdir(dir_in)

    print("( -_-) < 周波数表ファイル(frq) ファイルをバックアップします。")
    backup_frq_files(dir_in)

    print("( -_-) < 周波数表ファイル(frq) を読み取ります。")
    frq_files = glob(f'{dir_in}/*.frq')
    d_frq_objects = {basename(p): Frq(p) for p in tqdm(frq_files)}

    print("( -_-) < 周波数表を DataFrame に変換します。")
    d_frq_dataframes = {key: frqobj_to_dataframe(val) for (key, val) in d_frq_objects.items()}

    print("( -w-) < 原音設定ファイル(oto.ini) を読み取って 周波数表の編集内容を考えます。")
    path_otoini = join(dir_in, 'oto.ini')
    l_frqpath_start_end = analyze_otoini(path_otoini) # [(frqpath, t_start, t_end), ...]

    print('( -w-) < 原音設定をもとに周波数表の編集位置を決めます。')
    for v in tqdm(l_frqpath_start_end):
        path_frq = v[0]
        t_start = v[1]
        t_end = v[2]
        df = d_frq_dataframes[path_frq]
        # 対象の周波数点が平坦化範囲か否かを判定する。
        set_f0_edit_flag(df, t_start, t_end)

    print('( -w-) < 周波数データを編集します。')
    for key, df in tqdm(d_frq_dataframes.items()):
        # # f0 = 0Hz の点もいったん補完するためにflagをTrueにする
        df[FLAGNAME] = [flag is True or f0 == 0 for flag, f0 in zip(df[FLAGNAME], df['f0'])]
        # 平坦化フラグが立っている部分は None に差し替える。そうでなければf0を使う
        df['_new_log_f0'] = df['_dummy'].where(df[FLAGNAME], df['_log_f0'])
        # Noneの部分を3次スプライン補間
        df['_new_log_f0'] = df['_new_log_f0'].interpolate(INTERP_METHOD,order=INTERP_ORDER)
        d_frq_dataframes[key]['_new_log_f0'] = df['_new_log_f0']
        # 補完できなかった部分(左右端を想定)は元のf0データを復元する
        df['_new_log_f0'] = [
            original_log_f0 if (new_log_f0 !=0 and np.isnan(new_log_f0)) else new_log_f0
            for original_log_f0, new_log_f0 in zip(df['_log_f0'], df['_new_log_f0'])
        ]
        df['_new_f0'] = [
            math.pow(10, log_f0) if f0 != 0 else 0 for (log_f0, f0) in zip(df['_new_log_f0'], df['f0'])
        ]

    print('( -_-) < 周波数表ファイル(frq) を出力します。')
    for path_frq in tqdm(frq_files):
        df = d_frq_dataframes[basename(path_frq)]
        df.to_csv(path_frq.replace('.frq', '.csv'), encoding='cp932', index_label='#')
        temp_frq: Frq = d_frq_objects[basename(path_frq)]
        temp_frq.f0 = df['_new_f0'].to_numpy()
        temp_frq.save()

    print('おわり！')

if __name__ == "__main__":
    main()
