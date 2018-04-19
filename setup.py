from setuptools import setup, find_packages

setup(
  name='tools',
  version='0.0.1',
  license='MIT',
  packages=find_packages(),
  platforms='any',
  zip_safe=False,
  include_package_data=True,
  author='none',
  author_email='none@null',
  description='pushid',
  entry_points = {
    'console_scripts': [
      'tools = tools:push_id'
    ]
  }
)


