from setuptools import setup, find_packages

setup(
    name="yt-chap",
    version="0.1.0",
    description="CLI tool to display YouTube chapters using yt-dlp",
    author="Mallik Mohammad Musaddiq",
    author_email="mallikmusaddiq1@gmail.com",
    url="https://github.com/mallikmusaddiq1/yt-chap",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "yt-chap=yt_chap.cli:main"
        ]
    },
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
)