---
title: "Linux内核学习笔记之虚拟文件系统"
author: Jinkai
date: 2023-03-02 09:00:00 +0800
published: true
categories: [学习笔记]
tags: [kernel, Linux]
---

`虚拟文件系统(VFS)`作为内核子系统，为用户空间程序提供了文件和文件系统相关的接口。系统中所有文件系统不但依赖 VFS 共存，而且也依靠 VFS 系统协同工作。

通过虚拟文件系统，程序可以利用标准的 **Uinx 系统调用**（open()、read() 和 write() 等）对不同的文件系统，甚至不同介质上的文件系统进行读写操作

![vfs](/assets/img/2023-03-02-linux-kernel-vfs/vfs.jpg)

上图中 VFS 执行的动作：使用 `cp(1)`命令从 `ext3` 文件系统格式的硬盘拷贝数据到 `ext2` 文件系统格式的可移动磁盘上。两种不同的文件系统，两种不同的介质，连接到同一个 VFS 上

## 通用文件系统接口

VFS 把各种不同的文件系统**抽象**后采用统一的方式进行操作。

在第 14 章中，我们将讨论块 I/O 层，它支持各种各样的存储设备——从 CD 到蓝光光盘，从硬件设备再到压缩闪存。

**VFS 与块 I/O 相结合**，提供抽象、接口以及交融，使得用户空间的程序调用统一的系统调用访问各种文件，不管**文件系统**是什么，也不管文件系统位于何种**介质**，采用的命名策略是统一的。

## 文件系统抽象层

VFS 抽象层之所以能衔接各种各样的文件系统，是因为它定义了所有文件系统都支持的基本的、概念上的接口和数据结构。同时实际文件系统也将自身的诸如“如何打开文件”，“目录是什么”等概念在形式上与 VFS 的定义保持一致

其实在内核中，除了文件系统本身外，其他部分并不需要了解文件系统的**内部细节**。比如一个简单的**用户空间程序**执行如下的操作:

```c
ret = write(fd, buf, len);
```

![f13-2](/assets/img/2023-03-02-linux-kernel-vfs/f13-2.jpg)

用户空间程序无需关心文件系统实现细节，只要数据被写入就行。

## Unix 风格文件系统

Unix 使用了四种和文件系统相关的传统抽象概念:**文件**、**目录项**、**索引节点**和**安装点**(mount point)。

- **文件**：文件是一个连续的、有序的字节串，有文件名用于识别，典型的文件操作有读、写、创建和删除等。
- **目录**：文件通过目录组织起来，目录可以嵌套。在 Unix 中，目录属于普通文件，它列出包含在其中的所有文件。由于 VFS 把目录当作文件对待，所以可以对目录执行和文件相同的操作。路径中的每一项称为目录项。
- **索引节点**：文件的相关信息(元数据)和文件本身这两个概念区分开，例如访问控制权限、大小、拥有者、创建时间等信息。被存储在一个单独的数据结构中，访结构被称为索引节点(inode)
- **安装点**：在 Unix 中，文件系统被安装在一个特定的安装点上，所有的已安装文件系统都作为根文件系统树的枝叶出现在系统中。

对于不是按照 Unix 风格设计的文件系统，如 NTFS 等，需要封装一层以支持 VFS。

## VFS 对象及其数据结构

VFS 对象：

- 超级块对象，它代表一个具体的已安装文件系统。
- 索引节点 inode 对象，它代表一个具体文件。
- 目录项对象，它代表一个目录项，是路径的一个组成部分。
- 文件对象，它代表由进程打开的文件。

