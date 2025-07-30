from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess

class CustomInstallCommand(install):
    def run(self):
        # Appel à la commande d'installation classique
        install.run(self)

        # Appel de ton script après l'installation
        subprocess.call(['bash', 'setup.sh'])

setup(
    name='autoomics',
    version='0.1.9',
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
    entry_points={
        'console_scripts': [
            'autoomics = autoomics.main:main',
        ],
    },
    cmdclass={'install': CustomInstallCommand},
)
