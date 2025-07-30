from typing import Final

import pyperclip
import typer
from beni import bcolor, btask
from beni.bfunc import syncCall

app: Final = btask.app


@app.command()
@syncCall
async def upgrade(
    name: str = typer.Argument('bcmdx', help='要更新的包名'),
):
    '使用 pipx 官方源更新指定包到最新版本'

    cmd = f'pipx upgrade {name} -i https://pypi.org/simple'
    pyperclip.copy(cmd + '\n')
    bcolor.printGreen(cmd)
    bcolor.printGreen('已复制到剪贴板（需要手动执行）')
    bcolor.printGreen('OK')
