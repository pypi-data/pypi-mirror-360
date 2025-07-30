from setuptools import setup
import os

this_directory = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "Molecular activity prediction using transformer neural networks with multiple implementation modes"

setup(
    name="molactivity",
    version="3.0",
    author="Dr. Jiang at BTBU",
    author_email="yale2011@163.com",
    description="Molecular activity prediction using transformer neural networks with 5 operational modes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NATSCREEN/molactivity",
    packages=['molactivity'],
    
    include_package_data=True,
    package_data={
        'molactivity': [
            '*.dict', '*.md', '*.txt', '*.json', '*.safetensors',
            'D8_pretrained_parameters/*'
        ],
    },
    
    # Base requirements (Standard Mode - A series)
    install_requires=[],
    
    # Optional dependencies for different modes
    extras_require={
        # Fast Mode (B series) 
        'fast': [
            'numpy>=1.21.0',
        ],
        
        # Rocket Mode (C series)
        'rocket': [
            'torch>=1.9.0',
            'numpy>=1.21.0',
        ],
        
        # Image Mode (D series)
        'image': [
            'torch>=1.9.0',
            'torchvision>=0.10.0',
            'numpy>=1.21.0',
            'pillow>=8.0.0',
        ],
        
        # Tools (E series)
        'tools': [
            'numpy>=1.21.0',
            'matplotlib>=3.3.0',
            'pandas>=1.3.0',
            'rdkit-pypi>=2022.09.1', 
        ],
        
        'chem': [
            'rdkit-pypi>=2022.09.1',
            'pandas>=1.3.0',
            'numpy>=1.21.0',
        ],
        
        'all': [
            'torch>=1.9.0',
            'torchvision>=0.10.0',
            'numpy>=1.21.0',
            'matplotlib>=3.3.0',
            'pandas>=1.3.0',
            'pillow>=8.0.0',
            'rdkit-pypi>=2022.09.1',
            'scipy>=1.7.0',
        ],
        
        'dev': [
            'pytest>=6.0.0',
            'pytest-cov>=2.10.0',
            'black>=21.0.0',
            'flake8>=3.8.0',
            'sphinx>=4.0.0',
            'sphinx-rtd-theme>=0.5.0',
        ],
    },
    
    entry_points={
        'console_scripts': [
            'molactivity-train-standard=molactivity.A28_train:training',
            'molactivity-predict-standard=molactivity.A21_predict:main',
            'molactivity-train-fast=molactivity.B17_train:training',
            'molactivity-predict-fast=molactivity.B10_predict:main',
            'molactivity-train-rocket=molactivity.C2_train:training',
            'molactivity-train-image=molactivity.D5_train:main',
            'molactivity-predict-image=molactivity.D4_predict:main',
            'molactivity-structure-analysis=molactivity.E1_structure_analysis:main',
            'molactivity-smiles-to-images=molactivity.E2_smiles_to_images:main',
            'molactivity-molecular-mass=molactivity.E3_molecular_mass:main',
        ],
    },
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Environment :: Console",
        "Natural Language :: English",
    ],
    
    python_requires=">=3.8",
    
    project_urls={
        "Homepage": "https://github.com/NATSCREEN/molactivity",
        "Source": "https://github.com/NATSCREEN/molactivity",
        "Bug Tracker": "https://github.com/NATSCREEN/molactivity/issues",
        "Documentation": "https://github.com/NATSCREEN/molactivity/blob/main/README.md",
        "Changelog": "https://github.com/NATSCREEN/molactivity/releases",
    },
    
    license="MIT",
    
    keywords=[
        "molecular-activity", "machine-learning", "transformer", "neural-networks", 
        "natural-products", "drug-discovery", "cheminformatics", "bioinformatics",
        "SMILES", "molecular-modeling", "deep-learning", "pharmaceutical",
        "chemical-analysis", "molecular-descriptors", "QSAR", "drug-development"
    ],
    
    zip_safe=False,
    
    platforms=["any"],
) 