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
