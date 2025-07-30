from setuptools import setup, find_packages

#Leer el contenido del archivo README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name = "gnotas",
    version = "0.1.0",
    packages=find_packages(),
    install_requires=[],
    author="Sir Pixel",
    description="Un gestor de notas simple",
    long_description=long_description,
    long_description_content_type="text/markdown",
        )
