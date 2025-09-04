"""
3D Viewport Editor - Основной редактор для работы с 3D сценой

Отображает 3D сцену в реальном времени с использованием raymarching движка.
Поддерживает все стандартные инструменты для работы с объектами.
"""

import imgui
import numpy as np
from .base_editor import BaseEditor, EditorMode
from typing import Optional, List, Tuple
import pygame

class ViewportTool:
    """Инструменты для работы в 3D viewport"""
    SELECT = "select"
    MOVE = "move"
    ROTATE = "rotate" 
    SCALE = "scale"
    ADD = "add"

class Viewport3DEditor(BaseEditor):
    """Редактор 3D Viewport"""
    
    def __init__(self, editor_id: str = "viewport_3d"):
        super().__init__(editor_id)
        
        # Viewport settings
        self.viewport_width = 800
        self.viewport_height = 600
        self.viewport_surface = None
        
        # Camera settings
        self.camera_pos = np.array([0.0, 0.0, 5.0])
        self.camera_target = np.array([0.0, 0.0, 0.0])
        self.camera_speed = 5.0
        
        # Mouse and interaction
        self.mouse_sensitivity = 0.1
        self.is_mouse_captured = False
        self.last_mouse_pos = (0, 0)
        
        # Viewport modes
        self.shading_mode = "Solid"  # Solid, Wireframe, Material, Rendered
        self.show_grid = True
        self.show_axes = True
        self.show_statistics = True
        
        # Selected objects
        self.selected_objects = []
        self.active_object = None
        
        # Tools
        self.active_tool = ViewportTool.SELECT
        self.gizmo_visible = True
        
        # Raymarcher instance (will be injected)
        self.raymarcher = None
        
    def set_raymarcher(self, raymarcher):
        """Установить экземпляр raymarcher для рендеринга"""
        self.raymarcher = raymarcher
        
    def render_content(self):
        """Отрендерить содержимое 3D viewport"""
        # Получаем размер доступной области
        content_size = imgui.get_content_region_available()
        self.viewport_width = int(content_size.x)
        self.viewport_height = int(content_size.y)
        
        if self.viewport_width <= 0 or self.viewport_height <= 0:
            return
            
        # Рендерим 3D сцену
        self._render_3d_scene()
        
        # Overlay UI поверх 3D viewport
        self._render_overlay_ui()
        
    def _render_3d_scene(self):
        """Отрендерить 3D сцену используя raymarcher"""
        if not self.raymarcher:
            # Если нет raymarcher, показываем placeholder
            imgui.text("3D Viewport")
            imgui.text(f"Size: {self.viewport_width}x{self.viewport_height}")
            imgui.text("Raymarcher not connected")
            return
            
        try:
            # Обновляем размер raymarcher если нужно
            if (self.raymarcher.width != self.viewport_width or 
                self.raymarcher.height != self.viewport_height):
                self.raymarcher.resize(self.viewport_width, self.viewport_height)
                
            # Рендерим кадр
            frame = self.raymarcher.render_frame()
            
            if frame is not None:
                # Создаем текстуру из кадра для отображения в ImGui
                # TODO: Интеграция с OpenGL текстурами для ImGui
                imgui.text(f"Rendered frame: {frame.shape}")
            else:
                imgui.text("Failed to render frame")
                
        except Exception as e:
            imgui.text(f"Render error: {e}")
            
    def _render_overlay_ui(self):
        """Отрендерить UI поверх 3D viewport"""
        # Статистика производительности
        if self.show_statistics:
            self._render_statistics()
            
        # Gizmo для трансформации объектов
        if self.gizmo_visible and self.active_object:
            self._render_gizmo()
            
        # Сетка и оси
        if self.show_grid or self.show_axes:
            self._render_grid_and_axes()
            
    def _render_statistics(self):
        """Отрендерить статистику"""
        # Позиционируем в левом верхнем углу
        draw_list = imgui.get_window_draw_list()
        pos = imgui.get_cursor_screen_pos()
        
        stats_text = [
            f"Camera: {self.camera_pos[0]:.2f}, {self.camera_pos[1]:.2f}, {self.camera_pos[2]:.2f}",
            f"Tool: {self.active_tool}",
            f"Mode: {self.mode.value}",
            f"Objects: {len(self.selected_objects)} selected"
        ]
        
        y_offset = 10
        for text in stats_text:
            draw_list.add_text(pos.x + 10, pos.y + y_offset, 
                             imgui.get_color_u32_rgba(1, 1, 1, 1), text)
            y_offset += 20
            
    def _render_gizmo(self):
        """Отрендерить gizmo для трансформации"""
        # Упрощенный gizmo - можно улучшить
        imgui.text("Gizmo (TODO: Implement)")
        
    def _render_grid_and_axes(self):
        """Отрендерить сетку и оси координат"""
        # TODO: Implement grid and axes rendering
        pass
        
    def _render_tools(self):
        """Отрендерить инструменты viewport"""
        imgui.text("Tools")
        imgui.separator()
        
        # Инструменты выбора и трансформации
        tools = [
            (ViewportTool.SELECT, "Select", "S"),
            (ViewportTool.MOVE, "Move", "G"),
            (ViewportTool.ROTATE, "Rotate", "R"),
            (ViewportTool.SCALE, "Scale", "S"),
            (ViewportTool.ADD, "Add", "A")
        ]
        
        for tool, name, hotkey in tools:
            is_active = self.active_tool == tool
            if is_active:
                imgui.push_style_color(imgui.COLOR_BUTTON, 0.2, 0.6, 0.2, 1.0)
                
            if imgui.button(f"{name}\n({hotkey})", width=50, height=40):
                self.active_tool = tool
                
            if is_active:
                imgui.pop_style_color()
                
    def _render_sidebar_content(self):
        """Отрендерить содержимое боковой панели"""
        imgui.text("Viewport Settings")
        imgui.separator()
        
        # Настройки отображения
        if imgui.collapsing_header("Display"):
            clicked, self.show_grid = imgui.checkbox("Show Grid", self.show_grid)
            clicked, self.show_axes = imgui.checkbox("Show Axes", self.show_axes)
            clicked, self.show_statistics = imgui.checkbox("Show Statistics", self.show_statistics)
            clicked, self.gizmo_visible = imgui.checkbox("Show Gizmo", self.gizmo_visible)
            
        # Режим затенения
        if imgui.collapsing_header("Shading"):
            shading_modes = ["Solid", "Wireframe", "Material", "Rendered"]
            for mode in shading_modes:
                clicked, selected = imgui.selectable(mode, mode == self.shading_mode)
                if clicked:
                    self.shading_mode = mode
                    
        # Настройки камеры
        if imgui.collapsing_header("Camera"):
            changed, self.camera_speed = imgui.slider_float("Speed", self.camera_speed, 0.1, 20.0)
            changed, self.mouse_sensitivity = imgui.slider_float("Mouse Sensitivity", self.mouse_sensitivity, 0.01, 1.0)
            
            if imgui.button("Reset Camera"):
                self.reset_camera()
                
        # Информация о выбранном объекте
        if imgui.collapsing_header("Selection"):
            if self.active_object:
                imgui.text(f"Active: {self.active_object}")
                imgui.text(f"Selected: {len(self.selected_objects)}")
            else:
                imgui.text("No selection")
                
    def _render_view_options(self):
        """Переопределить опции отображения для viewport"""
        super()._render_view_options()
        
        imgui.same_line()
        if imgui.button("Shading"):
            imgui.open_popup("shading_options")
            
        if imgui.begin_popup("shading_options"):
            shading_modes = ["Solid", "Wireframe", "Material", "Rendered"]
            for mode in shading_modes:
                clicked, selected = imgui.selectable(mode, mode == self.shading_mode)
                if clicked:
                    self.shading_mode = mode
            imgui.end_popup()
            
    def handle_mouse_input(self, mouse_pos: Tuple[int, int], mouse_buttons: Tuple[bool, bool, bool]):
        """Обработать ввод мыши"""
        # TODO: Implement mouse handling for camera control and object selection
        self.last_mouse_pos = mouse_pos
        
    def handle_keyboard_input(self, keys):
        """Обработать ввод клавиатуры"""
        # TODO: Implement keyboard shortcuts
        pass
        
    def select_object(self, object_id: str):
        """Выбрать объект"""
        if object_id not in self.selected_objects:
            self.selected_objects.append(object_id)
        self.active_object = object_id
        
    def deselect_object(self, object_id: str):
        """Отменить выбор объекта"""
        if object_id in self.selected_objects:
            self.selected_objects.remove(object_id)
        if self.active_object == object_id:
            self.active_object = self.selected_objects[0] if self.selected_objects else None
            
    def clear_selection(self):
        """Очистить выбор"""
        self.selected_objects.clear()
        self.active_object = None
        
    def reset_camera(self):
        """Сбросить камеру в исходное положение"""
        self.camera_pos = np.array([0.0, 0.0, 5.0])
        self.camera_target = np.array([0.0, 0.0, 0.0])
        
    def focus_on_selection(self):
        """Сфокусировать камеру на выбранных объектах"""
        # TODO: Implement focus on selection
        pass
        
    def set_viewport_size(self, width: int, height: int):
        """Установить размер viewport"""
        self.viewport_width = width
        self.viewport_height = height
