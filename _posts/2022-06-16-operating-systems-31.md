---
title: "《Operating Systems: Three Easy Pieces》学习笔记(三十) 插叙：文件和目录"
author: Jinkai
date: 2022-06-16 11:03:00 +0800
published: true
categories: [学习笔记]
tags: [Operating Systems, 操作系统导论]
---

操作系统应该如何管理持久存储设备？

## 文件和目录

存储虚拟化形成了两个关键的抽象。

### 文件（file）

文件就是一个`线性字节数组`，每个字节都可以读取或写入。每个文件都有一个与其关联的`低级名称`（low-level name），通常是某种数字。用户通常不知道这个名字（我们稍后会看到）。由于历史原因，文件的低级名称通常称为 `inode` 号（inode number）。

### 目录（directory）

一个目录，像一个文件一样，也有一个`低级名字`（即 inode 号），但是它的内容非常具体：它包含一个（`用户可读名字，低级名字`）对的列表。例如，假设存在一个低级别名称为“10”的文件，它的用户可读的名称为“foo”。“foo”所在的目录因此会有`条目（“foo”，“10”）`，将用户可读名称映射到低级名称。目录中的每个条目都`指向文件或其他目录`。通过将目录放入其他目录中，用户可以构建任意的`目录树`（directory tree，或目录层次结构，directory hierarchy），在该目录树下存储所有文件和目录。

目录层次结构从`根目录（root directory）`开始（在基于 UNIX 的系统中，根目录就记为“/”），并使用某种分隔符（separator）来命名后续子目录（sub-directories），直到命名所需的文件或目录。例如，如果用户在根目录中创建了一个目录 foo，然后在目录 foo 中创建了一个文件 bar.txt，我们就可以通过它的绝对路径名（absolute pathname）来引用该文件，在这个例子中，它将是/foo/bar.txt。示例中的有效目录是/，/foo，/bar，/bar/bar，/bar/foo，有效的文件是/foo/bar.txt 和/bar/foo/bar.txt。目录和文件可以具有相同的名称，只要它们位于文件系统树的不同位置（例如，图中有两个名为 bar.txt 的文件：/foo/bar.txt 和/bar/foo/bar.txt）

![F39.1](/assets/img/2022-06-16-operating-systems-31/F39.1.jpg)

## 文件系统接口

可以先阅读[《Operating Systems: Three Easy Pieces》学习笔记(三) 插叙：进程 API](/posts/operating-systems-3/)

### 创建文件

通过调用 `open()` 系统调用并传入 `O_CREAT` 标志，程序可以创建一个新文件

```c
int fd = open("foo", O_CREAT | O_WRONLY | O_TRUNC);
```

- O_CREAT:创建
- O_WRONLY:只写，因为创建只需要写权限
- O_TRUNC:如果已存在则先删除

open()的一个重要方面是它的返回值：`文件描述符`（file descriptor，或叫`句柄`）。文件描述符只是一个`整数`，是每个`进程私有`的，在 UNIX 系统中用于`访问文件`。

### 读写文件

使用 `read` 和 `write` 系统调用

示例：用 `echo` 和`重定向`向 foo 文件写入字符串 "hello"

```shell
prompt> echo hello > foo
prompt> cat foo
hello
prompt>
```

> 提示：使用 `strace`（和类似工具）
>
> strace 工具提供了一种非常棒的方式，来查看程序在做什么。通过运行它，你可以`跟踪`程序生成的`系统调用`，查看参数和返回代码，通常可以很好地了解正在发生的事情。
>
> 该工具还接受一些非常有用的`参数`。例如，-f 跟踪所有 fork 的子进程，-t 报告每次调用的时间，-e trace=open,close,read,write 只跟踪对这些系统调用的调用，并忽略所有其他调用。还有许多更强大的标志，请阅读手册页，弄清楚如何利用这个奇妙的工具。

示例：使用 strace 追踪 cat

```console
prompt> strace cat foo
...
open("foo", O_RDONLY|O_LARGEFILE) = 3
read(3, "hello\n", 4096) = 6
write(1, "hello\n", 6) = 6
hello
read(3, "", 4096) = 0
close(3) = 0
...
prompt>
```

