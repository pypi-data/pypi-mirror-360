from setuptools import setup, find_packages

setup(
    name='numira',  # 替换为你的包名
    version='0.1.0',
    packages=find_packages(where='src'),  # 指定代码目录
    package_dir={'': 'src'},  # 指定包的根目录
    description='A toolbox for math experimentation',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='ZT_Production',
    author_email='zhenting37@gmail.com',
    url='https://github.com/ZT-devinci/numira',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)