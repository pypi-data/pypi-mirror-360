from setuptools import setup, find_packages

setup(
    name="uspto-data",
    version="0.1.4.0",
    description="Structured Python datamodels and wrappers for accessing USPTO patent data APIs.",
    long_description="See README.md for usage and license terms.",
    long_description_content_type="text/markdown",
    author="ForGen AI, LLC",
    author_email="support@forgen.ai",
    url="https://forgen.ai",
    license="Proprietary",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4==4.13.4",
        "blinker==1.9.0",
        "certifi==2025.6.15",
        "charset-normalizer==3.4.2",
        "flask_requests==0.0.14",
        "idna==3.10",
        "pampy==0.3.0",
        "requests==2.32.4",
        "setuptools==80.9.0",
        "soupsieve==2.7",
        "typing_extensions==4.14.0",
        "urllib3==2.5.0"
    ],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
