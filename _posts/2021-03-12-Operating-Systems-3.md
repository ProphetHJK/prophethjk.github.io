---
title: "《Operating Systems: Three Easy Pieces》学习笔记(三) 插叙：进程 API"
author: Jinkai
date: 2021-03-12 17:00:00 +0800
published: true
categories: [学习笔记]
tags: [Operating Systems, 操作系统导论]
---

> 参考：
>
> - [Operating Systems: Three Easy Pieces 中文版](https://pages.cs.wisc.edu/~remzi/OSTEP/Chinese/)

## fork()系统调用

在执行函数 fork()时，创建了一个子进程，此时是两个进程同时运行

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char *argv[])
{
    printf("hello world (pid:%d)\n", (int)getpid());
    int rc = fork();
    if (rc < 0)
    { // fork failed; exit
        fprintf(stderr, "fork failed\n");
        exit(1);
    }
    else if (rc == 0)
    { // child (new process)
        printf("hello, I am child (pid:%d)\n", (int)getpid());
    }
    else
    { // parent goes down this path (main)
        printf("hello, I am parent of %d (pid:%d)\n",
               rc, (int)getpid());
    }
    return 0;
}
```

输入如下：

```shell
prompt> ./p1
hello world (pid:29146)
hello, I am parent of 29147 (pid:29146)
hello, I am child (pid:29147)
prompt>
```

上面这段程序执行了一次 fork 操作，`fork()`函数是一个神奇的操作，它只被调用了一次，却产生了两个返回值。对于`父进程`来说，其返回值是子进程的 pid；对于`子进程`来说，其返回值为 0。

子进程并`不是完全拷贝`了父进程，所以子进程不会从 main 开始执行，该程序的首行打印并未被子进程执行。**它拥有自己的`地址空间`（即拥有自己的私有内存）、`寄存器`、`程序计数器`等**。

此处父进程与子进程的执行顺序并不是绝对的，取决于 cpu 的调度算法，子进程也可能比父进程先执行完

> TODO: fork()函数的具体原理还有待进一步学习

## wait()系统调用

`wait()`函数用于使父进程（也就是调用 wait()的进程）`阻塞`，直到`一个子进程结束`或者该进程接收到了一个`指定的信号`为止。

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int main(int argc, char *argv[])
{
    printf("hello world (pid:%d)\n", (int)getpid());
    int rc = fork();
    if (rc < 0)
    { // fork failed; exit
        fprintf(stderr, "fork failed\n");
        exit(1);
    }
    else if (rc == 0)
    { // child (new process)
        printf("hello, I am child (pid:%d)\n", (int)getpid());
    }
    else
    { // parent goes down this path (main)
        int wc = wait(NULL);
        printf("hello, I am parent of %d (wc:%d) (pid:%d)\n",
               rc, wc, (int)getpid());
    }
    return 0;
}
```

```shell
prompt> ./p2
hello world (pid:29266)
hello, I am child (pid:29267)
hello, I am parent of 29267 (wc:29267) (pid:29266)
prompt>
```

本例中，子进程却优先于父进程执行完毕，这是因为父进程调用了`wait()`操作

当父进程先执行时，会等待子进程结束，才会继续执行

## exec()系统调用

exec()这个系统调用可以让子进程执行与父进程不同的程序

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/wait.h>

int main(int argc, char *argv[])
{
    printf("hello world (pid:%d)\n", (int)getpid());
    int rc = fork();
    if (rc < 0)
    { // fork failed; exit
        fprintf(stderr, "fork failed\n");
        exit(1);
    }
    else if (rc == 0)
    { // child (new process)
        printf("hello, I am child (pid:%d)\n", (int)getpid());
        char *myargs[3];
        myargs[0] = strdup("wc");   // program: "wc" (word count)
        myargs[1] = strdup("p3.c"); // argument: file to count
        myargs[2] = NULL;           // marks end of array
        execvp(myargs[0], myargs);  // runs word count
        printf("this shouldn't print out");
    }
    else
    { // parent goes down this path (main)
        int wc = wait(NULL);
        printf("hello, I am parent of %d (wc:%d) (pid:%d)\n",
               rc, wc, (int)getpid());
    }
    return 0;
}
```

```shell
prompt> ./p3
hello world (pid:29383)
hello, I am child (pid:29384)
 29 107 1030 p3.c
