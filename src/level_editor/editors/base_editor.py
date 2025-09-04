"""
Base Editor - Базовый класс для всех редакторов

Все редакторы наследуются от этого класса и реализуют свою логику.
Каждый редактор имеет свое меню, панели инструментов и контекстные действия.
"""

import imgui
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum

class EditorMode(Enum):
    """Режимы работы редактора"""
    OBJECT = "Object Mode"
    EDIT = "Edit Mode"
    SCULPT = "Sculpt Mode"
    TEXTURE = "Texture Mode"
    MATERIAL = "Material Mode"

class BaseEditor(ABC):
    """Базовый класс для всех редакторов"""
    
    def __init__(self, editor_id: str):
        self.editor_id = editor_id
        self.mode = EditorMode.OBJECT
        self.is_focused = False
        self.show_toolbar = True
        self.show_sidebar = True
        self.context_data = {}
        
    @abstractmethod
    def render_content(self):
        """Отрендерить основное содержимое редактора"""
        pass
        
    def render_header(self):
        """Отрендерить заголовок редактора (верхняя панель)"""
        if imgui.begin_menu_bar():
            self._render_mode_selector()
            self._render_view_options()
            self._render_editor_menu()
            imgui.end_menu_bar()
            
    def _render_mode_selector(self):
        """Отрендерить селектор режимов"""
        if imgui.begin_combo("Mode", self.mode.value):
            for mode in EditorMode:
                clicked, selected = imgui.selectable(mode.value, mode == self.mode)
                if clicked:
                    self.mode = mode
            imgui.end_combo()
            
    def _render_view_options(self):
        """Отрендерить опции отображения"""
        imgui.same_line()
        if imgui.button("View"):
            imgui.open_popup("view_options")
            
        if imgui.begin_popup("view_options"):
            clicked, self.show_toolbar = imgui.checkbox("Show Toolbar", self.show_toolbar)
            clicked, self.show_sidebar = imgui.checkbox("Show Sidebar", self.show_sidebar)
            imgui.end_popup()
            
    def _render_editor_menu(self):
        """Отрендерить меню редактора"""
        imgui.same_line()
        if imgui.begin_menu("Editor"):
            if imgui.menu_item("Reset View")[0]:
                self.reset_view()
            if imgui.menu_item("Properties")[0]:
                self.show_properties()
            imgui.end_menu()
            
    def render_toolbar(self):
        """Отрендерить панель инструментов (левая панель)"""
        if not self.show_toolbar:
            return
            
        imgui.begin_child("toolbar", width=60, height=0, border=True)
        self._render_tools()
        imgui.end_child()
        
    def _render_tools(self):
        """Отрендерить инструменты (переопределяется в наследниках)"""
        imgui.text("Tools")
        if imgui.button("Select", width=50):
            self.set_tool("select")
        if imgui.button("Move", width=50):
            self.set_tool("move")
        if imgui.button("Rotate", width=50):
            self.set_tool("rotate")
        if imgui.button("Scale", width=50):
            self.set_tool("scale")
            
    def render_sidebar(self):
        """Отрендерить боковую панель (правая панель)"""
        if not self.show_sidebar:
            return
            
        imgui.same_line()
        imgui.begin_child("sidebar", width=200, height=0, border=True)
        self._render_sidebar_content()
        imgui.end_child()
        
    def _render_sidebar_content(self):
        """Отрендерить содержимое боковой панели"""
        imgui.text("Properties")
        imgui.separator()
        # Переопределяется в наследниках
        
    def render(self):
        """Основной метод рендеринга редактора"""
        # Заголовок с меню
        self.render_header()
        
        # Основная область с тулбаром и сайдбаром
        if self.show_toolbar:
            self.render_toolbar()
            imgui.same_line()
            
        # Центральная область
        available_width = imgui.get_content_region_available_width()
        if self.show_sidebar:
            available_width -= 210  # Ширина сайдбара + отступы
            
        imgui.begin_child("content", width=available_width, height=0)
        self.render_content()
        imgui.end_child()
        
        # Сайдбар
        if self.show_sidebar:
            self.render_sidebar()
            
    def set_tool(self, tool_name: str):
        """Установить активный инструмент"""
        self.context_data['active_tool'] = tool_name
        
    def get_tool(self) -> str:
        """Получить активный инструмент"""
        return self.context_data.get('active_tool', 'select')
        
    def reset_view(self):
        """Сбросить вид (переопределяется в наследниках)"""
        pass
        
    def show_properties(self):
        """Показать окно свойств"""
        pass
        
    def set_context_data(self, key: str, value: Any):
        """Установить контекстные данные"""
        self.context_data[key] = value
        
    def get_context_data(self, key: str, default: Any = None) -> Any:
        """Получить контекстные данные"""
        return self.context_data.get(key, default)
