from setuptools import setup

from setuptools.command.sdist import sdist
import subprocess
import sys
import co6co.setupUtils as setupUtils
# try:
#    from co6co import setupUtils
# except ImportError:
#    subprocess.check_call([sys.executable, "-m", "pip", "install", "co6co>=0.0.25"])
#    from co6co import setupUtils

version = setupUtils.get_version(__file__)
packageName, packages = setupUtils.package_name(__file__)
long_description = setupUtils.readme_content(__file__)


setup(
    name=packageName,
    version=version,
    description="web permissionsAPI",
    packages=packages,

    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=setupUtils.get_classifiers(),
    include_package_data=True, zip_safe=True,
    # 依赖哪些模块
    install_requires=['requests', "co6co>=0.0.29", "co6co.sanic_ext>=0.0.9", "co6co.web-db>=0.0.14", "opencv-python==4.10.0.82", "numpy==1.26.4", "Pillow>=10.1.0"],

    # package_dir= {'utils':'src/log','main_package':'main'},#告诉Distutils哪些目录下的文件被映射到哪个源码
    author='co6co',
    author_email='co6co@qq.com',
    url="http://github.com/co6co",
    data_file={
        ('', "*.txt"),
        ('', "*.md"),
    },
    package_data={
        '': ['*.txt', '*.md'],
        'bandwidth_reporter': ['*.txt']
    }, cmdclass={
        'sdist': setupUtils.CustomSdist
    }
)
