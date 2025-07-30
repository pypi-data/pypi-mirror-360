# setup.py
from setuptools import setup, find_packages

setup(
    name='asanak_web_call_client',
    version='0.0.0',
    description='Asanak Web Call client for making and managing calls via REST API',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Farzad Forouzanfar',
    author_email='forouzanfar2000f@gmail.com',
    url='https://github.com/Asanak-Team/python-web-call-client',
    packages=find_packages(),
    install_requires=[
        'requests>=2.25',
    ],
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
