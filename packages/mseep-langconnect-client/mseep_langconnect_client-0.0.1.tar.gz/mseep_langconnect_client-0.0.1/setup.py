from setuptools import setup, find_packages

setup(
    name='mseep-langconnect-client',
    version='0.0.1',
    description='LangConnect Client: GUI interface for managing knowledge bases and connected to RAG service',
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
    install_requires=['fastapi>=0.115.6', 'langchain>=0.3.20', 'langchain-openai>=0.3.7', 'langchain-community>=0.0.20', 'langchain-core>=0.2.37', 'langchain-text-splitters>=0.0.1', 'langchain-postgres>=0.0.2', 'langgraph-sdk>=0.1.48', 'python-dotenv>=1.0.1', 'uvicorn>=0.34.0', 'aiohttp>=3.11.13', 'python-multipart>=0.0.20', 'httpx>=0.28.1', 'beautifulsoup4>=4.12.3', 'pdfminer.six>=20231228', 'pdfplumber>=0.11.0', 'asyncpg>=0.30.0', 'psycopg[binary]>=3.2.6', 'pillow>=11.2.1', 'pdfminer.six>=20250416', 'lxml>=5.4.0', 'unstructured[docx]>=0.17.2', 'python-docx>=1.1.0', 'supabase>=2.15.1', 'requests>=2.31.0', 'pandas>=2.2.0', 'fastmcp>=0.1.0', 'email-validator>=2.1.0'],
    keywords=['mseep'],
)
