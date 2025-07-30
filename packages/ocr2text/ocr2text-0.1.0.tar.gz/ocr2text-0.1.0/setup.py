# setup.py
from setuptools import setup, find_packages

setup(
    name='ocr2text',
    version='0.1.0',
    description='Convert scanned PDFs to text file using OCR',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Krishna',
    author_email='krishna857191@gmail.com',
    url='https://github.com/krishna525/free-ocr-pdf-maker',
    packages=find_packages(),
    install_requires=[
        'requests',
        'websocket-client'
    ],
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
)
