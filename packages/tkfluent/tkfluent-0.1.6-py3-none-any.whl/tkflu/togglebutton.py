from easydict import EasyDict
from tkdeft.windows.draw import DSvgDraw
from tkdeft.windows.canvas import DCanvas
from tkdeft.windows.drawwidget import DDrawWidget


class FluToggleButtonDraw(DSvgDraw):
    def create_roundrect_with_text(self,
                                   x1, y1, x2, y2, radius, radiusy=None, temppath=None,
                                   fill="transparent", fill_opacity=1,
                                   outline="black", outline2=None, outline_opacity=1, outline2_opacity=1, width=1,
                                   ):
        if radiusy:
            _rx = radius
            _ry = radiusy
        else:
            _rx, _ry = radius, radius
        drawing = self.create_drawing(x2 - x1, y2 - y1, temppath=temppath)
        if outline2:
            border = drawing[1].linearGradient(start=(x1, y1), end=(x1, y2), id="DButton.Border",
                                               gradientUnits="userSpaceOnUse")
            border.add_stop_color("0.9", outline, outline_opacity)
            border.add_stop_color("1", outline2, outline2_opacity)
            drawing[1].defs.add(border)
            stroke = f"url(#{border.get_id()})"
            stroke_opacity = 1
        else:
            stroke = outline
            stroke_opacity = outline_opacity
        drawing[1].add(
            drawing[1].rect(
                (x1, y1), (x2 - x1, y2 - y1), _rx, _ry,
                fill=fill, fill_opacity=fill_opacity,
                stroke=stroke, stroke_width=width, stroke_opacity=stroke_opacity,
                transform="translate(0.500000 0.500000)"
            )
        )
        drawing[1].save()
        return drawing[0]


class FluToggleButtonCanvas(DCanvas):
    draw = FluToggleButtonDraw

    def create_round_rectangle_with_text(self,
                                         x1, y1, x2, y2, r1, r2=None, temppath=None, temppath2=None,
                                         fill="transparent", fill_opacity=1,
                                         outline="black", outline2="black", outline_opacity=1, outline2_opacity=1,
                                         width=1,
                                         ):
        self._img = self.svgdraw.create_roundrect_with_text(
            x1, y1, x2, y2, r1, r2, temppath=temppath,
            fill=fill, fill_opacity=fill_opacity,
            outline=outline, outline2=outline2, outline_opacity=outline_opacity, outline2_opacity=outline2_opacity,
            width=width,
        )
        from .designs.renderer import get_renderer
        self._tkimg = self.svgdraw.create_svg_image(self._img, temppath2, way=get_renderer())
        return self.create_image(x1, y1, anchor="nw", image=self._tkimg)

    create_roundrect = create_round_rectangle_with_text


from .tooltip import FluToolTipBase
from .designs.gradient import FluGradient


