from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="model-manage-client",
    version="0.0.1.7",
    author="Model-Manager",
    author_email="hello@advantech.ai",
    description="A package for interacting with the Model management Service-API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/model-management",
    license="MIT",
    packages=["model_manage_client"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=["requests"],
    keywords="model management nlp ai language-processing",
    include_package_data=True,
)
