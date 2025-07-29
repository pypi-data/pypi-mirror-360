from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="orm_core",
    version="0.0.3",
    author="Erik Soloviev",
    author_email="eriksoloviev@gmail.com",
    description="ORM Core Library for FastAPI and SQLAlchemy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ErJokeCode/orm_core",
    packages=find_packages(),
    install_requires=[
        'pydantic>=2.11.4',
        'fastapi>=0.115.12',
        'SQLAlchemy>=2.0.41',
        'asyncpg==0.30.0'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
    package_data={"orm_core": ["py.typed"]},
    license="MIT",
    keywords="sqlalchemy fastapi orm pydantic",
)
