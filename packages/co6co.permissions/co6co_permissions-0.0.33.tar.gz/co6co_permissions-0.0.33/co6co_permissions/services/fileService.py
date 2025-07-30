
import os
import shutil


def delFileOrFolder(path: str):
    """
    删除文件或目录
    """
    if os.path.isfile(path):
        os.unlink(path)
    elif os.path.isdir(path):
        # os.rmdir(path) 删除空文件夹
        shutil.rmtree(path)
