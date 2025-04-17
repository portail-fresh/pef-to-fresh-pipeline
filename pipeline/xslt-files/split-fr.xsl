<xsl:stylesheet version="3.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:fresh="urn:fresh-enrichment:v1"
    exclude-result-prefixes="fresh">

    <xsl:mode on-no-match="shallow-copy" />

    <xsl:template match="/">
        <!-- Direct output, without 'href' -->
        <Root>
            <xsl:apply-templates select="*"/>
        </Root>
    </xsl:template>

    <xsl:template match="*">
        <xsl:variable name="local" select="local-name()" />
        <xsl:variable name="lang" select="'FR'" />

        <xsl:choose>
            <xsl:when test="ends-with($local, $lang)">
                <xsl:element name="{substring($local, 1, string-length($local) - 2)}">
                    <xsl:apply-templates select="node()"/>
                </xsl:element>
            </xsl:when>
            <xsl:when test="matches($local, '(FR|EN)$')">
                <!-- ignora -->
            </xsl:when>
            <xsl:otherwise>
                <xsl:element name="{$local}" namespace="{namespace-uri()}">
                    <xsl:apply-templates select="node()"/>
                </xsl:element>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="text()">
        <xsl:value-of select="." />
    </xsl:template>

</xsl:stylesheet>
