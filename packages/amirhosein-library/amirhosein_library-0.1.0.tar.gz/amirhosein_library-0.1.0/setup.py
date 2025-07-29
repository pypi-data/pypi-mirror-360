from setuptools import setup, find_packages

setup(
    name="amirhosein_library",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'emoji>=2.0.0',
    ],
    description="A simple library management system.",
    long_description="",
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
