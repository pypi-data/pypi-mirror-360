from setuptools import setup, find_packages

setup(
    name='fssucatools2',  # 模块名
    version='0.1.0',  # 初始版本号
    packages=find_packages(),
    install_requires=[
        'numpy',
        'sounddevice',
        'scipy',
        'vosk',
        'pyttsx3',
        'requests'
    ],
    python_requires='>=3.10',
    author='你的名字',
    author_email='your_email@example.com',
    description='简化版语音助手工具模块，支持录音、本地识别、DeepSeek API调用与TTS朗读',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    url='https://github.com/你的用户名/fssucatools2',  # 可选
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License'
    ],
)
