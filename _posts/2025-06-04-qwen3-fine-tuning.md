---
title: "使用 LLaMA-Factory 微调 Qwen3 小参数模型"
date: 2025-06-04 08:00:00 +0800
published: true
categories: [教程]
tags: [AI,AMD,Qwen3,fine-tuning]
---

## 环境搭建

### wsl + torch

详见 [使用 WSL2 + WSLg 在 Windows 上跑带图形界面的 AI 应用](/posts/wsl2-gpu-gui/)

### LLaMA-Factory

参考[本文](https://github.com/hiyouga/LLaMA-Factory/blob/main/README_zh.md)进行安装

```shell
git clone --depth 1 https://github.com/hiyouga/LLaMA-Factory.git
cd LLaMA-Factory
pip install -e ".[torch,metrics]" --no-build-isolation
```

### 下载 Qwen3 模型

这里使用最小的 0.6B 模型，虽然参数量少，但功能依然强大

可以选择 **hugging face** 或**魔搭社区**下载

```shell
huggingface-cli download Qwen/Qwen3-0.6B --local-dir ./model
```

或是：

```shell
modelscope download Qwen/Qwen3-0.6B --cache-dir ./model
```

注意下载的是 instruct 模型，而不是 base 模型(Qwen/Qwen3-0.6B-Base)。

## 准备数据集

可以下载预设的数据集，比如这个[新闻分类数据集](https://atp-modelzoo-sh.oss-cn-shanghai.aliyuncs.com/release/llama_factory/data_news_300.zip)

对于自己的数据，可以参考该格式编写，也可以使用 [easy-dataset](https://github.com/ConardLi/easy-dataset) 项目从文档中自动提取数据集，参考这个[教程](https://buaa-act.feishu.cn/wiki/KY9xwTGs1iqHrRkjXBwcZP9WnL9)

### easy-dataset

使用 easy-dataset 时，需要一个强大的 LLM 模型用来做问题提取，可以使用付费的 api，比如 OpenAI、Qwen 等。

当然也可以自行本地搭建，DeepSeek 最新发布的 DeepSeek-R1-0528-Qwen3-8B 模型已经非常强悍，完全可以胜任这个工作，可以使用 **llama.cpp** 运行量化的版本，在低显存的电脑上也能流畅运行：

1. 下载 [llama.cpp](https://github.com/ggml-org/llama.cpp/releases/tag/b5581)，选择合适的版本，非 NVIDIA 显卡可以选择 windows vulkan 版本
2. 下载 GGUF 格式的[量化版 DeepSeek-R1-0528-Qwen3-8B 模型](https://huggingface.co/unsloth/DeepSeek-R1-0528-Qwen3-8B-GGUF/tree/main)，根据需要下载合适的量化版，我这边使用的是 4bit 的 `DeepSeek-R1-0528-Qwen3-8B-UD-Q4_K_XL.gguf`
3. 启动服务端：`.\llama-server -m model/DeepSeek-R1-0528-Qwen3-8B-UD-Q4_K_XL.gguf --host 0.0.0.0 -ngl 99`，然后可以打开网页 **<http://127.0.0.1:8080>** 进行测试，同时该工具也会提供 openai 风格的 api(<http://127.0.0.1:8080/v1/chat/completions>)。

如果想去掉 DeepSeek-R1-0528-Qwen3-8B 模型的 `<think>` 标签：

```python
from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

# llama.cpp 的 API 地址
LLAMA_CPP_API_URL = 'http://localhost:8080/chat/completions'  # 默认端口

# 正则用于去除 <think> 标签内容
def remove_think_blocks(text):
    return re.sub(r"<think>(.*?)</think>", "", text, flags=re.DOTALL)

@app.route('/chat/completions', methods=['POST'])
def proxy_completion():
    # 客户端发来的数据
    payload = request.get_json()

    # 转发到 llama.cpp 的 /completion 接口
    response = requests.post(LLAMA_CPP_API_URL, json=payload)
    llama_response = response.json()
    print(llama_response)

    # 过滤 <think> 标签内容
    llama_response['choices'][0]['message']['content'] = remove_think_blocks(llama_response['choices'][0]['message']['content'])

    print(llama_response)
    return jsonify(llama_response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## 启动微调

1. 进入 wsl，进入 LLaMA-Factory 的目录

    ```console
    dev@DESKTOP-MVN3D3J:/mnt/h/repo/LLaMA-Factory$ ls
    CITATION.cff  MANIFEST.in  README.md     assets  config  datasets  evaluation  models   pyproject.toml    saves    setup.py  start.sh
    LICENSE       Makefile     README_zh.md  cache   data    docker    examples    offload  requirements.txt  scripts  src       tests 
    ```

2. (激活虚拟 python 环境)，运行命令 `llamafactory-cli webui`，默认运行在 7860 端口
3. 打开 <http://127.0.0.1:7860>，选择正确的模型类型 **Qwen3-0.6B-Instruct**，填写正确的本地已经下载的模型地址
    ![alt text](/assets/img/2025-06-04-qwen3-fine-tuning/image.png)
4. 填写准备好的数据集的本地目录，选择数据集类型，这里选 `train`
    ![alt text](/assets/img/2025-06-04-qwen3-fine-tuning/image-1.png)
5. 配置训练参数，这里把学习率配置为 `5e-6`，梯度累积配置为 `2`
    ![alt text](/assets/img/2025-06-04-qwen3-fine-tuning/image-4.png)
6. 配置 LoRA 参数，这里开启了 LoRA+ ，同时作用模块配置为 all
    ![alt text](/assets/img/2025-06-04-qwen3-fine-tuning/image-3.png)
7. 点击`开始`按钮开始训练，同时会显示进度和损失曲线，等待训练完成
    ![alt text](/assets/img/2025-06-04-qwen3-fine-tuning/image-2.png)
8. 训练完成后可以进行测试，填写`检查点路径`并切换到 `chat` 页面，再点击`加载模型`
    ![alt text](/assets/img/2025-06-04-qwen3-fine-tuning/image-6.png)
9. 可以在验证集中找一个数据进行测试，因为验证集并没有参与训练，可以检验出训练的效果
    ![alt text](/assets/img/2025-06-04-qwen3-fine-tuning/image-7.png)

    ![alt text](/assets/img/2025-06-04-qwen3-fine-tuning/image-8.png)
10. 微调后的模型成功理解了`新闻分类`指令并给出预期的结果，训练成功。

训练前的效果：

![alt text](/assets/img/2025-06-04-qwen3-fine-tuning/image-9.png)

![alt text](/assets/img/2025-06-04-qwen3-fine-tuning/image-10.png)

### QLoRA

如果想在训练过程中节省 VRAM 的占用，可以启用 QLoRA 功能

1. 使用 pip 安装 bitsandbytes，对于 AMD 用户需要使用 [ROCm/bitsandbytes](https://github.com/ROCm/bitsandbytes) 进行手动编译：

    ```shell
    git clone --recurse https://github.com/ROCm/bitsandbytes
    cd bitsandbytes
    git checkout rocm_enabled_multi_backend
    pip install -r requirements-dev.txt
    cmake -DCOMPUTE_BACKEND=hip -S . #Use -DBNB_ROCM_ARCH="gfx90a;gfx942" to target specific gpu arch
    make
    pip install .
    ```

2. 启用 LLaMA-Factory 相关功能，一般将量化等级配置为 4 来减少 VRAM 占用

    ![alt text](/assets/img/2025-06-04-qwen3-fine-tuning/image-11.png)

3. 之后的训练过程和上面介绍的相同

## 参考

- [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory)
- [LLaMA Factory：微调DeepSeek-R1-Distill-Qwen-7B模型实现新闻标题分类器](https://gallery.pai-ml.com/#/preview/deepLearning/nlp/llama_factory_deepseek_r1_distill_7b)
- [bitsandbytes](https://github.com/ROCm/bitsandbytes)
- [llama.cpp](https://github.com/ggml-org/llama.cpp)
- [Easy Dataset × LLaMA Factory: 让大模型高效学习领域知识](https://buaa-act.feishu.cn/wiki/KY9xwTGs1iqHrRkjXBwcZP9WnL9)
