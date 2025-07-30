from setuptools import setup, find_packages

setup(
    name="wdg-kombu-sdk",
    version="0.1.0",
    description="Reusable Kombu-based publisher/consumer SDK for Django projects.",
    long_description=open("README.md").read() if __import__('os').path.exists('README.md') else "",
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/wdg-kombu-sdk",
    packages=find_packages(),
    install_requires=[
        "kombu>=5.0.0",
        "Django>=3.2",
    ],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
