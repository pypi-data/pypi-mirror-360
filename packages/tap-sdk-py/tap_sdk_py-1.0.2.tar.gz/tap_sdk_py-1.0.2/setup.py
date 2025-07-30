from setuptools import setup, find_packages

setup(
    name='tap-sdk-py',
    version='1.0.0',
    packages=find_packages(
        include=['zakotap', 'zakotap.*']
    ),
    install_requires=[
        "eventemitter>=0.2.0",
        "requests>=2.32.4",
        "websockets>=15.0.1",
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.11',
    ],
    author='ridanit_ruma',
    author_email='me@inizeno.com',
    description='Zako tap server sdk for python',
    url='https://github.com/zako-ac/tap-sdk-py',\
    license='MIT',
)
