a = {'aaa': 3,
     'bbb': 'ccc'}
with open('a.dat', 'wb') as f:
    f.write(bytes(str(a).encode()))
with open('a.dat', 'rb') as g:
    data = g.read()

data = data.decode()
print(type(data))
b = eval(f'{data}')
print(type(b))
print(b.get('ccc'))
print(b.get('aaa'))
print(b.get('bbb'))