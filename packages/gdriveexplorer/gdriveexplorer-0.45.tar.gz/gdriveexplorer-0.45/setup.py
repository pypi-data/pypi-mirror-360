from distutils.core import setup
setup(
  name='gdriveexplorer',         # How you named your package folder (MyLib)
  packages=['gdriveexplorer'],   # Chose the same as "name"
  version='0.45',      # Start with a small number and increase it with every change you make
  license='GPLv3+',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description='Class to help managing google drive files',   # Give a short description about your library
  author='Sunep',                   # Type in your name
  author_email='soporte.gdriveexplorer@gmail.com',      # Type in your E-Mail
  url='https://github.com/sunep12/gdriveexplorer',   # Provide either the link to your gitHub or to your website
  download_url='https://github.com/sunep12/gdriveexplorer/archive/refs/tags/v_045.tar.gz',
   install_requires=[            # I get to this in a second
          'PyDrive2',
          'google.colab',
          'oauth2client',
          'google-api-python-client',
          'pandas',
          'dill',
          'polars',
          'httplib2'
      ],
)
