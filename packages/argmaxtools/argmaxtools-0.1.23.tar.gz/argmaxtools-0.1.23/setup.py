from setuptools import setup, find_packages

from argmaxtools._version import __version__

with open('README.md') as f:
    readme = f.read()

setup(
    name='argmaxtools',
    version=__version__,
    url='https://github.com/argmaxinc/argmaxtools',
    description="Argmax Model Optimization Toolkit",
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Argmax, Inc.',
    install_requires=[
        "beartype",
        "coremltools>=8.1",
        "jaxtyping",
        "scikit-learn",
        "torch",
        "wandb",
        "tabulate",
        "huggingface-hub",
    ],
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development",
    ],
)
