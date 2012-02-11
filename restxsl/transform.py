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
Transforms reStructuredText files into XML files (XHTML, usually) using
XSL stylesheets.
"""


# Python imports.
import cStringIO
import os
import sys

# Docutils imports.
import docutils.core

# xmlsoft imports.
import libxml2

# restxsl imports.
import loader
import restxmldoc
import xslt

# restxsl directives and roles.
import directives
import roles



# ######################################################################
# restxsl Exceptions.
#

class RestException(Exception):
    """Raised when an error is found while parsing the reST document."""
    pass

class InvalidXpathExpression(Exception):
    """Exception raised when an invalid XPATH expression is given to the
    xpath role."""
    pass



# ######################################################################
# restxsl function.
#

def restxsl(
        restPath,
        smartPunctuation=False,
        extModule=None, extModuleCookie=None,
        encoding='ASCII',
        xslBasePath=None,
        xslPath=None, xslParams=None):
    """
    Transform reStructuredText to XML using an XSL stylesheet.

    @param restPath: The path to the reStructuredText file to transform.
    @type restPath: C{str}
    @param smartPunctuation: C{True} to convert quotes, dashes, and
        ellipses to their smart (and curly) Unicode counterparts;
        C{False} to leave the punctuation alone.
    @type smartPunctuation: C{bool}
    @param extModule: The Python module that contains the extension
        functions used by the C{pyxslt} directive.
    @type extModule: C{module}
    @param extModuleCookie: The Python object (or list, string, dict,
        etc.) that will be passed to the methods called by the C{pyxslt}
        directive.  This can be used to pass state from the code that
        calls the C{restxsl} method to the code in the extension module.
    @type extModuleCookie: C{object}
    @param encoding: The character encoding to use when outputting the
        final XML document.  Values such as C{UTF-8}, C{ISO-8859-1},
        C{ASCII}, etc. are appropriate.
    @type encoding: C{str}
    @param xslBasePath: The path to prepend to absolute stylesheet
        references.
    @type xslBasePath: C{str}
    @param xslPath: The path to the XSL file that should be used to
        transform the reStructuredText document, or C{None} to use the
        stylesheet specified in the document's (C{:xsl-template:}
        field).
    @type xslPath: C{str} containing the path to an XSL stylesheet.
    @param xslParams: Parameters to pass to the XSL stylesheet.
    @type xslParams: C{dict}
    @return: A list of C{(filename, XML text)} tuples, one for each
        result document.  There will normally be only a single document,
        but in the case of a multi-instance call to the L{pyxslt}
        directive, there will be multiple result documents.  Note that
        the C{filename} portion of the tuple will always be C{None} in
        the single-document case.
    @rtype: C{list} of C{(filename, XML text)} tuples
    """

    # Create the settings_override dictionary so that we can get
    # docutils warnings.
    warnings = cStringIO.StringIO()
    settingsOverrides = {
        'report_level': 0,
        'warning_stream': warnings,
    }

    # Create the docutils SettingsSpec used to pass information to our
    # extension modules.
    settingsSpec = docutils.SettingsSpec()
    settingsSpec.settings_spec = (
        None, None,
            (
                (None, ('--restxsl-ext-module', ), {}),
                (None, ('--restxsl-ext-module-cookie', ), {}),
                (None, ('--restxsl-multidoc', ), {}),
            ),
    )
    settingsSpec.settings_defaults = {
        'restxsl_ext_module': extModule,
        'restxsl_ext_module_cookie': extModuleCookie,
        'restxsl_multidoc': None,
    }

    # Parse the reStructuredText file into a reStructuredText document
    # tree.
    try:
        restDoc = docutils.core.publish_doctree(
            source_class=docutils.io.FileInput, source=None,
            source_path=restPath,
            settings_spec=settingsSpec, settings_overrides=settingsOverrides)
    except docutils.utils.SystemMessage, msg:
        raise RestException(msg)

    # Print out any warnings.
    # TODO Return these to the caller.
    warningsText = warnings.getvalue()
    if warningsText:
        sys.stderr.write(warningsText)

    # Turn the reStructuredText document tree into a reStructuredText
    # XML document.
    restXml = restxmldoc.RestXmlDocument(restDoc, smartPunctuation)


    # Use the document's stylesheet if the caller did not give us an
    # override stylesheet.
    if not xslPath:
        xslPath = restXml.xslTemplate

    # Initialize the entity loader if we were given a base path.
    if xslBasePath:
        entityLoader = loader.EntityLoader(
            xslBasePath, os.path.dirname(restPath))
        libxml2.setEntityLoader(entityLoader)

    # Load the XSL file.
    stylesheet = xslt.Stylesheet(xslPath)


    # Is this a multiple-instance document (multidoc)?  If so, we need
    # to process the file multiple times, one for each document
    # instance.  If not, just process the current document.
    resultDocuments = []
    if restDoc.settings.restxsl_multidoc:
        # Generate a document for each of the multidoc's children.
        for mdChildIndex, mdChild in enumerate(
                restXml.doc.xpathEval('//pyxslt[@multidoc="true"]/*')):
            # Get the name of the document using the multidoc XPATH
            # expression.
            filenameNode = restXml.doc.xpathEval(
                '//pyxslt[@multidoc="true"]/%s' % (
                    restDoc.settings.restxsl_multidoc))
            instanceFilename = filenameNode[mdChildIndex].getContent()

            # Make a copy of the original document.
            instanceDoc = libxml2.newDoc('1.0')
            xmlNode = restXml.doc.getRootElement().docCopyNode(instanceDoc, 1)
            instanceDoc.setRootElement(xmlNode)

            # Find the multidoc root.
            mdRoot = instanceDoc.doc.xpathEval('//pyxslt[@multidoc="true"]')[0]

            # Replace the multidoc element in the instance document with
            # a new 'pyxslt' node containing the current child.
            mdChildCopy = mdChild.docCopyNode(instanceDoc, 1)
            mdPythonNode = libxml2.newNode('pyxslt')
            mdPythonNode.addChild(mdChildCopy)
            mdRoot.replaceNode(mdPythonNode)

            # Process the copy of the document.
            xml = _restxsl(instanceDoc, stylesheet, xslParams, encoding)
            resultDocuments.append((instanceFilename, xml))

            # Free the instance document.
            instanceDoc.freeDoc()
    else:
        # Process the document.
        xml = _restxsl(restXml.doc, stylesheet, xslParams, encoding)
        resultDocuments.append((None, xml))

    # Free the stylesheet and parsed document.
    del stylesheet
    del restXml

    # Return the result document list.
    return resultDocuments


def _restxsl(xmlDoc, stylesheet, xslParams=None, encoding='ASCII'):
    # Resolve pyxslt XPATH references.
    for xmlNode in xmlDoc.xpathEval('//pyxslt-xpath-reference'):
        # Get the XPATH expression.
        xpath = origXpath = xmlNode.getContent()

        # Prepend the ``//pyxslt/`` root to relative XPATH expressions.
        if xpath[0] != '/':
            xpath = '//pyxslt/' + xpath

        # Look up this reference.
        targetNode = xmlDoc.xpathEval(xpath)
        if not targetNode:
            raise InvalidXpathExpression, origXpath

        # Replace the XPATH reference with the contents of the found
        # node.
        newTextNode = libxml2.newText(targetNode[0].getContent())
        xmlNode.replaceNode(newTextNode)


    # Apply the stylesheet to the reStructuredText XML document.
    out = stylesheet.apply(xmlDoc, xslParams)

    # Get the contents of the XML file.
    xml = out.serialize(encoding=encoding)

    # Free the transformed document.
    out.freeDoc()


    # Return the XML text.
    return xml
