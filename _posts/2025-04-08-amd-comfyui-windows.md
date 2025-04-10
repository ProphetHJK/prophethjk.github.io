---
title: "在windows+AMD显卡平台上运行 ComfyUI"
date: 2025-04-08 08:00:00 +0800
published: true
categories: [教程]
tags: [AI,AMD]
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

## 执行

可以直接双击 ComfyUI-Zluda 目录下的 `comfyui.bat` 启动 ComfyUI

该项目自带了 [ComfyUI-Manager](https://github.com/Comfy-Org/ComfyUI-Manager)，可以很方便的下载第三方节点依赖

## 参考

- [patientx/ComfyUI-Zluda](https://github.com/patientx/ComfyUI-Zluda)