1. open 只读方式打开 foo 文件，使用 64 位偏移量（O_LARGEFILE，这个参数一般不由用户使用），返回文件描述符 3（标准输入，标准输出，以及标准错误占用了 0、1、2，一般进程的用户句柄都是从 3 开始）
2. read 读取文件内容，第一参数为文件描述符，第二参数为用于存放 read()结果的缓冲区地址，这里 strace 直接用读取后的缓冲区内容字符串填充了，第三参数为缓冲区大小
3. write 将缓冲区内容写入标准输出。
4. 再次尝试读取是否有剩余内容，没有就用 close 关闭

### 随机位置写入和读取

```c
off_t lseek(int fildes, off_t offset, int whence);
```

参数：

- `文件描述符`
- `偏移量`：它将文件偏移量定位到文件中的特定位置。
- `whence`：明确地指定了搜索的执行方式，也就是偏移量参数 offset 的使用方式

  - If whence is `SEEK_SET`, the offset is set to offset bytes.（从起始位置偏移）
  - If whence is `SEEK_CUR`, the offset is set to its current location plus offset bytes.（从当前位置偏移）
  - If whence is `SEEK_END`, the offset is set to the size of the file plus offset bytes.（从结束位置开始的偏移，比如`-3`表示倒数第三字节）

    From the start:

    ```console
    01234         <---position
    ABCDEFGHIJK   <---file content
    ```

    From the end:

    ```console
           43210  <---position
    ABCDEFGHIJK   <---file content
    ```

### 用 fsync() 立即写入

操作系统对于 `write` 系统掉用会先写入`缓存`，等待一段时间再写入磁盘，如果需要立即写入，需要调用 `fsync` 系统调用强制写入所有`脏数据`，该调用会阻塞直到操作完成

可以理解为 write 是个异步过程，需要 fsync 转换为同步过程

```c
int fd = open("foo", O_CREAT | O_WRONLY | O_TRUNC);
assert(fd > -1);
int rc = write(fd, buffer, size);
assert(rc == size);
rc = fsync(fd);
assert(rc == 0);
```

以上代码存在问题，调用 fsync() 不一定确保包含文件的`目录`中的条目也`已到达磁盘`。为此，还需要在目录的文件描述符上使用`显式的 fsync()`。

### 文件重命名

`rename(char * old, char * new)` 系统调用

```shell
prompt> mv foo bar
```

正在使用`文件编辑器`（例如 emacs），并将一行`插入`到文件的中间。例如，该文件的名称是 `foo.txt`。编辑器更新文件（会产生个临时文件 `foo.txt.tmp`）并确保新文件包含原有内容和插入行的方式如下：

```console
int fd = open("foo.txt.tmp", O_WRONLY|O_CREAT|O_TRUNC);
write(fd, buffer, size); // write out new version of file
fsync(fd);
close(fd);
rename("foo.txt.tmp", "foo.txt");
```

### 获取文件信息

我们还希望文件系统能够保存关于它正在存储的每个文件的`大量信息`。我们通常将这些数据称为`文件元数据（metadata）`。要查看特定文件的元数据，我们 可以使用 `stat()` 或 `fstat()` 系统调用。

```c
struct stat {
    dev_t st_dev; /* ID of device containing file */
    ino_t st_ino; /* inode number */
    mode_t st_mode; /* protection */
    nlink_t st_nlink; /* number of hard links */
    uid_t st_uid; /* user ID of owner */
    gid_t st_gid; /* group ID of owner */
    dev_t st_rdev; /* device ID (if special file) */
    off_t st_size; /* total size, in bytes */
    blksize_t st_blksize; /* blocksize for filesystem I/O */
    blkcnt_t st_blocks; /* number of blocks allocated */
    time_t st_atime; /* time of last access */
    time_t st_mtime; /* time of last modification */
    time_t st_ctime; /* time of last status change */
};
```

包括其大小（以字节为单位），其`低级名称`（即 `inode 号`），一些`所有权`信息以及有关`何时`文件被`访问`或`修改`的一些信息，等等。

要查看此信息，可以使用命令行工具 `stat`：

```c
prompt> echo hello > file
prompt> stat file
    File: 'file'
    Size: 6 Blocks: 8 IO Block: 4096 regular file
Device: 811h/2065d Inode: 67158084 Links: 1
Access: (0640/-rw-r-----) Uid: (30686/ remzi) Gid: (30686/ remzi)
Access: 2011-05-03 15:50:20.157594748 -0500
Modify: 2011-05-03 15:50:20.157594748 -0500
Change: 2011-05-03 15:50:20.157594748 -0500
```

