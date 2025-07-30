<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0">

	<xsl:output method="html" indent="yes" name="html"/>



	<xsl:template match="/tei">
		<html>
			<head>
				<style>
					<xsl:text>span.name</xsl:text>
					<xsl:text>{color: blue;}</xsl:text>
					<xsl:text>span.place</xsl:text>
					<xsl:text>{color: green;}</xsl:text>
					<xsl:text>span.date</xsl:text>
					<xsl:text>{color: orange;}</xsl:text>
					<xsl:text>span.page</xsl:text>
					<xsl:text>{color: red;}</xsl:text>
				</style>
			</head>
			<body>
				<xsl:apply-templates/>
			</body>
		</html>
	</xsl:template>

	<xsl:template match="/tei/teiHeader">
		<h1><xsl:value-of select="."/></h1>
	</xsl:template>

	<xsl:template match="/tei/text/body">
		<!-- <xsl:value-of select="."/> -->
		<xsl:apply-templates/>
	</xsl:template>

	<xsl:template match="//pb">
		<span class="page">
			<xsl:text>[Page </xsl:text>
			<xsl:value-of select="@n"/>
			<xsl:text>]</xsl:text>
		</span>
	</xsl:template>

	<xsl:template match="//date">
		<span class="date"><xsl:value-of select="."/></span>
	</xsl:template>

	<xsl:template match="//name[@type='person']">
		<span class="name person"><xsl:value-of select="."/></span>
	</xsl:template>

	<xsl:template match="//name[@type='place']">
		<span class="name place"><xsl:value-of select="."/></span>
	</xsl:template>

	<xsl:template match="//hi[@rend='bold']">
		<b><xsl:value-of select="."/></b>
	</xsl:template>

	<xsl:template match="//hi[@rend='italic']">
		<i><xsl:value-of select="."/></i>
	</xsl:template>

	<xsl:template match="//hi[@rend='sup']">
		<sup><xsl:value-of select="."/></sup>
	</xsl:template>

	<xsl:template match="//hi[@rend='sub']">
		<sub><xsl:value-of select="."/></sub>
	</xsl:template>

	<xsl:template match="//hi[@rend='underline']">
		<u><xsl:value-of select="."/></u>
	</xsl:template>

	<xsl:template match="//del[@rend='overstrike']">
		<del><xsl:value-of select="."/></del>
	</xsl:template>

	<xsl:template match="//add">
		<ins><xsl:value-of select="."/></ins>
	</xsl:template>

	<xsl:template match="//unclear[@reason='illegible']">
		<span class="illegible"><xsl:value-of select="."/></span>
	</xsl:template>

	<xsl:template match="//note[@place='margin']">
		<span class="note-margin"><xsl:value-of select="."/></span>
	</xsl:template>

	<xsl:template match="//q">
		<q><xsl:value-of select="."/></q>
	</xsl:template>

	<xsl:template match="//head">
		<h2><xsl:value-of select="."/></h2>
	</xsl:template>


	<!-- replace newline characters with br tag -->
    <xsl:template match="text()" name="repNL">
     <xsl:param name="pText" select="."/>
     <xsl:copy-of select=
     "substring-before(concat($pText,'&#xA;'),'&#xA;')"/>
     <xsl:if test="contains($pText, '&#xA;')">
      <br />
      <xsl:call-template name="repNL">
       <xsl:with-param name="pText" select=
       "substring-after($pText, '&#xA;')"/>
      </xsl:call-template>
     </xsl:if>
    </xsl:template>

</xsl:stylesheet>
