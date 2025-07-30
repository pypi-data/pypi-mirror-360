from setuptools import setup, find_packages

setup(name="hhfactor",
	  version="1.3.10",
	  packages=find_packages(),
	  install_requires=["h5py",
						"tables"],
	  author="hh",
	  author_email="hehuang0717@outlook.com",
	  description="factor",
	  long_description=open('README.md').read(),
	  long_description_content_type="text/markdown",
	  url="https://your.project.url",
	  classifiers=["Programming Language :: Python :: 3", "License :: OSI Approved :: MIT License",
				   "Operating System :: OS Independent", ],
	  python_requires='>=3.12',
      package_data={
          'hhfactor': ['data/tradedate.json'],  # 在此指定数据文件
      })
