from distutils.core import setup
setup(
  name = 'pyknmi',
  packages = ['pyknmi'],
  version = '0.1.0',
  license='MIT',
  description = 'Python Wrapper for KNMI Weather data', 
  author = 'Erik YOIUR LAST NAME',
  author_email = 'YOUR EMAIL',
  url = 'https://github.com/dutch-erik/pyknmi',
  keywords = ['knmi', 'Python', 'Meteoserver'],
  install_requires=[
          'aiohttp',
      ],
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers', 
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
)