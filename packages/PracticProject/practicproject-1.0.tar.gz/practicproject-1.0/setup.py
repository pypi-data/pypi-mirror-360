from setuptools import setup, find_packages


def readme():
  with open('README.md', 'r') as f:
    return f.read()


setup(
  name='PracticProject',
  version='1.0',
  author='Maxitot',
  author_email='maximkafom6@gmail.com',
  description='Addition, subtraction and comparison of numbers.',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/Maxitot/PracticProject',
  packages=find_packages(),
  install_requires=['requests>=2.25.1'],
  classifiers=[
    'Programming Language :: Python :: 3.11',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='files speedfiles ',
  project_urls={
    'GitHub': 'https://github.com/Maxitot/PracticProject'
  },
  python_requires='>=3.6'
)