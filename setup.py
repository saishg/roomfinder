from setuptools import setup, find_packages

setup(name='roomfinder',
      author='Saish Gersappa',
      author_email='sgersapp@cisco.com',
      version='0.9',
      packages=find_packages(),
      install_requires = [
            'argparse',
            'flask',
            'gunicorn',
          ]
     )
