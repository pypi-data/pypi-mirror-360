from setuptools import setup, find_packages
import os
# Dynamically read version from wedata/__init__.py
version = {}
with open(os.path.join(os.path.dirname(__file__), 'wedata', '__init__.py')) as f:
    exec(f.read(), version)

setup(
    name="wedata-automl",
    version=version["__version__"],
    packages=find_packages(include=['wedata', 'wedata.*']),
    python_requires='>=3.7',
    author="maxxhe",
    install_requires=[
        "h2o_pysparkling_3.5",
        "mlflow==2.17.2",
        "scikit-learn",
        "pandas",
        "h2o",
        "numpy<2.0",
        "flaml[automl,ts_forecast]",
        # flaml[spark] 除去pysaprk依赖，TODO 更新前检查开源版本是否有依赖更新https://github.com/microsoft/FLAML/blob/main/setup.py
        "joblibspark>=0.5.0",
        "joblib<=1.3.2",
        "optuna"
    ],
    description="AutoML wrapper with integrated MLflow logging, designed in the wedata style.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="Apache 2.0",
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)