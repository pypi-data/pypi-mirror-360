"""Setup script for talem_ai_cli package."""

import pathlib  # C0411: Move standard library import before third-party imports
from setuptools import setup, find_packages  # C0411

# Get the long description from the README file
here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name='talem_ai_cli',
    version='0.1.0',
    author='Hemit Patel',
    author_email='hemitvpatel@gmail.com',
    description='Administrative tool for RAG apps',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/hemit99123/talem-ai-cli',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.8',
    install_requires=[
        'click',
        'aiofiles',
        'PyPDF2',
        'pypdf',
        'pyfiglet',
        'langchain',
        'langchain-community',
        'langchain-astradb',
        'langchain-huggingface',
        'bs4',
        'reportlab'
    ],
    entry_points={
        'console_scripts': [
            'talemai=main.__init__:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
