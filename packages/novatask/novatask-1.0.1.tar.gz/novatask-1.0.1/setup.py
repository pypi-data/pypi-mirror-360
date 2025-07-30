from setuptools import setup, find_packages

setup(
    name='novatask',
    version='1.0.1',
    author='Neel Bhadani',
    author_email='bhadanin123@gmail.com',
    description='Database-agnostic CRUD + AI decision library',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/NeelBhadani/novatask',
    packages=find_packages(),
    install_requires=[
        'pymongo',
        'tensorflow',
        'numpy',
        'matplotlib'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.7',
)
