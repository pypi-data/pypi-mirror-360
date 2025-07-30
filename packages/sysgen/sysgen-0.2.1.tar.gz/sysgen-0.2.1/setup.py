from setuptools import setup, find_packages

setup(
    name="sysgen",  
    version="0.2.1",
    author="Adhishtanaka",
    author_email="kulasoooriyaa@gmail.com",
    description="SysGen - High-quality synthetic datasets creating tool using Gemini API",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/adhishtanaka/sysgen",  
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "google-genai>=1.5.0",
        "sentence-transformers>=5.0.0",
        "scikit-learn>=1.7.0",
        "tiktoken>=0.5.0",
        "torch>=2.0.0",
        "transformers>=4.30.0",
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "tf-keras"
    ],
    entry_points={
        "console_scripts": [
            "sysgen=sysgen.cli:main",  
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    keywords="ai machine-learning dataset generation gemini synthetic-data qa-generation",
    project_urls={
        "Bug Reports": "https://github.com/adhishtanaka/sysgen/issues",
        "Source": "https://github.com/adhishtanaka/sysgen",
        "Documentation": "https://github.com/adhishtanaka/sysgen#readme",
    },
)