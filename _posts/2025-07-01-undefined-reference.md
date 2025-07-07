---
title: "undefined reference 问题查找"
date: 2025-07-01 08:00:00 +0800
published: true
categories: [教程]
tags: [C++,C]
image: 
---

## 问题

当编译器在链接报 undefined symbol 时，大部分情况下都会给出函数的调用链，但有些情况下不会给出相关信息，所以需要手动查找

假设有如下代码：

```cpp
#include <variant>
int main()
{
    std::variant<int,double> v = 1.1;
    auto i = std::get<int>(v);
}
```

编译:

```bash
arm-none-eabi-g++ test.cpp -fno-exceptions
```

如果部分嵌入式 C++ 库没有实现 abort 函数的定义，则会报错:

```plaintext
$ arm-none-eabi-g++ test.cpp -fno-exceptions
d:/tools/arm gnu toolchain arm-none-eabi/12.2 rel1/bin/../lib/gcc/arm-none-eabi/12.2.1/../../../../arm-none-eabi/bin/ld.exe: d:/tools/arm gnu toolchain arm-none-eabi/12.2 rel1/bin/../lib/gcc/arm-none-eabi/12.2.1\libc.a(libc_a-exit.o): in function `exit':
exit.c:(.text.exit+0x28): undefined reference to `_exit'
d:/tools/arm gnu toolchain arm-none-eabi/12.2 rel1/bin/../lib/gcc/arm-none-eabi/12.2.1/../../../../arm-none-eabi/bin/ld.exe: d:/tools/arm gnu toolchain arm-none-eabi/12.2 rel1/bin/../lib/gcc/arm-none-eabi/12.2.1\libc.a(libc_a-abort.o): in function `abort':
abort.c:(.text.abort+0x10): undefined reference to `_exit'
```

## 解决过程

生成 `.o` 文件:

```bash
arm-none-eabi-g++ -g -c test.cpp
```

使用 nm 工具(列出符号表)查找目录下引用了该函数的 `.o` 文件(假设是个大型项目，有很多文件)：

```cpp
find . -name '*.o' -exec sh -c 'nm -C {} | grep " U.* abort" >/dev/null && echo {}' \;
```

查找到其中的 `./test.o` 使用了 `abort`:

```cpp
$ find . -name '*.o' -exec sh -c 'nm -C {} | grep " U.* abort" >/dev/null && echo {}' \;
./test.o
```

```plaintext
$ nm -C test.o
00000000 t $a
00000000 t $a
00000000 t $a
00000000 t $a
00000000 t $a
00000000 t $a
00000000 t $a
00000000 t $a
00000000 t $a
00000000 t $a
00000000 t $a
00000000 t $a
00000000 t $a
00000044 t $d
00000000 r $d
00000068 t $d
00000000 W std::variant<int, double>::valueless_by_exception() const
00000000 W std::variant<int, double>::index() const
00000000 W std::__detail::__variant::_Variant_storage<true, int, double>::_M_valid() const
00000000 W std::__detail::__variant::_Uninitialized<int, true>::_M_get() &
00000000 W decltype(auto) std::__detail::__variant::__get<0u, std::variant<int, double>&>(std::variant<int, double>&)
00000000 W decltype(auto) std::__detail::__variant::__get_n<0u, std::__detail::__variant::_Variadic_union<int, double>&>(std::__detail::__variant::_Variadic_union<int, double>&)
00000000 W std::__throw_bad_variant_access(bool)
00000000 W std::__throw_bad_variant_access(char const*)
00000000 W int& std::get<int, int, double>(std::variant<int, double>&)
00000000 W std::variant_alternative<0u, std::variant<int, double> >::type& std::get<0u, int, double>(std::variant<int, double>&)
00000000 W std::__detail::__variant::_Variadic_union<int, double>& std::forward<std::__detail::__variant::_Variadic_union<int, double>&>(std::remove_reference<std::__detail::__variant::_Variadic_union<int, double>&>::type&)
00000000 W std::variant<int, double>& std::forward<std::variant<int, double>&>(std::remove_reference<std::variant<int, o 
uble>&>::type&)
         U abort
00000000 T main
```

