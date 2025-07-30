from setuptools import setup, find_packages

setup(
    name="blackbox_logger",
    version="0.2.4",
    description="Framework-agnostic HTTP logger with payload masking",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Avinash Ranjan",
    author_email="avinashranjan633@gmail.com",
    url="https://github.com/avi9r/blackbox_logger",
    packages=find_packages(),
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
)
