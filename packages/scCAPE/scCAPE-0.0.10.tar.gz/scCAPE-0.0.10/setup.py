from distutils.core import setup
from setuptools import find_packages

with open("README.md", "r") as f:
  long_description = f.read()

setup(name='scCAPE',  # 包名
      version='0.0.10',  # 版本号
      description='Inference of heterogeneous perturbation effects in single cell CRISPR screening data',
      long_description=long_description,
      # long_description_content_type="text/markdown",
      author='ZichuFu',
      author_email='1779404540@qq.com',
      #url='',
      # license='BSD License',
      packages=find_packages(),
      platforms=["all"],
      classifiers=[
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Natural Language :: Chinese (Simplified)',
          'Programming Language :: Python'
      ],
      install_requires=[                 
            "torch", "scanpy", 
            "econml","scikit-learn",
            "scipy","scib","statsmodels"],
      )