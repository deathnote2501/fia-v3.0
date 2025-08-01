"""
Setup script for FIA v3.0 Railway deployment
This ensures proper dependency management for Railway/Nixpacks builds
"""

from setuptools import setup, find_packages

setup(
    name="fia-v3",
    version="0.1.0",
    description="FIA v3.0 - AI-powered e-learning platform",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "sqlalchemy>=2.0.0",
        "alembic>=1.12.0",
        "psycopg2-binary>=2.9.0",
        "asyncpg>=0.29.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "python-multipart>=0.0.6",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "fastapi-users[sqlalchemy]>=12.1.0",
        "google-generativeai>=0.3.0",
        "python-dotenv>=1.0.0",
        "structlog>=23.2.0",
        "httpx>=0.25.0",
        "aiohttp>=3.9.0",
        "aiofiles>=23.0.0",
        "google-cloud-aiplatform>=1.71.1",
        "vertexai>=1.71.1",
        "websockets>=12.0",
        "openai>=1.98.0",
        "google-genai>=1.27.0",
        "google-cloud-texttospeech>=2.27.0",
    ],
)