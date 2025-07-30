from setuptools import setup, find_packages

setup(
    name='FlaskFloodgate',
    version='1.1.3',
    packages=find_packages(),
    description='A small customizable package to rate-limit your Flask endpoints.',
    author='Evscion',
    author_email='ivoscev@gmail.com',
    url='https://github.com/Evscion/FlaskFloodgate',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Flask",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.6',
)
