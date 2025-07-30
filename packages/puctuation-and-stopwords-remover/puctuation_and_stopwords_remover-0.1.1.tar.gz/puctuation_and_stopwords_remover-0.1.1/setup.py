from setuptools import setup, find_packages
setup(
    name='puctuation_and_stopwords_remover',
    version='0.1.1',
    author='Muhammad Wajahat Hussain',
    author_email='rajawajahat@example.com',
    description='A Python package for data cleaning process of NLP tasks, specifically for removing punctuation and stopwords.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/RMWajahat/tpsc',
    packages=find_packages(),
    install_requires=[
        'nltk',
    ],
    python_requires='>=3.6',
)