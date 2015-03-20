from setuptools import setup

setup(name='gridftp_transfer_manager',
      version='0.1',
      description='Command line tools to automate file transfers using gridftp and Globus',
#      url='http://dionne.biz/projects/gridftp-transfer-manager',
      author='Jean-Philippe Dionne',
      author_email='jp@dionne.biz',
      license='MIT',
      packages=['gridftp_transfer_manager'],
      install_requires=[
          'argparse',
          'keyring',
          'globusonline-transfer-api-client',
          'm2crypto',
          'pycrypto',
      ],
      scripts=[
          'bin/myproxy-logon.py',
          'bin/globus-endpoint-activate.py'
      ],
      zip_safe=True)

