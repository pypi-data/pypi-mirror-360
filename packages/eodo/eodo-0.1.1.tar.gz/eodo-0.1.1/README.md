# EdgeOne Dynamic Origin

EdgeOne 是腾讯云的边缘安全加速平台。该脚本为其提供动态更新源站组 IP 的功能。
此功能特别适用于那些 IP 地址可能会变化的源站，确保 CDN 始终能够正确地获取最新的内容。比如仅有动态 IPV6 地址的服务器，
也能够长期稳定部署WEB服务，而不必使用 frp / ngork 等内网端口转发工具。

注意，若要使用该脚本，在 EdgeOne 中的加速域名必须使用源站组配置源站。

### 使用方法

1. 必要依赖：
    ```shell
    python -m pip install --upgrade pip
    pip install requests pyyaml
    ```
2. 重命名 `config.example.yaml` 为 `config.yaml` ，并编辑配置项，具体配置项请参考 `config.example.yaml` 中的注释。
3. 可以执行 `python main.py` 进行测试。
4. 对于 windows，可以通过 **任务计划程序** 将脚本配置为定期执行；对于 linux，可以使用 **cron** 将脚本配置为定期执行

#### Windows 任务计划程序配置示例
1. 打开任务计划程序。
2. 创建一个基本任务。
3. 选择触发器（例如，每日）。
4. 在操作中选择“启动程序”，并选择 Python 可执行文件和脚本路径。
5. 设置脚本的工作目录和参数。

#### Linux cron 配置示例
1. 打开终端。
2. 编辑 crontab 文件：
    ```shell
    crontab -e
    ```
3. 添加一行来定期执行脚本，例如每小时执行一次：
    ```
    0 * * * * python /your_path/main.py
    ```
