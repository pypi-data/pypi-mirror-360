from setuptools import setup, find_packages

setup(
    name='DecoderBot',
    version='1.0.2',
    packages=find_packages(),
    author='Unknown Decoder',
    description='A simple trainable chatbot using OOP in Python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
