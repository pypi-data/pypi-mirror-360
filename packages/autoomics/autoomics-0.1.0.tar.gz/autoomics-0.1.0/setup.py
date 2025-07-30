from setuptools import setup, find_packages

setup(
    name='autoomics',  # Nom de ton package
    version='0.1.0',     # Version du package
    packages=find_packages(),
    install_requires=open('requirements.txt').readlines(),
    author='Jordan BABADOUDOU',
    author_email='jordan.babadoudou@umontreal.ca',
    description='Un outil pour faire du multi-omique analyse (bulk seq, rnaseq, chip seq, atac seq)',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/TonNom/mon_package',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],

)
