from setuptools import setup, find_packages

setup(
    name='CSNAnalysis',
    version='0.6.0',
    py_modules=['csnanalysis'],
    author='Alex Dickson',
    author_email='alexrd@msu.edu',
    description="Tools for creating, analyzing and visualizing Conformation Space Networks.",
    license="MIT",
    url="https://github.com/ADicksonLab/CSNAnalysis",
    classifiers=[
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        'Programming Language :: Python :: 3'
    ],

    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'numpy',
        'networkx>=2.1',
        'scipy>=0.19',
    ],
)