每个 VFS 对象都包含一个操作对象，描述了可以使用的方法，其实就是 OOP 中的**成员函数**，使用[虚拟表](/posts/c-oop/#虚拟表-vtbl-和虚拟指针-vptr)的方式实现：

- super_operations 对象，其中包括内核针对特定文件系统所能调用的方法，比如`write_inode()`和`sync_fs()`等方法。
- inode_operations 对象，其中包括内核针对特定文件所能调用的方法，比如`create()`和`link()`等方法。
- dentry_operations 对象，其中包括内核针对特定目录所能调用的方法，比如`d_compare()`和`d_delete()`等方法。
- file_operations 对象，其中包括进程针对已打开文件所能调用的方法，比如`read()`和`write()`等方法。

以上设计使用了基于 C 语言的 OOP 实现，可以按照 OOP 的视角来看待。

## 超级块对象 super_block

该对象用于存储特定文件系统的信息，通常对应于存放在磁盘特定扇区中的文件系统**超级块**或文件系统控制块(所以称为超级块对象)。对于并非基于磁盘的文件系统(如基于内存的文件系统，比如 sysfs)，它们会在使用现场创建超级块并将其保存到内存中。

创建、管理和撤销超级块对象的代码位于文件`<fs/super.c>`中。超级块对象通过`alloc_super()`函数创建并初始化。在文件系统安装时，文件系统会调用该函数以便**从磁盘读取文件系统超级块**，并且将其信息填充到内存中的超级块对象中。

```c
// <linux/fs.h>
struct super_block
{
    struct list_head s_list; /* Keep this first */
    dev_t s_dev;             /* search index; _not_ kdev_t */
    unsigned char s_blocksize_bits;
    unsigned long s_blocksize;
    loff_t s_maxbytes; /* Max file size */
    struct file_system_type *s_type;
    const struct super_operations *s_op;
    const struct dquot_operations *dq_op;
    const struct quotactl_ops *s_qcop;
    const struct export_operations *s_export_op;
    unsigned long s_flags;
    unsigned long s_magic;
    struct dentry *s_root;
    struct rw_semaphore s_umount;
    int s_count;
    atomic_t s_active;
#ifdef CONFIG_SECURITY
    void *s_security;
#endif
    const struct xattr_handler **s_xattr;

    struct list_head s_inodes;   /* all inodes */
    struct hlist_bl_head s_anon; /* anonymous dentries for (nfs) exporting */
    struct list_head s_mounts;   /* list of mounts; _not_ for fs use */
    /* s_dentry_lru, s_nr_dentry_unused protected by dcache.c lru locks */
    struct list_head s_dentry_lru; /* unused dentry lru */
    int s_nr_dentry_unused;        /* # of dentry on lru */

    /* s_inode_lru_lock protects s_inode_lru and s_nr_inodes_unused */
    spinlock_t s_inode_lru_lock ____cacheline_aligned_in_smp;
    struct list_head s_inode_lru; /* unused inode lru */
    int s_nr_inodes_unused;       /* # of inodes on lru */

    struct block_device *s_bdev;
    struct backing_dev_info *s_bdi;
    struct mtd_info *s_mtd;
    struct hlist_node s_instances;
    struct quota_info s_dquot; /* Diskquota specific options */

    struct sb_writers s_writers;

    char s_id[32]; /* Informational name */
    u8 s_uuid[16]; /* UUID */

    void *s_fs_info; /* Filesystem private info */
    unsigned int s_max_links;
    fmode_t s_mode;

    /* Granularity of c/m/atime in ns.
       Cannot be worse than a second */
    u32 s_time_gran;

    /*
     * The next field is for VFS *only*. No filesystems have any business
     * even looking at it. You had been warned.
     */
    struct mutex s_vfs_rename_mutex; /* Kludge */

    /*
     * Filesystem subtype.  If non-empty the filesystem type field
     * in /proc/mounts will be "type.subtype"
     */
    char *s_subtype;

    /*
     * Saved mount options for lazy filesystems using
     * generic_show_options()
     */
    char __rcu *s_options;
    const struct dentry_operations *s_d_op; /* default d_op for dentries */

    /*
     * Saved pool identifier for cleancache (-1 means none)
     */
    int cleancache_poolid;

    struct shrinker s_shrink; /* per-sb shrinker handle */

    /* Number of inodes with nlink == 0 but still referenced */
    atomic_long_t s_remove_count;

    /* Being remounted read-only */
    int s_readonly_remount;
};
```

### 超级块操作

超级块对象中最重要的一个域是`s_op`，它指向超级块的操作函数表。

```c
// <linux/fs.h>
struct super_operations
{
    // 创建和初始化一个新的inode
    struct inode *(*alloc_inode)(struct super_block *sb);
    void (*destroy_inode)(struct inode *);

    void (*dirty_inode)(struct inode *, int flags);
    // 将inode写入磁盘，wbc表示同步写/异步写
    int (*write_inode)(struct inode *, struct writeback_control *wbc);
    int (*drop_inode)(struct inode *);
    void (*evict_inode)(struct inode *);
    // 卸载文件系统
    void (*put_super)(struct super_block *);
    // 同步元数据
    int (*sync_fs)(struct super_block *sb, int wait);
    int (*freeze_fs)(struct super_block *);
    int (*unfreeze_fs)(struct super_block *);
    int (*statfs)(struct dentry *, struct kstatfs *);
    int (*remount_fs)(struct super_block *, int *, char *);
    void (*umount_begin)(struct super_block *);

    int (*show_options)(struct seq_file *, struct dentry *);
    int (*show_devname)(struct seq_file *, struct dentry *);
    int (*show_path)(struct seq_file *, struct dentry *);
    int (*show_stats)(struct seq_file *, struct dentry *);
#ifdef CONFIG_QUOTA
    ssize_t (*quota_read)(struct super_block *, int, char *, size_t, loff_t);
    ssize_t (*quota_write)(struct super_block *, int, const char *, size_t, loff_t);
#endif
    int (*bdev_try_to_free_page)(struct super_block *, struct page *, gfp_t);
    int (*nr_cached_objects)(struct super_block *);
    void (*free_cached_objects)(struct super_block *, int);
};
```

当文件系统需要对其超级块执行操作时，首先要在超级块对象中寻找需要的操作方法。

如文件系统需要写入自己的超级块，调用 write_super：

```c
sb->s_op->write_super(sb);
```

sb 为 super_block 对象，由于 C 语言实现 OOP 的局限性，操作函数必须带入自身对象的指针，而 C++ 语言可以自动隐含 this 指针。

这其中的一些函数是可选的（无需重载 VFS 的默认实现）。在超级块操作表中，文件系统可以将不需要的函数指针设置成 NULL。如果 VFS 发现操作函数指针是 NULL，那它要么就会调用**通用函数**执行相应操作，要么什么也不做，如何选择取决于具体操作。

## 索引节点对象 inode

索引节点 inode 对象包含了内核在操作文件或目录时需要的全部信息（元数据）。

不管元数据信息怎么存放(单独存放还是和文件存放在一起)，都必须提取(或虚构)后放入索引节点对象。

```c
// <linux/fs.h>
struct inode
{
    umode_t i_mode;
    unsigned short i_opflags;
    kuid_t i_uid;
    kgid_t i_gid;
    unsigned int i_flags;

#ifdef CONFIG_FS_POSIX_ACL
    struct posix_acl *i_acl;
    struct posix_acl *i_default_acl;
#endif

    const struct inode_operations *i_op;
    struct super_block *i_sb;
    struct address_space *i_mapping;

#ifdef CONFIG_SECURITY
    void *i_security;
#endif

    /* Stat data, not accessed from path walking */
    unsigned long i_ino;
    /*
     * Filesystems may only read i_nlink directly.  They shall use the
     * following functions for modification:
     *
     *    (set|clear|inc|drop)_nlink
     *    inode_(inc|dec)_link_count
     */
    union
    {
        const unsigned int i_nlink;
        unsigned int __i_nlink;
    };
    dev_t i_rdev;
    loff_t i_size;
    struct timespec i_atime;
    struct timespec i_mtime;
    struct timespec i_ctime;
    spinlock_t i_lock; /* i_blocks, i_bytes, maybe i_size */
    unsigned short i_bytes;
    unsigned int i_blkbits;
    blkcnt_t i_blocks;

#ifdef __NEED_I_SIZE_ORDERED
    seqcount_t i_size_seqcount;
#endif

    /* Misc */
    unsigned long i_state;
    struct mutex i_mutex;

    unsigned long dirtied_when; /* jiffies of first dirtying */

    struct hlist_node i_hash;
    struct list_head i_wb_list; /* backing dev IO list */
    struct list_head i_lru;     /* inode LRU list */
    struct list_head i_sb_list;
    union
    {
        struct hlist_head i_dentry;
        struct rcu_head i_rcu;
    };
    u64 i_version;
    atomic_t i_count;
    atomic_t i_dio_count;
    atomic_t i_writecount;
    const struct file_operations *i_fop; /* former ->i_op->default_file_ops */
    struct file_lock *i_flock;
    struct address_space i_data;
#ifdef CONFIG_QUOTA
    struct dquot *i_dquot[MAXQUOTAS];
#endif
    struct list_head i_devices;
    union
    {
        struct pipe_inode_info *i_pipe;
        struct block_device *i_bdev;
        struct cdev *i_cdev;
    };

    __u32 i_generation;

#ifdef CONFIG_FSNOTIFY
    __u32 i_fsnotify_mask; /* all events this inode cares about */
    struct hlist_head i_fsnotify_marks;
#endif

#ifdef CONFIG_IMA
    atomic_t i_readcount; /* struct files open RO */
#endif
    void *i_private; /* fs or device private pointer */
};
```

一个索引节点代表文件系统中的一个文件，它也可以是设备或管道这样的特殊文件。因此索引节点结构体中有一些和特殊文件相关的项，比如 `i_pipe` 项就指向一个代表有名管道的数据结构，`i_bdev` 指向块设备结构体，`i_cdev` 指向字符设备结构体。这三个指针被存放在一个 union 中，因为一个给定的索引节点每次只能表示三者之一(或三者均不)。

某些文件系统可能并不能完整地包含索引节点结构体要求的所有信息。这时可以选择虚构或者只在内存对象中更新而不回写。如文件系统不支持 i_atime(最后一次访问时间)，则 inode 对象中的 i_atime 可以虚构为 0，且不会向硬盘 inode 中回写。

### 索引节点操作

```c
struct inode_operations
{
    struct dentry *(*lookup)(struct inode *, struct dentry *, unsigned int);
    void *(*follow_link)(struct dentry *, struct nameidata *);
    int (*permission)(struct inode *, int);
    struct posix_acl *(*get_acl)(struct inode *, int);

    int (*readlink)(struct dentry *, char __user *, int);
    void (*put_link)(struct dentry *, struct nameidata *, void *);

    // 创建文件，由create和open系统调用调用
    int (*create)(struct inode *, struct dentry *, umode_t, bool);
    int (*link)(struct dentry *, struct inode *, struct dentry *);
    int (*unlink)(struct inode *, struct dentry *);
    int (*symlink)(struct inode *, struct dentry *, const char *);
    int (*mkdir)(struct inode *, struct dentry *, umode_t);
    int (*rmdir)(struct inode *, struct dentry *);
    int (*mknod)(struct inode *, struct dentry *, umode_t, dev_t);
    int (*rename)(struct inode *, struct dentry *,
                  struct inode *, struct dentry *);
    int (*setattr)(struct dentry *, struct iattr *);
    int (*getattr)(struct vfsmount *mnt, struct dentry *, struct kstat *);
    int (*setxattr)(struct dentry *, const char *, const void *, size_t, int);
    ssize_t (*getxattr)(struct dentry *, const char *, void *, size_t);
    ssize_t (*listxattr)(struct dentry *, char *, size_t);
    int (*removexattr)(struct dentry *, const char *);
    int (*fiemap)(struct inode *, struct fiemap_extent_info *, u64 start,
                  u64 len);
    int (*update_time)(struct inode *, struct timespec *, int);
    int (*atomic_open)(struct inode *, struct dentry *,
                       struct file *, unsigned open_flag,
                       umode_t create_mode, int *opened);
} ____cacheline_aligned;
```

## 目录项对象 dentry

Linux 中的目录也是文件，没有单独的对象。但为了使路径的解析更加便捷，引入了目录项的概念，将字符串路径`"/root/file.txt"`拆分成目录项就是三部分`'/'`,`'root'`,`'file.txt'`，这三部分分别对应三个 dentry 对象（用对象方式表示路径，用链表连接）。

```console
dentry('/') -> dentry('root') -> dentry('file.txt')
```

使用目录项表示路径，免去了每次解析字符串的繁琐(通过 hash 表)，且目录的切换也更加简单。每个目录项都关联一个 inode，也就是解析路径定位文件时可以通过目录项快速定位。如果没有目录项，查找 `file.txt` 文件就要扫描 root 目录(目录保存了其下所有文件的文件名和 inode 的映射)中所有文件名，再找到对应的 inode 信息

```c
// include/linux/dcache.h
struct dentry
{
    /* RCU lookup touched fields */
    unsigned int d_flags;        /* protected by d_lock */
    seqcount_t d_seq;            /* per dentry seqlock */
    struct hlist_bl_node d_hash; /* lookup hash list */
    struct dentry *d_parent;     /* parent directory */
    struct qstr d_name;
    struct inode *d_inode;                   /* Where the name belongs to - NULL is
                                              * negative */
    unsigned char d_iname[DNAME_INLINE_LEN]; /* small names */

    /* Ref lookup also touches following */
    unsigned int d_count; /* protected by d_lock */
    spinlock_t d_lock;    /* per dentry lock */
    const struct dentry_operations *d_op;
    struct super_block *d_sb; /* The root of the dentry tree */
    unsigned long d_time;     /* used by d_revalidate */
    void *d_fsdata;           /* fs-specific data */

    struct list_head d_lru;     /* LRU list */
    struct list_head d_child;   /* child of parent list */
    struct list_head d_subdirs; /* our children */
    /*
     * d_alias and d_rcu can share memory
     */
    union
    {
        struct hlist_node d_alias; /* inode alias list */
        struct rcu_head d_rcu;
    } d_u;
};
```

目录项对象没有对应的**磁盘数据结构**，VFS 根据字符串形式的路径名**现场创建**它。而且由于目录项对象并非真正保存在磁盘上，所以目录项结构体没有是否被修改的标志(也就是是否为胜、是否需要写回磁盘的标志)。

### 目录项状态

目录项对象有三种有效状态:被使用、未被使用和负状态。

- **被使用**：关联着一个 inode（`d_inode`指向），且正在被 VFS 使用（`d_count`大于 0）
- **未被使用**：关联着一个 inode（`d_inode`指向），但未被 VFS 使用（`d_count`等于 0）。可能将来会被访问
- **负状态**(无效目录项)：未关联任何 inode（`d_inode`为 NULL）。一般用于 VFS 频繁访问一个不存在的文件(比如某个进程定时查询自己的配置文件)，在内存中保留负状态的目录项就会有用。

目录项是为了加速目录字符串解析的，所以只要有频繁访问目录或文件的操作就应该保留目录项对象。

### 目录项缓存

为了提高性能，引入了缓存(dcache)，通过链表管理，当目录项被频繁访问时可以大大提高性能：

- **被使用**目录项链表：链表由被使用目录项 dentry 节点构成，由 inode 结构中的 i_dentry 指向（每个 inode 可以由多个 dentry 描述，比如`'/root/file.txt'`是`'/var/spool/file.txt'`的一个链接，它们就指向同一文件 inode，但 dentry 不同）。
- **最近被使用 LRU**双向链表：链表由**未被使用**和**负状态** dentry 节点构成，是个先进先出队列，需要回收内存时从链表尾部回收

VFS 如果每次都解析路径字符串来定位目录项（缓存），会是很费时的操作，所以引入**散列表(dentry_hashtable)**，让路径和目录项直接映射。key 为路径字符串的 hash（TODO:是完整的绝对路径还是分割后的路径），value 为对应的目录项的一条链表（hash 表特性，不同的路径可能被 hash 成相同的 key，value 会是一条链表），然后在这条链表中找到对应路径的目录项缓存（TODO：怎么在链表中找到对应的目录项）。

> 举例说明，假设你需要在自己目录中编译一个源文件，`/home/dracula/src/the_sun_sucks.c`，每一次对文件进行访问(比如说，首先要打开它，然后要存储它，还要进行编译等)，VFS 都必须沿着嵌套的目录依次解析全部路径:`/`、`home`、`dracula`、`src`和最终的`the_sun_sucks.c`。为了避免每次访问该路径名都进行这种耗时的操作,VFS 会先在目录项缓存中搜索路径名(散列表 dentry_hashtable)，如果找到了，就无须花费那么大的力气了。相反，如果该目录项在目录项缓存中并不存在，VFS 就必须自己通过遍历文件系统为每个路径分量解析路径，解析完毕后，再将目录项对象加入 dcache 中，以便以后可以快速查找到它。

### 目录项操作

```c
// include/linux/dcache.h
struct dentry_operations
{
    int (*d_revalidate)(struct dentry *, unsigned int);
    int (*d_weak_revalidate)(struct dentry *, unsigned int);
    // 生成hash, qstr为路径字符串
    int (*d_hash)(const struct dentry *, const struct inode *,
                  struct qstr *);
    int (*d_compare)(const struct dentry *, const struct inode *,
                     const struct dentry *, const struct inode *,
                     unsigned int, const char *, const struct qstr *);
    int (*d_delete)(const struct dentry *);
    void (*d_release)(struct dentry *);
    void (*d_prune)(struct dentry *);
    void (*d_iput)(struct dentry *, struct inode *);
    char *(*d_dname)(struct dentry *, char *, int);
    struct vfsmount *(*d_automount)(struct path *);
    int (*d_manage)(struct dentry *, bool);
} ____cacheline_aligned;
```

## 文件对象 file

文件对象用于表示进程已打开的文件，每个进程都对应一个，也就是说同一个文件可能同时对应多个文件对象（多个进程同时使用）。

文件对象和目录项对象一样是仅存于内存中的**临时对象**，磁盘上没有对应的结构（不同于 inode 对象）。通过 `f_inode` 成员对应的 **inode 对象**，可以让文件系统找到文件在磁盘中的位置，包括记录是否为脏等信息

file 对象存在的意义就是它是每个进程一个的，这样可以为同一个文件用 `f_mode` 指定不同的权限。比如 A 进程只读，B 进程读写。还有就是每个进程单独记录偏移量。

```c
// include/linux/fs.h
struct file
{
    union
    {
        struct llist_node fu_llist;
        struct rcu_head fu_rcuhead;
    } f_u;
    struct path f_path;
#define f_dentry f_path.dentry
    struct inode *f_inode; /* cached value */
    const struct file_operations *f_op;

    /*
     * Protects f_ep_links, f_flags, f_pos vs i_size in lseek SEEK_CUR.
     * Must not be taken from IRQ context.
     */
    spinlock_t f_lock;
    atomic_long_t f_count;
    unsigned int f_flags;
    fmode_t f_mode;
    loff_t f_pos; // 文件当前位移量（文件指针）
    struct fown_struct f_owner;
    const struct cred *f_cred;
    struct file_ra_state f_ra;

    u64 f_version;
#ifdef CONFIG_SECURITY
    void *f_security;
#endif
    /* needed for tty driver, and maybe others */
    void *private_data;

#ifdef CONFIG_EPOLL
    /* Used by fs/eventpoll.c to link all the hooks to this file */
    struct list_head f_ep_links;
    struct list_head f_tfile_llink;
#endif /* #ifdef CONFIG_EPOLL */
    struct address_space *f_mapping;
#ifdef CONFIG_DEBUG_WRITECOUNT
    unsigned long f_mnt_write_state;
#endif
};
```

### 文件操作

如果文件系统是基于 Unix 风格设计的，那么 VFS 提供的默认实现就基本可以满足要求，文件系统无需重载这些实现（将对应函数指针置为 NULL）。

```c
// include/linux/fs.h
struct file_operations
{
    struct module *owner;
    loff_t (*llseek)(struct file *, loff_t, int);
    ssize_t (*read)(struct file *, char __user *, size_t, loff_t *);
    ssize_t (*write)(struct file *, const char __user *, size_t, loff_t *);
    ssize_t (*aio_read)(struct kiocb *, const struct iovec *, unsigned long, loff_t);
    ssize_t (*aio_write)(struct kiocb *, const struct iovec *, unsigned long, loff_t);
    int (*readdir)(struct file *, void *, filldir_t);
    unsigned int (*poll)(struct file *, struct poll_table_struct *);
    long (*unlocked_ioctl)(struct file *, unsigned int, unsigned long);
    long (*compat_ioctl)(struct file *, unsigned int, unsigned long);
    int (*mmap)(struct file *, struct vm_area_struct *);
    int (*open)(struct inode *, struct file *);
    int (*flush)(struct file *, fl_owner_t id);
    int (*release)(struct inode *, struct file *);
    int (*fsync)(struct file *, loff_t, loff_t, int datasync);
    int (*aio_fsync)(struct kiocb *, int datasync);
    int (*fasync)(int, struct file *, int);
    int (*lock)(struct file *, int, struct file_lock *);
    ssize_t (*sendpage)(struct file *, struct page *, int, size_t, loff_t *, int);
    // 获取未映射的地址空间给文件
    unsigned long (*get_unmapped_area)(struct file *, unsigned long, unsigned long, unsigned long, unsigned long);
    int (*check_flags)(int);
    int (*flock)(struct file *, int, struct file_lock *);
    ssize_t (*splice_write)(struct pipe_inode_info *, struct file *, loff_t *, size_t, unsigned int);
    ssize_t (*splice_read)(struct file *, loff_t *, struct pipe_inode_info *, size_t, unsigned int);
    int (*setlease)(struct file *, long, struct file_lock **);
    long (*fallocate)(struct file *file, int mode, loff_t offset,
                      loff_t len);
    int (*show_fdinfo)(struct seq_file *m, struct file *f);
};
```

## 和文件系统相关的数据结构

除了以上几种**VFS 基础对象**外，内核还使用了另外一些标准数据结构来管理文件系统的其他相关数据。

### 文件系统类型对象 file_system_type

每种文件系统类型只有一个 file_system_type 对象，即使有多个硬盘被挂载多次。

```c
// include/linux/fs.h
struct file_system_type
{
    const char *name;
    int fs_flags;
#define FS_REQUIRES_DEV 1
#define FS_BINARY_MOUNTDATA 2
#define FS_HAS_SUBTYPE 4
#define FS_USERNS_MOUNT 8           /* Can be mounted by userns root */
#define FS_USERNS_DEV_MOUNT 16      /* A userns mount does not imply MNT_NODEV */
#define FS_RENAME_DOES_D_MOVE 32768 /* FS will handle d_move() during rename() internally. */
    // 挂载函数，（会读取硬盘上的超级块对象）
    struct dentry *(*mount)(struct file_system_type *, int,
                            const char *, void *);
    void (*kill_sb)(struct super_block *);
    struct module *owner;
    struct file_system_type *next;
    struct hlist_head fs_supers;

    struct lock_class_key s_lock_key;
    struct lock_class_key s_umount_key;
    struct lock_class_key s_vfs_rename_key;
    struct lock_class_key s_writers_key[SB_FREEZE_LEVELS];

    struct lock_class_key i_lock_key;
    struct lock_class_key i_mutex_key;
    struct lock_class_key i_mutex_dir_key;
};
```

### 安装点对象 vfsmount

文件系统被安装时，会有一个 vfsmount 对象对应安装点

```c
// include/linux/mount.h
struct vfsmount
{
    struct dentry *mnt_root;    /* root of the mounted tree */
    struct super_block *mnt_sb; /* pointer to superblock */
    int mnt_flags;
};
```

`mnt_flags` 保存了安装时的标志：

- **MNT_NOSUID**：禁止该文件系统的可执行文件设置 setuid 和 setgid 标志
- **MNT_MODEV**：禁止访问该文件系统上的设备文件
- **MNT_NOEXEC**：禁止执行该文件系统上的可执行文件

还有一些在`include/linux/mount.h`中，不在这列出

## 进程相关的数据结构

系统中的每一个进程都有自己的一组打开的文件（像根文件系统、当前工作目录、安装点等），对于线程组来说可能会共享这些对象

### 进程已打开文件列表对象 files_struct

所有与单个进程(per-process)相关的信息(如打开的文件及文件描述符)都包含在其中:

```c
// include/linux/fdtable.h
/*
 * Open file table structure
 */
struct files_struct
{
    /*
     * read mostly part
     */
    atomic_t count;
    struct fdtable __rcu *fdt; //fd扩展表，fd_array不够时作为扩展
    struct fdtable fdtab;
    /*
     * written part on a separate cache line in SMP
     */
    spinlock_t file_lock ____cacheline_aligned_in_smp;
    int next_fd;
    unsigned long close_on_exec_init[1];
    unsigned long open_fds_init[1];
    struct file __rcu *fd_array[NR_OPEN_DEFAULT]; // fd表，64位机默认为64个
};
```

### 进程相关文件系统信息对象 fs_struct

```c
// include/linux/fs_struct.h
struct fs_struct
{
    int users;
    spinlock_t lock;
    seqcount_t seq;
    int umask;
    int in_exec; // 真正执行的文件
    struct path root, pwd;// 当前进程的根目录和当前目录
};
```

### 挂载点命名空间对象 mnt_namespace

由进程描述符中的[mnt_namespace 域](/posts/linux-kernel-process/#命名空间)指向，它使得每一个进程在系统中都看到唯一的安装文件系统（比如某个进程只能看到`/mnt/disk2`被挂载，看不到`/mnt/disk3`被挂载）

```c
// fs/mount.h
struct mnt_namespace
{
    atomic_t count;
    unsigned int proc_inum;
    struct mount *root;
    struct list_head list;
    struct user_namespace *user_ns;
    u64 seq; /* Sequence number to prevent loops */
    wait_queue_head_t poll;
    int event;
};
```

大多数情况下所有进程都共享同一个 mnt_namespace 命名空间，命名空间在容器技术上用的比较多

## 参考

- [Linux 内核设计与实现（第三版）第十三章](https://www.amazon.com/Linux-Kernel-Development-Robert-Love/dp/0672329468/ref=as_li_ss_tl?ie=UTF8&tag=roblov-20)
- [Robert Love](https://rlove.org/)
