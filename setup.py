from setuptools import setup, find_packages

with open('README.md') as fh:
    readme = fh.read()

with open('requirements.txt') as fh:
    requirements = fh.read().strip().splitlines()

setup(
    name='courtbot-pycore',
    version='0.0.1a1',
    author='Eric L. Truitte',
    author_email='etruitte@privateerconsulting.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Legal Industry',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
    description='A hub for allowing mutliple jurisdictions to integrate their court case search with the ability for interested parties to Opt-In to receiving case hearing reminders.',
    long_description=readme,
    long_description_content_type='text/markdown',
    #install_requires=requirements,
    packages=find_packages(),
    license='LICENSE.txt',
    python_requires='>=3.8',
    scripts=[],
    url='http://pypi.python.org/pypi/courtbot-pycore/',
)
