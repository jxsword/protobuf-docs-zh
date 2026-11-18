+++
title = "Protobuf 编译器安装"
weight = 15
description = "如何安装 Protobuf 编译器。"
type = "docs"
no_list = "true"
linkTitle = "Protoc 安装"
source_url = "https://protobuf.dev/installation/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

Protobuf 编译器 `protoc` 用于编译包含服务（service）与消息（message）定义的 `.proto` 文件。请从下面给出的方法中选择一种来安装 `protoc`。

### 安装预编译二进制文件（任意操作系统）{#binary-install}

要通过预编译二进制文件安装协议编译器的最新发布（release）版，请按照以下说明操作：

1.  前往最新的
    [GitHub 发布页](https://github.com/protocolbuffers/protobuf/releases/latest)。
2.  下载与你的操作系统和计算机架构对应的
    zip 文件（`protoc-<version>-<os>-<arch>.zip`）。

    *   例如，Linux x86-64 平台 34.1 版本对应的文件名将为
        `protoc-34.1-linux-x86_64.zip`。

    **替代方案：使用命令下载**

    无需手动下载，你可以使用以下命令自动获取最新的 Linux x86_64 发布产物（asset）文件：

    ```sh
    # 从 GitHub API 获取最新 Linux x86_64 发布产物文件的下载 URL
    URL=$(curl -s https://api.github.com/repos/protocolbuffers/protobuf/releases/latest \
      | jq -r '.assets[] | select(.name | endswith("linux-x86_64.zip")) | .browser_download_url')
    curl -LO $URL
    ```

3.  将文件解压到 `$HOME/.local` 或你选择的目录下。例如：

    ```sh
    # 如果你使用了上面的命令：
    unzip $(basename $URL) -d $HOME/.local

    # 如果你是手动下载的（将 <version> 替换为实际版本）：
    # unzip protoc-<version>-linux-x86_64.zip -d $HOME/.local
    ```

4.  更新你所在环境的 path 变量，使其包含 `protoc` 可执行文件所在的路径。例如：

    ```sh
    export PATH="$PATH:$HOME/.local/bin"
    ```

### 使用包管理器安装 {#package-manager}

{{% alert title="Warning" color="warning" %}} 使用包管理器安装后，请运行 `protoc --version` 检查 `protoc` 的版本，以确保其足够新。某些包管理器安装的 `protoc` 版本可能相当陈旧。请查看[版本支持页面](https://protobuf.dev/support/version-support)，将版本检查的输出与你所用语言的受支持版本的次版本号进行比较。{{% /alert %}}

你可以使用包管理器，通过以下命令在 Linux、macOS 或 Windows 下安装协议编译器 `protoc`。

-   Linux，例如使用 `apt` 或 `apt-get`：

    ```sh
    apt install -y protobuf-compiler
    protoc --version  # 确保编译器版本为 33.0+
    ```

-   macOS，使用 [Homebrew](https://brew.sh)：

    ```sh
    brew install protobuf
    protoc --version  # 确保编译器版本为 33.0+
    ```

-   Windows，使用
    [Winget](https://learn.microsoft.com/en-us/windows/package-manager/winget/)

    ```sh
    > winget install protobuf
    > protoc --version # 确保编译器版本为 33.0+
    ```

### 其他安装选项 {#other}

如果你想从源码构建协议编译器，或获取预编译二进制文件的旧版本，请参阅[下载 Protobuf](https://protobuf.dev/downloads)。
