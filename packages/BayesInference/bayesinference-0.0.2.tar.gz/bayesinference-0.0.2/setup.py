import setuptools 

VERSION = '0.0.2' 

# Setting up
setuptools.setup(
        name="BayesInference", 
        version=VERSION,
        author="Sebastian Sosa",
        author_email="<s.sosa@live.fr>",
        description="GNU GENERAL PUBLIC LICENSE",
        long_description="Bayesian Inference (BI) software is available in both Python and R. It aims to unify the modeling experience by integrating an intuitive model-building syntax with the flexibility of low-level abstraction coding available but also pre-build function for high-level of abstraction and including hardware-accelerated computation for improved scalability.",
        packages=setuptools.find_packages(),
        install_requires=['jax[cuda12]', 'numpyro', 'pandas', 'seaborn', 'tensorflow_probability', 'arviz'],
        python_requires=">=3.9",
        keywords=['python', 'Bayesian inferences'],
        include_package_data=True,
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows"
        ],
        project_urls={
            "Homepage": "https://github.com/BGN-for-ASNA/BI",
            "Bug Tracker": "https://github.com/BGN-for-ASNA/BI/issues"
        }
)