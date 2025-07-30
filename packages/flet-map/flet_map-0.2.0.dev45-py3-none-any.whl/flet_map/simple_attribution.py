from dataclasses import field
from typing import Union

import flet as ft

from .map_layer import MapLayer

__all__ = ["SimpleAttribution"]


@ft.control("SimpleAttribution")
class SimpleAttribution(MapLayer):
    """
    A simple attribution layer displayed on the Map.
    """

    text: Union[str, ft.Text]
    """
    The attribution message to be displayed.
    
    Value is of type `str` and `ft.Text`.
    """

    alignment: ft.Alignment = field(default_factory=lambda: ft.Alignment.bottom_right())
    """
    The alignment of this attribution on the map.
    """

    bgcolor: ft.ColorValue = ft.Colors.SURFACE
    """
    The color of the box containing the `text`.
    """

    on_click: ft.OptionalControlEventHandler["SimpleAttribution"] = None
    """Fired when this attribution is clicked/pressed."""
