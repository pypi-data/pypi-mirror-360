from setuptools import setup, find_packages

setup(
    name="doxtract",
    version="0.0.3",
    author="Bhavesh Kumar",
    author_email="bhaveshk@gmail.com",
    description="Structured document processor with diagram/image/text extraction and dataset output",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/EthanRyne/Advanced_pdf_extractor",
    packages=find_packages(exclude=["tests", "examples"]),
    include_package_data=True,
    install_requires=[
        "PyMuPDF>=1.22.0",
        "tqdm>=4.60.0",
        "datasets>=2.0.0",
    ],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ]
)

