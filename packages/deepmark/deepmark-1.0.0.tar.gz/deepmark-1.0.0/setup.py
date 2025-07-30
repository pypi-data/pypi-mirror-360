from setuptools import setup, find_packages

setup(
    name='deepmark',
    version='1.0.0',
    description='deepmark: Model-agnostic, robust, and compliance-ready text watermarking library for LLMs and content platforms.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your@email.com',
    url='https://github.com/yourusername/deepmark',
    packages=find_packages(),
    install_requires=[
        'spacy',
        'nltk',
        'cryptography',
        'click',
        'pydantic',
        'requests',
        'numpy',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.7',
) 