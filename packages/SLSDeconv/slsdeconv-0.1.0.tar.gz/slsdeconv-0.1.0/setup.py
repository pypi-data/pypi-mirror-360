from setuptools import setup, find_packages

setup(
    name="SLSDeconv",
    version="0.1.0",
    author="Yunlu Chen",
    author_email="yunluchencyl@gmail.com",
    description="Fast Spatial Transcriptomics Deconvolution",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/tinachentc/SLSDeconv",
    packages=find_packages(),
    install_requires=[
        "scanpy",
        "pandas",
        "numpy",
        "scipy",
        "matplotlib",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
)