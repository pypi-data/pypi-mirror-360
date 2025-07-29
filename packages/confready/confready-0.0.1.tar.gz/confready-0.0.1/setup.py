from setuptools import setup, find_packages
from pathlib import Path

# Load README.md as long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="confready",
    version="0.0.1",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "confready": [
            "frontend/*",
            "frontend/**/*",
            "server/*",
            "server/**/*",
        ]
    },
    entry_points={
        "console_scripts": [
            'confready=confready.cli:main',
        ],
    },
    install_requires=[
        "flask",
        "flask_cors",
        "jupyterlab",  
        "llama-index",
        "llama-index-embeddings-together",
        "matplotlib",
        "openai",
        "pylatexenc",
        "python-dotenv"
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Michael Galarnyk, Rutwik Routu, Vidhyakshaya Kannan, Kosha Bheda, Prasun Banerjee, Agam Shah and Sudheer Chava",
    license="AGPL-3.0",
    url="https://github.com/gtfintechlab/ConfReady",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Intended Audience :: Science/Research",
    ],
    python_requires='>=3.8',
)
