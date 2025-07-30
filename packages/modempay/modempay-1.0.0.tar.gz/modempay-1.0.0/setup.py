from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as readme_file:
    long_description = readme_file.read()

setup(
    name="modempay",
    version="1.0.0",
    description="A Python SDK for integrating with the Modem Pay payment gateway, enabling seamless payment processing and financial services in your applications.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Caleb Okpara",
    author_email="info@modempay.com",
    url="https://modempay.com",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.8",
    keywords="payment gateway modem pay fintech api sdk",
    project_urls={
        "Documentation": "https://docs.modempay.com",
    },
)
