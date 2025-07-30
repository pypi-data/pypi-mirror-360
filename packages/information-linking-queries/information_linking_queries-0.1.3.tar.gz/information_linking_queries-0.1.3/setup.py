from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='information-linking--queries',
    version='0.1.3',
    packages=find_packages(),
    long_description = long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        "requests",
        "SPARQLWrapper==2.0.0"
    ],
    author='Nikolas Kapralos',
    description='A library for enriching metadata through semantic queries. It performs API calls to Wikipedia, Wikidata, DBpedia, and ORCID to retrieve and integrate structured information from multiple open knowledge sources.',
    license_files = "LICENSE.txt",
    python_requires='>=3.11',
    project_urls={"GitHub": "https://github.com/Digital-Methods-for-Knowledge-Graphs/information-linking-queries-python-library"}

)