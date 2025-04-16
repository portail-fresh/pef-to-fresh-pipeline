<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet 
    version="1.0" 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:fresh="urn:fresh-enrichment:v1"
    exclude-result-prefixes="fresh"> 

    <!-- Identity transform: copy everything as-is -->
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()" />
        </xsl:copy>
    </xsl:template>

    <!-- Match the root element and add the fresh namespace -->
    <xsl:template match="FichePortailEpidemiologieFrance">
        <xsl:element name="FichePortailEpidemiologieFrance" namespace="">
            <xsl:namespace name="fresh">urn:fresh-enrichment:v1</xsl:namespace> 
            <xsl:apply-templates select="@* | node()" />
        </xsl:element>
    </xsl:template>

</xsl:stylesheet>
