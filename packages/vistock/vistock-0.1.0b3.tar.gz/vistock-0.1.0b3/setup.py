from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='vistock',
    version='0.1.0-beta.3',
    install_requires=requirements,
    include_package_data=True,
    packages=find_packages(exclude=['tests', 'tests.*']),
    author='Thang Duong',
    author_email="kaiismith.business@gmail.com",
    description='Vistock is an open-source library focused on searching, retrieving, and analyzing Vietnamese stock market data.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='Apache-2.0',
    keywords='stock, vietnamese, vietnam, financial data, stock market',
    python_requires='>=3.12',
    url='https://github.com/kaiismith/vistock',
    project_urls={
        'Bug Reports': 'https://github.com/kaiismith/vistock/issues',
        'Source': 'https://github.com/kaiismith/vistock',
        'Documentation': 'https://github.com/kaiismith/vistock#readme',
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Programming Language :: Python :: 3.15',
        'Topic :: Software Development :: Libraries',
        'Topic :: Office/Business :: Financial',
    ],
)