from setuptools import setup, find_packages

setup(
    name='phantom_cleaner',
    version='0.1.0',
    author='Arjun M',
    description='A lightweight data cleaning library for Python',
    packages=find_packages(),
    install_requires=[
        'pandas>=1.0.0',
        'numpy>=1.18.0',
        'scikit-learn>=0.22.0'
    ],
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/phantom_cleaner',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
