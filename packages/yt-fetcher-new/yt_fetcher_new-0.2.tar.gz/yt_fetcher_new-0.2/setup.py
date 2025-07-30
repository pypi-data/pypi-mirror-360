from setuptools import setup, find_packages
from pathlib import Path
this_directory = Path(__file__).parent
setup(
    name='yt-fetcher-new',
    version='0.2',
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
    long_description = (this_directory / "README.md").read_text(encoding='utf-8'),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
)
