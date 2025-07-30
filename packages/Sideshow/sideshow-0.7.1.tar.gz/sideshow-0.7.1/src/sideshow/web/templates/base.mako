## -*- coding: utf-8; -*-
<%inherit file="wuttaweb:templates/base.mako" />
<%namespace file="/sideshow-components.mako" import="make_sideshow_components" />

<%def name="render_vue_templates()">
  ${make_sideshow_components()}
  ${parent.render_vue_templates()}
</%def>
