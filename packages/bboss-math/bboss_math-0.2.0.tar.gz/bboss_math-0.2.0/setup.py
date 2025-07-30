from setuptools import setup, find_packages

setup(
    name='bboss-math',          # 库名
    version='0.2.0',            # 版本号
    author='bboss',
    author_email='your.email@example.com',
    description='A short description of your bboss library',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/my_library',  # 项目主页
    packages=find_packages(),   # 自动发现所有包
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)