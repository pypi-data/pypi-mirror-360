"""
 * @Author：cyg
 * @Package：setup
 * @Project：Default (Template) Project
 * @name：setup
 * @Date：2025/5/8 09:54
 * @Filename：setup
"""

from setuptools import setup, find_packages

setup(
    name="fic_data_api",
    version="0.1.6",
    packages=find_packages(),
    install_requires=[
        'requests'
    ],
    description="FIC数据接口",
    author="FIC",
    author_email="fic_server@126.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
