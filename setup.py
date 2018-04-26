from setuptools import setup, find_packages

setup(
  name='python-tools',
  version='0.0.5',
  license='MIT',
  packages=find_packages(),
  platforms='any',
  zip_safe=False,
  include_package_data=True,
  author='Eduard Generalov',
  author_email='eduard@generalov.net',
  description='Some tools for python (sites parsing)',
  entry_points = {
    'console_scripts': [
      'tools = tools:push_id',
      'mqrecive = tools:cmd_mqrecive'
    ]
  }
)


