# Copyright (c) 2022, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.

import omni.kit.ui

MENU_PATH = "Window/OSC"


class OscMenu:
    def __init__(self, on_click):
        editor_menu = omni.kit.ui.get_editor_menu()
        if not editor_menu:
            return
        editor_menu.add_item(menu_path=MENU_PATH, on_click=on_click, toggle=True, value=True)

    def set_item_value(self, val: bool) -> None:
        editor_menu = omni.kit.ui.get_editor_menu()
        if not editor_menu:
            return
        editor_menu.set_value(MENU_PATH, val)

    def __del__(self):
        editor_menu = omni.kit.ui.get_editor_menu()
        if not editor_menu:
            return
        if editor_menu.has_item(MENU_PATH):
            editor_menu.remove_item(MENU_PATH)
