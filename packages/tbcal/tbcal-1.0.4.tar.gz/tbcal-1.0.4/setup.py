from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='tbcal',
    version='1.0.4',
    packages=find_packages(),
    install_requires=[
        'numpy',
    ],
    author='ShiyinJia',
    author_email='ShiyinJia@foxmail.com',
    description='A package for tight-binding calculations',
    url='https://github.com/Jia-Shiyin/TB_model_calculation',  
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)


