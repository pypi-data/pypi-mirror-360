import setuptools


setuptools.setup(
    name="cuttly-service",
    version="0.0.1",
    author="selviler",
    author_email="slvler@proton.me",
    description="cuttyl service api wrapper",
    url="https://github.com/selviler/cuttly-service",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9.6',
    install_requires=["feedparser>=6.0.0", "future>=0.18.3", "pywebview>=4.0.1"]
)