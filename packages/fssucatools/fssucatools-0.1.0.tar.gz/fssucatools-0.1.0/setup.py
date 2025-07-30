from setuptools import setup, find_packages

setup(
    name='fssucatools',                      # 模块名称
    version='0.1.0',                         # 初始版本号
    author='你的名字',
    author_email='307262079@qq.com',
    description='简易录音工具模块，适合Tkinter教学使用',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'sounddevice',
        'scipy'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: Microsoft :: Windows',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Education',
        'Topic :: Multimedia :: Sound/Audio :: Capture/Recording'
    ],
    python_requires='>=3.10',
)
