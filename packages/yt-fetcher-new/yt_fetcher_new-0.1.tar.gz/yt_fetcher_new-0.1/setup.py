from setuptools import setup, find_packages

setup(
    name='yt-fetcher-new',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'yt-dlp'
    ],
    entry_points={
        'console_scripts': [
            'yt-fetcher = yt_fetcher.cli:main',
        ],
    },
    author='Om Dev Karki',
    author_email='omdevkarki@gmail.com',
    description='A simple CLI tool to download YouTube videos using yt-dlp.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
)
