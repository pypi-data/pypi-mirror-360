from setuptools import setup, find_packages

setup(
    name="isro-helpbot",
    version="1.0.0",
    description="AI-based Help Bot for Information Retrieval from MOSDAC using a Knowledge Graph",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),  # now it will auto-include core
    include_package_data=True,
    install_requires=[
        "streamlit",
        "spacy",
        "networkx",
        "pyvis",
        "pandas",
        "scikit-learn",
        "openpyxl",
        "python-docx",
        "PyPDF2",
    ],
    entry_points={
        "console_scripts": [
            "isro_helpbot = isro_helpbot.cli:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Streamlit",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
