"""
Level Editor - Главное приложение редактора уровней

Использует Dear ImGui для создания модульного интерфейса в стиле Blender.
Поддерживает систему областей (Areas) с различными редакторами.
"""

import sys
import os
import pygame
import OpenGL.GL as gl
from OpenGL.GL import *
import imgui
from imgui.integrations.pygame import PygameRenderer

# Добавляем пути для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from .core.area_manager import AreaManager, Area, EditorType
from .editors.base_editor import BaseEditor
from .editors.viewport_3d import Viewport3DEditor
from .editors.outliner import OutlinerEditor
from .editors.properties import PropertiesEditor
from ..core.raymarcher import RayMarcher
from ..core.camera import Camera

class LevelEditor:
    """Главное приложение Level Editor"""
    
    def __init__(self, width: int = 1400, height: int = 900):
        self.width = width
        self.height = height
        self.running = True
        
        # Инициализация Pygame и OpenGL
        self._init_pygame()
        self._init_opengl()
        self._init_imgui()
        
        # Система управления областями
        self.area_manager = AreaManager()
        
        # Создание редакторов
        self.editors = {}
        self._create_editors()
        
        # Raymarcher для 3D viewport
        self.raymarcher = None
        self._init_raymarcher()
        
        # Главное меню
        self.show_main_menu = True
        
        # Состояние приложения
        self.show_demo_window = False
        self.show_about = False
        
    def _init_pygame(self):
        """Инициализация Pygame"""
        pygame.init()
        pygame.display.set_mode((self.width, self.height), 
                               pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE)
        pygame.display.set_caption("Intel Render Engine - Level Editor")
        
        self.clock = pygame.time.Clock()
        
    def _init_opengl(self):
        """Инициализация OpenGL"""
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0.1, 0.1, 0.1, 1.0)
        
    def _init_imgui(self):
        """Инициализация ImGui"""
        imgui.create_context()
        self.imgui_renderer = PygameRenderer()
        
        # Настройка IO
        io = imgui.get_io()
        io.display_size = self.width, self.height
        io.fonts.get_tex_data_as_rgba32()
        
        # Настройка стиля
        self._setup_imgui_style()
        
    def _setup_imgui_style(self):
        """Настройка стиля ImGui под Blender"""
        style = imgui.get_style()
        
        # Цвета в стиле Blender
        style.colors[imgui.COLOR_WINDOW_BACKGROUND] = (0.15, 0.15, 0.15, 1.0)
        style.colors[imgui.COLOR_CHILD_BACKGROUND] = (0.12, 0.12, 0.12, 1.0)
        style.colors[imgui.COLOR_POPUP_BACKGROUND] = (0.18, 0.18, 0.18, 1.0)
        style.colors[imgui.COLOR_FRAME_BACKGROUND] = (0.2, 0.2, 0.2, 1.0)
        style.colors[imgui.COLOR_FRAME_BACKGROUND_HOVERED] = (0.25, 0.25, 0.25, 1.0)
        style.colors[imgui.COLOR_FRAME_BACKGROUND_ACTIVE] = (0.3, 0.3, 0.3, 1.0)
        style.colors[imgui.COLOR_TITLE_BACKGROUND] = (0.1, 0.1, 0.1, 1.0)
        style.colors[imgui.COLOR_TITLE_BACKGROUND_ACTIVE] = (0.15, 0.4, 0.8, 1.0)
        style.colors[imgui.COLOR_BUTTON] = (0.2, 0.2, 0.2, 1.0)
        style.colors[imgui.COLOR_BUTTON_HOVERED] = (0.3, 0.3, 0.3, 1.0)
        style.colors[imgui.COLOR_BUTTON_ACTIVE] = (0.4, 0.4, 0.4, 1.0)
        style.colors[imgui.COLOR_HEADER] = (0.2, 0.2, 0.2, 1.0)
        style.colors[imgui.COLOR_HEADER_HOVERED] = (0.3, 0.3, 0.3, 1.0)
        style.colors[imgui.COLOR_HEADER_ACTIVE] = (0.4, 0.4, 0.4, 1.0)
        
        # Настройки размеров
        style.window_rounding = 0.0
        style.frame_rounding = 2.0
        style.grab_rounding = 2.0
        style.window_border_size = 1.0
        style.frame_border_size = 0.0
        
    def _create_editors(self):
        """Создание экземпляров редакторов"""
        # 3D Viewport
        self.viewport_editor = Viewport3DEditor()
        self.editors[EditorType.VIEWPORT_3D] = self.viewport_editor
        
        # Outliner
        self.outliner_editor = OutlinerEditor()
        self.editors[EditorType.OUTLINER] = self.outliner_editor
        
        # Properties
        self.properties_editor = PropertiesEditor()
        self.editors[EditorType.PROPERTIES] = self.properties_editor
        
        # TODO: Добавить другие редакторы
        
    def _init_raymarcher(self):
        """Инициализация raymarcher для 3D viewport"""
        try:
            self.raymarcher = RayMarcher(
                width=800, 
                height=600, 
                scene_name='demo',
                enable_hdr=True
            )
            
            # Подключаем raymarcher к viewport
            self.viewport_editor.set_raymarcher(self.raymarcher)
            
        except Exception as e:
            print(f"Ошибка инициализации raymarcher: {e}")
            
    def run(self):
        """Главный цикл приложения"""
        while self.running:
            self._handle_events()
            self._update()
            self._render()
            
            self.clock.tick(60)  # 60 FPS
            
        self._cleanup()
        
    def _handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            # Передаем события в ImGui
            self.imgui_renderer.process_event(event)
            
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.VIDEORESIZE:
                self.width, self.height = event.w, event.h
                glViewport(0, 0, self.width, self.height)
                
                # Обновляем размер для ImGui
                io = imgui.get_io()
                io.display_size = self.width, self.height
                
                self.area_manager.resize_window(self.width, self.height)
                
            elif event.type == pygame.KEYDOWN:
                self._handle_keyboard_shortcuts(event)
                
    def _handle_keyboard_shortcuts(self, event):
        """Обработка горячих клавиш"""
        if event.key == pygame.K_F12:
            # F12 - показать/скрыть demo window
            self.show_demo_window = not self.show_demo_window
            
        elif event.key == pygame.K_TAB:
            # Tab - переключение между редакторами
            active_area = self.area_manager.get_active_area()
            if active_area:
                self._cycle_editor_type(active_area)
                
    def _cycle_editor_type(self, area: Area):
        """Переключение типа редактора в области"""
        current_type = area.editor_type
        editor_types = list(EditorType)
        
        current_index = editor_types.index(current_type)
        next_index = (current_index + 1) % len(editor_types)
        
        area.editor_type = editor_types[next_index]
        
    def _update(self):
        """Обновление логики приложения"""
        # Синхронизация между редакторами
        self._sync_editors()
        
        # Обновление raymarcher
        if self.raymarcher:
            try:
                # Можно добавить обновление камеры и т.д.
                pass
            except Exception as e:
                print(f"Ошибка обновления raymarcher: {e}")
                
    def _sync_editors(self):
        """Синхронизация данных между редакторами"""
        # Синхронизация выбранных объектов между Outliner и Properties
        selected_objects = self.outliner_editor.get_selected_objects()
        
        if selected_objects:
            # Устанавливаем активный объект в Properties
            self.properties_editor.set_active_object(selected_objects[0])
        else:
            self.properties_editor.set_active_object(None)
            
    def _render(self):
        """Рендеринг кадра"""
        # Очистка экрана
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Начало нового кадра ImGui
        self.imgui_renderer.process_inputs()
        imgui.new_frame()
        
        # Рендеринг UI
        self._render_ui()
        
        # Завершение кадра ImGui
        imgui.render()
        self.imgui_renderer.render(imgui.get_draw_data())
        
        # Обновление экрана
        pygame.display.flip()
        
    def _render_ui(self):
        """Рендеринг пользовательского интерфейса"""
        # Главное меню
        if self.show_main_menu:
            self._render_main_menu()
            
        # Области с редакторами
        self._render_areas()
        
        # Дополнительные окна
        if self.show_demo_window:
            self.show_demo_window = imgui.show_demo_window(self.show_demo_window)[1]
            
        if self.show_about:
            self._render_about_window()
            
    def _render_main_menu(self):
        """Рендеринг главного меню"""
        if imgui.begin_main_menu_bar():
            # File меню
            if imgui.begin_menu("File"):
                if imgui.menu_item("New Scene")[0]:
                    self._new_scene()
                if imgui.menu_item("Open Scene")[0]:
                    self._open_scene()
                if imgui.menu_item("Save Scene")[0]:
                    self._save_scene()
                imgui.separator()
                if imgui.menu_item("Import")[0]:
                    self._import_objects()
                if imgui.menu_item("Export")[0]:
                    self._export_scene()
                imgui.separator()
                if imgui.menu_item("Exit")[0]:
                    self.running = False
                imgui.end_menu()
                
            # Edit меню
            if imgui.begin_menu("Edit"):
                if imgui.menu_item("Undo")[0]:
                    self._undo()
                if imgui.menu_item("Redo")[0]:
                    self._redo()
                imgui.separator()
                if imgui.menu_item("Preferences")[0]:
                    self._show_preferences()
                imgui.end_menu()
                
            # View меню
            if imgui.begin_menu("View"):
                if imgui.menu_item("Reset Layout")[0]:
                    self._reset_layout()
                if imgui.menu_item("Save Layout")[0]:
                    self._save_layout()
                if imgui.menu_item("Load Layout")[0]:
                    self._load_layout()
                imgui.end_menu()
                
            # Window меню
            if imgui.begin_menu("Window"):
                clicked, self.show_demo_window = imgui.menu_item(
                    "ImGui Demo", selected=self.show_demo_window)
                if imgui.menu_item("About")[0]:
                    self.show_about = True
                imgui.end_menu()
                
            # Help меню
            if imgui.begin_menu("Help"):
                if imgui.menu_item("Documentation")[0]:
                    self._show_documentation()
                if imgui.menu_item("Hotkeys")[0]:
                    self._show_hotkeys()
                if imgui.menu_item("About")[0]:
                    self.show_about = True
                imgui.end_menu()
                
            imgui.end_main_menu_bar()
            
    def _render_areas(self):
        """Рендеринг всех областей с их редакторами"""
        def render_area_content(area: Area):
            editor = self.editors.get(area.editor_type)
            if editor:
                editor.render()
            else:
                imgui.text(f"Editor {area.editor_type.value} not implemented")
                
        self.area_manager.render_areas(render_area_content)
        
    def _render_about_window(self):
        """Рендеринг окна About"""
        if imgui.begin("About Intel Render Engine", True)[0]:
            imgui.text("Intel Render Engine - Level Editor")
            imgui.text("Version 1.0")
            imgui.separator()
            imgui.text("A powerful real-time raymarching level editor")
            imgui.text("Built with Dear ImGui and OpenCL")
            imgui.separator()
            imgui.text("Features:")
            imgui.bullet_text("Modular area-based interface")
            imgui.bullet_text("Real-time raymarching preview")
            imgui.bullet_text("HDR rendering support")
            imgui.bullet_text("Material and lighting editor")
            imgui.separator()
            
            if imgui.button("Close"):
                self.show_about = False
                
        else:
            self.show_about = False
            
        imgui.end()
        
    def _new_scene(self):
        """Создать новую сцену"""
        # TODO: Implement new scene
        print("New scene")
        
    def _open_scene(self):
        """Открыть сцену"""
        # TODO: Implement open scene
        print("Open scene")
        
    def _save_scene(self):
        """Сохранить сцену"""
        # TODO: Implement save scene
        print("Save scene")
        
    def _import_objects(self):
        """Импорт объектов"""
        # TODO: Implement import
        print("Import objects")
        
    def _export_scene(self):
        """Экспорт сцены"""
        # TODO: Implement export
        print("Export scene")
        
    def _undo(self):
        """Отмена действия"""
        # TODO: Implement undo
        print("Undo")
        
    def _redo(self):
        """Повтор действия"""
        # TODO: Implement redo
        print("Redo")
        
    def _show_preferences(self):
        """Показать настройки"""
        # TODO: Implement preferences
        print("Show preferences")
        
    def _reset_layout(self):
        """Сброс раскладки"""
        self.area_manager._create_default_layout()
        
    def _save_layout(self):
        """Сохранить раскладку"""
        self.area_manager.save_layout("layouts/default.json")
        
    def _load_layout(self):
        """Загрузить раскладку"""
        self.area_manager.load_layout("layouts/default.json")
        
    def _show_documentation(self):
        """Показать документацию"""
        # TODO: Implement documentation
        print("Show documentation")
        
    def _show_hotkeys(self):
        """Показать горячие клавиши"""
        # TODO: Implement hotkeys window
        print("Show hotkeys")
        
    def _cleanup(self):
        """Очистка ресурсов"""
        if self.raymarcher:
            self.raymarcher.cleanup()
            
        self.imgui_renderer.shutdown()
        pygame.quit()

def main():
    """Точка входа в Level Editor"""
    editor = LevelEditor()
    editor.run()

if __name__ == "__main__":
    main()
