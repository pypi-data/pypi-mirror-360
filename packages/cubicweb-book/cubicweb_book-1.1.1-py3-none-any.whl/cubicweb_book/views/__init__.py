from logilab.mtconverter import xml_escape

from cubicweb_web import component
from cubicweb.predicates import has_related_entities, is_instance

# XXX this component looks generic... move it to cubicweb ?


class ExternalUriComponent(component.EntityCtxComponent):
    """component to display link to external uri"""

    __regid__ = "externaluricomp"
    __select__ = (
        component.EntityCtxComponent.__select__
        & has_related_entities("same_as")
        & ~is_instance("ExternalUri")
    )
    context = "ctxtoolbar"

    def render_body(self, row, col, view=None):
        self.w('<div class="toolbarButton">')
        imgurl = self._cw.uiprops["BLUE_ARROW"]
        if hasattr(self.entity, "url"):
            url = self.entity.url
        else:
            url = self.entity.same_as[0].uri
        self.w(
            '<a href="%s"><img src="%s" alt="blue arrow"/></a>'
            % (xml_escape(url), xml_escape(imgurl))
        )
        self.w("</div>")
