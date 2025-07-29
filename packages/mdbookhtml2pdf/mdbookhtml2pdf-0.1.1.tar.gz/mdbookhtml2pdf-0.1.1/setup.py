from setuptools import setup, find_packages

setup(
    name="mdbookhtml2pdf",
    version="0.1.1",
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        "beautifulsoup4>=4.9.3",
        "weasyprint>=52.5",
        "Pygments>=2.10.0",
    ],
    entry_points={
        "console_scripts": [
            "mdbookhtml2pdf=mdbookhtml2pdf.mdbookhtml2pdf:main",
        ],
    },
    author="min",
    author_email="testmin@outlook.com",
    description="Convert mdBook HTML to PDF with TOC, code highlighting and mermaid diagrams",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://gitee.com/jakHall/mdbookhtml2pdf.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)