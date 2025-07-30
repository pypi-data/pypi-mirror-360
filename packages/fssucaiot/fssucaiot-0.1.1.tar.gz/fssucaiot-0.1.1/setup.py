from setuptools import setup, find_packages

setup(
    name="fssucaiot",  # 模块名
    version="0.1.1",  # 初始版本
    description="一个适用于教学的语音控制物联网模块，支持VOSK语音识别和MQTT控制",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="你的名字",
    author_email="307262079@qq.com",
    url="https://github.com/yourname/fssucaiot",  # 若有GitHub项目地址
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "vosk",
        "numpy",
        "sounddevice",
        "scipy",
        "paho-mqtt",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.7',
)
