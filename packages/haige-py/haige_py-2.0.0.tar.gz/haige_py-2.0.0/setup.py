from haige_py import __version__
from setuptools import setup, find_packages

setup(
    name="haige_py",
    version=__version__,
    author="喜欢吃白米饭",
    author_email="gzhehai@foxmail.com",
    description="江湖海哥的常用 python 封装通用包。",
    # long_description=open("README.md").read(),
    # long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "astunparse>=1.6.3"
    ],
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
