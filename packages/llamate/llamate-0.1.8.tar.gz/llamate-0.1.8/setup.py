from setuptools import setup, find_packages

setup(
    name="llamate",
    version="0.1.0",
    description="A memory-augmented framework for LLMs",
    author="Andy Thompson",
    author_email="andy338@gmail.com",
    packages=find_packages(include=["llamate", "llamate.*"]),
    install_requires=[
        "openai>=1.0.0",
        "faiss-cpu",
        "numpy",
        "python-dotenv"
    ],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'llamate=llamate.cli:main',
        ],
    },
)
