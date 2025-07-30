from setuptools import setup, find_packages

setup(
    name='mseep-borsa-mcp',
    version='0.7.0',
    description='A modular MCP Server for Borsa Istanbul (BIST) data using KAP and Yahoo Finance.',
    long_description="Package managed by MseeP.ai",
    long_description_content_type="text/plain",
    author='mseep',
    author_email='support@skydeck.ai',
    maintainer='mseep',
    maintainer_email='support@skydeck.ai',
    url='https://github.com/mseep',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=['fastmcp>=2.6.0', 'pydantic>=2.7.0', 'httpx>=0.27.0', 'pdfplumber>=0.11.0', 'beautifulsoup4>=4.12.3', 'lxml>=5.2.0', 'yfinance>=0.2.37', 'pandas>=2.0.0', 'markitdown>=0.1.1', 'openpyxl>=3.1.5', 'requests>=2.31.0'],
    keywords=['mseep'],
)
