from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='patchmind',
    version='0.1.4',
    packages=find_packages(exclude=('tests',)),
    install_requires=[
        'GitPython',
        'jinja2',
        'pyyaml',
        'pytest',
        'rich'
    ],
    entry_points={
        'console_scripts': [
            'patchmind=cli.main:main',
        ],
    },
    author='Your Name or DOA',
    description='AI-powered Git patch assistant with HTML report generation.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/your-user/patchmind',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
