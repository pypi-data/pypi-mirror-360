from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    description = f.read()

setup(
    name='make_otp',
    version='1.0.0',
    description='A simple Python library to generate numeric, alphabetic, or alphanumeric OTPs',
    author='Muhammed Aman S S',
    author_email='aman251104@gmail.com',
    packages=find_packages(),
    py_modules=['otp'],
    install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Security :: Cryptography',
    ],
    python_requires='>=3.1',
    long_description=description,
    long_description_content_type='text/markdown',
)
