import os
from typing import Final

from beni import bcolor, bfile, bpath, btask, binput
from beni.bfunc import syncCall

app: Final = btask.newSubApp('Debian 系统管理')


@app.command()
@syncCall
async def install_python():
    '安装python脚本'
    pythonZipFile = ''
    pythonName = ''
    pythonVersion = ''
    bcolor.printYellow(f'官网地址：https://www.python.org/downloads/source/')
    bcolor.printYellow(f'先从官网上下载 python 源码压缩包（.tar.xz）')
    while True:
        pythonZipFile = input('输入python压缩文件名（如：Python-3.12.1.tar.xz）：').strip()
        if pythonZipFile.endswith('.tar.xz'):
            pythonName = pythonZipFile.replace('.tar.xz', '')
            pythonVersion = '.'.join(pythonName.split('-')[-1].split('.')[:-1])
            break
        else:
            print('输入有误，请重新输入')
    cmdList: list[str] = [
        f'apt update',
        f'apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev libbz2-dev -y',
        f'tar -xf {pythonZipFile}',
        f'cd {pythonName}',
        f'./configure --enable-optimizations',  # 配置编译选项
        f'make -j `nproc`',                     # 编译源代码，`nproc` 会利用所有可用的 CPU 核心加快编译速度
        f'make altinstall',                     # 安装 Python，altinstall 避免替换默认的 python 命令
        f'cd ..',
        f'rm -rf {pythonName}',
        f'rm -rf /usr/local/bin/python',
        f'ln -s /usr/local/bin/python{pythonVersion} /usr/local/bin/python',
        f'rm -rf /usr/local/bin/pip',
        f'ln -s /usr/local/bin/pip{pythonVersion} /usr/local/bin/pip',
        f'python --version',
        f'pip --version',
        f'pip install pipx',
        f'pipx install bcmd',
    ]
    shFile = bpath.desktop(f'install-python-{pythonName}.sh')
    await bfile.writeText(shFile, '\n'.join(cmdList))
    bcolor.printGreen(f'将以下两个文件拷贝到服务器上，然后执行 sh {shFile.name} 即可安装 python')
    print(pythonZipFile)
    print(shFile)


@app.command()
@syncCall
async def install_software():
    '安装常用软件'
    await binput.confirm('即将安装这些软件（7z nginx mariadb），是否确认？')
    cmdList: list[str] = [
        f'echo 更新软件包列表',
        f'apt update',
        f'echo 安装 7z',
        f'apt install p7zip-full -y',
        f'echo 安装 nginx',
        f'apt install nginx -y',
        f'systemctl start nginx',
        f'systemctl enable nginx',
        f'systemctl status nginx',
        f'echo 安装 MariaDB',
        f'apt install mariadb-server -y',
        f'systemctl start mariadb',
        f'systemctl enable mariadb',
        f"sed -i 's/bind-address/# bind-address/' /etc/mysql/mariadb.conf.d/50-server.cnf"
        f'systemctl restart mariadb',
        f'systemctl status mariadb',

    ]
    for cmd in cmdList:
        os.system(cmd)
