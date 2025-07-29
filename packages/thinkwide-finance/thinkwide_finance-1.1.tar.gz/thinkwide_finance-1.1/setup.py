# setup.py
from setuptools import setup, find_packages

setup(
    name='thinkwide_finance',
    version='1.1',
    packages=find_packages(),  # 自动查找包和子包
    install_requires=[],  # 依赖项列表（如果有的话）

    author='ThinkWide',
    author_emAIl='15115829@qq.com',
    description='Thinkwide_Finance is an elegant and simple financial data interface library for Python, built for '
                'human beings! ',
    long_description='Thinkwide_Finance is an elegant and simple financial data interface library for Python, '
                     'built for human beings!',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
)

'''
# 构建包（这将创建一个dist目录）
python setup.py sdist bdist_wheel

# 上传到PyPI（需要先配置~/.pypirc文件）
twine upload dist / *

'''
