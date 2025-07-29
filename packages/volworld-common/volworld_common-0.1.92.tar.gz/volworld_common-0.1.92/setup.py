from setuptools import setup, find_packages


setup(
    name='volworld_common',
    version='0.1.92',
    license='MIT',
    author="Che-Wri, Chang",
    author_email='gobidesert.mf@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='',
    keywords='volsite',
    install_requires=[
          'aenum',
      ],
)