每个文件系统通常将这种类型的信息保存在一个名为 `inode` 的结构中

### 删除文件

`unlink()` 只需要待删除文件的`名称`，并在成功时返回零。

```shell
prompt> strace rm foo
...
unlink("foo") = 0
...
```

### 创建目录

`bash` 里的 `mkdir` 命令可以使用同名的 `mkdir 系统调用`创建目录

```shell
prompt> strace mkdir foo
...
mkdir("foo", 0777) = 0
...
prompt>
```

`空目录`有两个条目：一个引用自身的条目(.)，一个引用其父目录的条目(..)

```shell
prompt> ls -a
./ ../
prompt> ls -al
total 8
drwxr-x--- 2 remzi remzi 6 Apr 30 16:17 ./
drwxr-x--- 26 remzi remzi 4096 Apr 30 16:17 ../
```

### 读取目录

```c
int main(int argc, char *argv[]) {
    DIR *dp = opendir(".");
    assert(dp != NULL);
    struct dirent *d;
    while ((d = readdir(dp)) != NULL) {
        printf("%d %s\n", (int) d->d_ino, d->d_name);
    }
    closedir(dp);
    return 0;
}
```

该程序使用了 `opendir()`、`readdir()`和 `closedir()`这 3 个调用来完成工作

```c
struct dirent {
    char d_name[256]; /* filename */
    ino_t d_ino; /* inode number */
    off_t d_off; /* offset to the next dirent */
    unsigned short d_reclen; /* length of this record */
    unsigned char d_type; /* type of file */
};
```

`dirent` 结构体包含了目录相关的信息，比 `stat` 的信息要少，不过都关联了 `inode` 号。目录同时有 dirent 和 stat 信息，可以通过 `ls` 命令的 `-l` 参数区分（好像新版本的 linux 都是读的 stat 信息）

### 删除目录

可以通过调用 `rmdir()` 系统调用（和 bash 里的 rmdir 同名）来删除目录

rmdir() 很`危险`，所以要求该目录在被删除之前是空的（只有“`.`”和“`..`”条目），否则会调用失败

### 硬链接

