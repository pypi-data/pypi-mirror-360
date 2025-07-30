from setuptools import setup, find_packages

setup(
    name='mseep-notebookllama',
    version='0.2.0.post1',
    description='An OSS and LlamaCloud-backed alternative to NotebookLM',
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
    install_requires=['audioop-lts>=0.2.1', 'elevenlabs>=2.5.0', 'fastmcp>=2.9.2', 'ffprobe>=0.5', 'llama-cloud>=0.1.29', 'llama-cloud-services>=0.6.38', 'llama-index-core>=0.12.44', 'llama-index-embeddings-openai>=0.3.1', 'llama-index-indices-managed-llama-cloud>=0.6.11', 'llama-index-llms-openai>=0.4.7', 'llama-index-observability-otel>=0.1.1', 'llama-index-tools-mcp>=0.2.5', 'llama-index-workflows>=1.0.1', 'mypy>=1.16.1', 'opentelemetry-exporter-otlp-proto-http>=1.34.1', 'plotly>=6.2.0', 'pre-commit>=4.2.0', 'psycopg2-binary>=2.9.10', 'pydub>=0.25.1', 'pytest>=8.4.1', 'pytest-asyncio>=1.0.0', 'python-dotenv>=1.1.1', 'pyvis>=0.3.2', 'streamlit>=1.46.1'],
    keywords=['mseep'],
)
