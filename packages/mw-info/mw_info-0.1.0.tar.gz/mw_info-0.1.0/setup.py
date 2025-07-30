from setuptools import setup, find_packages

setup(
    name="mw-info",
    version="0.1.0",
    description="Malawi Information Library (Districts, Currency, Agriculture, Health, Demographics)",
    author="Tuntufye Mwanyongo",
    author_email="tuntumwanyongo@gmail.com",
    url="https://github.com/Tuntufye4/mw-info", 
    packages=find_packages(),    
    include_package_data=True,  
    install_requires=[
        "PyYAML",
    ],       
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
  