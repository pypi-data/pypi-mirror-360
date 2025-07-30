from setuptools import setup, find_packages

setup(
    name="kuka",
    version="0.3.1.3",
    author="tenoriolms",
    description="Library for EDA, data modeling, and ML modeling analysis/interpretation",
    long_description='',#open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/tenoriolms/kuka_lib",
    packages=find_packages(),
    install_requires=[
        'numpy', 
        'pandas', 
        'matplotlib',
        'scipy',
        'scikit-learn',
        'graphviz',
        'optuna',
        'pathlib',
        ],  
    classifiers=[
        'Development Status :: 3 - Alpha',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    include_package_data=True, #For include text .txt files
)