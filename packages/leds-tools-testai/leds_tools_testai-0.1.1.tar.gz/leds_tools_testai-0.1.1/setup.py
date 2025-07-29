import setuptools
#apagar o dist toda vez que subir uma nova versão
setuptools.setup(
    name="leds-tools-testai",
    version="0.1.1", #Sempre modificar a versão quando houver mudanças significativas
    description="Ferramentas de testes de BDD usando ia",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Davi Alvarenga",
    author_email="davialvarenga@hotmial.com.br",
    url="https://github.com/DaviAlvarenga01/leds-tools-testai.git",
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "crewai",
        "crewai[tools]",
        "fastapi",
        "uvicorn",
        "uuid",             
        "entrypoints==0.3",
    ],
    
     extras_require={
        "tests": [
            "pytest",
            "pytest-cov",
        ],
    },
    
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
