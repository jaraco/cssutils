Fixed ``CSSCaptureHTMLParser`` (used by ``CSSCapture``) sharing its list of found stylesheets across all instances, so stylesheets from earlier captures no longer leak into later ones.
