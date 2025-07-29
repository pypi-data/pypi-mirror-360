from setuptools import setup, find_packages

setup(
    name="geo-optimizer",
    version="1.0.2",
    author="MrPsyghost (Shivay)",
    author_email="shivaypuri2000@gmail.com",
    description="GEO: Genetic & Evolutionary Optimizer — A Neural Network Training framework.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    # url="https://github.com/MrPsyghost/geo",
    project_urls={
        "YouTube": "https://www.youtube.com/@MrPsyghost",
        # "Bug Tracker": "https://github.com/MrPsyghost/geo/issues",
        # "Documentation": "https://github.com/MrPsyghost/geo/wiki",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        # "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    install_requires=[
        "torch>=2.0.0",
        "matplotlib>=3.10.0",
        "rich>=13.0.0",
        "tqdm>=4.0.0",
        "halo>=0.0.3"
    ],
    python_requires=">=3.10",
    include_package_data=True,
    # license="MIT",
    keywords=[
        "neural networks",
        "evolution",
        "optimizer",
        "genetic algorithm",
        "deep learning",
        "pytorch",
        "neuroevolution",
        "geo"
    ],
)
