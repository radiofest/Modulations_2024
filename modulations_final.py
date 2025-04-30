# реализована передача пакетов до и после старта
# чтение из файла реализовано
# старт по появлению файла реализован
# гейн не меняется

import numpy as np
import random
import string
import math
import re
from time import sleep, time

import SoapySDR
from SoapySDR import SOAPY_SDR_CF32, SOAPY_SDR_TX

def generate_random_string(length):
    letters = string.ascii_lowercase
    rand_string = ''.join(random.choice(letters) for i in range(length))
    #print("Random string of length", length, "is:", rand_string)
    return rand_string

def m_bpsk(seq, n):
    seq_new = np.zeros(len(seq)).astype(np.complex64)
    for i in range(len(seq)): 
        seq_new[i] = int(seq[i]) + 0j
    return np.repeat(seq_new*2 - 1, n)

def m_qpsk(seq, n):
    bits = re.findall(r'\d\d', seq)
    seq_new = np.zeros(int(len(bits))).astype(np.complex64)
    m_4psk_dict = {'00': 1+0j, '01': 1j, '10': -1+0j, '11': -1j}
    i = 0
    for item in bits:
        seq_new[i] = m_4psk_dict[item]
        i += 1
    return np.repeat(seq_new, n*2)

def m_4qam(seq, n):
    bits = re.findall(r'\d\d', seq)
    seq_new = np.zeros(int(len(bits))).astype(np.complex64)
    m_qpsk_dict = {'00': -1-1j, '01': -1+1j, '10': 1-1j, '11': 1+1j}
    i = 0
    for item in bits:
        seq_new[i] = m_qpsk_dict[item]
        i += 1
    return np.repeat(seq_new, n*2)

def m_8psk(seq, n):
    s = math.sqrt(2)/2
    bits = re.findall(r'\d\d\d', seq)
    seq_new = np.zeros(int(len(bits))).astype(np.complex64)
    m_8psk_dict = {'000': 1 + 0j, '001': s + s*1j, '010': 1j, '011': -s + s*1j, '100': -1 + 0j, '101': -s - s*1j, '110': -1j, '111': s - s*1j}
    i = 0
    for item in bits:
        seq_new[i] = m_8psk_dict[item]
        i += 1
    return np.repeat(seq_new, n*3)

def m_8qam(seq, n):
    s = 0.5
    bits = re.findall(r'\d\d\d', seq)
    seq_new = np.zeros(int(len(bits))).astype(np.complex64)
    m_8qam_dict = {'000': -1 + s*1j, '001': -1 - s*1j, '010': -s - s*1j, '011': -s + s*1j, '100': 1 + s*1j, '101': 1 - s*1j, '110': s + s*1j, '111': s - s*1j}
    i = 0
    for item in bits:
        seq_new[i] = m_8qam_dict[item]
        i += 1
    return np.repeat(seq_new, n*3)

def m_16qam(seq, n):
    s = 0.5
    bits = re.findall(r'\d\d\d\d', seq)
    seq_new = np.zeros(int(len(bits))).astype(np.complex64)
    m_16qam_dict = {'0000': -2*s + s*2j, '0001': -2*s + s*1j, '0011': -2*s - s*1j, '0010': -2*s - s*2j, '0100': -s + s*2j, '0101': -s + s*1j, '0111': -s - s*1j, '0110': -s - s*2j,
                    '1100': s + s*2j, '1101': s + s*1j, '1111': s - s*1j, '1110': s - s*2j, '1000': 2*s + s*2j, '1001': 2*s + s*1j, '1011': 2*s - s*1j, '1010': 2*s - s*2j}
    i = 0
    for item in bits:
        seq_new[i] = m_16qam_dict[item]
        i += 1
    return np.repeat(seq_new, n*4)

def generate_modulations_list(num_mods, num_elements):
    modtypes_dict = {1: 'BPSK', 2: 'QPSK', 3: '4QAM', 4: '8PSK', 5: '8QAM', 6: '16QAM', 7: '16PSK'}
    rndm = np.random.randint(1, num_mods+1, num_elements)
    lst = []
    for i in rndm:
        lst.append(modtypes_dict[i])
    return lst

def num_form(n, samples):
    n_bin = '{0:08b}'.format(n)
    n_bpsk = np.zeros(len(n_bin)).astype(np.complex64)
    for i in range(len(n_bin)): 
        n_bpsk[i] = int(n_bin[i]) + 0j
    return np.repeat(n_bpsk, samples)

