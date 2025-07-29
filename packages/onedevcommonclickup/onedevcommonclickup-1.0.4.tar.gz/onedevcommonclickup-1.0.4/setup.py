import io
import setuptools

try:
    with io.open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "A package for connectivity with ClickUp"

setuptools.setup(
    name="onedevcommonclickup", # Replace with your own username
    version="1.0.2",
    author="Giovani Moreira",
    author_email="giovani.moreira@ufly.com.br",
    description="Conectividade com ClickUp",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="", # não tem ainda
    packages=setuptools.find_packages(),
    install_requires=[
       
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)