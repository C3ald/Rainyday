import sys
from io import BytesIO
from itertools import cycle
print('first arg is key, second is mode (1 is encrypt and 2 is decrypt), and third is the file')
key = sys.argv[1].encode()
MODE = int(sys.argv[2])
file = open(sys.argv[3], 'rb')

def xore(data, key):
        return bytes(a ^ b for a, b in zip(data, cycle(key)))
def encrypt():
        f = BytesIO(file.read())
        enc = xore(f.read(), key)
        out = open('enc.txt', 'wb')
        out.write(enc)

def decrypt():
        f = BytesIO(file.read())
        dec = xore(f.read(), key)
        out = open('dec.exe', 'wb')
        out.write(dec)

if MODE == 1:
        encrypt()
if MODE == 2:
        decrypt()