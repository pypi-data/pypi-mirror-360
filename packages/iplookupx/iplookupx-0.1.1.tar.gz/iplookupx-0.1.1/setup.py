from setuptools import setup, find_packages

setup(
    name="iplookupx",  # Name of your package
    version="0.1.1",  # Initial version
    install_requires=[
        "requests",
        # "UnicodeDammit",  # Remove if it's incorrectly added
    ],
    author="Ramesh Chandra",
    author_email="rameshsofter@gmail.com",
    description="A Python package to fetch public and local IP information, and to make HTTP requests with proxy support, including HTML content fetching via requests or Selenium.",
    long_description=open('README.md').read(),  # Optional: include a README
    long_description_content_type="text/markdown",
    packages=find_packages(),  # This will find all the packages in your project
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
