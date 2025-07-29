from setuptools import setup, find_packages

setup(
    name="sigconv",
    version="0.1.0",
    author="AleirJDawn",
    author_email="",
    description="Convert binary signature patterns between spaced format, escaped format, and bytes+mask format used in reverse engineering and pattern scanning.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),   
    python_requires='>=3.6',
    url="https://github.com/zwalloc/sigconv", 
    install_requires=[
    ],
    entry_points={     
        'console_scripts': [
            'sigconv=sigconv.main:main', 
        ],
    },
    classifiers=[      
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)