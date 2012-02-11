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
Apply U{SmartyPants-style <http://daringfireball.net/projects/smartypants/>}
filtering to a string, transforming the magic character sequences to
their Unicode equivalents.  This is in contrast to SmartyPants which
transforms character sequences to HTML entity references.

This code is based on the U{smartypants.py module <http://web.chad.org/projects/smartypants.py/>}
by Chad Miller.

@author: Michael Alyn Miller <malyn@strangeGizmo.com>
@copyright: 2006 by Michael Alyn Miller
@license: BSD License (see source code for full license)
"""


# ######################################################################
# IMPORTS
#

# Python imports.
import re



# ######################################################################
# En and em dash handling.
#

RE_EMDASH = re.compile(r"""---""")
RE_EMDASH_SUB = u'\N{EM DASH}'
RE_ENDASH = re.compile(r"""--""")
RE_ENDASH_SUB = u'\N{EN DASH}'

def transformDashes(text):
    """
    Transform ASCII dashes into Unicode em and en dashes.

    Two dashes (--) are converted into an en dash:

        >>> transformDashes('Wait 10--15 minutes.')
        u'Wait 10\u201315 minutes.'

    Three dashes (---) are converted into an em dash:

        >>> transformDashes('Wait---or not.')
        u'Wait\u2014or not.'
    """

    # Must do em dash first, otherwise every em dash will look like an
    # en dash (because every '---' begins with '--').
    text = RE_EMDASH.sub(RE_EMDASH_SUB, text)
    text = RE_ENDASH.sub(RE_ENDASH_SUB, text)
    return text



# ######################################################################
# Ellipsis handling.
#

RE_ELLIPSIS = re.compile(r"""\.\.\.""")
RE_ELLIPSIS_SUB = u'\N{HORIZONTAL ELLIPSIS}'

def transformEllipses(text):
    """
    Transform ASCII ellipses into Unicode ellipsis characters.

    Three dots (...) are converted into an ellipsis:

        >>> transformEllipses('Wait for it...')
        u'Wait for it\u2026'

    """

    text = RE_ELLIPSIS.sub(RE_ELLIPSIS_SUB, text)
    return text



# ######################################################################
# Quote handling.
#

def transformQuotes(text):
    """
    Transform ASCII quote characters (" and ') into curly quotes.

    Double quotes are converted into the correct, Unicode curly quotes:

        >>> transformQuotes('"Hello there"')
        u'\u201cHello there\u201d'
        >>> transformQuotes("I 'believe' you.")
        u'I \u2018believe\u2019 you.'

    Single quotes embedded in double quotes are parsed correctly:

        >>> transformQuotes('Did he just say, "I \\'believe\\' you?"')
        u'Did he just say, \u201cI \u2018believe\u2019 you?\u201d'

    Apostrophes are turned into curly single quotes:

        >>> transformQuotes("He's got some nerve.")
        u'He\u2019s got some nerve.'

    The sequence 's at the beginning of a string usually indicates a
    possessive phrase that was split due to some sort of formatting.
    For example, the string "<i>Bill</i>'s Noodle House" would be split
    into "Bill" and "'s Noodle House".

        >>> transformQuotes("He")
        'He'
        >>> transformQuotes("'s got some nerve.")
        u'\u2019s got some nerve.'
        >>> transformQuotes("'spose so.")
        u'\u2018spose so.'

    Decade abbreviations get special handling:

        >>> transformQuotes("Dot-coms?  Yeah, I remember the '90s.")
        u'Dot-coms?  Yeah, I remember the \u201990s.'
    """

    punct_class = r"""[!"#\$\%'()*+,-.\/:;<=>?\@\[\\\]\^_`{|}~]"""

    # Special case if the very first character is a quote followed by
    # punctuation at a non-word-break. Close the quotes by brute force:
    text = re.sub(
        r"""(?u)^'(?=%s\\B)""" % (punct_class,),
        u'\N{RIGHT SINGLE QUOTATION MARK}', text)
    text = re.sub(
        r"""(?u)^"(?=%s\\B)""" % (punct_class,),
        u'\N{RIGHT DOUBLE QUOTATION MARK}', text)

    # Special case for double sets of quotes, e.g.:
    #   He said, "'Quoted' words in a larger quote."
    text = re.sub(
        r"""(?u)"'(?=\w)""",
        u'\N{LEFT DOUBLE QUOTATION MARK}\N{LEFT SINGLE QUOTATION MARK}', text)
    text = re.sub(
        r"""(?u)'"(?=\w)""",
        u'\N{LEFT SINGLE QUOTATION MARK}\N{LEFT DOUBLE QUOTATION MARK}', text)

    # Special case for decade abbreviations (the '80s):
    text = re.sub(
        r"""(?u) '(?=\d{2}s)""",
        u' \N{RIGHT SINGLE QUOTATION MARK}', text)

    close_class = r"""[^\ \t\r\n\[\{\(\-]"""

    # Get most opening single quotes:
    opening_single_quotes_regex = re.compile(r"""
            (
                \s          |   # a whitespace char, or
                \N{EN DASH} |   # en dash or
                \N{EM DASH}     # em dash
            )
            '                 # the quote
            (?=\w)            # followed by a word character
            """, re.VERBOSE|re.UNICODE)
    text = opening_single_quotes_regex.sub(
        u'\\1\N{LEFT SINGLE QUOTATION MARK}', text)

    closing_single_quotes_regex = re.compile(r"""
            (%s)
            '
            (?!\s | s\b | \d)
            """ % (close_class,), re.VERBOSE|re.UNICODE)
    text = closing_single_quotes_regex.sub(
        u'\\1\N{RIGHT SINGLE QUOTATION MARK}', text)
 
    closing_single_quotes_regex = re.compile(r"""
            (%s|)
            '
            (\s | s\b)
            """ % (close_class,), re.VERBOSE|re.UNICODE)
    text = closing_single_quotes_regex.sub(
        u'\\1\N{RIGHT SINGLE QUOTATION MARK}\\2', text)

    # Any remaining single quotes should be opening ones:
    text = re.sub(r"""'""", u'\N{LEFT SINGLE QUOTATION MARK}', text)

    # Get most opening double quotes:
    opening_double_quotes_regex = re.compile(r"""
            (
                \s          |   # a whitespace char, or
                \N{EN DASH} |   # en dash or
                \N{EM DASH}     # em dash
            )
            "                 # the quote
            (?=\w)            # followed by a word character
            """, re.VERBOSE|re.UNICODE)
    text = opening_double_quotes_regex.sub(
        u'\\1\N{LEFT DOUBLE QUOTATION MARK}', text)

    # Double closing quotes:
    closing_double_quotes_regex = re.compile(r"""
            #(%s)?   # character that indicates the quote should be closing
            "
            (?=\s)
            """ % (close_class,), re.VERBOSE|re.UNICODE)
    text = closing_double_quotes_regex.sub(
        u'\N{RIGHT DOUBLE QUOTATION MARK}', text)

    closing_double_quotes_regex = re.compile(r"""
            (%s)   # character that indicates the quote should be closing
            "
            """ % (close_class,), re.VERBOSE|re.UNICODE)
    text = closing_double_quotes_regex.sub(
        u'\\1\N{RIGHT DOUBLE QUOTATION MARK}', text)

    # Any remaining quotes should be opening ones.
    text = re.sub(
        r'"',
        u'\N{LEFT DOUBLE QUOTATION MARK}', text)

    return text



# ######################################################################
# doctest entry point.
#

if __name__ == '__main__':
    import doctest
    doctest.testmod()
