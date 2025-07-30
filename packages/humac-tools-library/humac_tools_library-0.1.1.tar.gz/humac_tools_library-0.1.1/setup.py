from setuptools import setup, find_packages

setup(
    name='humac_tools_library',
    version='0.1.1',
    author='somanath',
    author_email='shindesomanath111@gamil.com',
    description='A simple Python library with correlation, seasonality ,optimzedGecode,graphExplainer,detectAnomalies  plus advanced data analysis tools.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/humacpspl/humac_tools_library.git',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'sqlalchemy==2.0.37',
        'statsmodels==0.14.4',
        'scipy==1.15.3',
        'pytest==8.3.5',
        'python-dotenv==1.0.1',
        'pyjwt==2.10.1',
        'matplotlib==3.10.3',
        'rapidfuzz==3.13.0',
        'scikit-learn==1.6.1',
        'pandas',
        'numpy',
    ],
)
