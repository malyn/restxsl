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
reStructuredText roles provided by the restxsl module.

@author: Michael Alyn Miller <malyn@strangeGizmo.com>
@copyright: 2006 by Michael Alyn Miller
@license: BSD License (see source code for full license)
"""


# ######################################################################
# IMPORTS
#

# Python imports.
import re

# xmlsoft imports.
import libxml2

# Docutils imports.
import docutils.nodes

# restxsl imports.
import uniquote



# ######################################################################
# Additional reStructuredText node types.
#

class XmlFragment(docutils.nodes.Element):
    """
    docutils node that stores a libxml2 document.
    """

    def __init__(self, doc):
        # Initialize the superclass.
        docutils.nodes.Element.__init__(self)

        # Store the XML document.
        self.doc = doc


class XpathReference(docutils.nodes.Element):
    """
    docutils node that stores an unresolved reference to the target of
    an XPATH expression.
    """

    def __init__(self, xpath):
        # Initialize the superclass.
        docutils.nodes.Element.__init__(self)

        # Store the XPATH reference.
        self.xpath = xpath



# ######################################################################
# RestXmlDocument class.
#

class RestXmlDocument(docutils.nodes.GenericNodeVisitor):
    """
    XML version of a reStructuredText document tree.  This object
    accepts a reStructuredText document tree and parses it into a
    libxml2 xmlDoc tree.  The result can then be output using libxml2,
    fed through a libxslt stylesheet, etc.

    @ivar doc: The XML document that was created when the given
        reStructuredText document tree was parsed.
    @type doc: L{libxml2.xmlDoc}
    """

    # ----------------------------------
    # Constructor and destructor.
    #

    def __init__(self, document, smartPunctuation=True):
        """
        Construct a RestXmlDocument from the given reStructuredText
        document tree.  Quotes, dashes, and ellipses in the document can
        optionally be transformed into their smart-and-curly Unicode
        counterparts.

        @param document: The reStructuredText document tree; usually
            obtained by calling L{docutils.core.publish_doctree}.
            Although this will almost always be a
            L{docutils.nodes.document} object, RestXmlDocument can
            actually accept any L{docutils.nodes.Node} object and will
            parse that into an XML tree.  This might be useful if you
            only want to parse a specific section of the docutils
            document.
        @type document: L{docutils.nodes.Node} or one of its subclasses
        @param smartPunctuation: C{True} to convert quotes, dashes, and
            ellipses to their smart (and curly) Unicode counterparts;
            C{False} to leave the punctuation alone.
        @type smartPunctuation: C{bool}
        """

        # Initialize the superclass.
        docutils.nodes.GenericNodeVisitor.__init__(self, document)

        # Initialize our attributes.
        self.xslTemplate = None
        self._smartPunctuation = smartPunctuation

        # Create the XML document.
        self.doc = libxml2.newDoc('1.0')


        # Create our node stack and initialize the root element flag.
        self.__nodeStack = []
        self.__haveRootElement = False

        # Walk through the reStructuredText document tree and use it to
        # populate our XML document.
        document.walkabout(self)


    def __del__(self):
        # Free the XML document.
        self.doc.freeDoc()


    # ----------------------------------
    # NodeVisitor methods.
    #

    def visit_field(self, node):
        # Store the contents of 'xsl-template' fields.
        fieldNameIdx = node.first_child_matching_class(
            docutils.nodes.field_name)
        if fieldNameIdx is not None \
                and node[fieldNameIdx].astext() == 'xsl-template':
            fieldBodyIdx = node.first_child_matching_class(
                docutils.nodes.field_body)
            if fieldBodyIdx is not None:
                self.xslTemplate = node[fieldBodyIdx].astext()

        # All fields, including 'xsl-template' fields, go to the
        # default handler.
        self.default_visit(node)


    def visit_system_message(self, node):
        # Suppress all system message elements and their children.
        raise docutils.nodes.SkipChildren()

    def depart_system_message(self, node):
        # Nothing to do here, but we do not want the default handler to
        # be called since we did not modify the node stack.
        pass


    def visit_XmlFragment(self, node):
        # Copy the XML fragment into the output tree.
        xmlNode = node.doc.getRootElement().docCopyNode(self.doc, 1)
        self.__nodeStack[-1][0].addChild(xmlNode)

    def depart_XmlFragment(self, node):
        # Free the XML fragment.
        node.doc.freeDoc()


    def visit_XpathReference(self, node):
        # Add a pyxslt-xpath-reference node as a child of the last node
        # on the stack.  No need to push this new node on the stack,
        # because we know that it is a leaf node in the docutils tree.
        xmlNode = self.__nodeStack[-1][0].newChild(
            None, 'pyxslt-xpath-reference', node.xpath)

    def depart_XpathReference(self, node):
        # Nothing to do here, but we cannot use the default handler
        # since XpathReference is an application-specific node type.
        # GenericNodeVisitor will throw an exception if it sees such a
        # thing.
        pass


    def visit_Text(self, node):
        # Get the text.
        text = unicode(node.astext())

        # If the user requested smart punctuation, and if the previous
        # node is not a raw node, then we run this text through uniquote
        # to convert basic punctuation to 'smart' punctuation.
        if self._smartPunctuation and not self.__nodeStack[-1][1]:
            text = uniquote.transformDashes(text)
            text = uniquote.transformEllipses(text)
            text = uniquote.transformQuotes(text)

        # Preserve whitespace if requested to do so.
        if self.__nodeStack[-1][2]:
            # Encode spaces as non-breaking spaces (to ensure that the
            # browser does not collapse runs of spaces or wrap long
            # lines).
            text = re.sub(r' ', u'\N{NO-BREAK SPACE}', text)

            # Encode hyphens as non-breaking hyphens (to ensure that the
            # browser does not wrap long lines).
            text = re.sub(r'-', u'\N{NON-BREAKING HYPHEN}', text)

            # Output the remaining text on a line-by-line basis.  Do not
            # output the last line; let the addContent line at the end
            # of this method take care of that line.
            for line in text.split('\n')[:-1]:
                # Output this line.
                self.__nodeStack[-1][0].addContent(line.encode('UTF-8'))

                # Output the br node.
                self.__nodeStack[-1][0].newChild(None, 'br', None)

            # Leave the last line alone.
            text = text.split('\n')[-1]

        # Add the text to the last node on the stack.
        self.__nodeStack[-1][0].addContent(text.encode('UTF-8'))

    def depart_Text(self, node):
        # Nothing to do here.  But, since we do not push text nodes onto
        # the stack, we have to override the depart_* method so that the
        # default_departure() method doesn't try and pop the
        # (non-existent) text node from the stack.
        pass


    def visit_literal(self, node):
        self.default_visit(node, True)

    def visit_literal_block(self, node):
        self.default_visit(node, True, True)

    def visit_option_string(self, node):
        # option_string elements often include double-dashes (--) as a
        # prefix, which we do not want to process with uniquote.
        self.default_visit(node, True)

    def visit_raw(self, node):
        self.default_visit(node, True)


    def default_visit(self, node, isRaw=False, preserveWhitespace=False):
        # Create the root element if necessary, otherwise just add this
        # node as a child of the last node on the stack.
        if not self.__haveRootElement:
            # Create the root node and add it to the document.
            xmlNode = libxml2.newNode(node.tagname)
            self.doc.setRootElement(xmlNode)
            self.__haveRootElement = True
        else:
            # Add the node as a child of the last node on the stack.
            xmlNode = self.__nodeStack[-1][0].newChild(None, node.tagname, None)

        # Add the docutils attributes to the XML node.
        for name, value in node.attlist():
            if type(value) == list:
                values = [docutils.nodes.serial_escape('%s' % v) for v in value]
                xmlNode.newProp(name, ' '.join(values))
            else:
                xmlNode.newProp(name, str(value))

        # Push the node onto the node stack.
        self.__nodeStack.append((xmlNode, isRaw, preserveWhitespace))

    def default_departure(self, node):
        # Remove the node from the node stack.
        self.__nodeStack.pop()
