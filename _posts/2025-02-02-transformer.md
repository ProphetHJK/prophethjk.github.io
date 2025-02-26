---
title: "Transformer 笔记"
date: 2025-02-02 08:00:00 +0800
published: true
mermaid: true
math: true
categories: [学习笔记]
tags: [AI, transformer]
---

## RNN 介绍

RNN 实际完成的就是从一个序列到另一个序列。对于自然语言，序列的单位就是一个词，序列中的某个词 t 有一个隐藏状态 $h_t$ ，它是由 t 本身和前一个词的隐藏状态 $h_{t-1}$ 作为参数来生成的，所以该隐藏状态能够包含之前所有词的信息(上下文)。

缺点：

1. 较难进行并行化处理，无法充分利用 GPU。
2. 当上下文信息很长是，隐藏状态需要占用大量内存空间。

## 架构

自然语言翻译一般使用 encoder-decoder 模型。

encoder 就是将一个序列 $(x_1,x_2,...,x_n)$ 转为计算机可以识别的 Tensor 序列 $ z = (z_1,z_2,...,z_n)$。比如 $x_t$ 是一个英文单词，$z_t$ 就是和该单词关联的一个向量。

decoder 就是将 encoder 的输出作为其输入，转为 $(y_1,y_2,...,y_m)$ 序列。长度可能和输入序列不同，比如英文翻译为中文。

这样的模型也是 auto-regressive(自回归) 的。每一次的输出都会使用之前的输出作为输入。

![alt text](/assets/img/2025-02-02-transformer/architecture.png)

本架构图中，左边是 encoder ,右边是 decoder。注意到右边下面的 output 作为输入说明它是 auto-regressive 的。Nx 表示方框内的同样的层有 N 个。“Add & Norm” 层有一个输入是跳过它之前的层的，这个就是残差连接(residual connection)。

### Encoder

简化的表示形式是 $LayerNorm(x + Sublayer(x))$。比如第一部分，Sublayer 就是 Multi-Head Attiontion 层，加上 x 表示是残差连接需要原始数据作为输入，这两个参数作为输入传递到 (Add & Norm) 层，上面一部分也是同理。

其中的 Normalization(标准化) 使用的是 LayerNorm 而不是 BatchNorm。

> Normalization(标准化)是让一组数据减去其均值再除以标准差得到的，得到的结果就是均值为 0 ，标准差为 1 的一组数据。通过这种方式让每一层的输出都相对标准化，类似于应用间进行数据通信的 API。

BatchNorm 是将一个 batch 内不同样本间的同一个的特征进行标准化，而 LayerNorm 是将一个 batch 内同一个样本的所有特征进行标准化。

### Decoder

decoder 相比于 Encoder 增加了一个 Masked Multi-Head Attention 层，该层用于实现 auto-regressive ，用于处理之前的输出结果来作为输入。因为 auto-regressive 的机制是将已经产生过的输出作为输入来提高预测的准确性，所以我们在训练时不希望让其看到完整的输出（训练时因为已经有完成的训练集了，可以看到完整的输出，但我们希望让其模拟在推理时将产生的输出作为输入的过程），所以增加一个 Mask 去遮盖后面的部分。

## Attention

注意力函数需要一个 query 和 一组 key-value 作为输入，它会根据 query 和 key 的相似度作为权重将对应的 value 进行相加。不同的注意力函数的区别就是计算相似度的**相似函数**。

在上面的模型图中， 下面的两个 Attention 层有三个输入，也就是 query、key、value，不过这三个参数其实是原始输入序列的三份相同的复制。此时对于 query 中的一项，也就是原始序列的一个词，计算注意力函数时它和 key 中相同位置的自身相似度肯定最高，权重也最高，然后如果序列中还有其他相似度较高的词，也会被考虑进来(较高权重)，最后得到输出。这就是 self-attention (自注意力)机制。自注意力机制实现了为 序列中的每一个词 附加同一个序列中其他它感兴趣的部分的信息。

公式如下：

$$Attention(Q,K,V)=softmax({QK^T\over \sqrt{d_k}})V$$

权重指的其实就是“correlation(相关性)”，Attention 计算权重的方式就是点乘，也就是将 query 和 key 矩阵做点乘($QK^T$)。从本质上来说点乘是计算两个矩阵 correlation 的一种方式，还有其他很多方式，只不过 Transformer 综合考虑选择了点乘。

架构图中上面的 Attention 层，它的 key ,value 来自于 Encoder 层，query 来自于下面的 Masked Multi-Head Attention 层。Encoder 和 Decoder 沟通的桥梁就是这个层。

### Multi-Head Attention

将 query 、key 和 value 都投影到各自的 h 个低维空间中，再进行 Attention 操作，可以增加可学习的参数数量(增加了 3\*h)。投影的概念就是降低维度，比如三维物体的三视图就是降低一个维度的投影，通过 3 个二维图来展现三维物体。

通过在不同的维度分别计算 Attention 后再进行组合，有什么好处？首先以三视图举例子，在三维物体中的一个点，投影到三个平面上，会出现 3 个点，原来我们是去三维空间找两点(类比 query 和 key)的距离信息(类比 attention 计算 value 的权重的过程)，现在是在三个平面上分别去找这 6 个点的距离信息($query_x$和$key_x$,$query_y$和$key_y$,$query_z$和$key_z$)，而且我们会为每个平面分配权重，这样假设 y 平面上的两个点($query_y$和$key_y$)距离很远，而在其他平面上距离较近，但因为我们并不关心 y 平面也就是其权重较小，那么这样计算出来的两个点间的最终距离就会很小，符合我们的预期。换个说法就是分成多个通道去找特征。

## Position-wise Feed-Forward Networks

Feed-Forward 层实际就是一个 MLP,它对输入序列的每个词单独进行 MLP 的计算。因为其输入是 attention 层的输出，而通过 attention 层的处理，每个词都已经被附加了整个原始序列中它感兴趣的部分(与之相关的部分)，所以不需要像 RNN 一样把前一个词的 MLP 计算结果作为输入，只要每个词单独输入就行，没有任何依赖。

## Embeddings and Softmax

Embedding 就是将输入数据映射成计算机可以进行计算的向量，这里固定每个词映射成 512 长度的向量。

## Positional Encoding

attention 机制带来的一个问题是其注意力信息是位置无关的，因为权重信息中没有位置信息，这也导致在翻译过程中将输入的词任意打乱，其注意力信息也是相同的，即使语义已经发生了很大的变化。

此时该模型在输入中加入了位置信息来解决该问题。

## 参考

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
