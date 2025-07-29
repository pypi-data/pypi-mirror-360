#IMAD 213 CODE 2025
import sys, os, zlib, base64
from Crypto.Cipher import AES

def f1(x): return x[::-1]
def f2(x): return ''.join(chr(ord(c)^0x5A) for c in x)
def f3(x): return ''.join(chr((ord(c)+7)%256) for c in x)
def f4(x): return ''.join(chr((ord(c)-7)%256) for c in x)
def f5(x): return x.swapcase()
uf = [f1, f2, f4, f3, f5]

def xor_decrypt(data, key):
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

def reconstruct_key(parts, indices, types):
    ordered = [None]*len(parts)
    for i, idx in enumerate(indices):
        part = parts[i][2:-2]
        func = uf[types[i]]
        ordered[idx] = func(part)
    k = ''.join(ordered)
    pad = len(k) % 4
    if pad: k += '='*(4-pad)
    return base64.b64decode(k)

def GX8XFzyS(): return 189
def ln7Nwl1c(): return 58
def WagMimzS(): return 960
def azyPe91b(): return 575
def GCaLsJKe(): return 139
def aoRNjAyr(): return 797
def DcB90Kfj(): return 883
def uxrB0y2M(): return 218
def doaWVsR4(): return 390
def fEvUHAmQ(): return 286
def oKbyIPDe(): return 387
def bVbf1Vwo(): return 139

parts = ['b4k\x17\x0c\x13\x13\x0fO2', 'x6WAf9K6Lg', 'DVm\x18\x1e\x11j\x0csF', 'PqpZvrVfBb', 'DFB6Bq', 'M6\x08nnj+(L7', 'OMfpkAHkLl', 'gkBHqF7yEy']
indices = [5, 6, 2, 4, 7, 3, 1, 0]
types = [1, 4, 1, 4, 3, 1, 0, 4]
nonce = base64.b64decode("op+F6ZATamPTxuwA")
tag = base64.b64decode("yc3+7RqrQYqKvEu1juHcBg==")
ciphertext_b64 = "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"
xorkey_b64 = "rYxhq1Edffopryy3DQH47g=="

if any(env in os.environ for env in ["PYCHARM_HOSTED", "VIRTUAL_ENV", "TERMUX", "SSH_CONNECTION"]) or "pydevd" in sys.modules:
    print("Blocked environment detected. Exiting.")
    sys.exit(1)

try:
    key = reconstruct_key(parts, indices, types)
    xorkey = base64.b64decode(xorkey_b64)
    ct = base64.b64decode(ciphertext_b64)
    raw = xor_decrypt(ct, xorkey)
    dec = AES.new(key, AES.MODE_GCM, nonce=nonce)
    code = dec.decrypt_and_verify(raw, tag)
    exec(zlib.decompress(code).decode())
except Exception as e:
    print("Decryption failed:", e)
    sys.exit(1)
