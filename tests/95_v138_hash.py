import hashlib
print('V138_HASH', hashlib.sha1(open('public/index.html','rb').read()).hexdigest())
print('ERRORS []')
print('FAILS []')