hello, I am parent of 29384 (wc:29384) (pid:29383)
prompt>
```

在这个例子中，子进程调用 `execvp()`来运行字符计数程序 wc。实际上，它针对源代码文件 p3.c 运行 wc，从而告诉我们该文件有多少行、多少单词，以及多少字节。

给定`可执行程序的名称`（如 wc）及`需要的参数`（如 p3.c）后，exec()会从可执行程序中加载代码和静态数据，**并用它`覆写`自己的代码段（以及静态数据），堆、栈及其他内存空间也会被重新初始化**。然后操作系统就执行该程序，将参数通过 argv 传递给该进程。因此，它并没有创建新进程，而是直接将当前运行的程序（以前的 p3）`替换`为不同的运行程序（wc）。子进程执行 exec()之后，几乎就像 p3.c 从未运行过一样。对 exec()的成功调用`永远不会返回`。如果 exec 函数执行失败, 它会返回失败的信息, 而且进程`继续执行后面的代码`。

> 注意：此时子进程的 pid 号并没有变，且还是该父进程的子进程，所以并不会影响 wait()操作，等待该进程的操作（统计字节）完成后，wait()才会返回，父进程同时退出阻塞状态

## 为什么这样设计 API

事实证明，这种分离 fork()及 exec()的做法在构建 `UNIX shell` 的时候非常有用，因为这给了 shell 在 fork 之后 exec 之前运行代码的机会，这些代码可以在运行新程序前改变环境，从而让一系列有趣的功能很容易实现。

shell 也是一个用户程序，它首先显示一个提示符（prompt），然后等待用户输入。你可以向它输入一个命令（一个可执行程序的名称及需要的参数），大多数情况下，**shell 可以在文件系统中找到这个可执行程序，调用 `fork()`创建新进程，并调用 `exec()`的某个变体来执行这个可执行程序，调用 `wait()`等待该命令完成**。子进程执行结束后，shell 从 wait()返回并再次输出一个提示符，等待用户输入下一条命令。

fork()和 exec()的分离，让 shell 可以方便地实现很多有用的功能。比如：

```shell
prompt> wc p3.c > newfile.txt
```

在上面的例子中，wc 的输出结果被重定向（redirect）到文件 newfile.txt 中（通过 newfile.txt 之前的大于号来指明重定向）。shell 实现结果重定向的方式也很简单，当完成子进程的创建后，shell 在调用 exec()之前先关闭了标准输出（standard output），打开了文件 newfile.txt。这样，即将运行的程序 wc 的输出结果就被发送到该文件，而不是打印在屏幕上。

### 扩展阅读：重定向

重定向的工作原理，是基于对操作系统管理文件描述符方式的假设，首先看实例：

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <fcntl.h>
#include <sys/wait.h>

int main(int argc, char *argv[])
{
    int rc = fork();
    if (rc < 0)
    { // fork failed; exit
        fprintf(stderr, "fork failed\n");
        exit(1);
    }
    else if (rc == 0)
    { // child: redirect standard output to a file
        close(STDOUT_FILENO);
        open("./p4.output", O_CREAT | O_WRONLY | O_TRUNC, S_IRWXU);

        // now exec "wc"...
        char *myargs[3];
        myargs[0] = strdup("wc");   // program: "wc" (word count)
        myargs[1] = strdup("p4.c"); // argument: file to count
        myargs[2] = NULL;           // marks end of array
        execvp(myargs[0], myargs);  // runs word count
    }
    else
    { // parent goes down this path (main)
        int wc = wait(NULL);
    }
    return 0;
}
```

```shell
prompt> ./p4
prompt> cat p4.output
 32 109 846 p4.c
prompt>
```

要看懂上面的例子，首先要补充点`Unix文件描述符`的知识

- 每个 Unix 进程（除了可能的守护进程）应均有三个标准的 POSIX 文件描述符，对应于三个标准流：

  | 整数值 |      名称       | <unistd.h>符号常量 | <stdio.h>文件流 |
  | :----: | :-------------: | :----------------: | :-------------: |
  |   0    | Standard input  |    STDIN_FILENO    |      stdin      |
  |   1    | Standard output |   STDOUT_FILENO    |     stdout      |
  |   2    | Standard error  |   STDERR_FILENO    |     stderr      |

1. UNIX 系统从 0 开始寻找可以使用的文件描述符，进程启动后默认打开了标准输出`STDOUT_FILENO`输出到屏幕，此时所有的对`标准输出文件描述符`的输出，如 `printf()`，都会打印的屏幕上：

   ```shell
   root@hjk:~/repo/os_test# ./a.out
   33 113 864 p4.c
   ```

2. 如果使用*close(STDOUT_FILENO)*关闭了这个描述符，再去调用`printf()`，系统会提示找不到文件描述符

   ```shell
   root@hjk:~/repo/os_test# ./a.out
   wc: write error: Bad file descriptor
   ```

3. 此时再打开`新的文件描述符`_open("./p4.output", O_CREAT | O_WRONLY | O_TRUNC, S_IRWXU)_，会将所有的对`标准输出文件描述符`的输出定向到该文件描述符上，因为 Unix 系统会从 0 开始寻找可用的文件描述符，当找不到`STDOUT_FILENO`自然会去找新打开的文件描述符

### 扩展阅读：管道

UNIX 管道也是用类似的方式实现的，但用的是 `pipe()`系统调用。在这种情况下，一个进程的输出被链接到了一个内核管道（pipe）上（队列），另一个进程的输入也被连接到了同一个管道上。因此，`前一个进程的输出无缝地作为后一个进程的输入`，许多命令可以用这种方式串联在一起，共同完成某项任务。比如通过将 grep、wc 命令用管道连接可以完成从一个文件中查找某个词，并统计其出现次数的功能：_grep -o foo file | wc -l_。

## 作业

1. 编写一个调用 fork()的程序。在调用 fork()之前，让主进程访问一个变量（例如 x）
    并将其值设置为某个值（例如 100）。子进程中的变量有什么值？当子进程和父进程都改变
    x 的值时，变量会发生什么？

>答：父进程在fork之前修改的值会同步到子进程中，当fork完成后，两个进程相互独立，修改fork前定义的变量时也是独立的。

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char *argv[])
{
    int x = 1;
    printf("hello world (pid:%d)\n", (int)getpid());
    x = 3;
    int rc = fork();
    if (rc < 0)
    { // fork failed; exit
        fprintf(stderr, "fork failed\n");
        exit(1);
    }
    else if (rc == 0)
    { // child (new process)
        x=4;
        printf("hello, I am child (pid:%d),x:%d\n", (int)getpid(),x);
    }
    else
    { // parent goes down this path (main)
        wait(NULL);
        printf("hello, I am parent of %d (pid:%d),x:%d\n",
            rc, (int)getpid(),x);
    }
    return 0;
}
```

```shell
root@hjk:~/repo/os_test# ./a.out 
hello world (pid:17699)
hello, I am child (pid:17700),x:4
hello, I am parent of 17700 (pid:17699),x:3
```

2. 