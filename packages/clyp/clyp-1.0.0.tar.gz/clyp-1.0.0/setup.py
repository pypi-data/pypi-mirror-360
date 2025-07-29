from setuptools import setup
import typeguard
from typing import List
from pathlib import Path

# Package is in ./clyp directory


@typeguard.typechecked
def get_requirements() -> List[str]:
    """
    Reads the requirements.txt file and returns a list of unique package names,
    excluding version specifiers, comments, empty lines, and non-package arguments.
    """
    import re
    
    requirements_file = Path('requirements.txt')
    if not requirements_file.exists():
        return []
    
    try:
        with open(requirements_file, 'r', encoding='utf-8') as file:
            lines = file.read().splitlines()
    except (IOError, UnicodeDecodeError):
        return []
    
    requirements = []
    for line in lines:
        # Skip empty lines and comments
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        # Remove inline comments
        line = line.split('#')[0].strip()
        if not line:
            continue
            
        # Skip pip arguments
        if line.startswith('-'):
            continue
            
        # Extract package name (remove version specifiers)
        package_name = re.split(r'[=<>~!]+', line)[0].strip()
        if package_name:
            requirements.append(package_name)
    
    # Return unique requirements while preserving order
    return list(dict.fromkeys(requirements))

# Read the README file for the long description
long_description = Path('README.md').read_text(encoding='utf-8')

print(f"Using requirements: {get_requirements()}")
setup(
    name='clyp',
    version='1.0.0',
    author='CodeSoft',
    packages=['clyp'],
    install_requires=get_requirements(),
    license='MIT',
    description='Clyp is a programming language that transpiles to Python.',
    url='https://codesoft.is-a.dev/clyp',
    project_urls={
        'Source': 'https://github.com/clyplang/clyp',
    },
    entry_points={
        'console_scripts': [
            'clyp=clyp.cli:main',
        ],
    },
    long_description=long_description,
    long_description_content_type='text/markdown',
)