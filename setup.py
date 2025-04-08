from setuptools import setup, find_packages

setup(
    name="trivo-ai",
    version="1.0.0",
    description="Sistema de Formulación Inteligente de Masas",
    author="TRIVO-AI Team",
    author_email="info@trivo-ai.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask==2.2.3",
        "pandas==1.5.3",
        "numpy==1.24.2",
        "scikit-learn==1.2.2",
        "matplotlib==3.7.1",
        "pytest==7.3.1",
        "python-dotenv==1.0.0",
        "requests==2.28.2",
        "gunicorn==20.1.0",
        "nltk==3.8.1"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "trivo-ai=app.app:main"
        ]
    }
) 