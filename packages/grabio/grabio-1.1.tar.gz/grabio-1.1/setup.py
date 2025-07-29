from setuptools import setup, find_packages

setup(
    name='grabio',
    version='1.1',
    description='Website information extractor library',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Ahmed Saoud',
    author_email='ahmedsaoud0work@gmail.com',
    url='https://github.com/xr-xr4/grabio',
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
        'user_agent',
        'python-whois'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
