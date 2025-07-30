from distutils.core import setup
setup(
  name = 'pbhstat',
  packages = ['pbhstat'],
  version = '0.0.2',
  license='MIT',
  description = 'A Python code for calculating the primordial black hole mass function and abundance.',
  author = 'Philippa Cole and Jacopo Fumagalli',
  author_email = 'philippa.cole@unimib.it',
  url = 'https://github.com/pipcole/pbhstat',
  download_url = 'https://github.com/pipcole/pbhstat/archive/refs/tags/v.0.0.2.tar.gz',
  keywords = ['PBH', 'abundance', 'mass function'],
  install_requires=[            # I get to this in a second
          'numpy',
          'scipy',
          'matplotlib',
          'tqdm',
      ],
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package

    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',

    'License :: OSI Approved :: MIT License',   # Again, pick a license

    'Programming Language :: Python :: 3.9',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3.12',
  ],
)