def mod_selector(seq, mod):
    if mod == 'BPSK': return m_bpsk(seq, samples_data)
    elif mod == 'QPSK': return m_qpsk(seq, samples_data)
    elif mod == '4QAM': return m_4qam(seq, samples_data)
    elif mod == '8PSK': return m_8psk(seq, samples_data)
    elif mod == '8QAM': return m_8qam(seq, samples_data)
    elif mod == '16QAM': return m_16qam(seq, samples_data)
    else: raise Exception("[ERROR] Modulation check error")

def countdown(t0, t):
    if (time() - t0) < t: 
        print('\n[INFO] Time to the end: ')
        while  (time() - t0) < t:
            print('\t%.0f seconds' % (t - (time() - t0)))
            sleep(1)
        print('\n[INFO] THE END.')

def print_info(packs_do_starta, packs_amount, packs_posle_finisha, pack_time, tone_time, num_time, body_time, qam16):
    print('\n---------- RADIOPEREHVAT 2024 ----------\n')

    print('[INFO] Pre-packs amount is: ', packs_do_starta)
    print('[INFO] Packs amount is: ', packs_amount)
    print('[INFO] Post-packs amount is: ', packs_posle_finisha)
    print('[INFO] One pack time is: %.0f ms' % (pack_time*1000))
    print('[INFO] Tone time is: %.2f ms' % (tone_time*1000))
    print('[INFO] Num time is: %.2f ms' % (num_time*1000))
    print('[INFO] Message time is: %.2f ms \n' % (body_time*1000))

    print('[INFO] Modulations are: ')
    print('\t 1. BPSK')
    print('\t 2. QPSK')
    print('\t 3. 4QAM')
    print('\t 4. 8PSK')
    print('\t 5. 8QAM')

    if qam16 == True: print('\t 6. 16QAM\n')
    else: print(' ')

    print('[INFO] Main freq is 450 MHz')
    print('[INFO] Freq range is 445 - 455 MHz')
    print('[INFO] Freq step is 1 MHz\n')

    #print('[INFO] Gain range is ', gain+gl, '-', gain+gh)
    #print('[INFO] Gain step is 1 \n')

def data_gen(n_packs, n_info):
    mods_list = generate_modulations_list(5, n_packs) # создать список модуляций, 5 - bez 16QAM, 6 - s 16QAM

    msg = generate_random_string(n_info) # сообщение, которое будет передаваться
    msg_bit = ''.join(format(ord(i), '08b') for i in msg) # то же сообщение, но в двоичном виде одним массивом
    data = np.tile(mod_selector(msg_bit, mods_list[0]), n_tile) # модулируем в соответствии со списком

    if len(data) % MTU == 0: data_sends_count = len(data) // MTU
    else: data_sends_count = 1 + len(data) // MTU

    pack_numbers = num_form(0, samples_num)

    # stakaem datu i nomer paketa po strokam
    for i in range(1, n_packs):
        msg = generate_random_string(n_info)
        msg_bit = ''.join(format(ord(i), '08b') for i in msg)

        data = np.vstack((data, np.tile(mod_selector(msg_bit, mods_list[i]), n_tile)))
        pack_numbers = np.vstack((pack_numbers, num_form(i, samples_num)))
    return data, data_sends_count

