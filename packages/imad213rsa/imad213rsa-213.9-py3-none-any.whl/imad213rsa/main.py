#IMAD 213 RSA PYTHON
import sys, base64, zlib, os
from Crypto.Cipher import AES

def fake1(x): return x[::-1]
def unfake1(x): return x[::-1]
def fake2(x): return ''.join(chr(ord(c) ^ 0x5A) for c in x)
def unfake2(x): return ''.join(chr(ord(c) ^ 0x5A) for c in x)
def fake3(x): return ''.join(chr((ord(c)+7)%256) for c in x)
def unfake3(x): return ''.join(chr((ord(c)-7)%256) for c in x)
def fake4(x): return ''.join(chr((ord(c)-7)%256) for c in x)
def unfake4(x): return ''.join(chr((ord(c)+7)%256) for c in x)
def fake5(x): return x.swapcase()
def unfake5(x): return x.swapcase()
fake_funcs = [fake1, fake2, fake3, fake4, fake5]
unfake_funcs = [unfake1, unfake2, unfake3, unfake4, unfake5]

def xor_decrypt(data: bytes, key: bytes):
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

def reconstruct_key(parts, indices, types):
    ordered = [None]*len(parts)
    for i, idx in enumerate(indices):
        part = parts[i][2:-2]
        func = unfake_funcs[types[i]]
        part = func(part)
        ordered[idx] = part
    key_b64 = ''.join(ordered)
    missing = len(key_b64) % 4
    if missing: key_b64 += "=" * (4-missing)
    return base64.b64decode(key_b64)

#IMAD 213 FUCK RSA
def EyMjuflUNe(): return 79
def kIMLGT0n56(): return 51
def lP1ERp6tZI(): return 29
def LqY0tRtEm0(): return 20
def ZJTEsXhs3D(): return 65
def lDG0GoxE5D(): return 42
def fM3pfAmQVL(): return 44
def mfLGuz4XRd(): return 4
def nNDnygYWdo(): return 63
def COJJhkRqVL(): return 6
def IP7Nn8Xq4c(): return 58
def dy5wO4HyCe(): return 54

parts = ['I9PB9PnalH', 'SR41#\x17b=MY', 'sNNega+pPs', 'dw,"\x0f4u,vi', 'uvvDq2', 'fa\x03\x1e4j1\x1bVh', 'pd=7]ltzsa', 'Tlg11spKpq']
indices = [2, 6, 4, 3, 7, 5, 0, 1]
types = [0, 1, 4, 1, 2, 1, 2, 3]

nonce = base64.b64decode("tLyCU7griaayr+yS")
tag = base64.b64decode("wrPLdKOa/HZt3V10Xm2TPg==")
ciphertext_b64 = "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"
xorkey_b64 = "JUzhOfbcCWvbQtOaz0QaNA=="

if any(x in os.environ for x in ["PYCHARM_HOSTED", "VIRTUAL_ENV"]) or "PYDEV_DEBUGGER" in sys.modules:
    print("Debugging/VM Detected! Exiting.")
    sys.exit(1)

try:
    key = reconstruct_key(parts, indices, types)
    xorkey = base64.b64decode(xorkey_b64)
    data = base64.b64decode(ciphertext_b64)
    data = xor_decrypt(data, xorkey)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    dec = cipher.decrypt_and_verify(data, tag)
    exec(zlib.decompress(dec).decode('utf-8'))
except Exception as e:
    print("\n[!] Error during decryption or execution:", e)
    sys.exit(1)
