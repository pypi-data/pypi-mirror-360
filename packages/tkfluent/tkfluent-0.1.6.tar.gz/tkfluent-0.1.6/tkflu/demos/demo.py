def run():
    from tkflu import *
    from tkinter import *
    from tkinter.font import *

    blue_primary_color()
    set_animation_steps(0)
    set_animation_step_time(0)

    def togglestate():
        if button1.dcget("state") == NORMAL:
            button1.dconfigure(state=DISABLED)
            button2.dconfigure(state=DISABLED)
            entry1.dconfigure(state=DISABLED)
            text1.dconfigure(state=DISABLED)
            togglebutton1.dconfigure(state=DISABLED)
            slider1.dconfigure(state=DISABLED)
        else:
            button1.dconfigure(state=NORMAL)
            button2.dconfigure(state=NORMAL)
            entry1.dconfigure(state=NORMAL)
            text1.dconfigure(state=NORMAL)
            togglebutton1.dconfigure(state=NORMAL)
            slider1.dconfigure(state=NORMAL)
        button1._draw()
        button2._draw()
        entry1._draw()
        text1._draw()
        togglebutton1._draw()
        slider1._draw()

    root = FluWindow()
    #root.wincustom(way=0)
    root.geometry("360x650")

    popupmenu = FluPopupMenu()

    thememanager = FluThemeManager()

    menubar = FluMenuBar(root)
    menubar.add_command(
        label="FluMenu1", command=lambda: print("FluMenu1 -> Clicked")
    )

    menu1 = FluMenu()
    menu1.add_command(
        label="FluMenu2-1", command=lambda: print("FluMenu2-1 -> Clicked")
    )
    menubar.add_cascade(
        label="FluMenu2", menu=menu1
    )

    menu2 = FluMenu(height=93)
    menu2.add_command(
        label="FluMenu3-1", command=lambda: print("FluMenu3-1 -> Clicked")
    )

    menu3 = FluMenu(height=93)
    menu3.add_command(
        label="FluMenu3-2-1", command=lambda: print("FluMenu3-2-1 -> Clicked")
    )
    menu3.add_command(
        label="FluMenu3-2-2", command=lambda: print("FluMenu3-2-2 -> Clicked")
    )

    menu2.add_cascade(
        label="FluMenu3-2", menu=menu3
    )
    menubar.add_cascade(
        label="FluMenu3", menu=menu2
    )

    menubar.pack(fill="x")

    frame = FluFrame(root)

    scrollbar1 = FluScrollBar(frame)
    scrollbar1.pack(fill="y", side="right", padx=5, pady=5)

    badge1 = FluBadge(frame, text="FluBadge", width=60)
    badge1.pack(padx=5, pady=5)

    badge2 = FluBadge(frame, text="FluBadge (Accent)", width=120, style="accent")
    badge2.pack(padx=5, pady=5)

    label1 = FluLabel(frame, text="FluLabel(Hover Me)")
    label1.tooltip(text="FluToolTip")
    label1.pack(padx=5, pady=5)

    label2 = FluLabel(frame, text="FluLabel2(Hover Me)")
    label2.tooltip(text="FluToolTip2", way=1)
    label2.pack(padx=5, pady=5)

    button1 = FluButton(
        frame, text="FluButton", command=lambda: print("FluButton -> Clicked")
    )
    button1.pack(fill="x", padx=5, pady=5)

    button2 = FluButton(
        frame, text="FluButton (Accent)", command=lambda: print("FluButton (Accent) -> Clicked"), style="accent"
    )
    button2.pack(fill="x", padx=5, pady=5)

    togglebutton1 = FluToggleButton(
        frame, text="FluToggleButton", command=lambda: print(f"FluToggleButton -> Toggled -> Checked: {togglebutton1.dcget('checked')}")
    )
    togglebutton1.pack(fill="x", padx=5, pady=5)

    togglebutton2 = FluToggleButton(
        frame, text="Toggle Theme", command=lambda: toggle_theme(togglebutton2, thememanager)
    )
    togglebutton2.pack(fill="x", padx=5, pady=5)

    togglebutton3 = FluToggleButton(
        frame, text="Toggle State", command=lambda: togglestate()
    )
    togglebutton3.pack(fill="x", padx=5, pady=5)

    entry1 = FluEntry(frame)
    entry1.pack(fill="x", padx=5, pady=5)

    text1 = FluText(frame)
    text1.pack(fill="x", padx=5, pady=5)

    slider1 = FluSlider(frame, value=5, min=0, max=10, tick=True, changed=lambda: print(f"FluSlider -> Changed -> Value: {slider1.dcget('value')}"))
    slider1.pack(fill="x", padx=5, pady=5)

    """listbox1 = FluListBox(frame)
    listbox1.dconfigure()
    listbox1.pack(fill="x", padx=5, pady=5)"""

    frame.pack(fill="both", expand="yes", side="right", padx=15, pady=15)
    #frame.update_idletasks()

    #thememanager.mode("light")

    root.mainloop()