def transmit(sdr_info, tone_sends_count, pack_numbers, data, data_sends_count, n_packs, freqs_list):
    global pnum
    #pnum = 1
    l_num = len(pack_numbers[1])
    sdr = sdr_info['sdr']
    MTU = sdr_info['MTU']
    sample_rate = sdr_info['sample_rate']
    tx_stream = sdr_info['stream']

    for i in range(n_packs):
        print('Sending pack number ', pnum)
        pnum += 1
        sdr.setFrequency(SOAPY_SDR_TX, sdr_info['chan'], freqs_list[i]) # перестройка на частоту из спискa, time spending is about 0.03 s
        #sdr.setGain(SOAPY_SDR_TX, chan, int(gain_list[i])) # перестройка на частоту из спискa, time spending is about 0.01 s
        
        # отправляем тоновый сигнал 1
        for _ in range(tone_sends_count-1):
            sdr.writeStream(tx_stream, [sdr_info['ones_MTU']], MTU)
            sleep(MTU / sample_rate)
        if sdr_info['len_add']:
            sdr.writeStream(tx_stream, [ones_add], sdr_info['len_add'])
            sleep(sdr_info['len_add'] / sample_rate)
        else:
            sdr.writeStream(tx_stream, [sdr_info['ones_MTU']], MTU)
            sleep(MTU / sample_rate)           
        
        # отправляем номер пакета
        sdr.writeStream(tx_stream, [pack_numbers[i]], l_num)
        sleep(l_num / sample_rate)

        # отправляем тоновый сигнал 2
        sdr.setFrequency(SOAPY_SDR_TX, sdr_info['chan'], freqs_list[i] + 1e3)
        for _ in range(tone_sends_count-1):
            sdr.writeStream(tx_stream, [sdr_info['ones_MTU']], MTU)
            sleep(MTU / sample_rate)
        if sdr_info['len_add']:
            sdr.writeStream(tx_stream, [ones_add], sdr_info['len_add'])
            sleep(sdr_info['len_add'] / sample_rate)
        else:
            sdr.writeStream(tx_stream, [sdr_info['ones_MTU']], MTU)
            sleep(MTU / sample_rate) 
        
        # отправляем символы 
        sdr.setFrequency(SOAPY_SDR_TX, sdr_info['chan'], freqs_list[i])
        if len(data) % MTU == 0:
            for j in range(data_sends_count):
                sdr.writeStream(tx_stream,  [data[i][j*MTU:(j+1)*MTU]], MTU)
                sleep(MTU / sample_rate)
        else:
            for j in range(data_sends_count-1):
                sdr.writeStream(tx_stream,  [data[i][j*MTU:(j+1)*MTU]], MTU)
                sleep(MTU / sample_rate)
            sdr.writeStream(tx_stream, [data[i][(data_sends_count-1)*MTU::]], len(data[i][(data_sends_count-1)*MTU::]))
            sleep(len(data[i][(data_sends_count-1)*MTU::]) / sample_rate)

# --------------------------------------------

qam16 = False
final = True

pnum = 1

packs_amount = 100 # количество пакетов
n_syms = 1500 # количество символов в сообщении
n_info = 18 # количество уникальных символов в сообщении

path = '/home/administrator/files/'

if final:
    game_type = 'final'
else: game_type = 'training'

n_tile = int(n_syms / n_info)

# НАСТРОЙКИ ЛАЙМА И ПАРАМЕТРОВ ПЕРЕДАЧИ ------------------------------------------

samples_data = 2 # 2 отсчёта на символ в дате
samples_num = 16 # 16 отсчётов на символ в номере
n_send = 16 # номер посылается 10 раз
# всё в восьмибитном виде кодируется

sample_rate = 200e3
freq = 450e6
MTU = 8000

pack_time = 0.4 # столько отправляется одна пачка в секундах
num_time = samples_num * n_send * 8 / sample_rate # s
body_time = samples_data * 8 * n_syms / sample_rate # s
tone_time = ((pack_time - body_time) - num_time) / 2 # s

# столько будет отправляться тоновый сигнал внутри пакетов
if int(tone_time*sample_rate) % MTU == 0: 
    tone_sends_count = int(tone_time*sample_rate) // MTU
    len_add = None
else: 
    tone_sends_count = 1 + int(tone_time*sample_rate) // MTU
    len_add = int(tone_time*sample_rate) % MTU

marker_tone_sends_count = int(sample_rate / MTU) # столько будет отправляться тоновый сигнал старта и финиша

# ФОРМИРОВАНИЕ ПАКЕТОВ --------------------------------------

ones_MTU = np.ones(MTU).astype(np.complex64)
ones_add = np.ones(len_add).astype(np.complex64)

# ждём файл старта
#print(path + 'start.txt')
start_file = None
print('[INFO] Waiting for game to start... \n')
while not start_file:
    try: start_file = open(path + 'start.txt')
    except IOError as e: pass

game_number = str(int(start_file.read()))
start_file.close()
print('[INFO] GAME NUMBER ', game_number)

name = game_type + '_' + game_number + '.txt'

# Читаем фай
with open(path + game_type + '/' + name, 'r') as file:
    data_from_file = file.read().split('\n')

packs_do_starta = int(data_from_file[0].split(':')[1]) # пакеты до старта считываем
packs_posle_finisha = np.random.randint(30) # столько будет пакетов после финиша

# Обрабатываем данные из файла
freqs_list = []
num_list = []
data_list = []
mods_list = []
for i in range(packs_amount):
    freqs_list.append(int(data_from_file[i].split(':')[0]) * 1e6)
    #num_list.append(int(data_from_file[i].split(':')[1]))
    mods_list.append(data_from_file[i].split(':')[2])
    data_list.append(data_from_file[i].split(':')[3])

