import setuptools

with open("README.md", "r") as f:
    description = f.read()

setuptools.setup(
    name="AppCategorizer",
    version="0.2.1",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "beautifulsoup4==4.13.4",
        "pandas==2.3.0",
        "Requests==2.32.4",
        "selenium==4.33.0",
        "transformers==4.52.4"
    ],
    entry_points={
        "console_scripts": [
            "AppCategorizer=AppCategorizer.main:fetch_category",
        ],
    },
    long_description=description,
    long_description_content_type="text/markdown"
)