之前提到[删除文件](#删除文件)用的是 `unlink`，其实文件是通过 `link` 的方式将`文件名`连接到`实际 inode` 上的，同一 inode 可以被重复引用。

通过 `ln` 命令创建硬链接:

```shell
prompt> echo hello > file
prompt> cat file
hello
prompt> ln file file2
prompt> cat file2
hello
```

link 只是在要创建链接的目录中创建了另一个名称，并将其指向原有文件的`相同 inode` 号（即低级别名称）。该文件不以任何方式复制。这两个人类可读的名称（file 和 file2），都指向`同一个文件`。

相同的 inode 号：

```shell
prompt> ls -i file file2
67158084 file
67158084 file2
prompt>
```

创建一个文件时，实际上做了两件事。首先，要构建一个`结构（inode）`，它将跟踪几乎所有关于`文件的信息`，包括其大小、文件块在磁盘上的位置等等。其次，将`人类可读的名称`链接到该文件，并将该链接`放入目录`中。增加 inode 的`引用计数`

当文件系统`取消链接`文件时，它检查 inode 号中的`引用计数`（reference count）。该引用计数（有时称为链接计数，link count）允许文件系统跟踪有多少不同的文件名已链接到这个 inode。调用 `unlink()` 时，会删除人类可读的名称（正在删除的文件）与给定 inode 号之间的“链接”，并`减少引用计数`。只有当引用计数达到`零`时，文件系统才会`释放` inode 和相关数据块，从而真正“删除”该文件。

```shell
prompt> echo hello > file
prompt> stat file
... Inode: 67158084 Links: 1 ...
prompt> ln file file2
prompt> stat file
... Inode: 67158084 Links: 2 ...
prompt> stat file2
... Inode: 67158084 Links: 2 ...
prompt> ln file2 file3
prompt> stat file
... Inode: 67158084 Links: 3 ...
prompt> rm file
prompt> stat file2
... Inode: 67158084 Links: 2 ...
prompt> rm file2
prompt> stat file3
... Inode: 67158084 Links: 1 ...
prompt> rm file3
```

### 符号链接(软链接)

硬链接两个问题：

- 不能跨文件系统(即使文件系统类型相同但分区不同也视为不同文件系统)

  - 不同的文件系统的文件管理方式不同，甚至有些文件系统不是索引文件系统，并不一定两个文件系统的 inode 有`相同的含义`。
  - 不同文件系统下 inode 的编号独立，可能会有重复的

- 不能连接目录

  - 因为如果使用 hard link 链接到目录时， 链接的数据需要连同被链接目录下面的所有数据都创建链接，举例来说，如果你要将 /etc 使用实体链接创建一个 /etc_hd 的目录时，那么在 /etc_hd 下面的所有文件名同时都与 /etc 下面的文件名要创建 hard link 的，而不是仅链接到 /etc_hd 与 /etc 而已。
  - 未来如果需要在 /etc_hd 下面创建新文件时，连带的， /etc 下面的数据又得要创建一次 hard link ，因此造成环境相当大的复杂度。
  - 可能造成回环，比如在目录中创建该目录本身的链接

`符号链接`本身实际上是一个不同类型的`文件`。符号链接是文件系统知道的除常规文件和目录外`第三种类型`。

```shell
prompt> echo hello > file
prompt> ln -s file file2
prompt> cat file2
hello
prompt> stat file
 ... regular file ...
prompt> stat file2
 ... symbolic link ...
```

使用`ls -al`打印详细信息，行开头的 `d` 表示目录，`-` 表示普通文件，`l` 表示符号链接文件

```shell
prompt> ls -al
drwxr-x--- 2 remzi remzi 29 May 3 19:10 ./
drwxr-x--- 27 remzi remzi 4096 May 3 15:14 ../
-rw-r----- 1 remzi remzi 6 May 3 19:10 file
lrwxrwxrwx 1 remzi remzi 4 May 3 19:10 file2 -> file
```

日期前的数字表示文件长度，符号链接文件的`大小`就是链接到的目标文件的`文件名长度`，可能会包含路径

```shell
prompt> echo hello > alongerfilename
prompt> ln -s alongerfilename file3
prompt> ls -al alongerfilename file3
-rw-r----- 1 remzi remzi 6 May 3 19:17 alongerfilename
lrwxrwxrwx 1 remzi remzi 15 May 3 19:17 file3 -> alongerfilename
```

alongerfilename 文件名长度为 15，那符号链接文件的`大小`就是 15 个字节

目标文件不存在或被删除时就会造成`悬空引用`

```shell
prompt> echo hello > file
prompt> ln -s file file2
prompt> cat file2
hello
prompt> rm file
prompt> cat file2
cat: file2: No such file or directory
```

## 创建并挂载文件系统

一般使用 `mkfs` 在`磁盘分区`上创建`特定类型`的空文件系统

再用 `mount` 挂载，相当于把该文件系统挂载到系统目录树的某个位置

```shell
prompt> mount -t ext3 /dev/sda1 /home/users
```

`mount` 将所有文件系统统一到一棵树中，而不是拥有多个独立的文件系统，这让命名统一而且方便

```shell
/dev/sda1 on / type ext3 (rw) 
proc on /proc type proc (rw) 
sysfs on /sys type sysfs (rw) 
/dev/sda5 on /tmp type ext3 (rw) 
/dev/sda7 on /var/vice/cache type ext3 (rw) 
tmpfs on /dev/shm type tmpfs (rw) 
AFS on /afs type afs (rw) 
```

ext3（标准的基于磁盘的文件系统）、proc 文件系统（用于访问当前进程信息的文件系统）、tmpfs（仅用于临时文件的文件系统） 和 AFS（分布式文件系统）

## 小结

更多详情，参阅《Advanced Programming in the UNIX Environment》

## 参考

- [Operating Systems: Three Easy Pieces 中文版](https://pages.cs.wisc.edu/~remzi/OSTEP/Chinese/39.pdf)
- [behaviour of fseek and SEEK_END](https://stackoverflow.com/questions/27549718/behaviour-of-fseek-and-seek-end)
- [Does fsync of a parent directory guarantee synchronization of meta data of all recursive sub directories?](https://stackoverflow.com/questions/17616485/does-fsync-of-a-parent-directory-guarantee-synchronization-of-meta-data-of-all-r)
- [Linux IO 同步函数:sync、fsync、fdatasync](http://byteliu.com/2019/03/09/Linux-IO%E5%90%8C%E6%AD%A5%E5%87%BD%E6%95%B0-sync%E3%80%81fsync%E3%80%81fdatasync/)