使用 objdump 反汇编并查找引用路径：

```plaintext
arm-none-eabi-objdump -Cd test.o | c++filt | grep -A10 -B10 'abort'
```

```bash
$ arm-none-eabi-objdump -Cd test.o | c++filt | grep -A10 -B10 'abort'
  68:   9999999a        .word   0x9999999a
  6c:   3ff19999        .word   0x3ff19999

Disassembly of section .text._ZSt26__throw_bad_variant_accessPKc:

00000000 <std::__throw_bad_variant_access(char const*)>:
   0:   e92d4800        push    {fp, lr}
   4:   e28db004        add     fp, sp, #4
   8:   e24dd008        sub     sp, sp, #8
   c:   e50b0008        str     r0, [fp, #-8]
  10:   ebfffffe        bl      0 <abort>

Disassembly of section .text._ZSt26__throw_bad_variant_accessb:

00000000 <std::__throw_bad_variant_access(bool)>:
   0:   e92d4800        push    {fp, lr}
   4:   e28db004        add     fp, sp, #4
   8:   e24dd008        sub     sp, sp, #8
   c:   e1a03000        mov     r3, r0
  10:   e54b3005        strb    r3, [fp, #-5]
  14:   e55b3005        ldrb    r3, [fp, #-5]
```

可以发现是 varient 库内部 abort。

## 附件

test.objdump:

