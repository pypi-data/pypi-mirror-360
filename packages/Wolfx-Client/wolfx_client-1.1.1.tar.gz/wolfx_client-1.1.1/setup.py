from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='Wolfx_Client',
    version='1.1.1',
    description='A WebSocket client for WolfX',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/aic-6301/wolfx_client',
    author='AIC_6301',
    author_email='hello@aisii.net',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.12',
        'Framework :: AsyncIO',
    ],
    packages=['wolfx_client', 'wolfx_client.types'],
    install_requires=[
        'websockets',
        'asyncio',
    ],
)
