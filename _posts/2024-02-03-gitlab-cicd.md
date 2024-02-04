---
title: "GitLab CI/CD部署"
author: Jinkai
date: 2024-02-03 08:00:00 +0800
published: true
categories: [教程]
tags: [git, gitlab]
---

## GitLab Runner

GitLab 提供了 CI/CD 功能，类似于 Github Action 和 Gitea Action。

GitLab 和 Gitea 一样，也需要一个独立的执行器(runner)用于管理 CI/CD 过程，包括接收命令、创建容器等。

### 安装

我一般会选择**手动安装**的方式，详情见官方文档：<https://docs.gitlab.cn/runner/install/linux-manually.html#%E4%BD%BF%E7%94%A8%E4%BA%8C%E8%BF%9B%E5%88%B6%E6%96%87%E4%BB%B6>

### 注册

首先要获获取仓库令牌，在仓库的`设置`-`CI/CD`页面获取令牌信息：

![runner](/assets/img/2024-02-03-gitlab-cicd/1706945000303.jpg)

按照官方文档步骤即可：<https://docs.gitlab.cn/runner/register/index.html#linux>

这里选择 Docker 作为执行环境。

### Docker 镜像

如果选择 Docker 作为执行环境，就需要准备实际执行 CI/CD 过程所需的 Docker 镜像，主要需要两个：

- gitlab-runner-helper：<https://hub.docker.com/r/alpinelinux/gitlab-runner-helper>
- 自定义的容器镜像

前者主要用于执行一些辅助操作，如 Git 相关的操作(GitLab 会自动拉取仓库，不像 Github 或 Gitea 需要手动执行)，后者用于实际执行相关操作(如使用 python 脚本检查代码格式，用 GCC 编译程序等)。

注意还要修改执行器的配置文件，`pull_policy = "never"`表示仅使用本地镜像，对于无法连接外网的服务器有用：

```plaintext
[[runners]]
  (...)
  executor = "docker"
  [runners.docker]
    (...)
    pull_policy = "never"
    helper_image = "alpinelinux/gitlab-runner-helper:latest-x86_64"
```

## 流水线(pipeline)配置

GitLab 使用 `.gitlab-ci.yml` 文件配置工作流(workflow)，类似于 Github 中 `.github` 目录下的工作流配置文件。

关于其语法可见官方文档：<https://docs.gitlab.cn/jh/ci/yaml/gitlab_ci_yaml.html>

这里提供一个简单示例：

```yaml
stages:
  - analyze
  - build

cppcheck:
  stage: analyze
  script:
    - python3 tools/checkcode.py

build:
  stage: build
  script:
    - mkdir -p build && cd build && cmake .. && make
```
