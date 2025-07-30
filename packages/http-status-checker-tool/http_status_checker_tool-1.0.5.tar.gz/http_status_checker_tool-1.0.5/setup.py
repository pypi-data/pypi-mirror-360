from setuptools import setup, find_packages

setup(
    name='http-status-checker-tool',
    author='Qazi Arsalan Shah',
    description='Basic - Fast, concurrent CLI tool to check HTTP status codes of provided URLs',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/qazi112/http-status-checker',
    project_urls={
        'Source': 'https://github.com/qazi112/http-status-checker',
        'Tracker': 'https://github.com/qazi112/http-status-checker/issues'
        },
    install_requires=[
        'requests>=2.25.1',
        'colorama>=0.4.6',
    ],
    entry_points={
        'console_scripts': [
            'status-check=status_checker.cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7'
)
