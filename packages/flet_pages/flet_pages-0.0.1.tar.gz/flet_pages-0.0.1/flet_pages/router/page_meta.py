from dataclasses import dataclass
import flet as ft
from typing import Callable as collableble

@dataclass
class PageMeta:
    label:str
    func:collableble
    title:collableble
    icon: ft.Icons = ft.Icons.INFO_ROUNDED
    selected_icon: ft.Icons = ft.Icons.INFO_OUTLINED

