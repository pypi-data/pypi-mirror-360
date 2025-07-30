from setuptools import setup, find_packages

setup(
    name='bcitoolbox',  
    version='0.1.0.4',         
    author='evans.zhu',
    author_email='evanszhu2001@gmail.com',
    description='A zero-programming package for Bayesian causal inference model',
    long_description='BCI Toolbox is a Python implementation of the hierarchical Bayesian Causal Inference (BCI) model for multisensory research. BCI model is a statistical framework for understanding the causal relationships between sensory inputs and prior expectations of a common cause, which can account for human perception in a number of tasks, including temporal numerosity judgment (Shams et al., 2005; Wozny et al., 2008), spatial localization judgment (Körding et al., 2007; Wozny & Shams, 2011), size-weight illusion paradigm (Peters et al., 2016), rubber-hand illusion paradigm (Chancel et al., 2022; Chancel & Ehrsson, 2023).',
    long_description_content_type='text/markdown',
    packages=['bcitoolbox'],
    package_data={'bcitoolbox': ['images/*']},
    install_requires=['numpy', 'matplotlib', 'scipy','pandas','scikit-learn', 'pyvbmc','requests'],  
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
