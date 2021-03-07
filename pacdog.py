#!/usr/bin/python3

import subprocess

def generate(code, intensity, button, beep):
    pre_checksum = code[0:2] + intensity + button[0] + code[2:]
    post_checksum = beep + button[1:]
    data = pre_checksum + "SSSSS" + post_checksum

    # a b c d e f g h i  j  k  l  m  n  o  p q   r  s
    # 7 6 5 4 3 2 1 0 15 14 13 12 11 10 09 8 23 22 21

    temp = pre_checksum
    temp = temp + str((int(data[0]) + int(data[ 8])) % 2)
    temp = temp + str((int(data[1]) + int(data[ 9]) + int(data[21])) % 2)
    temp = temp + str((int(data[2]) + int(data[10]) + int(data[22])) % 2)
    temp = temp + str((int(data[3]) + int(data[11]) + int(data[23])) % 2)
    temp = temp + str((int(data[4]) + int(data[12])) % 2)
    temp = temp + post_checksum
    return temp

def encode(data):
    prefix = "0101010101010101111"
    filler = "10"
    res = prefix + filler
    for bit in data:
        res = res + bit + filler
    return res

def send(data):
    cmd = [
        "urh_cli",
        "--transmit",
        "--device", "HackRF",
        "--frequency", "27.1e6",
        "--sample-rate", "2e6",
        "--carrier-frequency", "27.1e6",
        "--modulation-type", "FSK",
        "--samples-per-symbol", "3100",
        "--parameters", "92e3", "95e3",
        "--messages", data]
    print(cmd)
    subprocess.run(cmd)
    
def test_encoding():
    expected = "010101010101010111110110010010110010010110010010010010110110110110110110110110010110110110010"
    data = "100100100001111111101110"
    encoded = encode(data)
    print(expected)
    print(encoded)
    print(expected == encoded)

def test_generate():
    expected = "100100100001111111101110"
    encoded = generate("100011111", "010010", "010", "1")
    print(expected)
    print(encoded)
    print(expected == encoded)

def test():
    test_encoding()
    test_generate()

# test()

send(encode(generate("100011111", "010010", "010", "1"))

