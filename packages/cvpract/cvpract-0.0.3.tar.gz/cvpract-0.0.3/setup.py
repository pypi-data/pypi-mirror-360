from setuptools import setup, find_packages

setup(
    name='cvpract',
    version='0.1.3',
    author="Arman",
    description="A package for computer visualaization",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        # Add dependencies here.
        # e.g. 'numpy>=1.11.1'
    ],
    lisence = "MIT",
)