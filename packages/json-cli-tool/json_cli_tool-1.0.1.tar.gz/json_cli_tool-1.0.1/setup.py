from setuptools import setup, find_packages

setup(
    name='json-cli-tool',
    author='Qazi Arsalan Shah',
    description='A CLI tool to beautify, validate, and minify JSON data.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/qazi112/json-validator',
    project_urls={
        'Source': 'https://github.com/qazi112/json-validator',
        'Tracker': 'https://github.com/qazi112/json-validator/issues',
    },
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pyperclip>=1.8',
        'rich>=13.0',
    ],
    entry_points={
        'console_scripts': [
            'json-cli=json_cli.cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
