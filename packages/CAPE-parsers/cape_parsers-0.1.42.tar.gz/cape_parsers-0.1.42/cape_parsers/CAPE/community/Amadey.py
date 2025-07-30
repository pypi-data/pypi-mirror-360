import base64
import re

str_hash_data = 'd6052c4fe86a6346964a6bbbe2423e20'
str_alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 '

def is_ascii(s):
    return all(c < 128 or c == 0 for c in s)

def decrypt(str_data, str_hash_data, str_alphabet):
    str_hash = ''

    for i in range(len(str_data)):
        str_hash += str_hash_data[i % len(str_hash_data)]

    out = ''

    for i in range(len(str_data)):
        if str_data[i] not in str_alphabet:
            out += str_data[i]
            continue
        alphabet_count = str_alphabet.find(str_data[i])
        hash_count = str_alphabet.find(str_hash[i])
        index_calc = (alphabet_count + len(str_alphabet) - hash_count) % len(str_alphabet)
        out += str_alphabet[index_calc]

    return base64.b64decode(out)

file_data = open('/tmp/amadey.bin','rb').read()

strings = []
for m in re.finditer(rb'[a-zA-Z =0-9]{4,}',file_data):
    strings.append(m.group().decode('utf-8'))

for s in strings:
    try:
        temp = decrypt(s, str_hash_data, str_alphabet)
        if is_ascii(temp) and len(temp) > 3:
            print(temp.decode('utf-8'))
    except:
        continue

decrypt('1RydQIOr3Zcp6emn RYv8IGzgUKS6r5ThSdqDVBERAP2Ir 0JQ1=', str_hash_data, str_alphabet)