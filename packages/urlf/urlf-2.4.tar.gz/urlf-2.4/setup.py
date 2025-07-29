from setuptools import setup, find_packages

setup(
    name="urlf",  # This will be the PyPI package name
    version="2.4",
    author="0xBobby",
    author_email="rule-entry-0d@icloud.com",  # Optional but recommended
    description="URL deduplication and normalization tool based on domain and parameter names",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Boopath1/urlF",
    packages=find_packages(),
    py_modules=["urlf"],  # Assuming your script is named urlf.py
    entry_points={
        "console_scripts": [
            "urlf = urlf:main"
        ]
    },
    include_package_data=True,
    install_requires=[
        "colorlog>=6.0.0",
        "tqdm>=4.60.0",
        "colorama>=0.4.4",
        "pyfiglet>=0.8.post1"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
)