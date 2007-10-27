<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:py="py"
    exclude-result-prefixes="py">
    <xsl:output encoding="utf-8" method="xml" indent="yes" omit-xml-declaration="yes"
        doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN"
        doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"/>
    <xsl:param name="level"/>
    <!--
		replace href="*.txt" with href="*.html"
	-->
    <xsl:template match="/ | @* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="@href | @src">
        <!-- .txt links to .html links -->
        <xsl:variable name="href">
            <xsl:choose>
                <xsl:when test="contains(., '#')">
                    <xsl:variable name="path" select="substring-before(., '#')"/>
                    <xsl:variable name="anchor" select="substring-after(., '#')"/>
                    <xsl:variable name="newpath">
                        <xsl:choose>
                            <xsl:when test="substring($path, string-length($path) - 3) = '.txt'">
                                <xsl:value-of
                                    select="concat(substring-before($path, '.txt'), '.html')"/>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:value-of select="$path"/>
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:variable>
                    <xsl:value-of select="concat($newpath, '#', $anchor)"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:choose>
                        <xsl:when test="substring(., string-length(.) - 3) = '.txt'">
                            <xsl:value-of select="concat(substring-before(., '.txt'), '.html')"/>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:value-of select="."/>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
        <!-- add index.html if link ends with / -->
        <xsl:variable name="abshref">
            <xsl:choose>
                <xsl:when test="substring($href, string-length($href)) = '/'">
                    <xsl:value-of select="concat($href, 'index.html')"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="$href"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
        <xsl:attribute name="{local-name()}">
			<xsl:choose>
				<xsl:when test="starts-with($abshref, '/') or starts-with($abshref, '../')">
		            <xsl:value-of select="py:rel(string($abshref), $level)"/>
					#<xsl:value-of select="$abshref"/> <xsl:value-of select="$level"/>
				</xsl:when>
				<xsl:otherwise>
		            <xsl:value-of select="$abshref"/>
				</xsl:otherwise>
			</xsl:choose>
        </xsl:attribute>
    </xsl:template>
</xsl:stylesheet>
