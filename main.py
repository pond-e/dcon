#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import spidev
import time
import os
import datetime
import serial
import csv
import matplotlib.pyplot as plt
import bluetooth

print('finish imports')

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

flag = True

# bluetooth setting
PORT = 1

# メインクラス
if __name__ == '__main__':
    while True:
        try:
            server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            server_sock.bind(('', PORT))
            server_sock.listen(1)

            client_sock, client_addport = server_sock.accept()
            print(client_addport)
            print('wait for bluetooth')
            while True:
                print('loop now!')
                flag = True
                # ready to write in file
                now = datetime.datetime.now()
                x = 0
                # make file name with current time
                fmt_name = "/home/pi/data/"
                fmt_name_body = "press_logs_{0:%Y%m%d-%H%M%S}_{number}.csv".format(now, number = x)
                f_press = open(fmt_name+fmt_name_body, 'w')
                value = "s, V0, V1, V2" # header row
                f_press.write(value+"\n")
                now_f = time.time()

                # setting graph
                template_fname = fmt_name
                filename = fmt_name_body
                start = 3030
                end = 660

                while flag==True:
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
                    client_sock.sendall(send_data_to_by+b'\n')
                    client_sock.recv(1024)  #Todo:普段はコメントアウトなし
                    f_press.write(value + "\n")  # ファイルを出力
                    # time.sleep(delay)
                    if(now > 120):
                        f_press.close()

                        with open(template_fname+filename) as f:
                            reader = csv.reader(f)
                            l = [row for row in reader]
                        f = [k[1:] for k in l[start:start+end]]
                        for i in range(len(f)):
                            for j in range(len(f[0])):
                                f[i][j] = float(f[i][j])

                        plt.rc('font', family='serif')
                        fig = plt.figure()
                        x = []
                        x.append([k[0] for k in f])
                        x.append([k[1] for k in f])
                        x.append([k[2] for k in f])
                        plt.plot(x[0], color='gray')
                        plt.plot(x[1], color='red')
                        plt.plot(x[2], color='blue')
                        plt.xlabel('time')
                        save_name = filename+'.png'
                        plt.savefig(save_name)
                    
                        with open(save_name, mode='rb') as pic:
                            client_sock.sendall(b'1\n')
                            time.sleep(10)
                            contents = pic.read()
                            client_sock.sendall(contents+b'\n')
                            time.sleep(10)
                            client_sock.sendall(b'2\n')
                            time.sleep(10)
                        #spi.close()
                        #sys.exit(0)
                        flag = False
        except:
            pass
