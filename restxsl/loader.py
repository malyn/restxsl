# Copyright (c) 2006, Michael Alyn Miller <malyn@strangeGizmo.com>.
# All rights reserved.
# vi:ts=4:sw=4:et
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1.  Redistributions of source code must retain the above copyright
#     notice unmodified, this list of conditions, and the following
#     disclaimer.
# 2.  Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
# 3.  Neither the name of Michael Alyn Miller nor the names of the
#     contributors to this software may be used to endorse or promote
#     products derived from this software without specific prior written
#     permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.

"""
Provides an extendable libxml2 entity loader.

@author: Michael Alyn Miller <malyn@strangeGizmo.com>
@copyright: 2006 by Michael Alyn Miller
@license: BSD License (see source code for full license)
"""


# ######################################################################
# IMPORTS
#

# Python imports.
import os



# ######################################################################
# EntityLoader class.
#

class EntityLoader(object):
    """
    libxml2 callback that applies a base path to all absolute stylesheet
    references.  This callback is used by libxml2 when an XSL include or
    import directive is encountered.

    Subclasses can extend this class and override loadFile() if they
    wish to load XSL files from other locations (a database, for
    example).
    """

    # ----------------------------------
    # Constructor and destructor.
    #

    def __init__(self, basePath, relPath):
        """
        Initialize the EntityLoader with the base and relative paths
        that will be used to locate stylesheets.

        @param basePath: The base path that should be used for absolute
            stylesheet references.
        @type basePath: C{str}
        @param relPath: The path that should be used for relative
            stylesheet references.
        @type relPath: C{str}
        """

        # Store the base path and relative path.
        self.__basePath = basePath
        self.__relPath = relPath


    # ----------------------------------
    # EntityLoader methods.
    #

    def loadFile(self, path):
        """
        Load the XSL file with the given path.

        @param path: The path to the XSL file that need to be loaded.
            This path is taken straight from the XSL file and may be
            relative, absolute, or even a URL>
        @type path: C{str}
        @return: The contents of the XSL file, or C{None} if the file
            was not found.
        @rtype: C{str}
        """

        # Create the path the file based on the type of incoming
        # reference (relative or absolute).
        if os.path.isabs(path):
            # Anchor the absolute path at our base path, stripping the
            # initial separator from the incoming path so that we can
            # join() it.
            filePath = os.path.join(self.__basePath, path[1:])
        else:
            # Anchor the relative path, then normalize it.
            filePath = os.path.normpath(os.path.join(self.__relPath, path))

        # Try to open the file.
        try:
            return open(filePath, 'r')
        except IOError:
            # Couldn't find the file; let libxml2 have a go at it.
            return None;


    # ----------------------------------
    # Magic methods.
    #

    def __call__(self, url, id, ctx):
        """libxml2 entity loader callback."""
        return self.loadFile(url)
