from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='SyloraQ',
    version='2.8',
    packages=find_packages(),
    install_requires=[],
    author='SyloraQ',
    author_email='syloraq.official@gmail.com',
    description='SyloraQ Python Module One Step Ahead',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/SyloraQ/SyloraQ',
    classifiers=[  
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
    ],
)
