import subprocess
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--interval', type=int, default=15, help='定时间隔（分钟）')
    parser.add_argument('-p', '--port', type=int, default=54321, help='Web UI 端口')
    args = parser.parse_args()

    from eodo import webui
    webui_path = webui.__file__
    args = [
        "streamlit", "run", webui_path,
        "--server.port", str(args.port),
        "--",
        f"--interval={args.interval}"
    ]
    proc = subprocess.Popen(args)
    try:
        proc.wait()
    except KeyboardInterrupt:
        print("收到中断信号，正在关闭 Streamlit 服务...")
        proc.kill()
        proc.wait()

if __name__ == "__main__":
    main()
