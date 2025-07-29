# -*- coding: utf-8 -*-

import setuptools

try:
    with io.open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "A package for MS Graph connectivity and email sending"

setuptools.setup(
    name="onedevcommonmsgraph", # Replace with your own username
    version="1.0.0",
    author="Marcus Simas",
    author_email="marcus.simas@ufly.com.br",
    description="Conectividade com envio de e-mail",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="", # não tem ainda
    packages=setuptools.find_packages(),
    install_requires=[
       
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)