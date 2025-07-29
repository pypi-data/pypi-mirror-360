from setuptools import setup, find_packages

setup(
    name='Vectoryx',
    version='0.1.1',
    author='Artem Kryachko',
    author_email='artemkryachko2007@email.com',
    description='A simple vector operations library',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ArtemK2007/Vectoryx',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
)
