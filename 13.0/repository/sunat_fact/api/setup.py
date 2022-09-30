import setuptools
from sys import version

if version < '2.2.3':
	from distutils.dist import DistributionMetadata
	DistributionMetadata.classifiers = None
	DistributionMetadata.download_url = None
	
from distutils.core import setup


setuptools.setup(
    name='sunatservice',
    version='1.0.133',
    author='@rockscripts',
    author_email='rockscripts@gmail.com',
    description='SUNAT - sign and verify xml',
    long_description="Generate signatures for Sunat e-documents",
    install_requires=[
                        'lxml >= 4.2.5',
                        'xmlsec >= 1.3.3'
                     ],
    platforms='any',
    url='https://instagram.com/rockscripts/',
    packages=['sunatservice'],
    python_requires='>=2.7.*',
    classifiers=[
                    'License :: OSI Approved :: BSD License',
                    'Programming Language :: Python :: 3',
                    'Topic :: Software Development :: Libraries :: Python Modules',
                ],
)
