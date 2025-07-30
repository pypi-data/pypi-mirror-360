import hashlib

# MD5 编码 应用haslib
"""
user = 'username:张三'.encode(encoding='utf-8')
pwd = 'pass123456'.encode('utf-8')
user_MD5 = hashlib.md5(user).hexdigest()
pwd_MD5 = hashlib.md5(pwd).hexdigest()
print('user_MD5:', user_MD5)
print('pwd_MD5:', pwd_MD5)

# hashlib的编码:md5 sha1 sha3_224 sha3_256 sha3_384 sha3_512 sha224 sha384 sha512 shake_128 shake_256
a = "hello word".encode()
print('hello word:md5 = ', hashlib.md5(a).hexdigest())
print('hello word:sha1 = ', hashlib.sha1(a).hexdigest())
print('hello word:sha224 = ', hashlib.sha224(a).hexdigest())
print('hello word:sha256 = ', hashlib.sha256(a).hexdigest())
print('hello word:sha384 = ', hashlib.sha384(a).hexdigest())
print('hello word:sha512 = ', hashlib.sha512(a).hexdigest())
"""



