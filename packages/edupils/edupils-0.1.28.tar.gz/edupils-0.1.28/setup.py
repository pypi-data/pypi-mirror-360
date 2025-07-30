from setuptools import setup, find_packages

# Read the contents of your requirements.txt file
with open('requirements.txt') as f:
    required_packages = f.read().splitlines()

setup(
    name='edupils',
    version='0.1.28',
    author='Georges Spyrides',
    author_email='georgesmss@gmail.com',
    packages=find_packages(),
    install_requires=required_packages,
    url='https://github.com/georgesms/edupils',
    license='MIT',
    description='A collection of educational tools for Python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    keywords='python education highschool pyodide',
    # Additional metadata like description, url, etc.
)
