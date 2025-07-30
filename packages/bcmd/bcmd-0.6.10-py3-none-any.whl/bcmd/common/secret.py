import getpass
from typing import Any, TypedDict, cast

from async_lru import alru_cache
from beni import bcrypto, btask
from beni.bcolor import printRed


class PypiSecret(TypedDict):
    username: str
    password: str


@alru_cache
async def getPypi(value: str = '') -> PypiSecret:
    return cast(
        Any,
        _getData(value or 'QbuF2mV/lqovtF5dskZGD7qHknYbNuF2QseWRtWxLZTPrC/jL1tcxV8JEKaRjLsu46PxJZ7zepJwggnUTIWnEAoV5VtgP2/hbuzxxHha8817kR5c65H9fXm8eOal7DYXsUoGPQMnm59UWNXUKjmIaP4sn9nySFlRYqa8sEZSbYQ4N0NL35Dpj1e3wyQxJ+7h2jwKAz50Hh8G4yAM3/js9+NUe4ymts+UXcwsP3ADIBMkzjnFc0lEYg2d+fw0A74XWCvoZPoGqHZR/THUOVNAYxoGgDzP4SPIk1XsmtpxvfO/DpJd/Cg/0fB3MYagGKI1+m6Bxqhvd1I/lf0YbM5y4E4='),
    )


class QiniuSecret(TypedDict):
    bucket: str
    baseUrl: str
    ak: str
    sk: str


@alru_cache
async def getQiniu(value: str = '') -> QiniuSecret:
    return cast(
        Any,
        _getData(value or 'vNroFKeKklrdcJ89suFm+iyuJsq/cyUB5+QWoeeiMc/J0oSLF9cg5rqbK1IRxF0cCQ8KmkQQhdVa+PI6kuTBhoSH6IviVTylzAOrJywEccz9jWkJkW28Y9Vo4ePZmfWf/j7wdxNB144z234KD8IxJn4lR2A0L9JN5kk1o1/hpcydXL74FNtt03lYL/E3WVcvpUfw37mri2HMYOfUw81dRwW35/hMuQjtq1BBrKrIsSKTHH44tROMcgyvt+Qy292AtDBcsYiZxBKhQtBFPMq/vUs='),
    )


def _getData(content: str) -> dict[str, Any]:
    index = content.find(' ')
    if index > -1:
        tips = f'请输入密码（{content[:index]}）：'
    else:
        tips = '请输入密码：'
    while True:
        try:
            pwd = getpass.getpass(tips)
            return bcrypto.decryptJson(content, pwd)
        except KeyboardInterrupt:
            print('')
            btask.abort('用户操作取消')
        except BaseException:
            printRed('密码错误')
