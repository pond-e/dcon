#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import spidev
import time
import os
import datetime
import serial

# SPIバスを開く
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 100000 # 100kHz サンプリングレートの設定(必ずいる)

# MCP3008から値を読み取るメソッド
# チャンネル番号は0から7まで
def ReadChannel(channel):
 adc = spi.xfer2([1,(8+channel)<<4,0])
 data = ((adc[1]&3) << 8) + adc[2]
 return data

# 得た値を電圧に変換するメソッド
# 指定した桁数で切り捨てる
def ConvertVolts(data,places):
 volts = (data * 5) / float(1)
 volts = round(volts,places)
 return volts

# センサのチャンネルの宣言
force_channel_0 = 0
force_channel_1 = 1
force_channel_2 = 2

# 値を読むのを遅らせる
delay = 0.1

x = 0
# ファイルへ書き出し準備
now = datetime.datetime.now()
# 現在時刻を織り込んだファイル名を生成
fmt_name = "/home/pi/data/press_logs_{0:%Y%m%d-%H%M%S}_{number}.csv".format(now, number = x)
f_press = open(fmt_name, 'w')   # 書き込みファイル
value = "s, V0, V1, V2"  # header行への書き込み内容
f_press.write(value+"\n")
now_f = time.time()

# 電圧をテスターで実測する(今回はデータシートから)
Vref = 1

# 値を0.5区切りにする
def Punctuate(volt):
    decimal = volt % 1
    volt -= decimal
    if(decimal >= 0.25 and decimal < 0.75):
        decimal = 0.5
    elif(decimal >= 0.75):
        decimal = 1
    else:
        decimal = 0
    volt += decimal
    return volt

# メインクラス
if __name__ == '__main__':
    # serial
    s = serial.Serial('/dev/rfcomm0', 9600, timeout=30)
    textlen = 1
    print('wait for bluetooth')
    #x = s.read(textlen)
    #print(x)
    while True:
        data_0 = ReadChannel(force_channel_0)
        data_1 = ReadChannel(force_channel_1)
        data_2 = ReadChannel(force_channel_2)
        print("A/D Converter: {0}, {1}, {2}".format(data_0, data_1, data_2))
        volts_0 = ConvertVolts(data_0, Vref)
        volts_1 = ConvertVolts(data_1, Vref)
        volts_2 = ConvertVolts(data_2, Vref)

        volts_0 = Punctuate(volts_0)
        volts_1 = Punctuate(volts_1)
        volts_2 = Punctuate(volts_2)
        print("Volts: {0}, {1}, {2}".format(volts_0, volts_1, volts_2))
        now = time.time() - now_f
        print(now)
        value = "%s,%6.2f,%6.2f,%6.2f" % (now, volts_0, volts_1, volts_2) # 時間, 電圧
        # bluetooth send
        send_data = '[{0}, {1}, {2}, {3}]'.format(volts_0, volts_1, volts_2, now)
        send_data_to_by = send_data.encode()
        s.write(send_data_to_by)
        #s.read(textlen)

        f_press.write(value + "\n")  # ファイルを出力
        # time.sleep(delay)
        if(now > 180):
            spi.close()
            sys.exit(0)
            f_press.close()
