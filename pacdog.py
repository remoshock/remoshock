#!/usr/bin/python3

import subprocess

def encode(data):
    prefix = "0101010101010101111"
    filler = "10"
    res = prefix + filler
    for bit in data:
        res = res + bit + filler
    return res

    
def test():
    expected = "010101010101010111110110010010110010010110010010010010110110110110110110110110010110110110010"
    data = "100100100001111111101110"
    encoded = encode(data)
    print(expected)
    print(encoded)
    print(expected == encoded)

test()

