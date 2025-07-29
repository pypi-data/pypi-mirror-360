from .get_favicon_url import get_favicon_url, test_get_favicon_url
from .download_file import download_file, test_download_file
from .pinyin import Pinyin
from .result import Result
from .ResModel import ResModel
from .res import res, from_result


__all__ = [
    "get_favicon_url",
    "test_get_favicon_url",
    "download_file",
    "test_download_file",
    "Pinyin",
    "ResModel",
    "test_response",
    "Result",
    "res",
    "from_result",
]
