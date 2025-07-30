import pathlib

from setuptools import setup, find_namespace_packages

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / 'README.md').read_text(encoding='utf-8')

requirements_list = (here / 'requirements.txt').read_text(encoding='utf-8').split()

def get_version(rel_path):
    init_content = (here / rel_path).read_text(encoding='utf-8')
    for line in init_content.split('\n'):
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

setup(
    name='push_service',
    version=get_version("push_service/__init__.py"),
    packages=find_namespace_packages(include=['push_service', 'push_service.templates']),
    install_requires=requirements_list,  # Add dependencies from requirements.txt if needed
    entry_points={
        'console_scripts': [
            'push_service=push_service.cli:main',
        ],
    },
    include_package_data=True,
    description='A Python implementation of the Push API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Andrea Esuli',
    author_email='andrea@esuli.it',
    url='https://github.com/aesuli/push_service',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    license='BSD-3-Clause',
    python_requires='>=3.8',
)
