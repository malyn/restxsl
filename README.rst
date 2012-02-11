========================================================================
restxsl
========================================================================


Overview
========================================================================

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

See the `restxsl product page`_ on the strangeGizmo.com site for more
information.

.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _SmartyPants-style: http://daringfireball.net/projects/smartypants/
.. _restxsl product page: http://www.strangeGizmo.com/products/restxsl/



Change List
========================================================================

0.9.1
-----

-   Hyphens in literal blocks are now encoded as non-breaking hyphens.
    This prevents web browsers from wrapping lines that should otherwise
    be preserved.

-   ``restxsl.transform.restxsl`` now accepts an additional keyword
    argument (``extModuleCookie``) that will be passed to the first
    argument of all methods called by the ``pyxslt`` directive.  This
    can be used to pass state information from the code that calls
    restxsl to the extension module's functions.

-   Corrected the code that handles the ``pyxslt`` directive so that it
    looks for a node with the name ``pyxslt`` instead of ``python``,
    which was the node name used by the alpha code.

-   The ``pyxslt`` directive now adds an additional attribute named
    ``method`` to the ``pyxslt`` tag.  This attribute includes the name
    of the method that was called by the ``pyxslt`` directive.

-   There was an error in the ``pyxslt`` directive that prevented it
    from properly serializing the result set.

-   Add the ``README.txt`` file.


0.9.0
-----

-   Initial release.
