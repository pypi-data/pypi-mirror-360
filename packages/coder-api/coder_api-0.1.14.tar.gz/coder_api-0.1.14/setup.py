from setuptools import find_packages, setup

setup(
    name="coder-api",
    version="0.1.14",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    author="Lucas Tarsitano Garcia",
    author_email="lucas.garcia@smartflowsistemas.com.br",
    description="Python bindings for the Coder API",
    maintainer="Nathan Daniel Breier",
    maintainer_email="nathan.breier@smartflowsistemas.com.br",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://gitlab.smartflow.me/coder/api-coder",
    license="LGPLv3",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
)
