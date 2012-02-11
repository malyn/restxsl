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
reStructuredText directives provided by the restxsl module.

@author: Michael Alyn Miller <malyn@strangeGizmo.com>
@copyright: 2006 by Michael Alyn Miller
@license: BSD License (see source code for full license)
"""


# ######################################################################
# IMPORTS
#

# Python imports.
import cStringIO
import os
import re
import sys

# Docutils imports.
import docutils.nodes
import docutils.parsers.rst

# restxsl imports.
import restxmldoc



# ######################################################################
# code-block directive.
#

def code_block_directive(name, arguments, options, content, lineno,
                         content_offset, block_text, state, state_machine):
    """
    Provides syntax highlighting for blocks of code.  It is used with
    the following syntax::
    
        .. code-block:: cpp
             
            #include <iostream>
            
            int main( int argc, char* argv[] )
            {
                std::cout << "Hello world" << std::endl;
            }
        
    The directive requires the name of a language supported by
    SilverCity as its only argument.  All code in the indented block
    following the directive will be colorized.

    The directive can also be told to include a source file directly::

        .. code-block::
             :language: Python
             :source-file: ../myfile.py

    You cannot both specify a source-file and include code directly.
    """

    # Get the language name.  Try the arguments first, then fall back to
    # the options.
    try:
        language = arguments[0]
    except IndexError:
        language = options['language']

    # The user cannot specify content and give us a source-file, they
    # must choose one or the other.
    if content and 'source-file' in options:
        error = state_machine.reporter.error(
            'Must specify a source-file or provide content, not both.',
            docutils.nodes.literal_block(block_text, block_text),
            line=lineno)
        return [error]
    
    # Load the content from a file if we were not given any content.
    if not content:
        try:
            sourceFile = state_machine.input_lines.source(
                lineno - state_machine.input_offset - 1)
            sourceDir = os.path.dirname(os.path.abspath(sourceFile))

            path = options['source-file']
            path = os.path.normpath(os.path.join(sourceDir, path))
            path = docutils.utils.relative_path(None, path)

            state.document.settings.record_dependencies.add(path)

            content = [line.rstrip() for line in file(path)]
        except IOError:
            error = state_machine.reporter.error(
                'Could not read file %s.' % (path),
                docutils.nodes.literal_block(block_text, block_text),
                line=lineno)
            return [error]

    # Load the SilverCity HTML generator for the specified language.
    try:
        module = getattr(SilverCity, language)
        generator = getattr(module, language + 'HTMLGenerator')
    except AttributeError:
        error = state_machine.reporter.error(
            'No SilverCity lexer found for language "%s".' % (language),
            docutils.nodes.literal_block(block_text, block_text),
            line=lineno)
        return [error]

    # Use the generator to render the content to HTML.  The HTML is
    # wrapped in a <code>..</code> block.
    io = cStringIO.StringIO()
    io.write('<code>')
    generator().generate_html(io, '\n'.join(content))
    io.write('</code>\n')

    # Enclose the rendered HTML in a raw docutils node and return the
    # node.
    raw = docutils.nodes.raw('', io.getvalue(), format='html')
    return [raw]

# Configure the code-block directive.
code_block_directive.arguments = (0, 2, True)
code_block_directive.options = {
    'language': docutils.parsers.rst.directives.unchanged,
    'source-file': docutils.parsers.rst.directives.path,
}
code_block_directive.content = True

# Register the directive with docutils if we are able to load the
# SilverCity module.
try:
    import SilverCity
    docutils.parsers.rst.directives.register_directive(
        'code-block', code_block_directive)
except ImportError:
    # Not an error; it just means that we do not have the SilverCity
    # module available.
    pass



# ######################################################################
# pyxslt directive.
#

def pyxslt_directive(name, arguments, options, content, lineno,
                     content_offset, block_text, state, state_machine):
    """
    The pyxslt directive allows you to call Python routines and include
    the serialized XML results in the input document.  These nodes will
    then be processed by the document's XSL template.

    Only keyword arguments may be passed to the target Python function::

        .. pyxslt:: sampleFunction
            :sampleArg: One
            :anotherArg: 27

    The resulting XML tree will be enclosed in a <pyxslt> tag, which
    will be passed straight-through to the XSL stylesheet for parsing.
    """

    # Parse the arguments into a method name and keyword arguments to
    # that method.
    lines = arguments[0].split('\n')
    methodName = lines[0]
    methodKeywordArgs = {}
    for line in lines[1:]:
        # Parse the line.
        m = re.match(
            '^:(?P<name>[A-Za-z][A-Za-z0-9_]*):\s*(?P<value>.*)$',
            line)
        if not m:
            error = state_machine.reporter.error(
                'Invalid function argument: %s' % (line),
                docutils.nodes.literal_block(block_text, block_text),
                line=lineno)
            return [error]

        # Store the argument.
        methodKeywordArgs[str(m.group('name'))] = m.group('value').strip()

    # Pull out the 'class' and 'multidoc' keyword arguments if they are
    # present.  These control the operation of the pyxslt directive and
    # are not passed as arguments to the target method.
    try:
        fragmentClass = methodKeywordArgs['class']
        del methodKeywordArgs['class']
    except KeyError:
        fragmentClass = None

    isMultidoc = 'multidoc' in methodKeywordArgs
    if isMultidoc:
        # There can only be one multidoc directive in the document.
        if state.document.settings.restxsl_multidoc:
            error = state_machine.reporter.error(
                'There can only be one multidoc directive in the document.',
                docutils.nodes.literal_block(block_text, block_text),
                line=lineno)
            return [error]

        # Store the multidoc filename XPATH expression and delete the
        # multidoc argument from the list.
        state.document.settings.restxsl_multidoc = methodKeywordArgs['multidoc']
        del methodKeywordArgs['multidoc']

    # Get the name of the Python function and retrieve it from our site
    # module.
    try:
        method = getattr(state.document.settings.restxsl_ext_module, methodName)
    except AttributeError:
        error = state_machine.reporter.error(
            'Cannot find Python function %s.' % (methodName),
            docutils.nodes.literal_block(block_text, block_text),
            line=lineno)
        return [error]

    # Execute the Python function and collect the results.
    try:
        results = method(
            state.document.settings.restxsl_ext_module_cookie,
            **methodKeywordArgs)
    except:
        error = state_machine.reporter.error(
            'Error executing Python function %s: %s' % (
                methodName, sys.exc_info()[1]),
            docutils.nodes.literal_block(block_text, block_text),
            line=lineno)
        return [error]

    # If this is a multidoc directive, then the result must be a list or
    # tuple.
    if isMultidoc:
        # Check the type.
        if type(results) not in (list, tuple):
            error = state_machine.reporter.error(
                'multidoc results must be list or tuple, not %s.' % (
                    type(results)),
                docutils.nodes.literal_block(block_text, block_text),
                line=lineno)
            return [error]

    # Serialize the results.
    ser = pyxslt.serialize.Serializer()
    ser.serializeOne(results)
    doc = ser.toXmlDoc()

    # Add the method name attribute.
    doc.getRootElement().newProp('method', methodName)

    # Add the XML fragment class attribute if we have one.
    # Serialize the results and store the XML document into an
    # XmlFragment node.
    if fragmentClass:
        doc.getRootElement().newProp('class', fragmentClass)

    # Add our multidoc tag if this is a multidoc directive.
    if isMultidoc:
        doc.getRootElement().newProp('multidoc', 'true')

    # Store the XML document in an XmlFragment node and return the node.
    fragment = restxmldoc.XmlFragment(doc)
    return [fragment]

# Configure the pyxslt directive.
pyxslt_directive.arguments = (1, 0, True)
pyxslt_directive.content = True
    
# Register the directive with docutils if we are able to load the pyxslt
# module.
try:
    import pyxslt.serialize
    docutils.parsers.rst.directives.register_directive(
        'pyxslt', pyxslt_directive)
except ImportError:
    # Not an error; it just means that we do not have the pyxslt module
    # available.
    pass
