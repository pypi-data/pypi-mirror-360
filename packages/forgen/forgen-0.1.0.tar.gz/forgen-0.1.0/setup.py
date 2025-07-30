from setuptools import setup, find_packages

setup(
    name="forgen",
    version="0.1.0",
    packages=find_packages(),
    license="Proprietary",
    classifiers=[
        "License :: Other/Proprietary License",
    ],
    install_requires=[
        "boto3>=1.35,<2.0",
        "requests>=2.32,<3.0",
        "chardet>=5.2,<6.0",
        "docx2txt>=0.9,<1.0",
        "pandas>=2.2,<3.0",
        "pytesseract>=0.3.13,<1.0",
        "pypdf>=4.3,<5.0",
        "beautifulsoup4>=4.12,<5.0",
        "striprtf>=0.0.29,<1.0",
        "pillow>=11.1,<12.0",
        "reportlab>=4.3,<5.0",
        "pdf2image>=1.17,<2.0",
        "python-dotenv>=1.0,<2.0",
        "openai>=1.73,<2.0",
        "feedparser>=6.0,<7.0",
        "tiktoken>=0.8,<1.0",
        "setuptools>=75.8,<76.0",
        "pypandoc>=1.15,<2.0",
        "langchain-text-splitters>=0.3,<1.0"
    ],
    include_package_data=True,
    zip_safe=False,
)
