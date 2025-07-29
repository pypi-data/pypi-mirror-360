from haige_pyqt import __version__
from setuptools import setup, find_packages

setup(
    name="haige_pyqt",
    version=__version__,
    author="喜欢吃白米饭",
    author_email="gzhehai@foxmail.com",
    description="江湖海哥的常用 pyqt 封装通用包。",
    packages=find_packages(),
    install_requires=[
        "PyQt5>=5.15.9",
        "astunparse>=1.6.3",
        "pywin32>=310",
        "astunparse>=1.6.3"
    ],
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
