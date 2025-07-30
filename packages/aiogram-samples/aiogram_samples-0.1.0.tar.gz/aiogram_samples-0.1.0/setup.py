from setuptools import setup, find_packages

setup(
    name="aiogram_samples",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "aiogram_samples = aiogram_samples.cli:main"
        ],
    },
    author="Lump",
    author_email="igropritegatel11@gmail.com",
    description="Генератор шаблонов для aiogram обработчиков",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ваш-репозиторий",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)


# happy birthday