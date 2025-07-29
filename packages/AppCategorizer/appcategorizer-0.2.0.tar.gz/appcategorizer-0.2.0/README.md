# AppCategorizer

A Library which you give yout the category for Software applications.

## Description

AppCategorizer is a Python package that get the application name as an input and provide you AI application categorization. It fetches application data from multiple sources including Snapcraft, Flathub, Apple Store, GOG, Itch.io, and, MyAbandonware, then uses Artificial Intelligence to provide most suitable Category.
## Features

- **Multi-source Data Fetching**: Gathers application information from 5+ different sources
- **Intelligent Tag Normalization**: Cleans and standardizes tags from various sources
- **Categorization**: Categorize the Application using NLP technique
- **Command Line Interface**: Simple CLI for quick energy assessments
- **Python API**: Programmatic access for integration into other projects

## Installation

```bash
pip install AppCategorizer
```
## Quick Start
Command Line Usage
bash# Single word applications

```bash 
AppCategorizer Facebook
# Output: Social Networking

# Multi-word applications
AppCategorizer 'Google Chrome'
# Output: Web Browser

```

## Python API Usage
```bash
from appcategorizer import fetch_category
category = fetch_category("Firefox")
print(category) 
```