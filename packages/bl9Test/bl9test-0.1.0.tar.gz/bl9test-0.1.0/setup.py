from setuptools import setup, find_packages

setup(
    name="bl9Test",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'bl9Test=bl9Test.cli:main',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple test CLI tool",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/bl9Test",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)