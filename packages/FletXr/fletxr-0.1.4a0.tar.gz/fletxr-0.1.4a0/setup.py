from setuptools import find_packages, setup

# LOADING DOCUMENTATION
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name = 'FletX',
    version = '0.1.0',
    packages = find_packages(),
    install_requires = [
        'httpx',
        'colorlog',
        'flet-core>=0.24.1',
        'flet[all]>=0.28.3',
        'pydantic>=2.11.5',
        'logging>=0.4.9.6',
        'typing-extensions',
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    author = '#Einswilli',
    author_email = 'einswilligoeh@email.com',
    description = 'The GetX-inspired Python Framework for Building Reactive, Cross-Platform Apps with Flet',
    url = 'https://github.com/AllDotPy/FletX.git',
)