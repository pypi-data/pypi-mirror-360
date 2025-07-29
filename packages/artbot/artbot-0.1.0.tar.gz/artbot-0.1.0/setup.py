from setuptools import setup, find_packages

setup(
    name="artbot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "requests",
        "beautifulsoup4",
        "pillow",
    ],
    entry_points={
        "console_scripts": [
            "artbot=artbot.api:endpoint",
        ],
    },
    author="GambeyNoa/MathieuPhilippe",
    description="Un convertisseur d'images vers ASCII à partir d'URLs Unsplash",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.8',
)
