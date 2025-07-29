from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='pypocketutils',
    version='0.1.1',
    author='Prathiksha J',
    author_email='your.email@example.com',
    description='A beginner-friendly utility module with handy math, string, and list functions',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/prathikshaj1203/handyutils',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Education',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.6',
)
