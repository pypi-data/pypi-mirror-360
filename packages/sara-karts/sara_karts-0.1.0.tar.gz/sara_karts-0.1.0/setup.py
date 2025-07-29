from setuptools import setup, find_packages

setup(
    name='sara-karts',
    version='0.1.0',
    author='Karthick Anandh RJ',
    author_email='karthickanandh1304@gmail.com',
    description='Sara - An AI-powered code generator assistant',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/sara',  # Replace with your GitHub repo
    packages=find_packages(),
    install_requires=[
        'pydantic>=2.0,<3.0'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)