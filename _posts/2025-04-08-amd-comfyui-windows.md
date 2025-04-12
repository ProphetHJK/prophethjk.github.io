---
title: "在windows+AMD显卡平台上运行 ComfyUI"
date: 2025-04-08 08:00:00 +0800
published: true
categories: [教程]
tags: [AI,AMD,ComfyUI]
---

## 环境搭建

主要依赖于该项目：<https://github.com/patientx/ComfyUI-Zluda>

1. clone 该仓库: <https://github.com/patientx/ComfyUI-Zluda>
2. 安装 python 3.10(推荐，我用的也是这个)
3. 安装 [hip sdk 最新版本](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)，只需要核心模块和运行时库模块
4. 修改系统环境，将 `C:\Program Files\AMD\ROCm\{version}\bin` 加入`系统`环境变量
5. 双击执行 ComfyUI-Zluda 目录下的 `install.bat`(不支持 powershell)，等待安装完成
6. 官方推荐使用 `patchzluda2.bat` 脚本自动打补丁，但是我自己试不成功，需要手动修改`patchzluda2.bat` 脚本，删除下载和解压过程，然后前往 <https://github.com/lshqqytiger/ZLUDA/releases> 手动下载 `ZLUDA-windows-rocm6-amd64.zip`，解压到 ComfyUI-Zluda 目录下的 zluda 文件夹，然后双击执行脚本直接进行打补丁操作。
7. 查询显卡是否在 hip sdk 支持范围内，如果没有，去 <https://github.com/brknsoul/ROCmLibs> 下载第三方支持库，我的显卡是 RX9070，没有官方支持，下载对应的 `rocm gfx1201 for rocm 6.2.4-no-optimized.7z`，然后用压缩包内的文件覆盖 `C:\Program Files\\AMD\ROCm\5.7\bin\rocblas\` 里的内容(里面的 dll 好像不覆盖也可以)

## 启动 WEBUI

可以直接双击 ComfyUI-Zluda 目录下的 `comfyui.bat` 启动 ComfyUI

该项目自带了 [ComfyUI-Manager](https://github.com/Comfy-Org/ComfyUI-Manager)，可以很方便的下载第三方节点依赖

可以修改 `comfyui.bat` ，监听 0.0.0.0 将 webui 暴露到公网，也可以用 nginx 等反代。

~~TODO：使用反代后无法在 webui 显示进度~~(已解决：<https://github.com/comfyanonymous/ComfyUI/issues/3384#issuecomment-2233791739>)

### 切换语言

在 ComfyUI 界面左下角点击 `Settings`，然后选择 `Language`，选择 `中文` 即可切换为中文界面

![alt text](/assets/img/2025-04-08-amd-comfyui-windows/image-20.png)

## Flux 换衣实例

### 环境

按[此处](https://dfldata.cc/forum.php?mod=viewthread&tid=19910&highlight=%E9%AB%98%E7%BA%A7%E6%95%99%E7%A8%8B%E3%80%91%E5%A4%AA%E5%8F%98%E6%80%81%E4%BA%86%2CFLUX%E5%AE%9E%E7%8E%B0%E8%B6%85%E8%87%AA%E7%84%B6%E6%8D%A2%E8%A1%A3%E6%9C%8D%E6%8D%A2%E7%89%A9%E5%93%81)教程下载模型和工作流文件，将 models 放入 ComfyUI-Zluda 目录下的 models 文件夹

需要以下模型：

- flux-fill-dev
- flux1-redux-dev
- clip
- vae
- clip-vision

打开 ComfyUI，点击左上角的 `Workflow` 按钮，选择 `Open`，然后选择下载好的工作流文件:

![alt text](/assets/img/2025-04-08-amd-comfyui-windows/image-5.png)

如果之前有加载过，可以在左侧边栏选择工作流：

![alt text](/assets/img/2025-04-08-amd-comfyui-windows/image-4.png)

如果显存只有16G，可以把这两个模型换成 fp8 版本的，不然会爆显存：

![alt text](/assets/img/2025-04-08-amd-comfyui-windows/image-8.png)

### 运行

1. 添加图片，一张是要换的衣服(平面图或模特图皆可)，另一张是被换的模特图

    ![alt text](/assets/img/2025-04-08-amd-comfyui-windows/image-7.png)
2. 点击下方的 `Run` 按钮开始图片预处理，然后会在“**手动绘制遮罩**”面板看到两张预处理后图片

    ![alt text](/assets/img/2025-04-08-amd-comfyui-windows/image-6.png)

    ![alt text](/assets/img/2025-04-08-amd-comfyui-windows/image-9.png)
3. 在“**手动绘制遮罩**”面板，右键单击上面的图片，点击 `Open in MaskEditor`为上面的图添加**目的区域遮罩**(涂抹右侧图片中需要被更换的部分)，同样也为下面的图添加**来源区域遮罩**(涂抹左侧图片中的衣服部分)，尽可能涂抹的**准确**些，仅把要被替换的部分包括进来

    ![alt text](/assets/img/2025-04-08-amd-comfyui-windows/image-10.png)

    ![alt text](/assets/img/2025-04-08-amd-comfyui-windows/image-11.png)

    ![alt text](/assets/img/2025-04-08-amd-comfyui-windows/image-12.png)

    ![alt text](/assets/img/2025-04-08-amd-comfyui-windows/image-17.png)
4. 在 **KSampler** 节点配置合适的轮次，一般来说轮次越多效果越好(但有时也可能效果越来越差)，在我的 RX9070 上是大概 10 秒一轮，也就是说运行 10 轮大概 2 分钟，20 轮就要 4 分钟。

    ![alt text](/assets/img/2025-04-08-amd-comfyui-windows/image-14.png)
5. 再次点击 **Run** 开始正式推理，根据设定的轮次，运行时间也会不同，等待运行完成即可（显卡风扇会开始狂转，请坐和放宽）
    ![alt text](/assets/img/2025-04-08-amd-comfyui-windows/image-6.png)

    ![alt text](/assets/img/2025-04-08-amd-comfyui-windows/image-15.png)
6. 在左侧面板查看当前正在执行的队列，完成后可在工作流右侧查看预览和下载图片(13轮耗时190秒)
   ![alt text](/assets/img/2025-04-08-amd-comfyui-windows/image-16.png)

   ![alt text](/assets/img/2025-04-08-amd-comfyui-windows/image-18.png)

## 参考

- [patientx/ComfyUI-Zluda](https://github.com/patientx/ComfyUI-Zluda)
- [【高级教程】太变态了,FLUX实现超自然换衣服换物品](https://dfldata.cc/forum.php?mod=viewthread&tid=19910&highlight=%E9%AB%98%E7%BA%A7%E6%95%99%E7%A8%8B%E3%80%91%E5%A4%AA%E5%8F%98%E6%80%81%E4%BA%86%2CFLUX%E5%AE%9E%E7%8E%B0%E8%B6%85%E8%87%AA%E7%84%B6%E6%8D%A2%E8%A1%A3%E6%9C%8D%E6%8D%A2%E7%89%A9%E5%93%81)
- [FLUX.1-Fill-dev](https://huggingface.co/black-forest-labs/FLUX.1-Fill-dev)