class FluToggleButton(FluToggleButtonCanvas, DDrawWidget, FluToolTipBase, FluGradient):
    def __init__(self, *args,
                 text="",
                 width=120,
                 height=32,
                 command=None,
                 font=None,
                 mode="light",
                 state="normal",
                 **kwargs):
        self._init(mode)

        super().__init__(*args, width=width, height=height, **kwargs)

        if command is None:
            def empty(): pass

            command = empty

        self.dconfigure(
            text=text,
            command=command,
            state=state,
        )

        self.bind("<<Clicked>>", lambda event=None: self.toggle(), add="+")
        self.bind("<<Clicked>>", lambda event=None: self.focus_set(), add="+")
        self.bind("<<Clicked>>", lambda event=None: self.invoke(), add="+")

        self.bind("<Return>", lambda event=None: self.invoke(), add="+")  # 可以使用回车键模拟点击
        self.bind("<Return>", lambda event=None: self.toggle(), add="+")  # 可以使用回车键模拟点击

        from .defs import set_default_font
        set_default_font(font, self.attributes)

    def _init(self, mode):

        from easydict import EasyDict

        self.attributes = EasyDict(
            {
                "text": "",
                "command": None,
                "font": None,
                "state": "normal",
                "checked": False,

                "uncheck": {},

                "check": {}
            }
        )

        self.theme(mode=mode)

    def _draw(self, event=None, tempcolor: dict = None):
        super()._draw(event)

        width = self.winfo_width()
        height = self.winfo_height()

        self.delete("all")

        state = self.dcget("state")

        _dict = None
        if not tempcolor:
            if not self.attributes.checked:
                if state == "normal":
                    if self.enter:
                        if self.button1:
                            _dict = self.attributes.uncheck.pressed
                        else:
                            _dict = self.attributes.uncheck.hover
                    else:
                        _dict = self.attributes.uncheck.rest
                else:
                    _dict = self.attributes.uncheck.disabled
            else:
                if state == "normal":
                    if self.enter:
                        if self.button1:
                            _dict = self.attributes.check.pressed
                        else:
                            _dict = self.attributes.check.hover
                    else:
                        _dict = self.attributes.check.rest
                else:
                    _dict = self.attributes.check.disabled

            _back_color = _dict.back_color
            _back_opacity = _dict.back_opacity
            _border_color = _dict.border_color
            _border_color_opacity = _dict.border_color_opacity
            _border_color2 = _dict.border_color2
            _border_color2_opacity = _dict.border_color2_opacity
            _border_width = _dict.border_width
            _radius = _dict.radius
            _text_color = _dict.text_color
        else:
            _back_color = tempcolor.back_color
            _back_opacity = tempcolor.back_opacity
            _border_color = tempcolor.border_color
            _border_color_opacity = tempcolor.border_color_opacity
            _border_color2 = tempcolor.border_color2
            _border_color2_opacity = tempcolor.border_color2_opacity
            _border_width = tempcolor.border_width
            _radius = tempcolor.radius
            _text_color = tempcolor.text_color

        from .designs.renderer import get_renderer
        if get_renderer() == 1:
            width -= 1
            height -= 1

        self.element_border = self.create_round_rectangle_with_text(
            0, 0, width, height, _radius, temppath=self.temppath, temppath2=self.temppath3,
            fill=_back_color, fill_opacity=_back_opacity,
            outline=_border_color, outline_opacity=_border_color_opacity, outline2=_border_color2,
            outline2_opacity=_border_color2_opacity,
            width=_border_width,
        )

        self.element_text = self.create_text(
            self.winfo_width() / 2, self.winfo_height() / 2, anchor="center",
            fill=_text_color, text=self.attributes.text, font=self.attributes.font
        )

    def theme(self, mode="light"):
        self.mode = mode
        if mode.lower() == "dark":
            self._dark()
        else:
            self._light()

    def _light(self):
        from tkflu.designs.primary_color import get_primary_color
        self.dconfigure(
            uncheck={
                "rest": {
                    "back_color": "#ffffff",
                    "back_opacity": "0.7",
                    "border_color": "#000000",
                    "border_color_opacity": "0.2",
                    "border_color2": "#000000",
                    "border_color2_opacity": "0.3",
                    "border_width": 1,
                    "radius": 6,
                    "text_color": "#000000",
                },
                "hover": {
                    "back_color": "#F9F9F9",
                    "back_opacity": "0.5",
                    "border_color": "#000000",
                    "border_color_opacity": "0.1",
                    "border_color2": "#000000",
                    "border_color2_opacity": "0.2",
                    "border_width": 1,
                    "radius": 6,
                    "text_color": "#000000",
                },
                "pressed": {
                    "back_color": "#F9F9F9",
                    "back_opacity": "0.3",
                    "border_color": "#000000",
                    "border_color_opacity": "0.1",
                    "border_color2": None,
                    "border_color2_opacity": None,
                    "border_width": 1,
                    "radius": 6,
                    "text_color": "#636363",
                },
                "disabled": {
                    "back_color": "#ffffff",
                    "back_opacity": "1.000000",
                    "border_color": "#000000",
                    "border_color_opacity": "0.058824",
                    "border_color2": "#000000",
                    "border_color2_opacity": "0.160784",
                    "border_width": 1,
                    "radius": 6,
                    "text_color": "#a2a2a2",
                },
            },
            check={
                "rest": {
                    "back_color": get_primary_color()[0],
                    "back_opacity": "1",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.08",
                    "border_color2": "#000000",
                    "border_color2_opacity": "0.4",
                    "border_width": 1,
                    "radius": 6,
                    "text_color": "#ffffff",
                },
                "hover": {
                    "back_color": get_primary_color()[0],
                    "back_opacity": "0.9",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.08",
                    "border_color2": "#000000",
                    "border_color2_opacity": "0.4",
                    "border_width": 1,
                    "radius": 6,
                    "text_color": "#ffffff",
                },
                "pressed": {
                    "back_color": get_primary_color()[0],
                    "back_opacity": "0.8",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.08",
                    "border_color2": "#FFFFFF",
                    "border_color2_opacity": "0.08",
                    "border_width": 1,
                    "radius": 6,
                    "text_color": "#c2d9ee",
                },
                "disabled": {
                    "back_color": "#000000",
                    "back_opacity": "0.22",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "1",
                    "border_color2": "#FFFFFF",
                    "border_color2_opacity": "1",
                    "border_width": 0,
                    "radius": 6,
                    "text_color": "#f3f3f3",
                }
            }
        )

    def _dark(self):
        from tkflu.designs.primary_color import get_primary_color
        self.dconfigure(
            uncheck={
                "rest": {
                    "back_color": "#FFFFFF",
                    "back_opacity": "0.06",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.09",
                    "border_color2": "#FFFFFF",
                    "border_color2_opacity": "0.07",
                    "border_width": 1,
                    "radius": 6,
                    "text_color": "#FFFFFF",
                },
                "hover": {
                    "back_color": "#FFFFFF",
                    "back_opacity": "0.08",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.09",
                    "border_color2": "#FFFFFF",
                    "border_color2_opacity": "0.07",
                    "border_width": 1,
                    "radius": 6,
                    "text_color": "#FFFFFF",
                },
                "pressed": {
                    "back_color": "#FFFFFF",
                    "back_opacity": "0.03",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.07",
                    "border_color2": None,
                    "border_color2_opacity": None,
                    "border_width": 1,
                    "radius": 6,
                    "text_color": "#7D7D7D",
                },
                "disabled": {
                    "back_color": "#FFFFFF",
                    "back_opacity": "0.04",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.07",
                    "border_color2": None,
                    "border_color2_opacity": None,
                    "border_width": 1,
                    "radius": 6,
                    "text_color": "#a2a2a2",
                }
            },
            check={
                "rest": {
                    "back_color": get_primary_color()[1],
                    "back_opacity": "1",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.08",
                    "border_color2": "#000000",
                    "border_color2_opacity": "0.14",
                    "border_width": 1,
                    "radius": 6,
                    "text_color": "#000000",
                },
                "hover": {
                    "back_color": get_primary_color()[1],
                    "back_opacity": "0.9",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.08",
                    "border_color2": "#000000",
                    "border_color2_opacity": "0.14",
                    "border_width": 1,
                    "radius": 6,
                    "text_color": "#000000",
                },
                "pressed": {
                    "back_color": get_primary_color()[1],
                    "back_opacity": "0.8",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.08",
                    "border_color2": None,
                    "border_color2_opacity": None,
                    "border_width": 1,
                    "radius": 6,
                    "text_color": "#295569",
                },
                "disabled": {
                    "back_color": "#FFFFFF",
                    "back_opacity": "0.16",
                    "border_color": "#FFFFFF",
                    "border_color_opacity": "0.16",
                    "border_color2": None,
                    "border_color2_opacity": None,
                    "border_width": 1,
                    "radius": 6,
                    "text_color": "#a7a7a7",
                }
            }
        )

    def invoke(self):
        if self.attributes.state == "normal":
            self.attributes.command()

    def toggle(self, animation_steps: int = None, animation_step_time: int = None):
        if self.attributes.state == "normal":
            if animation_steps is None:
                from .designs.animation import get_animation_steps
                animation_steps = get_animation_steps()
            if animation_step_time is None:
                from .designs.animation import get_animation_step_time
                animation_step_time = get_animation_step_time()
            check = self.attributes.check
            uncheck = self.attributes.uncheck
            if not animation_steps == 0 or not animation_step_time == 0:
                steps = animation_steps
                if uncheck.pressed.border_color2 is None:
                    uncheck.pressed.border_color2 = uncheck.pressed.border_color
                if check.pressed.border_color2  is None:
                    check.pressed.border_color2 = check.pressed.border_color
                if uncheck.pressed.border_color2_opacity is None:
                    uncheck.pressed.border_color2_opacity = uncheck.pressed.border_color_opacity
                if check.pressed.border_color2_opacity is None:
                    check.pressed.border_color2_opacity = check.pressed.border_color_opacity
                if self.attributes.checked:
                    self.attributes.checked = False
                    back_colors = self.generate_hex2hex(
                        check.pressed.back_color, uncheck.rest.back_color, steps
                    )
                    border_colors = self.generate_hex2hex(
                        check.pressed.border_color, uncheck.rest.border_color, steps
                    )
                    border_colors2 = self.generate_hex2hex(
                        check.pressed.border_color2, uncheck.rest.border_color2, steps
                    )
                    text_colors = self.generate_hex2hex(
                        check.pressed.text_color, uncheck.rest.text_color, steps
                    )
                    import numpy as np
                    back_opacitys = np.linspace(
                        float(check.pressed.back_opacity), float(uncheck.rest.back_opacity), steps).tolist()
                    border_color_opacitys = np.linspace(
                        float(check.pressed.border_color_opacity), float(uncheck.rest.border_color_opacity), steps).tolist()
                    border_color2_opacitys = np.linspace(
                        float(check.pressed.border_color2_opacity), float(uncheck.rest.border_color2_opacity), steps).tolist()
                else:
                    self.attributes.checked = True
                    back_colors = self.generate_hex2hex(
                        uncheck.pressed.back_color, check.rest.back_color, steps
                    )
                    border_colors = self.generate_hex2hex(
                        uncheck.pressed.back_color, check.rest.back_color, steps
                    )
                    border_colors2 = self.generate_hex2hex(
                        uncheck.pressed.border_color2, check.rest.border_color2, steps
                    )
                    text_colors = self.generate_hex2hex(
                        uncheck.pressed.text_color, check.rest.text_color, steps
                    )
                    import numpy as np
                    back_opacitys = np.linspace(float(uncheck.pressed.back_opacity), float(check.rest.back_opacity),
                                                steps).tolist()
                    border_color_opacitys = np.linspace(float(uncheck.pressed.border_color_opacity), float(check.rest.border_color_opacity),
                                                steps).tolist()
                    border_color2_opacitys = np.linspace(float(uncheck.pressed.border_color2_opacity),
                                                        float(check.rest.border_color2_opacity),
                                                        steps).tolist()
                for i in range(steps):
                    def update(ii=i):
                        from easydict import EasyDict
                        tempcolor = EasyDict(
                            {
                                "back_color": back_colors[ii],
                                "back_opacity": back_opacitys[ii],
                                "border_color": border_colors[ii],
                                "border_color_opacity": str(border_color_opacitys[ii]),
                                "border_color2": border_colors2[ii],
                                "border_color2_opacity": str(border_color2_opacitys[ii]),
                                "border_width": 1,
                                "text_color": text_colors[ii],
                                "radius": 6,
                            }
                        )
                        self._draw(None, tempcolor)
                    self.after(i*animation_step_time, update)
                self.after(steps*animation_step_time+10, lambda: self._draw(None, None))
            else:
                if self.attributes.checked:
                    self.attributes.checked = False
                else:
                    self.attributes.checked = True
                self._draw()