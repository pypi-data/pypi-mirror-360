from setuptools import setup, find_packages
# setup.py 最顶部添加
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
setup(
    name='Bruce_li_tc',
    version='0.3.5',
    description='A versatile utility library by Bruce Li',
    author='Bruce Li',
    author_email='bruce.li@example.com',
    packages=find_packages(),
    install_requires=[
        'requests',
        'loguru',
        'openpyxl',
        'aiohttp'
    ],
    extras_require={
        'excel': ['openpyxl'],
        'async': ['aiohttp'],
        'loguru': ['loguru']
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',

)