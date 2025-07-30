import uuid

from .JHTML import HTML

__all__ = [
    "JSMol"
]

__reload_hooks__ = [".JHTML"]

class JSMol:
    class Applet(HTML.Div):
        version = "16.3.7.6"
        jsmol_source = f"https://cdn.jsdelivr.net/gh/b3m2a1/jsmol-cdn@{version}/jsmol/JSmol.min.js"
        jmol2_source = f"https://cdn.jsdelivr.net/gh/b3m2a1/jsmol-cdn@{version}/jsmol/js/Jmol2.js"
        patch_script = f"""
        if (typeof Jmol._patched === 'undefined') {{
            Jmol._patched = true;
            jmolInitialize('https://cdn.jsdelivr.net/gh/b3m2a1/jsmol-cdn@{version}/jsmol/');
        }};
        """
        @classmethod
        def load_applet_script(cls, id, loader):
            return HTML.Script(src=cls.jsmol_source,
                               onload=f"""
(function() {{
   $.getScript('{cls.jmol2_source}').then(
   () => {{
       {cls.patch_script}
       let loaded = false;
        if (!loaded) {{
            loaded = true;
            let applet = {loader};
             document.getElementById('{id}').innerHTML = applet._code;
        }}
    }})
}})();
"""
                               )

        def __init__(self, *model_etc, width='500px', height='500px',
                     animate=False, vibrate=False,
                     load_script=None,
                     suffix=None,
                     dynamic_loading=None,
                     **attrs):
            if suffix is None:
                suffix = str(uuid.uuid4())[:6].replace("-", "")
            self.suffix = suffix
            self.id = "jsmol-applet-" + self.suffix
            if len(model_etc) > 0 and isinstance(model_etc[0], str):
                model_file = model_etc[0]
                rest = model_etc[1:]
            else:
                model_file = None
                rest = model_etc

            if load_script is None:
                load_script = []
            if isinstance(load_script, str):
                load_script = [load_script]
            load_script = list(load_script)

            if animate:
                load_script.extend(["anim mode palindrome", "anim on"])
            elif vibrate:
                load_script.append("vibration on")

            if dynamic_loading is None:
                from ..Jupyter.JHTML import JupyterAPIs
                dynamic_loading = JupyterAPIs().in_jupyter_environment()

            self.dynamic_loading = dynamic_loading

            self.load_script = load_script
            elems = [self.create_applet(model_file)] + list(rest)
            super().__init__(*elems, id=self.id, width=width, height=height, **attrs)

        @property
        def applet_target(self):
            return f"_{self.suffix}"
        def prep_load_script(self):
            return '; '.join(self.load_script)
        def create_applet(self, model_file):
            targ = self.applet_target
            load_script = self.prep_load_script()
            if model_file is None:
                loader = f"jmolApplet(400, 'load {model_file}; {load_script}', '{targ}')"
            elif (
                    model_file.startswith("https://")
                    or model_file.startswith("file://")
                    or model_file.startswith("http://")
            ):
                loader = f"jmolApplet(400, 'load {model_file}; {load_script}', '{targ}')"
            else:
                loader = f"jmolAppletInline(400, `{model_file}`, '{load_script}', '{targ}')"

            kill_id = "tmp-" + str(uuid.uuid4())[:10]
            load_script = self.load_applet_script(self.id, loader)

            if self.dynamic_loading:
                load_script = load_script.tostring().replace("`", "\`")
                return HTML.Image(
                        src='data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7',
                        id=kill_id,
                        onload=f"""
                            (function() {{
                                document.getElementById('{kill_id}').remove();
                                const frag = document.createRange().createContextualFragment(`{load_script}`);
                                document.head.appendChild(frag);
                            }})()"""
                    )
            else:
                return load_script

        def show(self):
            return self.display()