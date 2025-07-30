from setuptools import setup

setup(
    name="comodityapi",
    version="0.3.0",
    description="Python SDK for the APIFreaks Commodity API",
    author="Muhammad Moeer",
    author_email="moeer3505@gmail.com",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=["comodityapi"],         # 👈 this matches folder name
    install_requires=["requests"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    python_requires=">=3.7",
)