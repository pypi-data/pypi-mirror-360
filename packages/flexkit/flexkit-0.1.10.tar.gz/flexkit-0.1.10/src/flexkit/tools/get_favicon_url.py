from favicon import get
from .result import Result


def get_favicon_url(url):
    try:
        icons = get(url)
        if icons:
            return Result.ok(icons[0].url)
        else:
            return Result.err("No favicon found")
    except Exception as e:
        Result.err(e)


def test_get_favicon_url():
    res = get_favicon_url("https://ai.m.taobao.com/")
    if res.is_ok():
        print(res.value)
    else:
        print(res.error)
