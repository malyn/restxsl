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

# Docutils imports.
import docutils.parsers.rst

# restxsl imports.
import restxmldoc



# ######################################################################
# xpath role.
#

def xpath_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    # Return an XpathReference node that will later be replaced by the
    # result of the XPATH expression.
    xpathRef = restxmldoc.XpathReference(text)
    return [xpathRef], []

# Configure the xpath role.
xpath_role.options = {
    'class': None,
}
xpath_role.content = False

# Register the role with docutils.
docutils.parsers.rst.roles.register_local_role(
    'xpath', xpath_role)
