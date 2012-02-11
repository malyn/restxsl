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
Wraps libxslt stylesheet objects to provide auto-deletion of the
underlying L{libxslt.stylesheet} class.

@author: Michael Alyn Miller <malyn@strangeGizmo.com>
@copyright: 2006 by Michael Alyn Miller
@license: BSD License (see source code for full license)
"""


# ######################################################################
# IMPORTS
#

# xmlsoft imports.
import libxml2
import libxslt



# ######################################################################
# Stylesheet exceptions.
#

class StylesheetException(Exception):
    """Exception raised when an XSL stylesheet cannot be parsed."""
    pass



# ######################################################################
# Stylesheet class.
#

class Stylesheet(object):
    """Wrapper around a libxslt stylesheet."""

    # ----------------------------------
    # Constructor and destructor.
    #

    def __init__(self, xslPath):
        """
        Construct a Stylesheet object given the path to an XSL
        stylesheet.

        @param xslPath: Path to the XSL file.
        @type xslPath: C{str}
        @raise StylesheetException: If an error occurs while parsing the
            stylesheet.
        """

        # Parse the XSL file into an XML document.
        self.__doc = libxml2.parseFile(xslPath)

        # Now parse the stylesheet.
        self.__stylesheet = libxslt.parseStylesheetDoc(self.__doc)

        # Throw an exception if we were unable to parse the stylesheet.
        if not self.__stylesheet:
            raise StylesheetException, 'Error parsing stylesheet.'

    def __del__(self):
        # Free the stylesheet.  This will also take care of freeing the
        # underlying XML document.
        try:
            self.__stylesheet.freeStylesheet()
        except:
            pass


    # ----------------------------------
    # Stylesheet methods.
    #

    def apply(self, doc, params):
        """
        Apply this stylesheet to the given libxml2 xmlDoc object.

        @param doc: The XML document.
        @type doc: L{libxml2.xmlDoc}
        @param params: Stylesheet parameters.
        @type params: C{dict}
        @return: The transformed XML document.
        @rtype: L{libxml2.xmlDoc}
        """

        return self.__stylesheet.applyStylesheet(doc, params)
