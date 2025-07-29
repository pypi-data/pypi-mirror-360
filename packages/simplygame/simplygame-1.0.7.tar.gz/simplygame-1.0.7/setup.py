from setuptools import setup, find_packages

setup(
    name="simplygame",
    version="1.0.7",  # convention : X.Y.Z
    author="CEDZEE",
    author_email="cedzee.contact@gmail.com",
    url="https://github.com/cedzeedev/simplygame",
    description="A package to create games more easily",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",  # nécessaire pour Markdown
    packages=find_packages(),
    install_requires=[
        "pygame"
    ],
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # modifie si tu as une autre licence
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment",
        "Intended Audience :: Developers",
    ],
)
