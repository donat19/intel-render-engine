#!/usr/bin/env python3
"""
Level Editor с OpenCL GUI - Полная замена ImGui

Использует собственную OpenCL GUI систему вместо ImGui.
Вся GUI рендерится на GPU как часть основного рендеринг пайплайна.
"""
import pygame
import numpy as np
import time
import os
import sys
from typing import Optional, Dict, Any, Callable

# Добавляем пути
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from src.gui.opencl_gui import (
    OpenCLGUI, GUITheme, Button, Text, Panel, Slider,
    create_main_menu, create_fps_display, create_camera_info_panel, 
    create_render_settings_panel, Color, Rect
)
from src.core.raymarcher import RayMarcher

class OpenCLLevelEditor:
    """Level Editor с полностью OpenCL GUI системой"""
    
    def __init__(self, width: int = 1400, height: int = 900):
        self.width = width
        self.height = height
        self.running = True
        
        # Инициализация Pygame
        self._init_pygame()
        
        # Инициализация Raymarcher (основной рендерер)
        self._init_raymarcher()
        
        # Инициализация OpenCL GUI системы
        self._init_opencl_gui()
        
        # Создание UI элементов
        self._create_ui_elements()
        
        # Состояние приложения
        self.last_frame_time = time.time()
        self.fps_counter = 0
        self.fps_display_timer = 0.0
        self.current_fps = 60.0
        
        # Состояние камеры и рендера для GUI
        self.camera_info_dirty = True
        self.render_settings_dirty = True
        
        print("🎨 OpenCL Level Editor инициализирован")
        print(f"📐 Разрешение: {width}x{height}")
        print(f"🎬 Raymarcher: готов")
        print(f"🖥️ OpenCL GUI: готов")
    
    def _init_pygame(self):
        """Инициализация Pygame"""
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("Intel Render Engine - Level Editor (OpenCL GUI)")
        self.clock = pygame.time.Clock()
        
        # Клавиши и мышь
        self.keys_pressed = set()
        self.mouse_pos = (0, 0)
        self.mouse_buttons = [False, False, False]
        
    def _init_raymarcher(self):
        """Инициализация Raymarcher"""
        try:
            self.raymarcher = RayMarcher(self.width, self.height, scene_name='demo', enable_hdr=True)
            print("✅ Raymarcher инициализирован")
        except Exception as e:
            print(f"❌ Ошибка инициализации Raymarcher: {e}")
            print("💡 Убедитесь что raymarcher.py находится в корневой директории")
            self.raymarcher = None
    
    def _init_opencl_gui(self):
        """Инициализация OpenCL GUI системы"""
        if self.raymarcher:
            try:
                # Используем тот же OpenCL контекст что и raymarcher
                self.gui = OpenCLGUI(
                    cl_context=self.raymarcher.context,
                    cl_queue=self.raymarcher.queue,
                    width=self.width,
                    height=self.height,
                    theme=GUITheme.BLENDER
                )
                print("✅ OpenCL GUI инициализирован")
            except Exception as e:
                print(f"❌ Ошибка инициализации OpenCL GUI: {e}")
                self.gui = None
        else:
            print("❌ OpenCL GUI не может быть инициализирован без Raymarcher")
            self.gui = None
    
    def _create_ui_elements(self):
        """Создание элементов пользовательского интерфейса"""
        if not self.gui:
            return
        
        # Главное меню
        self._create_main_menu()
        
        # Панель FPS
        self._create_fps_panel()
        
        # Панель информации о камере
        self._create_camera_panel()
        
        # Панель настроек рендера
        self._create_render_panel()
        
        # Панель инструментов
        self._create_tools_panel()
        
        # Статусная строка
        self._create_status_bar()
        
        print("🎛️ UI элементы созданы")
    
    def _create_main_menu(self):
        """Создание главного меню"""
        # Фон меню
        menu_bg = self.gui.create_panel("menu_bg", 0, 0, self.width, 30, "")
        menu_bg.colors['normal'] = Color(0.1, 0.1, 0.1, 0.95)
        
        # Кнопки меню
        self.gui.create_button("menu_file", 10, 5, 60, 20, "File", 
                              on_click=self._on_menu_file_click)
        self.gui.create_button("menu_edit", 80, 5, 60, 20, "Edit",
                              on_click=self._on_menu_edit_click)
        self.gui.create_button("menu_scene", 150, 5, 80, 20, "Scene",
                              on_click=self._on_menu_scene_click)
        self.gui.create_button("menu_render", 240, 5, 80, 20, "Render",
                              on_click=self._on_menu_render_click)
        self.gui.create_button("menu_help", 330, 5, 60, 20, "Help",
                              on_click=self._on_menu_help_click)
    
    def _create_fps_panel(self):
        """Создание панели FPS"""
        # Фон панели
        fps_bg = self.gui.create_panel("fps_bg", self.width - 200, 35, 195, 60, "Performance")
        fps_bg.colors['normal'] = Color(0.05, 0.05, 0.05, 0.9)
        
        # Текст FPS
        self.fps_text = self.gui.create_text("fps_text", self.width - 190, 55, "FPS: 60.0")
        self.fps_text.colors['text'] = Color(0.0, 1.0, 0.0, 1.0)
        
        # Время рендера
        self.render_time_text = self.gui.create_text("render_time", self.width - 190, 75, "Render: 16.7ms")
        self.render_time_text.colors['text'] = Color(0.0, 0.8, 1.0, 1.0)
    
    def _create_camera_panel(self):
        """Создание панели информации о камере"""
        # Фон панели
        cam_bg = self.gui.create_panel("camera_bg", 10, 35, 280, 140, "Camera")
        cam_bg.colors['normal'] = Color(0.05, 0.05, 0.05, 0.9)
        
        # Информация о позиции
        self.camera_pos_text = self.gui.create_text("camera_pos", 20, 55, "Position: 0.0, 0.0, 5.0")
        self.camera_pos_text.colors['text'] = Color(0.9, 0.9, 0.9, 1.0)
        
        # Информация об углах
        self.camera_angles_text = self.gui.create_text("camera_angles", 20, 75, "Angles: 0.0°, 0.0°, 0.0°")
        self.camera_angles_text.colors['text'] = Color(0.9, 0.9, 0.9, 1.0)
        
        # Скорость камеры
        self.gui.create_text("camera_speed_label", 20, 95, "Speed:")
        self.camera_speed_slider = self.gui.create_slider("camera_speed", 70, 95, 150, 20, 0.1, 10.0, 1.0,
                                                         on_change=self._on_camera_speed_change)
        self.camera_speed_text = self.gui.create_text("camera_speed_value", 230, 95, "1.0")
        
        # Чувствительность мыши
        self.gui.create_text("mouse_sens_label", 20, 120, "Mouse:")
        self.mouse_sens_slider = self.gui.create_slider("mouse_sens", 70, 120, 150, 20, 0.001, 0.01, 0.005,
                                                       on_change=self._on_mouse_sens_change)
        
        # Кнопка сброса камеры
        self.gui.create_button("reset_camera", 20, 145, 80, 25, "Reset Cam",
                              on_click=self._on_reset_camera_click)
    
    def _create_render_panel(self):
        """Создание панели настроек рендера"""
        # Фон панели
        render_bg = self.gui.create_panel("render_bg", 300, 35, 250, 200, "Render Settings")
        render_bg.colors['normal'] = Color(0.05, 0.05, 0.05, 0.9)
        
        # HDR настройки
        self.gui.create_text("hdr_label", 310, 55, "HDR Settings")
        
        # Exposure
        self.gui.create_text("exposure_label", 310, 75, "Exposure:")
        self.exposure_slider = self.gui.create_slider("exposure", 380, 75, 120, 20, 0.1, 5.0, 1.0,
                                                    on_change=self._on_exposure_change)
        self.exposure_text = self.gui.create_text("exposure_value", 510, 75, "1.0")
        
        # Gamma
        self.gui.create_text("gamma_label", 310, 100, "Gamma:")
        self.gamma_slider = self.gui.create_slider("gamma", 380, 100, 120, 20, 1.0, 3.0, 2.2,
                                                 on_change=self._on_gamma_change)
        self.gamma_text = self.gui.create_text("gamma_value", 510, 100, "2.2")
        
        # Tone Mapping кнопки
        self.gui.create_text("tone_mapping_label", 310, 125, "Tone Mapping:")
        self.gui.create_button("tm_linear", 310, 145, 50, 25, "Linear",
                              on_click=lambda btn: self._set_tone_mapping('linear'))
        self.gui.create_button("tm_reinhard", 365, 145, 50, 25, "Reinh",
                              on_click=lambda btn: self._set_tone_mapping('reinhard'))
        self.gui.create_button("tm_filmic", 420, 145, 50, 25, "Filmic",
                              on_click=lambda btn: self._set_tone_mapping('filmic'))
        self.gui.create_button("tm_aces", 475, 145, 50, 25, "ACES",
                              on_click=lambda btn: self._set_tone_mapping('aces'))
        
        # Сцены
        self.gui.create_text("scene_label", 310, 175, "Scene:")
        self.gui.create_button("scene_demo", 310, 195, 50, 25, "Demo",
                              on_click=lambda btn: self._switch_scene('demo'))
        self.gui.create_button("scene_clouds", 365, 195, 50, 25, "Clouds",
                              on_click=lambda btn: self._switch_scene('clouds'))
        self.gui.create_button("scene_adv_clouds", 420, 195, 80, 25, "Adv Clouds",
                              on_click=lambda btn: self._switch_scene('advanced_clouds'))
    
    def _create_tools_panel(self):
        """Создание панели инструментов"""
        # Фон панели
        tools_bg = self.gui.create_panel("tools_bg", self.width - 200, 100, 195, 200, "Tools")
        tools_bg.colors['normal'] = Color(0.05, 0.05, 0.05, 0.9)
        
        # Инструменты редактора
        self.gui.create_button("tool_select", self.width - 190, 120, 80, 30, "Select",
                              on_click=self._on_tool_select_click)
        self.gui.create_button("tool_move", self.width - 100, 120, 80, 30, "Move",
                              on_click=self._on_tool_move_click)
        
        self.gui.create_button("tool_rotate", self.width - 190, 155, 80, 30, "Rotate",
                              on_click=self._on_tool_rotate_click)
        self.gui.create_button("tool_scale", self.width - 100, 155, 80, 30, "Scale",
                              on_click=self._on_tool_scale_click)
        
        # Режимы отображения
        self.gui.create_text("display_label", self.width - 190, 195, "Display Mode:")
        self.gui.create_button("display_solid", self.width - 190, 215, 60, 25, "Solid",
                              on_click=self._on_display_solid_click)
        self.gui.create_button("display_wireframe", self.width - 125, 215, 60, 25, "Wire",
                              on_click=self._on_display_wireframe_click)
        
        # Настройки GUI
        self.gui.create_text("gui_label", self.width - 190, 250, "GUI Theme:")
        self.gui.create_button("theme_dark", self.width - 190, 270, 45, 25, "Dark",
                              on_click=lambda btn: self._set_theme(GUITheme.DARK))
        self.gui.create_button("theme_light", self.width - 140, 270, 45, 25, "Light",
                              on_click=lambda btn: self._set_theme(GUITheme.LIGHT))
        self.gui.create_button("theme_cyber", self.width - 90, 270, 45, 25, "Cyber",
                              on_click=lambda btn: self._set_theme(GUITheme.CYBERPUNK))
    
    def _create_status_bar(self):
        """Создание статусной строки"""
        # Фон статусной строки
        status_bg = self.gui.create_panel("status_bg", 0, self.height - 25, self.width, 25, "")
        status_bg.colors['normal'] = Color(0.08, 0.08, 0.08, 0.95)
        
        # Статусный текст
        self.status_text = self.gui.create_text("status_text", 10, self.height - 20, "Ready | OpenCL GUI Active")
        self.status_text.colors['text'] = Color(0.7, 0.7, 0.7, 1.0)
        
        # Информация о версии
        self.version_text = self.gui.create_text("version_text", self.width - 200, self.height - 20, 
                                               "Intel Render Engine v2.0")
        self.version_text.colors['text'] = Color(0.5, 0.5, 0.5, 1.0)
    
    # Callback функции для GUI элементов
    def _on_menu_file_click(self, button: Button):
        """Обработка клика по меню File"""
        print("📁 File menu clicked")
        self._update_status("File menu opened")
    
    def _on_menu_edit_click(self, button: Button):
        """Обработка клика по меню Edit"""
        print("✏️ Edit menu clicked")
        self._update_status("Edit menu opened")
    
    def _on_menu_scene_click(self, button: Button):
        """Обработка клика по меню Scene"""
        print("🎬 Scene menu clicked")
        self._update_status("Scene menu opened")
    
    def _on_menu_render_click(self, button: Button):
        """Обработка клика по меню Render"""
        print("🎨 Render menu clicked")
        self._update_status("Render menu opened")
    
    def _on_menu_help_click(self, button: Button):
        """Обработка клика по меню Help"""
        print("❓ Help menu clicked")
        self._update_status("Help: WASD - move, Mouse - look, F11 - fullscreen")
    
    def _on_camera_speed_change(self, slider: Slider):
        """Изменение скорости камеры"""
        if self.raymarcher:
            self.raymarcher.set_camera_speed(slider.value)
            self.camera_speed_text.text = f"{slider.value:.1f}"
            print(f"📷 Camera speed: {slider.value:.1f}")
    
    def _on_mouse_sens_change(self, slider: Slider):
        """Изменение чувствительности мыши"""
        if self.raymarcher:
            self.raymarcher.set_mouse_sensitivity(slider.value)
            print(f"🖱️ Mouse sensitivity: {slider.value:.3f}")
    
    def _on_reset_camera_click(self, button: Button):
        """Сброс камеры"""
        if self.raymarcher:
            self.raymarcher.reset_camera()
            self._update_status("Camera reset to default position")
            print("📷 Camera reset")
    
    def _on_exposure_change(self, slider: Slider):
        """Изменение exposure"""
        if self.raymarcher:
            self.raymarcher.set_exposure(slider.value)
            self.exposure_text.text = f"{slider.value:.2f}"
            print(f"💡 Exposure: {slider.value:.2f}")
    
    def _on_gamma_change(self, slider: Slider):
        """Изменение gamma"""
        if self.raymarcher:
            self.raymarcher.set_gamma(slider.value)
            self.gamma_text.text = f"{slider.value:.2f}"
            print(f"🎛️ Gamma: {slider.value:.2f}")
    
    def _set_tone_mapping(self, mode: str):
        """Установка режима tone mapping"""
        if self.raymarcher:
            self.raymarcher.set_tone_mapping(mode)
            self._update_status(f"Tone mapping: {mode}")
            print(f"🎨 Tone mapping: {mode}")
    
    def _switch_scene(self, scene_name: str):
        """Переключение сцены"""
        if self.raymarcher:
            self.raymarcher.switch_scene(scene_name)
            self._update_status(f"Switched to scene: {scene_name}")
            print(f"🎬 Scene: {scene_name}")
    
    def _on_tool_select_click(self, button: Button):
        """Выбор инструмента Select"""
        self._update_status("Tool: Select")
        print("🎯 Tool: Select")
    
    def _on_tool_move_click(self, button: Button):
        """Выбор инструмента Move"""
        self._update_status("Tool: Move")
        print("📐 Tool: Move")
    
    def _on_tool_rotate_click(self, button: Button):
        """Выбор инструмента Rotate"""
        self._update_status("Tool: Rotate")
        print("🔄 Tool: Rotate")
    
    def _on_tool_scale_click(self, button: Button):
        """Выбор инструмента Scale"""
        self._update_status("Tool: Scale")
        print("📏 Tool: Scale")
    
    def _on_display_solid_click(self, button: Button):
        """Режим отображения Solid"""
        self._update_status("Display: Solid")
        print("🎨 Display: Solid")
    
    def _on_display_wireframe_click(self, button: Button):
        """Режим отображения Wireframe"""
        self._update_status("Display: Wireframe")
        print("📐 Display: Wireframe")
    
    def _set_theme(self, theme: GUITheme):
        """Установка темы GUI"""
        if self.gui:
            self.gui.set_theme(theme)
            self._update_status(f"Theme: {theme.value}")
            print(f"🎨 Theme: {theme.value}")
    
    def _update_status(self, message: str):
        """Обновление статусной строки"""
        if hasattr(self, 'status_text'):
            self.status_text.text = message
    
    def run(self):
        """Главный цикл приложения"""
        print("🚀 Запуск OpenCL Level Editor...")
        
        last_fps_update = time.time()
        frame_count = 0
        
        while self.running:
            current_time = time.time()
            delta_time = current_time - self.last_frame_time
            self.last_frame_time = current_time
            
            # Обработка событий
            self._handle_events()
            
            # Обновление состояния
            self._update(delta_time)
            
            # Рендеринг
            render_time = self._render()
            
            # Обновление FPS
            frame_count += 1
            if current_time - last_fps_update >= 1.0:
                self.current_fps = frame_count / (current_time - last_fps_update)
                frame_count = 0
                last_fps_update = current_time
                
                # Обновляем GUI элементы с FPS
                if hasattr(self, 'fps_text'):
                    self.fps_text.text = f"FPS: {self.current_fps:.1f}"
                if hasattr(self, 'render_time_text'):
                    self.render_time_text.text = f"Render: {render_time*1000:.1f}ms"
            
            # Ограничение FPS
            self.clock.tick(120)  # Максимум 120 FPS
        
        print("👋 OpenCL Level Editor завершен")
        self._cleanup()
    
    def _handle_events(self):
        """Обработка событий Pygame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
                
                # Глобальные горячие клавиши
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_F11:
                    self._toggle_fullscreen()
                elif event.key == pygame.K_F1:
                    self._toggle_help()
                
                # Передаем в GUI
                if self.gui:
                    self.gui.handle_keyboard_event(event.key, True)
            
            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)
                if self.gui:
                    self.gui.handle_keyboard_event(event.key, False)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_buttons[event.button - 1] = True
                if self.gui:
                    self.gui.handle_mouse_event(event.pos[0], event.pos[1], event.button - 1, True)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_buttons[event.button - 1] = False
                if self.gui:
                    self.gui.handle_mouse_event(event.pos[0], event.pos[1], event.button - 1, False)
            
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
                if self.gui:
                    self.gui.handle_mouse_event(event.pos[0], event.pos[1], -1, False)
                
                # Управление камерой мышью (если нет фокуса на GUI)
                if pygame.mouse.get_pressed()[0] and self.raymarcher:
                    rel_x, rel_y = event.rel
                    if abs(rel_x) > 0 or abs(rel_y) > 0:
                        self.raymarcher.handle_mouse_movement(rel_x * 0.005, rel_y * 0.005)
            
            elif event.type == pygame.VIDEORESIZE:
                self._handle_resize(event.w, event.h)
        
        # Обработка нажатых клавиш для движения камеры
        self._handle_camera_movement()
    
    def _handle_camera_movement(self):
        """Обработка движения камеры клавишами"""
        if not self.raymarcher:
            return
        
        # Движение камеры
        if pygame.K_w in self.keys_pressed:
            self.raymarcher.move_camera('forward')
        if pygame.K_s in self.keys_pressed:
            self.raymarcher.move_camera('backward')
        if pygame.K_a in self.keys_pressed:
            self.raymarcher.move_camera('left')
        if pygame.K_d in self.keys_pressed:
            self.raymarcher.move_camera('right')
        if pygame.K_q in self.keys_pressed:
            self.raymarcher.move_camera('down')
        if pygame.K_e in self.keys_pressed:
            self.raymarcher.move_camera('up')
        
        # Поворот камеры стрелками
        if pygame.K_LEFT in self.keys_pressed:
            self.raymarcher.rotate_camera(0, -0.02, 0)
        if pygame.K_RIGHT in self.keys_pressed:
            self.raymarcher.rotate_camera(0, 0.02, 0)
        if pygame.K_UP in self.keys_pressed:
            self.raymarcher.rotate_camera(-0.02, 0, 0)
        if pygame.K_DOWN in self.keys_pressed:
            self.raymarcher.rotate_camera(0.02, 0, 0)
    
    def _handle_resize(self, width: int, height: int):
        """Обработка изменения размера окна"""
        self.width = width
        self.height = height
        
        # Обновляем Pygame поверхность
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        
        # Обновляем Raymarcher
        if self.raymarcher:
            self.raymarcher.resize(width, height)
        
        # Обновляем GUI
        if self.gui:
            self.gui.resize(width, height)
            # Пересоздаем UI элементы с новыми позициями
            self._recreate_ui_for_new_size()
        
        print(f"📐 Resized to: {width}x{height}")
    
    def _recreate_ui_for_new_size(self):
        """Пересоздание UI элементов для нового размера"""
        # Обновляем позиции элементов которые привязаны к краям экрана
        if hasattr(self, 'fps_text'):
            self.fps_text.rect.x = self.width - 190
        if hasattr(self, 'render_time_text'):
            self.render_time_text.rect.x = self.width - 190
        
        # Обновляем статусную строку
        if hasattr(self, 'status_text'):
            self.status_text.rect.y = self.height - 20
        if hasattr(self, 'version_text'):
            self.version_text.rect.x = self.width - 200
            self.version_text.rect.y = self.height - 20
    
    def _toggle_fullscreen(self):
        """Переключение полноэкранного режима"""
        # Простая реализация - можно расширить
        print("🖥️ Fullscreen toggle requested")
    
    def _toggle_help(self):
        """Показать/скрыть справку"""
        print("❓ Help toggle requested")
    
    def _update(self, delta_time: float):
        """Обновление состояния приложения"""
        # Обновляем GUI
        if self.gui:
            self.gui.update(delta_time)
        
        # Обновляем информацию о камере в GUI
        if self.raymarcher and hasattr(self, 'camera_pos_text'):
            camera_info = self.raymarcher.get_camera_info()
            pos = camera_info['position']
            angles = camera_info.get('angles', [0, 0, 0])
            
            self.camera_pos_text.text = f"Position: {pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}"
            self.camera_angles_text.text = f"Angles: {np.degrees(angles[0]):.1f}°, {np.degrees(angles[1]):.1f}°, {np.degrees(angles[2]):.1f}°"
    
    def _render(self) -> float:
        """Рендеринг кадра"""
        start_time = time.time()
        
        try:
            if self.raymarcher:
                # Рендерим основную сцену
                image_array = self.raymarcher.render()
                
                # Рендерим GUI поверх основной сцены
                if self.gui:
                    self.gui.render_to_buffer(self.raymarcher.output_buffer)
                
                # Конвертируем в pygame поверхность
                rgb_array = image_array[:, :, :3]  # Убираем alpha канал
                surface = pygame.surfarray.make_surface(rgb_array.swapaxes(0, 1))
                
                # Отображаем на экране
                self.screen.blit(surface, (0, 0))
            else:
                # Fallback - черный экран с текстом
                self.screen.fill((0, 0, 0))
                font = pygame.font.Font(None, 36)
                text = font.render("Raymarcher не инициализирован", True, (255, 0, 0))
                self.screen.blit(text, (50, 50))
                
        except Exception as e:
            # Обработка ошибок рендеринга
            self.screen.fill((50, 0, 0))
            font = pygame.font.Font(None, 24)
            error_text = font.render(f"Render Error: {str(e)[:60]}...", True, (255, 255, 255))
            self.screen.blit(error_text, (10, 10))
            print(f"❌ Render error: {e}")
        
        # Обновляем экран
        pygame.display.flip()
        
        render_time = time.time() - start_time
        return render_time
    
    def _cleanup(self):
        """Очистка ресурсов"""
        if self.gui:
            self.gui.cleanup()
        if self.raymarcher:
            self.raymarcher.cleanup()
        pygame.quit()

def main():
    """Точка входа в Level Editor"""
    print("🏗️ Intel Render Engine - Level Editor (OpenCL GUI)")
    print("=" * 60)
    
    try:
        editor = OpenCLLevelEditor(width=1400, height=900)
        editor.run()
    except KeyboardInterrupt:
        print("\n🛑 Прервано пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
