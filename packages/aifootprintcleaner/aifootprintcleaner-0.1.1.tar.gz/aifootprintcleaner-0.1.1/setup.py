from setuptools import setup, find_packages

setup(
    name="aifootprintcleaner",
    version="0.1.1",
    author="Adriano A. Santos",
    author_email="adriano@copin.ufcg.edu.br",
    description="Removes invisible Unicode characters, control codes, and non-printable artifacts commonly introduced by AI assistants like ChatGPT, Copilot, and others.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",
    ],
)
