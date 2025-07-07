---
title: "使用 rclone 挂载远程 webdav 为本地盘"
date: 2025-06-20 08:00:00 +0800
published: true
categories: [教程]
tags: [rclone, nginx, webdav]
image: /assets/img/2025-06-20-rclone-webdav/image.png
---

## rclone 下载

从 <https://github.com/rclone/rclone/releases> 下载对应的文件，只有命令行工具，没有 gui，包含了 server 和 client。

## rclone webdav server

如果服务器没有提供 webdav，可以使用 rclone 自带的 webdav 服务，通过 docker 或使用 rclone cli 即可运行，这里给出 docker compose 示例：

```yaml
services:
  rclone:
    image: rclone/rclone:latest
    container_name: rclone
    command:
      - serve
      - webdav
      - /mnt/disk
      - --baseurl
      - webdav2
      - --addr
      - :8686
      - --user
      - yourname
      - --pass
      - yourpassword
      - --no-modtime
    volumes:
      - /mnt/disk:/mnt/disk:ro
    restart: unless-stopped
```

`/mnt/disk` 下的所有文件将被共享

### nginx 反向代理

通过 nginx 反代为 webdav 服务添加 tls 加密：

```plaintext

server {
    # SSL configuration
    listen 443 ssl;
    listen [::]:443 ssl;

    http2 on;
    ssl_certificate /home/dev/ssl/fullchain.cer;
    ssl_certificate_key /home/dev/ssl/key.pem;
    ssl_protocols TLSv1.3 TLSv1.2;
    ssl_prefer_server_ciphers on;
    #ssl_early_data on;
    keepalive_timeout 70;
    ssl_ciphers TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256:TLS13-AES-128-CCM-8-SHA256:TLS13-AES-128-CCM-SHA256:EECDH+CHACHA20:EECDH+CHACHA20-draft:EECDH+ECDSA+AES128:EECDH+aRSA+AES128:RSA+AES128:EECDH+ECDSA+AES256:EECDH+aRSA+AES256:RSA+AES256:EECDH+ECDSA+3DES:EECDH+aRSA+3DES:RSA+3DES:!MD5;

	server_name webdav.test.com;

	root /var/www/html;
	index index.html;

    location /webdav2 {
        proxy_pass http://rclone:8686;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        client_max_body_size 2G;
        proxy_read_timeout 600;
    }
}
```

注意 location 指定的 url 要和 rclone 配置中的 baseurl 匹配，否则客户端会无法识别，见<https://github.com/rclone/rclone/issues/8528>

## rclone client

### 创建配置

进入 rclone 解压目录，执行：

```powershell
New-Item -Path 'rclone.conf' -ItemType File
.\rclone.exe config
```

按提示填写 webdav 配置即可，生成的 `rclone.conf` 示例:

```conf
[dav]
type = webdav
url = https://webdav.test.com/webdav2/
vendor = rclone
user = yourname
pass = yourpassword_hash
```

### 启动 client

编写一个 powershell 脚本，保存为 `start.ps1`:

```powershell
Start-Process -FilePath ".\rclone.exe" -ArgumentList @(
    "mount",
    "--config", ".\rclone.conf",
    "dav:", "R:",
    "--vfs-cache-mode", "full",
    "--dir-cache-time", "10m",
    "--read-only",
    "--network-mode",
    "--no-modtime",
    "--links"
) -WindowStyle Hidden
```

运行该脚本，即可将 webdav 挂载到 `R:` 盘，相关参数见[官方文档](https://rclone.org/commands/rclone_mount/)

如需关闭后台服务并取消挂载，使用：

```powershell
Get-Process rclone | Stop-Process
```

## TODO

- 当前无法显示总空间和剩余空间

## 参考

- [rclone](https://rclone.org/)
- [rclone_serve_webdav](https://rclone.org/commands/rclone_serve_webdav/)
- [rclone_mount](https://rclone.org/commands/rclone_mount/)
