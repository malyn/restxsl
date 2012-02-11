#!/usr/bin/env python

# Python imports.
import re
import sys

# Distutils imports.
from distutils.core import setup

# restxsl imports.
import restxsl


# Set the distribution name.
NAME = 'restxsl'

# Get the metadata from the restxsl package.
VERSION = str(restxsl.__version__)
(AUTHOR, EMAIL) = re.match('^(.*?)\s*<(.*)>$', restxsl.__author__).groups()
URL = restxsl.__url__
LICENSE = restxsl.__license__

# Patch distutils if it can't cope with the 'classifiers' or
# 'download_url' keywords.
from sys import version
if version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

# Set the long description.
long_description = """
restxsl transforms reStructuredText_ files into XML files using XSL
stylesheets.  Most users will output XHTML files, but any form of XML
file can be created.

Every aspect of the generated content and layout can be controlled.  A
sample XSL stylesheet is provided to get you going, but you can easily
create stylesheets to match any type of site design.

As an added bonus, restxsl can apply `SmartyPants-style`_ processing to
your reStructuredText files.  Quotes, dashes, and ellipses are all
educated automatically as part of the restxsl processing pipeline.  This
behavior is controlled by a parameter to restxsl and can be enabled and
disabled as desired.

.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _SmartyPants-style: http://daringfireball.net/projects/smartypants/
"""

# Configure distutils.
setup(name=NAME,
      version=VERSION,
      description='Transform reStructuredText into XML using XSL stylesheets.',
      long_description=long_description,
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Text Processing :: Markup :: XML',
      ],
      author=AUTHOR,
      author_email=EMAIL,
      license=LICENSE,
      url=URL,
      download_url='%s%s-%s.tar.gz' % (URL, NAME, VERSION),
      scripts=['scripts/restxsl'],
      packages=['restxsl'])
