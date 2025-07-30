from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open("README.md", "r") as f:
    long_description = f.read()

setup(name='onboard_client',
      version='1.15.0',
      author='Nathan Merritt, John Vines',
      author_email='support@onboarddata.io',
      description='Onboard API SDK',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/onboard-data/client-py',
      packages=['onboard.client'],
      install_requires=requirements,
      package_data={
          'onboard.client': ['py.typed'],
      },
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Programming Language :: Python :: 3.12',
          'Programming Language :: Python :: 3.13',
          'Topic :: Scientific/Engineering :: Information Analysis',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      python_requires='>=3.8',
      )