pack_numbers = num_form(0, samples_num)
msg_bit = ''.join(format(ord(x), '08b') for x in data_list[0])
data_main = np.tile(mod_selector(msg_bit, mods_list[0]), n_tile)

if len(data_main) % MTU == 0: data_sends_count_main = len(data_main) // MTU
else: data_sends_count_main = 1 + len(data_main) // MTU

# в комплексный вид переводим дату
for i in range(1, packs_amount):
    msg_bit = ''.join(format(ord(x), '08b') for x in data_list[i])
    data_main = np.vstack((data_main, np.tile(mod_selector(msg_bit, mods_list[i]), n_tile)))

# и номер тоже
for i in range(1, packs_amount+packs_do_starta+packs_posle_finisha):
    pack_numbers = np.vstack((pack_numbers, num_form(i, samples_num)))
pack_numbers_final = np.tile(pack_numbers, n_send) # посылаем номер много раз

print_info(packs_do_starta, packs_amount, packs_posle_finisha, pack_time, tone_time, num_time, body_time, qam16) # выводим на экран информацию о конкурсе

# Формируем пакеты до и после старта

data_pre, data_pre_sends_count = data_gen(packs_do_starta, n_info)
data_post, data_post_sends_count = data_gen(packs_posle_finisha, n_info)

freqs_list_pre = np.random.randint(-5, 6, packs_do_starta)*1e6 + 450e6 # генерируем заранее список частот
freqs_list_post = np.random.randint(-5, 6, packs_posle_finisha)*1e6 + 450e6

# ПЕРЕДАЧА ПАКЕТОВ -----------------------------------------

chan = 0
gain = 50

sdr = SoapySDR.Device("lime")
sdr.setSampleRate(SOAPY_SDR_TX, chan, sample_rate)
sdr.setGain(SOAPY_SDR_TX, chan, gain)
sdr.setAntenna(SOAPY_SDR_TX, chan, "BAND1")

tx_stream = sdr.setupStream(SOAPY_SDR_TX, SOAPY_SDR_CF32, [chan])
sdr.activateStream(tx_stream)

sdr_info = {'sdr': sdr, 'chan': chan, 'len_add': len_add, 'stream': tx_stream, 'ones_MTU': ones_MTU, 'sample_rate': sample_rate, 'ones_add': ones_add, 'MTU': MTU}

input("\n[ACTION] Press Enter to continue...") # нажать, чтобы начать конкурс

t0 = time() # начинаем отсчёт времени

print('\n[EVENT] Sending additional packs...')
#transmit(sdr_info, tone_sends_count, pack_numbers, data, data_sends_count, n_packs, freqs_list)
transmit(sdr_info, tone_sends_count, pack_numbers_final[0:packs_do_starta], data_pre, data_pre_sends_count, packs_do_starta, freqs_list_pre) # отправляем пакеты до старта

# отправляем сигнал старта
sdr.setFrequency(SOAPY_SDR_TX, chan, freq)
sdr.setGain(SOAPY_SDR_TX, chan, gain)
print('\n[EVENT] START!')
for _ in range(marker_tone_sends_count):
    sdr.writeStream(tx_stream, [ones_MTU], MTU)
    sleep(MTU / sample_rate)

print('\n[EVENT] Sending actual packs...')
t00 = time()
transmit(sdr_info, tone_sends_count, pack_numbers_final[packs_do_starta:packs_do_starta+packs_amount], data_main, data_sends_count_main, packs_amount, freqs_list) # основные пакеты
                        
# отправляем сигнал финиша
print('\n[EVENT] FINISH!')
sdr.setFrequency(SOAPY_SDR_TX, chan, freq)
sdr.setGain(SOAPY_SDR_TX, chan, gain)
for _ in range(marker_tone_sends_count):
    sdr.writeStream(tx_stream, [ones_MTU], MTU)
    sleep(MTU/sample_rate)

print('\n[EVENT] Sending additional packs...')
t_main = time() - t00
transmit(sdr_info, tone_sends_count, pack_numbers_final[packs_do_starta+packs_amount::], data_post, data_post_sends_count, packs_posle_finisha, freqs_list_post) # отправляем пакеты после старта

print('\n[EVENT] STOP!')
t_end = time() - t0
print('[RESULT]: Time passed: %.2f s' % t_end)
print('[RESULT]: Real time passed: %.2f s' % t_main)
sleep(1)

# закрываем стрим
sdr.deactivateStream(tx_stream)
sdr.closeStream(tx_stream)

countdown(t0, 60)

print('\n--- ALL DONE --- \n')
