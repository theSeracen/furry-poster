from distutils.core import setup

setup(name = 'furryposter',
	  version='0.2',
	  description='Tool for distributing stories to several different furry websites from the command-line',
	  author='Seracen',
	  packages = ['furryposter'],
	  install_requires=['requests',
					 'bs4',
					 'tqdm'])