from setuptools import setup, find_packages
from pathlib import Path

# Get the long description from the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='ultragpt',
    version='3.1.0',
    license="MIT",
    author='Ranit Bhowmick',
    author_email='bhowmickranitking@duck.com',
    description='UltraGPT: A modular library for advanced GPT-based reasoning and step pipelines',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages('src', include=["ultragpt", "ultragpt.*"]),
    package_dir={'': 'src'},
    url='https://github.com/Kawai-Senpai',
    install_requires=[
        'pydantic>=2.10.4',
        'openai>=1.59.3',
        'ultraprint>=3.2.0',
        'google-api-python-client>=2.0.0',
        'requests>=2.25.0',
        'beautifulsoup4>=4.9.0',
        'readability-lxml>=0.8.0',
        'lxml>=4.6.0'
    ],
    python_requires='>=3.6',
)
