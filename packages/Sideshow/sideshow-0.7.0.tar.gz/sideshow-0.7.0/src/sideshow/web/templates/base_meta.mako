<%inherit file="wuttaweb:templates/base_meta.mako" />

## TODO: you can override parent template as needed below, or you
## can simply delete this file if no customizations are needed

<%def name="favicon()">
  ${parent.favicon()}
</%def>

<%def name="header_logo()">
  ${parent.header_logo()}
</%def>

<%def name="footer()">
  ${parent.footer()}
</%def>
