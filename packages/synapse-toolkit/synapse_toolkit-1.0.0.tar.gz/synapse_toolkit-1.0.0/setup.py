from setuptools import setup, find_packages

# Read the contents of README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(

    name='synapse-toolkit', 

    version='1.0.0',
    
    author='Kalan Jarvis-Loewen',
    
    description='A modular Man-in-the-Middle (MitM) toolkit for network analysis.',
    
    long_description=long_description,
    long_description_content_type='text/markdown',
    
    url='https://github.com/kalandjl/SYNapse',
    
    packages=find_packages(),
    
    install_requires=[
        'scapy',
        'NetfilterQueue ; platform_system=="Linux"',
    ],

    entry_points={
        'console_scripts': [
            'syn-apse = syn_apse.cli:main',
        ],
    },
    
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Security',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    
    python_requires='>=3.8',
)