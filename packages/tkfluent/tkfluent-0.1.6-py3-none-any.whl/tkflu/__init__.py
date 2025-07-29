"""

Fluent设计的tkinter组件库（模板）

-------------
作者：XiangQinxi

贡献者：totowang-hhh
-------------
"""

from .badge import FluBadge
from .button import FluButton
from .bwm import BWm
from .constants import *
from .defs import *
from .entry import FluEntry
from .frame import FluFrame
from .icons import *
from .label import FluLabel
from .menu import FluMenu
from .menubar import FluMenuBar
from .popupmenu import FluPopupMenu, FluPopupMenuWindow
from .popupwindow import FluPopupWindow
from .scrollbar import FluScrollBar
from .slider import FluSlider
from .text import FluText
from .thememanager import FluThemeManager
from .togglebutton import FluToggleButton
from .tooltip import FluToolTip, FluToolTip2, FluToolTipBase
from .toplevel import FluToplevel
from .window import FluWindow

from .designs import *

FluChip = FluBadge
FluPushButton = FluButton
FluTextInput = FluEntry
FluTextBox = FluText
FluPanel = FluFrame
FluMainWindow = FluWindow
FluSubWindow = FluToplevel

# 