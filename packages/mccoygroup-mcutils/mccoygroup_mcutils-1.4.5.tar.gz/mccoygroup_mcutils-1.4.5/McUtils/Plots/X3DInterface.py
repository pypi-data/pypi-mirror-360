import abc
import uuid

import numpy as np

from ..Jupyter import JHTML, X3DHTML
from .. import Numputils as nput

__all__ = [
    "X3D",
    "X3DPrimitive",
    "X3DGeometryObject",
    "X3DGeometryGroup",
    "X3DGroup",
    "X3DScene",
    "X3DMaterial",
    "X3DLine",
    "X3DSphere",
    "X3DCone",
    "X3DCylinder",
    "X3DArrow",
    "X3DTorus",
    "X3DSwitch",
    "X3DListAnimator"
]

class X3DObject(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def to_x3d(self):
        ...

class X3D(X3DObject):
    defaults = dict(
        width=500,
        height=500
    )
    def __init__(self, *children, id=None, dynamic_loading=True, **opts):
        if len(children) == 1 and isinstance(children[0], (tuple, list)):
            children = children[0]
        self.children = children
        self.opts = opts
        if id is None:
            id = "x3d-" + str(uuid.uuid4())[:6]
        self.id = id
        self.dynamic_loading = dynamic_loading

    X3DOM_JS = 'http://www.x3dom.org/download/x3dom.js'
    X3DOM_CSS = 'http://www.x3dom.org/download/x3dom.css'

    def get_export_script(self, id):
        return f"""
(function(){{
  let link = document.createElement('a');
  let base_name = '{id}';
  link.download = base_name + '.png';
  link.href = document.getElementById('{id}').getElementsByTagName('canvas')[0].toDataURL()
  link.click();
}})()
       """

    def get_record_screen_script(self, id, polling_rate=30, recording_duration=2):
            return f"""
    (function(){{
        let canvas = document.getElementById('{id}').getElementsByTagName('canvas')[0];
        
        let x3DRecordingStream = canvas.captureStream({polling_rate});
        let mediaRecorder = new MediaRecorder(x3DRecordingStream, {{mimeType: "video/mp4"}});
        
        mediaRecorder.frames = [];
        mediaRecorder.ondataavailable = function(e) {{
          mediaRecorder.frames.push(e.data);
        }};
        
        mediaRecorder.onstop = function(e) {{
          link = document.createElement('a');
          const base_name = '{id}';
          const blob = mediaRecorder.frames[0];
          link.download = base_name + '.mp4';
          console.log(blob);
          const blobURL = window.URL.createObjectURL(blob);
          link.href = blobURL;
          console.log(blobURL);
          mediaRecorder.frames = [];
          link.click();
        }};
        
        let duration = {recording_duration} * 1000;
        setTimeout(() => {{mediaRecorder.stop()}}, duration);
        mediaRecorder.start()
    }})()
           """

    include_export_button = False
    include_record_button = False
    def to_widget(self, dynamic_loading=None, include_export_button=None, include_record_button=None):
        id = self.id
        x3d_embed = self.to_x3d()#.tostring()

        if dynamic_loading is None:
            dynamic_loading = self.dynamic_loading
        if include_export_button is None:
            include_export_button = self.include_export_button
        if include_record_button is None:
            include_record_button = self.include_record_button

        if not dynamic_loading:
            base_fig = JHTML.Div(
                JHTML.Link(rel='stylesheet', href=self.X3DOM_CSS),
                JHTML.Script(src=self.X3DOM_JS),
                x3d_embed,
                id=id
            )
        else:
            JHTML.Link(rel='stylesheet', href=self.X3DOM_CSS),
            load_script = JHTML.Script(src=self.X3DOM_JS).tostring()
            kill_id = "tmp-"+str(uuid.uuid4())[:10]
            base_fig = JHTML.Figure(
                # JHTML.Link(rel='stylesheet', href=self.X3DOM_CSS),
                x3d_embed,
                JHTML.Image(
                    src='data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7',
                    id=kill_id,
                    onload=f"""
                    (function() {{
                        document.getElementById("{kill_id}").remove();
                        const frag = document.createRange().createContextualFragment(`{load_script}`);
                        document.head.appendChild(frag);
                    }})()"""
                    ),
                id=id
            )

        elems = [base_fig]
        if include_export_button:
            elems.append(JHTML.Button("Save Figure", onclick=self.get_export_script(self.id)))
        if include_record_button:
            elems.append(JHTML.Button("Record Animation", onclick=self.get_record_screen_script(self.id)))

        if len(elems) > 1:
            return JHTML.Div(
                *elems
            )
        else:
            return elems[0]

    def to_html(self, *base_elems, header_elems=None, **header_info):
        id = self.id
        x3d_embed = self.to_x3d()  # .tostring()

        return JHTML.Html(
            JHTML.Head(
                *(header_elems if header_elems is not None else []),
                JHTML.Link(rel='stylesheet', href=self.X3DOM_CSS),
                JHTML.Script(src=self.X3DOM_JS),
                **header_info
            ),
            JHTML.Body(
                *base_elems,
                x3d_embed
            ),
            id=id
        )

    def _ipython_display_(self):
        return self.to_widget()._ipython_display_()
    def get_mime_bundle(self):
        return self.to_widget().get_mime_bundle()
    def to_x3d(self):
        base_opts = dict(self.defaults, **self.opts)
        for k in ['width', 'height']:
            if k in base_opts:
                v = base_opts[k]
                if nput.is_numeric(v):
                    base_opts[k] = f'{v:.0f}px'
        return X3DHTML.X3D(
            JHTML.HTML.Head(),
            *[a.to_x3d() if hasattr(a, 'to_x3d') else a for a in self.children],
            **base_opts
        )
    def display(self):
        return self.to_widget().display()

    def show(self):
        from ..Jupyter.JHTML import JupyterAPIs
        dynamic_loading = JupyterAPIs().in_jupyter_environment()
        self.to_widget(dynamic_loading=dynamic_loading).display()

    def dump(self, file, write_html=True, **opts):
        if write_html:
            html = self.to_html()
        else:
            html = self.to_x3d()
        return html.write(file, **opts)

class X3DMaterial(X3DObject):
    __props__ = {
        "diffuseColor",
        "ambientIntensity",
        "emissiveColor",
        "specularColor",
        "shininess",
        "transparency",
        # "metadata"
    }
    def __init__(self, **attrs):
        self.attrs = attrs

    conversion_map = {
        "brightness": "ambientIntensity",
        "glow":"emissiveColor",
        "color": "diffuseColor",
        "specularity": "specularColor"
    }
    @classmethod
    def prop_keys(cls):
        return (cls.__props__ | cls.conversion_map.keys())
    def prep_attrs(self, attrs:dict):
        attrs = {
            self.conversion_map.get(k, k):v
            for k,v in attrs.items()
        }
        excess_keys = attrs.keys() - self.__props__
        if len(excess_keys) > 0:
            raise ValueError(f"keys {excess_keys} are invalid material keys")
        return attrs
    def to_x3d(self):
        return X3DHTML.Material(**self.prep_attrs(self.attrs))

class X3DPrimitive(X3DObject):
    wrapper_class = None
    tag_class = None
    def __init__(self, *children, **opts):
        if len(children) == 1 and isinstance(children[0], (tuple, list)):
            children = children[0]
        self.children = children
        self.opts = opts
    def split_opts(self, opts:dict):
        material_keys = opts.keys() & X3DMaterial.prop_keys()
        rem_keys = opts.keys() - material_keys
        return {k:opts[k] for k in rem_keys}, {k:opts[k] for k in material_keys}
    def get_appearance(self, material_opts):
        if len(material_opts) == 0:
            return None
        else:
            return X3DHTML.Appearance(X3DMaterial(**material_opts).to_x3d())
    def to_x3d(self):
        obj_opts, material_opts = self.split_opts(self.opts)
        kids = [k.to_x3d() if hasattr(k, 'to_x3d') else k for k in self.children]
        appearance = self.get_appearance(material_opts)
        if self.tag_class is None:
            if appearance is not None:
                kids = [appearance] + kids
            return self.wrapper_class(
                kids,
                **obj_opts
            )
        else:
            core = self.tag_class(kids, **obj_opts)
            appearance = self.get_appearance(material_opts)
            if appearance is not None:
                return self.wrapper_class(appearance, core)
            else:
                return core

class X3DScene(X3DPrimitive):
    wrapper_class = X3DHTML.Scene
    default_viewpoint = {'viewAll':True}
    def __init__(self, *children, viewpoint=None, **opts):
        if viewpoint is None:
            viewpoint = self.default_viewpoint
        elif viewpoint is False:
            viewpoint = {}
        super().__init__(*children, **opts)
        if len(viewpoint) > 0:
            self.children = [X3DHTML.Viewpoint(**viewpoint)] + list(self.children)

class X3DGroup(X3DPrimitive):
    wrapper_class = X3DHTML.Group

class X3DSwitch(X3DPrimitive):
    wrapper_class = X3DHTML.Switch

class X3DGeometryObject(X3DPrimitive):
    wrapper_class = X3DHTML.Shape
    def __init__(self, *args, **opts):
        geom_opts, self.material_opts = self.split_opts(opts)
        self.geometry_opts = self.prep_geometry_opts(*args, **geom_opts)
        super().__init__()
    @abc.abstractmethod
    def prep_geometry_opts(self, *args, **opts) -> dict:
        ...
    def create_object(self, translation=None, rotation=None, scale=None, **core_opts):
        base_obj = self.tag_class(**core_opts)
        tf = {}
        for k,v in [["translation",translation], ["rotation",rotation], ["scale", scale]]:
            if v is not None:
                tf[k] = v
        if len(tf) == 0:
            tf = None
        # base_obj = X3DHTML.Transform(base_obj, translation=translation, rotation=rotation, scale=scale)
        return base_obj, tf
    def get_rotation(self, axis, up_vector=None):
        if up_vector is None:
            up_vector = [0, 1, 0]
        angs, crosses, norms = nput.vec_angles(up_vector, axis, return_crosses=True, return_norms=True)
        if nput.is_numeric(angs):
            return np.concatenate([crosses, [angs]]), norms[1]
        else:
            return np.concatenate([crosses, angs[..., np.newaxis]], axis=-1), norms[1]
    def to_x3d(self):
        # obj_opts, material_opts = self.split_opts(self.opts)
        # kids = [k.to_x3d() for k in self.children]
        core, tf = self.create_object(**self.geometry_opts)
        appearance = self.get_appearance(self.material_opts)
        if appearance is not None:
            core = self.wrapper_class(appearance, core)
        if tf is not None:
            core = X3DHTML.Transform(core, **tf)
        return core

class X3DGeometryGroup(X3DGeometryObject):
    @abc.abstractmethod
    def prep_geometry_opts(self, *args, **opts) -> list[dict]:
        ...
    def prep_vecs(self, vecs, nstruct=None):
        if vecs is None:
            return [None] * nstruct
        else:
            vecs = np.asanyarray(vecs)
            if vecs.ndim == 1:
                vecs = vecs[np.newaxis]
            if nstruct is not None:
                vecs = np.broadcast_to(vecs, (nstruct, vecs.shape[-1]))
        return vecs
    def prep_mats(self, mats, nstruct=None):
        if mats is None:
            return [None] * nstruct
        else:
            mats = np.asanyarray(mats)
            if mats.ndim == 2:
                mats = mats[np.newaxis]
            if nstruct is not None:
                mats = np.broadcast_to(mats, (nstruct,) + mats.shape[-2:])
            return mats
    def prep_const(self, const, nstruct):
        if const is None:
            return [None] * nstruct
        else:
            const = np.asanyarray(const)
            if const.ndim == 0:
                const = const[np.newaxis]
            const = np.broadcast_to(const, (nstruct,))
            return const
    def to_x3d(self):
        kids = [self.create_object(**g) for g in self.geometry_opts]
        appearance = self.get_appearance(self.material_opts)
        objs = []
        for o,tf in kids:
            if appearance is not None:
                o = self.wrapper_class(appearance, o)
            if tf is not None:
                o = X3DHTML.Transform(o, **tf)
            objs.append(o)
        if len(objs) == 1:
            return objs[0]
        else:
            return X3DHTML.Group(objs)

class X3DLine(X3DGeometryObject):
    tag_class = X3DHTML.LineSet

    def prep_geometry_opts(self, points, **opts)->dict:
        return {"coords":np.asanyarray(points).flatten()}

class X3DSphere(X3DGeometryGroup):
    tag_class = X3DHTML.Sphere

    def prep_geometry_opts(self, centers, radius=1, **opts):
        centers = self.prep_vecs(centers)
        rads = self.prep_const(radius, centers.shape[0])
        return [{"translation":c, "radius":r} for c,r in zip(centers, rads)]

class X3DCylinder(X3DGeometryGroup):
    tag_class = X3DHTML.Cylinder

    def prep_geometry_opts(self, starts, ends, radius=1, **opts):
        starts = self.prep_vecs(starts)
        ends = self.prep_vecs(ends)
        radius = self.prep_const(radius, starts.shape[0])

        axes = ends - starts
        rots, norms = self.get_rotation(axes)

        return [
            {"translation":s, "rotation":a, "height":n, "radius":r}
            for s,a,n,r in zip((starts + ends) / 2, rots, norms, radius)
        ]

class X3DCone(X3DGeometryGroup):
    tag_class = X3DHTML.Cone

    def prep_geometry_opts(self, starts, ends, radius=1, top_radius=None, **opts):
        starts = self.prep_vecs(starts)
        ends = self.prep_vecs(ends)
        radius = self.prep_const(radius, starts.shape[0])
        top_radius = self.prep_const(top_radius, starts.shape[0])

        axes = ends - starts
        rots, norms = self.get_rotation(axes)

        return [
            {"translation":s, "rotation":a, "height":n, "bottomRadius":r, "topRadius":t}
            for s,a,n,r,t in zip((starts + ends) / 2, rots, norms, radius, top_radius)
        ]

class X3DArrow(X3DGroup):

    arrowhead_class = X3DCone
    cylinder_class = X3DCylinder

    def __init__(self,
                 starts, ends,
                 radius=1,
                 top_radius=None,
                 arrowhead_radius=2,
                 arrowhead_radius_mode='scaled',
                 arrowhead_offset=.3,
                 arrowhead_offset_mode='scaled',
                 cylinder_class=None,
                 arrowhead_class=None,
                 **opts):
        if arrowhead_class is None:
            arrowhead_class = self.arrowhead_class
        if cylinder_class is None:
            cylinder_class = self.cylinder_class

        ends = np.asanyarray(ends)
        starts = np.asanyarray(starts)
        arrow_vectors = ends - starts
        norms = nput.vec_norms(arrow_vectors)
        if arrowhead_offset_mode == 'scaled':
            arrowhead_offset = arrowhead_offset * norms
        disp_vectors = arrowhead_offset * nput.vec_normalize(arrow_vectors, norms=norms)
        arrow_starts = ends - disp_vectors
        if arrowhead_radius_mode == 'scaled':
            arrowhead_radius = arrowhead_radius * radius
        arrowheads = arrowhead_class(arrow_starts, ends,
                                     radius=arrowhead_radius,
                                     top_radius=top_radius,
                                     **opts)
        cylinders = cylinder_class(starts, arrow_starts, radius=radius, **opts)

        super().__init__(
            arrowheads, cylinders
        )

class X3DTorus(X3DGeometryGroup):
    tag_class = X3DHTML.Torus

    def prep_geometry_opts(self, centers, radius=1, inner_radius=None, **opts):
        centers = self.prep_vecs(centers)
        radius = self.prep_const(radius, centers.shape[0])
        inner_radius = self.prep_const(inner_radius, centers.shape[0])

        return [
            {"translation":s,  "outerRadius":r, "innerRadius":i}
            for s,r,i in zip(centers, radius, inner_radius)
        ]

class X3DListAnimator(X3DGroup):
    def __init__(self, *frames, id=None, animation_duration=2, running=True, slider=False,
                 # allow_interpolation=True,
                 **opts):
        self.uuid = str(uuid.uuid4())
        if id is None:
            id = f"animation-{self.uuid}"
        self.id = id
        anim_frames = X3DSwitch(
                *frames,
                id=id,
                whichChoice="0"
            )
        nframes = len(anim_frames.children) - 1
        key_frames = np.linspace(0, 1, nframes)
        elements = []
        if slider:
            elements.append(
                JHTML.Input(type="range", value="0", min="0", max=f"{nframes}", step="1", cls="slider",
                            oninput=f"""document.getElementById("{id}").setAttribute("whichChoice", this.value)""")
            )
        elements.append(anim_frames)
        if running:
            elements.extend([
                X3DHTML.TimeSensor(id=f'animation-clock-{self.uuid}', cycleInterval=animation_duration, loop=True,
                                   enabled=running
                                   ),
                X3DHTML.IntegerSequencer(id=f'animation-indexer-{self.uuid}', key=key_frames,
                                         keyValue=np.arange(nframes)),
                X3DHTML.Route(
                    fromField='fraction_changed', fromNode=f'animation-clock-{self.uuid}',
                    toField='set_fraction', toNode=f'animation-indexer-{self.uuid}'
                ),
                X3DHTML.Route(
                    fromField='value_changed', fromNode=f'animation-indexer-{self.uuid}',
                    toField='whichChoice', toNode=self.id
                )
            ])

        super().__init__(elements, **opts)