```plaintext

test.o:     file format elf32-littlearm


Disassembly of section .text:

00000000 <main>:
   0:	e92d4800 	push	{fp, lr}
   4:	e28db004 	add	fp, sp, #4
   8:	e24dd018 	sub	sp, sp, #24
   c:	e24b301c 	sub	r3, fp, #28
  10:	e3a02000 	mov	r2, #0
  14:	e5832000 	str	r2, [r3]
  18:	e5832004 	str	r2, [r3, #4]
  1c:	e5832008 	str	r2, [r3, #8]
  20:	e583200c 	str	r2, [r3, #12]
  24:	e28f303c 	add	r3, pc, #60	; 0x3c
  28:	e893000c 	ldm	r3, {r2, r3}
  2c:	e50b201c 	str	r2, [fp, #-28]	; 0xffffffe4
  30:	e50b3018 	str	r3, [fp, #-24]	; 0xffffffe8
  34:	e3a03001 	mov	r3, #1
  38:	e54b3014 	strb	r3, [fp, #-20]	; 0xffffffec
  3c:	e24b301c 	sub	r3, fp, #28
  40:	e1a00003 	mov	r0, r3
  44:	ebfffffe 	bl	0 <main>
  48:	e1a03000 	mov	r3, r0
  4c:	e5933000 	ldr	r3, [r3]
  50:	e50b3008 	str	r3, [fp, #-8]
  54:	e3a03000 	mov	r3, #0
  58:	e1a00003 	mov	r0, r3
  5c:	e24bd004 	sub	sp, fp, #4
  60:	e8bd4800 	pop	{fp, lr}
  64:	e12fff1e 	bx	lr
  68:	9999999a 	.word	0x9999999a
  6c:	3ff19999 	.word	0x3ff19999

Disassembly of section .text._ZSt26__throw_bad_variant_accessPKc:

00000000 <std::__throw_bad_variant_access(char const*)>:
   0:	e92d4800 	push	{fp, lr}
   4:	e28db004 	add	fp, sp, #4
   8:	e24dd008 	sub	sp, sp, #8
   c:	e50b0008 	str	r0, [fp, #-8]
  10:	ebfffffe 	bl	0 <abort>

Disassembly of section .text._ZSt26__throw_bad_variant_accessb:

00000000 <std::__throw_bad_variant_access(bool)>:
   0:	e92d4800 	push	{fp, lr}
   4:	e28db004 	add	fp, sp, #4
   8:	e24dd008 	sub	sp, sp, #8
   c:	e1a03000 	mov	r3, r0
  10:	e54b3005 	strb	r3, [fp, #-5]
  14:	e55b3005 	ldrb	r3, [fp, #-5]
  18:	e3530000 	cmp	r3, #0
  1c:	0a000002 	beq	2c <std::__throw_bad_variant_access(bool)+0x2c>
  20:	e59f001c 	ldr	r0, [pc, #28]	; 44 <std::__throw_bad_variant_access(bool)+0x44>
  24:	ebfffffe 	bl	0 <std::__throw_bad_variant_access(bool)>
  28:	ea000001 	b	34 <std::__throw_bad_variant_access(bool)+0x34>
  2c:	e59f0014 	ldr	r0, [pc, #20]	; 48 <std::__throw_bad_variant_access(bool)+0x48>
  30:	ebfffffe 	bl	0 <std::__throw_bad_variant_access(bool)>
  34:	e1a00000 	nop			; (mov r0, r0)
  38:	e24bd004 	sub	sp, fp, #4
  3c:	e8bd4800 	pop	{fp, lr}
  40:	e12fff1e 	bx	lr
  44:	00000000 	.word	0x00000000
  48:	00000020 	.word	0x00000020

Disassembly of section .text._ZSt3getIiJidEERT_RSt7variantIJDpT0_EE:

00000000 <int& std::get<int, int, double>(std::variant<int, double>&)>:
   0:	e92d4800 	push	{fp, lr}
   4:	e28db004 	add	fp, sp, #4
   8:	e24dd010 	sub	sp, sp, #16
   c:	e50b0010 	str	r0, [fp, #-16]
  10:	e3a03000 	mov	r3, #0
  14:	e50b3008 	str	r3, [fp, #-8]
  18:	e51b0010 	ldr	r0, [fp, #-16]
  1c:	ebfffffe 	bl	0 <int& std::get<int, int, double>(std::variant<int, double>&)>
  20:	e1a03000 	mov	r3, r0
  24:	e1a00003 	mov	r0, r3
  28:	e24bd004 	sub	sp, fp, #4
  2c:	e8bd4800 	pop	{fp, lr}
  30:	e12fff1e 	bx	lr

Disassembly of section .text._ZNSt8__detail9__variant7__get_nILj0ERNS0_15_Variadic_unionIJidEEEEEDcOT0_:

00000000 <decltype(auto) std::__detail::__variant::__get_n<0u, std::__detail::__variant::_Variadic_union<int, double>&>(std::__detail::__variant::_Variadic_union<int, double>&)>:
   0:	e92d4800 	push	{fp, lr}
   4:	e28db004 	add	fp, sp, #4
   8:	e24dd008 	sub	sp, sp, #8
   c:	e50b0008 	str	r0, [fp, #-8]
  10:	e51b0008 	ldr	r0, [fp, #-8]
  14:	ebfffffe 	bl	0 <decltype(auto) std::__detail::__variant::__get_n<0u, std::__detail::__variant::_Variadic_union<int, double>&>(std::__detail::__variant::_Variadic_union<int, double>&)>
  18:	e1a03000 	mov	r3, r0
  1c:	e1a00003 	mov	r0, r3
  20:	ebfffffe 	bl	0 <decltype(auto) std::__detail::__variant::__get_n<0u, std::__detail::__variant::_Variadic_union<int, double>&>(std::__detail::__variant::_Variadic_union<int, double>&)>
  24:	e1a03000 	mov	r3, r0
  28:	e1a00003 	mov	r0, r3
  2c:	e24bd004 	sub	sp, fp, #4
  30:	e8bd4800 	pop	{fp, lr}
  34:	e12fff1e 	bx	lr

Disassembly of section .text._ZNSt8__detail9__variant5__getILj0ERSt7variantIJidEEEEDcOT0_:

00000000 <decltype(auto) std::__detail::__variant::__get<0u, std::variant<int, double>&>(std::variant<int, double>&)>:
   0:	e92d4800 	push	{fp, lr}
   4:	e28db004 	add	fp, sp, #4
   8:	e24dd008 	sub	sp, sp, #8
   c:	e50b0008 	str	r0, [fp, #-8]
  10:	e51b0008 	ldr	r0, [fp, #-8]
  14:	ebfffffe 	bl	0 <decltype(auto) std::__detail::__variant::__get<0u, std::variant<int, double>&>(std::variant<int, double>&)>
  18:	e1a03000 	mov	r3, r0
  1c:	e1a00003 	mov	r0, r3
  20:	ebfffffe 	bl	0 <decltype(auto) std::__detail::__variant::__get<0u, std::variant<int, double>&>(std::variant<int, double>&)>
  24:	e1a03000 	mov	r3, r0
  28:	e1a00003 	mov	r0, r3
  2c:	e24bd004 	sub	sp, fp, #4
  30:	e8bd4800 	pop	{fp, lr}
  34:	e12fff1e 	bx	lr

Disassembly of section .text._ZSt3getILj0EJidEERNSt19variant_alternativeIXT_ESt7variantIJDpT0_EEE4typeERS4_:

00000000 <std::variant_alternative<0u, std::variant<int, double> >::type& std::get<0u, int, double>(std::variant<int, double>&)>:
   0:	e92d4800 	push	{fp, lr}
   4:	e28db004 	add	fp, sp, #4
   8:	e24dd008 	sub	sp, sp, #8
   c:	e50b0008 	str	r0, [fp, #-8]
  10:	e51b0008 	ldr	r0, [fp, #-8]
  14:	ebfffffe 	bl	0 <std::variant_alternative<0u, std::variant<int, double> >::type& std::get<0u, int, double>(std::variant<int, double>&)>
  18:	e1a03000 	mov	r3, r0
  1c:	e3530000 	cmp	r3, #0
  20:	13a03001 	movne	r3, #1
  24:	03a03000 	moveq	r3, #0
  28:	e20330ff 	and	r3, r3, #255	; 0xff
  2c:	e3530000 	cmp	r3, #0
  30:	0a000004 	beq	48 <std::variant_alternative<0u, std::variant<int, double> >::type& std::get<0u, int, double>(std::variant<int, double>&)+0x48>
  34:	e51b0008 	ldr	r0, [fp, #-8]
  38:	ebfffffe 	bl	0 <std::variant_alternative<0u, std::variant<int, double> >::type& std::get<0u, int, double>(std::variant<int, double>&)>
  3c:	e1a03000 	mov	r3, r0
  40:	e1a00003 	mov	r0, r3
  44:	ebfffffe 	bl	0 <std::variant_alternative<0u, std::variant<int, double> >::type& std::get<0u, int, double>(std::variant<int, double>&)>
  48:	e51b0008 	ldr	r0, [fp, #-8]
  4c:	ebfffffe 	bl	0 <std::variant_alternative<0u, std::variant<int, double> >::type& std::get<0u, int, double>(std::variant<int, double>&)>
  50:	e1a03000 	mov	r3, r0
  54:	e1a00003 	mov	r0, r3
  58:	e24bd004 	sub	sp, fp, #4
  5c:	e8bd4800 	pop	{fp, lr}
  60:	e12fff1e 	bx	lr

Disassembly of section .text._ZNKSt7variantIJidEE5indexEv:

00000000 <std::variant<int, double>::index() const>:
   0:	e52db004 	push	{fp}		; (str fp, [sp, #-4]!)
   4:	e28db000 	add	fp, sp, #0
   8:	e24dd00c 	sub	sp, sp, #12
   c:	e50b0008 	str	r0, [fp, #-8]
  10:	e51b3008 	ldr	r3, [fp, #-8]
  14:	e5d33008 	ldrb	r3, [r3, #8]
  18:	e1a00003 	mov	r0, r3
  1c:	e28bd000 	add	sp, fp, #0
  20:	e49db004 	pop	{fp}		; (ldr fp, [sp], #4)
  24:	e12fff1e 	bx	lr

Disassembly of section .text._ZNKSt7variantIJidEE22valueless_by_exceptionEv:

00000000 <std::variant<int, double>::valueless_by_exception() const>:
   0:	e92d4800 	push	{fp, lr}
   4:	e28db004 	add	fp, sp, #4
   8:	e24dd008 	sub	sp, sp, #8
   c:	e50b0008 	str	r0, [fp, #-8]
  10:	e51b3008 	ldr	r3, [fp, #-8]
  14:	e1a00003 	mov	r0, r3
  18:	ebfffffe 	bl	0 <std::variant<int, double>::valueless_by_exception() const>
  1c:	e1a03000 	mov	r3, r0
  20:	e2233001 	eor	r3, r3, #1
  24:	e20330ff 	and	r3, r3, #255	; 0xff
  28:	e1a00003 	mov	r0, r3
  2c:	e24bd004 	sub	sp, fp, #4
  30:	e8bd4800 	pop	{fp, lr}
  34:	e12fff1e 	bx	lr

Disassembly of section .text._ZSt7forwardIRSt7variantIJidEEEOT_RNSt16remove_referenceIS3_E4typeE:

00000000 <std::variant<int, double>& std::forward<std::variant<int, double>&>(std::remove_reference<std::variant<int, double>&>::type&)>:
   0:	e52db004 	push	{fp}		; (str fp, [sp, #-4]!)
   4:	e28db000 	add	fp, sp, #0
   8:	e24dd00c 	sub	sp, sp, #12
   c:	e50b0008 	str	r0, [fp, #-8]
  10:	e51b3008 	ldr	r3, [fp, #-8]
  14:	e1a00003 	mov	r0, r3
  18:	e28bd000 	add	sp, fp, #0
  1c:	e49db004 	pop	{fp}		; (ldr fp, [sp], #4)
  20:	e12fff1e 	bx	lr

Disassembly of section .text._ZSt7forwardIRNSt8__detail9__variant15_Variadic_unionIJidEEEEOT_RNSt16remove_referenceIS5_E4typeE:

00000000 <std::__detail::__variant::_Variadic_union<int, double>& std::forward<std::__detail::__variant::_Variadic_union<int, double>&>(std::remove_reference<std::__detail::__variant::_Variadic_union<int, double>&>::type&)>:
   0:	e52db004 	push	{fp}		; (str fp, [sp, #-4]!)
   4:	e28db000 	add	fp, sp, #0
   8:	e24dd00c 	sub	sp, sp, #12
   c:	e50b0008 	str	r0, [fp, #-8]
  10:	e51b3008 	ldr	r3, [fp, #-8]
  14:	e1a00003 	mov	r0, r3
  18:	e28bd000 	add	sp, fp, #0
  1c:	e49db004 	pop	{fp}		; (ldr fp, [sp], #4)
  20:	e12fff1e 	bx	lr

Disassembly of section .text._ZNRSt8__detail9__variant14_UninitializedIiLb1EE6_M_getEv:

00000000 <std::__detail::__variant::_Uninitialized<int, true>::_M_get() &>:
   0:	e52db004 	push	{fp}		; (str fp, [sp, #-4]!)
   4:	e28db000 	add	fp, sp, #0
   8:	e24dd00c 	sub	sp, sp, #12
   c:	e50b0008 	str	r0, [fp, #-8]
  10:	e51b3008 	ldr	r3, [fp, #-8]
  14:	e1a00003 	mov	r0, r3
  18:	e28bd000 	add	sp, fp, #0
  1c:	e49db004 	pop	{fp}		; (ldr fp, [sp], #4)
  20:	e12fff1e 	bx	lr

Disassembly of section .text._ZNKSt8__detail9__variant16_Variant_storageILb1EJidEE8_M_validEv:

00000000 <std::__detail::__variant::_Variant_storage<true, int, double>::_M_valid() const>:
   0:	e52db004 	push	{fp}		; (str fp, [sp, #-4]!)
   4:	e28db000 	add	fp, sp, #0
   8:	e24dd00c 	sub	sp, sp, #12
   c:	e50b0008 	str	r0, [fp, #-8]
  10:	e3a03001 	mov	r3, #1
  14:	e1a00003 	mov	r0, r3
  18:	e28bd000 	add	sp, fp, #0
  1c:	e49db004 	pop	{fp}		; (ldr fp, [sp], #4)
  20:	e12fff1e 	bx	lr
```
