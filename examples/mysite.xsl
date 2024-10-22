<!--
	 Copyright (c) 2006, Michael Alyn Miller <malyn@strangeGizmo.com>.
	 All rights reserved.
	 
	 Redistribution and use in source and binary forms, with or without
	 modification, are permitted provided that the following conditions
	 are met:
	 
	 1.  Redistributions of source code must retain the above copyright
		 notice unmodified, this list of conditions, and the following
		 disclaimer.
	 2.  Redistributions in binary form must reproduce the above
		 copyright notice, this list of conditions and the following
		 disclaimer in the documentation and/or other materials provided
		 with the distribution.
	 3.  Neither the name of Michael Alyn Miller nor the names of the
		 contributors to this software may be used to endorse or promote
		 products derived from this software without specific prior
		 written permission.
	 
	 THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS "AS IS"
	 AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
	 TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
	 PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR
	 CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
	 SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
	 LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
	 USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
	 ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
	 OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
	 OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
	 SUCH DAMAGE.
-->

<xsl:stylesheet
	version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns="http://www.w3.org/1999/xhtml">


<!-- Import the reStructuredText XSL template. -->
<xsl:import href="/xsl/reST.xsl" />


<!-- Set the output parameters. -->
<xsl:output
  method="xml"
  indent="no"
  doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN" />


<!-- The base template. -->
<xsl:template match="/">
	<html>
		<head>
			<title>
				<xsl:text>My.Site : </xsl:text>
				<xsl:value-of select='/document/title' />
			</title>

			<style type="text/css">
				@import url(mysite.css);
			</style>
		</head>

		<body>
			<!-- Output the page header. -->
			<div class="header">
				<span class="logo">My.Site</span>
				<span class="logo_tagline">An exciting test site since 2006.</span>
			</div>

			<!-- Include the document content. -->
			<xsl:apply-templates />

			<!-- Include the page footer. -->
			<hr />
			<div class="footer">
				<span class="copyright">Copyright: This document is in the public domain.</span>
				<span class="restxsl_tagline">Generated by <a href="http://www.strangeGizmo.com/products/restxsl/">restxsl</a></span>
			</div>
		</body>
	</html>
</xsl:template>


</xsl:stylesheet>
