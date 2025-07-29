import requests
from .result import Result


def download_file(url, save_path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return Result.ok(f"文件已保存到: {save_path}")
    except Exception as e:
        return Result.err(f"下载失败: {e}")


def test_download_file():
    url = "https://img.alicdn.com/tps/TB1PlWbKFXXXXbmXFXXXXXXXXXX-16-16.ico"
    save_path = "test.ico"
    res = download_file(url, save_path)
    if res.is_ok():
        print(res.value)
    else:
        print(res.error)
