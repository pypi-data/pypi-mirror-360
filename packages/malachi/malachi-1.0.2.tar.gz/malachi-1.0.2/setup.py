from setuptools import setup, find_packages

setup(
    name="malachi",
    version="1.0.2",
    author="Tarmica Chiwara",
    author_email="tarimicac@gmail.com",
    description="A Python module for Windows 10 toast notifications",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/lordskyzw/malachi",
    packages=find_packages(),
    install_requires=[
        "pywin32"
    ],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.6",
)
