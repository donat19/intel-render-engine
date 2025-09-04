#!/usr/bin/env python3
"""
OpenCL GUI System - Полностью GPU-ускоренная система интерфейса

Вместо ImGui используем собственную систему рендеринга UI на OpenCL.
Все элементы интерфейса рендерятся на GPU как часть основного рендеринг пайплайна.
"""
import pyopencl as cl
import numpy as np
import time
import os
from typing import Dict, List, Optional, Tuple, Any, Callable
from enum import Enum
from dataclasses import dataclass
import pygame

class GUIElementType(Enum):
    """Типы GUI элементов"""
    BUTTON = "button"
    TEXT = "text"
    PANEL = "panel"
    WINDOW = "window"
    SLIDER = "slider"
    CHECKBOX = "checkbox"
    TEXTBOX = "textbox"
    MENU = "menu"
    PROGRESS_BAR = "progress_bar"
    SEPARATOR = "separator"

class GUITheme(Enum):
    """Темы интерфейса"""
    DARK = "dark"
    LIGHT = "light"
    BLENDER = "blender"
    CYBERPUNK = "cyberpunk"

@dataclass
class Color:
    """RGBA цвет для GPU"""
    r: float
    g: float  
    b: float
    a: float = 1.0
    
    def to_float4(self) -> np.ndarray:
        """Конвертация в float4 для OpenCL"""
        return np.array([self.r, self.g, self.b, self.a], dtype=np.float32)
    
    def to_int(self) -> int:
        """Конвертация в int32 для компактного хранения"""
        r = int(self.r * 255) & 0xFF
        g = int(self.g * 255) & 0xFF
        b = int(self.b * 255) & 0xFF
        a = int(self.a * 255) & 0xFF
        return (a << 24) | (b << 16) | (g << 8) | r

@dataclass
class Rect:
    """Прямоугольник для UI элементов"""
    x: float
    y: float
    width: float
    height: float
    
    def contains_point(self, x: float, y: float) -> bool:
        """Проверяет, содержит ли прямоугольник точку"""
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height)
    
    def to_float4(self) -> np.ndarray:
        """Конвертация в float4 для OpenCL"""
        return np.array([self.x, self.y, self.width, self.height], dtype=np.float32)

class GUIElement:
    """Базовый класс для всех GUI элементов"""
    
    def __init__(self, element_id: str, element_type: GUIElementType, 
                 rect: Rect, visible: bool = True, enabled: bool = True):
        self.id = element_id
        self.type = element_type
        self.rect = rect
        self.visible = visible
        self.enabled = enabled
        self.z_order = 0
        
        # Состояние взаимодействия
        self.hovered = False
        self.pressed = False
        self.focused = False
        
        # Callback функции
        self.on_click: Optional[Callable] = None
        self.on_hover: Optional[Callable] = None
        self.on_focus: Optional[Callable] = None
        
        # Стиль
        self.colors = {
            'normal': Color(0.2, 0.2, 0.2, 0.9),
            'hovered': Color(0.3, 0.3, 0.3, 0.9),
            'pressed': Color(0.1, 0.1, 0.1, 0.9),
            'text': Color(1.0, 1.0, 1.0, 1.0)
        }
        
        # Дополнительные данные
        self.user_data: Dict[str, Any] = {}
    
    def get_current_color(self) -> Color:
        """Получить текущий цвет в зависимости от состояния"""
        if self.pressed:
            return self.colors['pressed']
        elif self.hovered:
            return self.colors['hovered']
        else:
            return self.colors['normal']
    
    def handle_mouse_event(self, x: float, y: float, button_pressed: bool) -> bool:
        """Обработка событий мыши. Возвращает True если событие обработано"""
        if not self.visible or not self.enabled:
            return False
            
        was_hovered = self.hovered
        self.hovered = self.rect.contains_point(x, y)
        
        if self.hovered:
            if not was_hovered and self.on_hover:
                self.on_hover(self)
                
            if button_pressed and not self.pressed:
                self.pressed = True
                if self.on_click:
                    self.on_click(self)
                return True
        
        if not button_pressed:
            self.pressed = False
            
        return self.hovered
    
    def to_gpu_data(self) -> np.ndarray:
        """Конвертация данных элемента для передачи в GPU"""
        # Структура: [type, rect(4), color(4), state_flags, z_order, padding(2)]
        data = np.zeros(16, dtype=np.float32)
        
        data[0] = float(list(GUIElementType).index(self.type))  # type
        data[1:5] = self.rect.to_float4()  # rect
        data[5:9] = self.get_current_color().to_float4()  # color
        
        # Флаги состояния (упакованы в один float)
        state_flags = 0
        if self.visible: state_flags |= 1
        if self.enabled: state_flags |= 2
        if self.hovered: state_flags |= 4
        if self.pressed: state_flags |= 8
        if self.focused: state_flags |= 16
        data[9] = float(state_flags)
        
        data[10] = float(self.z_order)  # z_order
        # data[11:16] - reserved для расширений
        
        return data

class Button(GUIElement):
    """Кнопка"""
    
    def __init__(self, element_id: str, rect: Rect, text: str = "", 
                 on_click: Optional[Callable] = None):
        super().__init__(element_id, GUIElementType.BUTTON, rect)
        self.text = text
        self.on_click = on_click
        
        # Настройки кнопки
        self.border_width = 2.0
        self.corner_radius = 4.0

class Text(GUIElement):
    """Текстовый элемент"""
    
    def __init__(self, element_id: str, rect: Rect, text: str = "", 
                 font_size: float = 16.0):
        super().__init__(element_id, GUIElementType.TEXT, rect)
        self.text = text
        self.font_size = font_size
        self.alignment = "left"  # left, center, right

class Panel(GUIElement):
    """Панель/контейнер для других элементов"""
    
    def __init__(self, element_id: str, rect: Rect, title: str = ""):
        super().__init__(element_id, GUIElementType.PANEL, rect)
        self.title = title
        self.children: List[GUIElement] = []
        self.border_width = 1.0
        self.title_height = 24.0
    
    def add_child(self, element: GUIElement):
        """Добавить дочерний элемент"""
        self.children.append(element)
        element.z_order = self.z_order + 1
    
    def remove_child(self, element_id: str):
        """Удалить дочерний элемент по ID"""
        self.children = [child for child in self.children if child.id != element_id]

class Slider(GUIElement):
    """Слайдер для изменения значений"""
    
    def __init__(self, element_id: str, rect: Rect, min_value: float = 0.0, 
                 max_value: float = 1.0, value: float = 0.5, 
                 on_change: Optional[Callable] = None):
        super().__init__(element_id, GUIElementType.SLIDER, rect)
        self.min_value = min_value
        self.max_value = max_value
        self.value = value
        self.on_change = on_change
        self.handle_width = 20.0
    
    def set_value(self, value: float):
        """Установить значение слайдера"""
        self.value = max(self.min_value, min(self.max_value, value))
        if self.on_change:
            self.on_change(self)
    
    def get_handle_position(self) -> float:
        """Получить позицию ручки слайдера"""
        t = (self.value - self.min_value) / (self.max_value - self.min_value)
        return self.rect.x + t * (self.rect.width - self.handle_width)

class OpenCLGUI:
    """Главный класс OpenCL GUI системы"""
    
    def __init__(self, cl_context: cl.Context, cl_queue: cl.CommandQueue, 
                 width: int, height: int, theme: GUITheme = GUITheme.DARK):
        self.context = cl_context
        self.queue = cl_queue
        self.width = width
        self.height = height
        self.theme = theme
        
        # GUI элементы
        self.elements: Dict[str, GUIElement] = {}
        self.element_order: List[str] = []  # Порядок рендеринга
        
        # Состояние ввода
        self.mouse_x = 0.0
        self.mouse_y = 0.0
        self.mouse_buttons = [False, False, False]  # Left, Middle, Right
        self.key_states: Dict[int, bool] = {}
        
        # Фокус и захват
        self.focused_element: Optional[str] = None
        self.captured_element: Optional[str] = None
        
        # OpenCL ресурсы для GUI
        self._init_opencl_resources()
        self._load_gui_kernels()
        
        # Встроенные шрифты и иконки (bitmap)
        self._init_font_data()
        
        print(f"OpenCL GUI initialized: {width}x{height}, theme: {theme.value}")
    
    def _init_opencl_resources(self):
        """Инициализация OpenCL ресурсов для GUI"""
        # Буфер для данных GUI элементов
        max_elements = 1000
        element_size = 16 * 4  # 16 float32 per element
        self.elements_buffer = cl.Buffer(self.context, cl.mem_flags.READ_WRITE, 
                                       max_elements * element_size)
        
        # Буфер для текстовых данных
        max_text_chars = 10000
        self.text_buffer = cl.Buffer(self.context, cl.mem_flags.READ_WRITE,
                                   max_text_chars * 4)  # 4 bytes per char
        
        # Буфер для font bitmap
        font_width, font_height = 512, 512
        self.font_texture_buffer = cl.Buffer(self.context, cl.mem_flags.READ_ONLY,
                                           font_width * font_height)
        
        # Массивы для CPU-стороны
        self.elements_array = np.zeros((1000, 16), dtype=np.float32)
        self.text_array = np.zeros(10000, dtype=np.uint8)
    
    def _load_gui_kernels(self):
        """Загрузка OpenCL ядер для GUI"""
        # Исправляем путь к шейдеру
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
        kernel_path = os.path.join(project_root, 'shaders', 'gui.cl')
        
        try:
            with open(kernel_path, 'r', encoding='utf-8') as f:
                kernel_source = f.read()
            
            self.program = cl.Program(self.context, kernel_source).build()
            
            # Основные ядра GUI
            self.render_gui_kernel = self.program.render_gui_kernel
            self.render_text_kernel = self.program.render_text_kernel
            self.composite_gui_kernel = self.program.composite_gui_kernel
            
            print(f"GUI kernels loaded successfully from {kernel_path}")
            
        except Exception as e:
            print(f"Error loading GUI kernels: {e}")
            # Создаем minimal fallback ядро
            self._create_fallback_kernel()
    
    def _create_fallback_kernel(self):
        """Создание fallback ядра если основное не загрузилось"""
        fallback_source = """
        __kernel void render_gui_kernel(__global uchar4* framebuffer,
                                      __global float16* elements,
                                      const int element_count,
                                      const int width,
                                      const int height) {
            int x = get_global_id(0);
            int y = get_global_id(1);
            
            if (x >= width || y >= height) return;
            
            // Simple colored rectangle rendering
            uchar4 pixel = (uchar4)(50, 50, 50, 255);
            framebuffer[y * width + x] = pixel;
        }
        """
        
        self.program = cl.Program(self.context, fallback_source).build()
        self.render_gui_kernel = self.program.render_gui_kernel
        print("Using fallback GUI kernel")
    
    def _init_font_data(self):
        """Инициализация bitmap шрифта"""
        # Простой bitmap шрифт 8x8 пикселей для каждого символа
        # В реальной реализации можно использовать более сложные шрифты
        self.font_char_width = 8
        self.font_char_height = 12
        self.font_chars_per_row = 16
        
        # Создаем простой bitmap для ASCII символов 32-127
        font_bitmap = np.zeros((512, 512), dtype=np.uint8)
        
        # Заполняем простыми прямоугольниками для тестирования
        for char_code in range(32, 128):
            char_x = (char_code - 32) % self.font_chars_per_row
            char_y = (char_code - 32) // self.font_chars_per_row
            
            x_start = char_x * self.font_char_width
            y_start = char_y * self.font_char_height
            
            # Простой паттерн для каждого символа
            font_bitmap[y_start:y_start+self.font_char_height-2, 
                       x_start+1:x_start+self.font_char_width-1] = 255
        
        # Загружаем в OpenCL буфер
        cl.enqueue_copy(self.queue, self.font_texture_buffer, font_bitmap)
        print("Font bitmap initialized")
    
    def add_element(self, element: GUIElement) -> str:
        """Добавить GUI элемент"""
        self.elements[element.id] = element
        if element.id not in self.element_order:
            self.element_order.append(element.id)
        return element.id
    
    def remove_element(self, element_id: str):
        """Удалить GUI элемент"""
        if element_id in self.elements:
            del self.elements[element_id]
        if element_id in self.element_order:
            self.element_order.remove(element_id)
    
    def get_element(self, element_id: str) -> Optional[GUIElement]:
        """Получить элемент по ID"""
        return self.elements.get(element_id)
    
    def handle_mouse_event(self, x: float, y: float, button: int, pressed: bool):
        """Обработка событий мыши"""
        self.mouse_x = x
        self.mouse_y = y
        
        if 0 <= button < len(self.mouse_buttons):
            self.mouse_buttons[button] = pressed
        
        # Обрабатываем элементы в обратном порядке (сверху вниз)
        for element_id in reversed(self.element_order):
            element = self.elements.get(element_id)
            if element and element.handle_mouse_event(x, y, pressed and button == 0):
                # Если элемент обработал событие, прерываем цепочку
                break
    
    def handle_keyboard_event(self, key: int, pressed: bool):
        """Обработка событий клавиатуры"""
        self.key_states[key] = pressed
        
        # Отправляем события фокусированному элементу
        if self.focused_element:
            element = self.elements.get(self.focused_element)
            if element and hasattr(element, 'handle_key_event'):
                element.handle_key_event(key, pressed)
    
    def update(self, delta_time: float):
        """Обновление состояния GUI"""
        # Обновляем анимации, таймеры и т.д.
        for element in self.elements.values():
            if hasattr(element, 'update'):
                element.update(delta_time)
    
    def render_to_buffer(self, framebuffer: cl.Buffer):
        """Рендеринг GUI поверх существующего фреймбуфера"""
        # Подготавливаем данные элементов для GPU
        self._prepare_elements_data()
        
        # Рендерим GUI элементы
        self.render_gui_kernel.set_args(
            framebuffer,
            self.elements_buffer,
            np.int32(len(self.elements)),
            np.int32(self.width),
            np.int32(self.height)
        )
        
        global_size = (self.width, self.height)
        cl.enqueue_nd_range_kernel(self.queue, self.render_gui_kernel, global_size, None)
        
        # Рендерим текст поверх элементов
        self._render_text_elements(framebuffer)
    
    def _prepare_elements_data(self):
        """Подготовка данных элементов для передачи в GPU"""
        element_count = 0
        
        # Сортируем элементы по z_order
        sorted_elements = sorted(self.elements.values(), key=lambda e: e.z_order)
        
        for i, element in enumerate(sorted_elements):
            if i >= self.elements_array.shape[0]:
                break
                
            self.elements_array[i] = element.to_gpu_data()
            element_count += 1
        
        # Копируем в GPU буфер
        if element_count > 0:
            data_to_copy = self.elements_array[:element_count]
            cl.enqueue_copy(self.queue, self.elements_buffer, data_to_copy)
    
    def _render_text_elements(self, framebuffer: cl.Buffer):
        """Рендеринг текстовых элементов"""
        # Собираем все текстовые элементы
        text_elements = [e for e in self.elements.values() 
                        if isinstance(e, (Text, Button)) and hasattr(e, 'text') and e.text]
        
        if not text_elements:
            return
        
        # Подготавливаем текстовые данные
        text_data_offset = 0
        
        for element in text_elements:
            if hasattr(element, 'text') and element.text:
                text_bytes = element.text.encode('ascii', errors='replace')[:100]  # Ограничиваем длину
                
                if text_data_offset + len(text_bytes) < self.text_array.shape[0]:
                    self.text_array[text_data_offset:text_data_offset+len(text_bytes)] = list(text_bytes)
                    
                    # Рендерим этот текст
                    if hasattr(self, 'render_text_kernel'):
                        self.render_text_kernel.set_args(
                            framebuffer,
                            self.text_buffer,
                            self.font_texture_buffer,
                            np.float32(element.rect.x),
                            np.float32(element.rect.y),
                            np.int32(len(text_bytes)),
                            np.int32(text_data_offset),
                            element.colors['text'].to_float4(),
                            np.int32(self.width),
                            np.int32(self.height)
                        )
                        
                        # Вычисляем размер области текста
                        text_width = len(text_bytes) * self.font_char_width
                        text_height = self.font_char_height
                        
                        text_global_size = (text_width, text_height)
                        cl.enqueue_nd_range_kernel(self.queue, self.render_text_kernel, 
                                                 text_global_size, None)
                    
                    text_data_offset += len(text_bytes)
        
        # Копируем текстовые данные в GPU
        if text_data_offset > 0:
            cl.enqueue_copy(self.queue, self.text_buffer, self.text_array[:text_data_offset])
    
    def resize(self, width: int, height: int):
        """Изменение размера GUI"""
        self.width = width
        self.height = height
        
        # Уведомляем элементы об изменении размера
        for element in self.elements.values():
            if hasattr(element, 'on_resize'):
                element.on_resize(width, height)
    
    # Утилиты для создания UI
    def create_button(self, element_id: str, x: float, y: float, 
                     width: float, height: float, text: str = "", 
                     on_click: Optional[Callable] = None) -> Button:
        """Создать кнопку"""
        rect = Rect(x, y, width, height)
        button = Button(element_id, rect, text, on_click)
        self.add_element(button)
        return button
    
    def create_text(self, element_id: str, x: float, y: float, 
                   text: str = "", font_size: float = 16.0) -> Text:
        """Создать текстовый элемент"""
        # Автоматически вычисляем размер на основе текста
        width = len(text) * self.font_char_width
        height = self.font_char_height
        rect = Rect(x, y, width, height)
        
        text_element = Text(element_id, rect, text, font_size)
        self.add_element(text_element)
        return text_element
    
    def create_panel(self, element_id: str, x: float, y: float, 
                    width: float, height: float, title: str = "") -> Panel:
        """Создать панель"""
        rect = Rect(x, y, width, height)
        panel = Panel(element_id, rect, title)
        self.add_element(panel)
        return panel
    
    def create_slider(self, element_id: str, x: float, y: float, 
                     width: float, height: float = 20.0,
                     min_value: float = 0.0, max_value: float = 1.0, 
                     value: float = 0.5, on_change: Optional[Callable] = None) -> Slider:
        """Создать слайдер"""
        rect = Rect(x, y, width, height)
        slider = Slider(element_id, rect, min_value, max_value, value, on_change)
        self.add_element(slider)
        return slider
    
    # Тема и стиль
    def set_theme(self, theme: GUITheme):
        """Установить тему интерфейса"""
        self.theme = theme
        self._apply_theme_to_elements()
    
    def _apply_theme_to_elements(self):
        """Применить текущую тему ко всем элементам"""
        theme_colors = self._get_theme_colors()
        
        for element in self.elements.values():
            for color_key, color_value in theme_colors.items():
                if color_key in element.colors:
                    element.colors[color_key] = color_value
    
    def _get_theme_colors(self) -> Dict[str, Color]:
        """Получить цвета текущей темы"""
        if self.theme == GUITheme.DARK:
            return {
                'normal': Color(0.2, 0.2, 0.2, 0.9),
                'hovered': Color(0.3, 0.3, 0.3, 0.9),
                'pressed': Color(0.1, 0.1, 0.1, 0.9),
                'text': Color(1.0, 1.0, 1.0, 1.0)
            }
        elif self.theme == GUITheme.LIGHT:
            return {
                'normal': Color(0.9, 0.9, 0.9, 0.9),
                'hovered': Color(0.8, 0.8, 0.8, 0.9),
                'pressed': Color(0.7, 0.7, 0.7, 0.9),
                'text': Color(0.0, 0.0, 0.0, 1.0)
            }
        elif self.theme == GUITheme.BLENDER:
            return {
                'normal': Color(0.15, 0.15, 0.15, 0.95),
                'hovered': Color(0.25, 0.25, 0.25, 0.95),
                'pressed': Color(0.1, 0.1, 0.1, 0.95),
                'text': Color(0.9, 0.9, 0.9, 1.0)
            }
        elif self.theme == GUITheme.CYBERPUNK:
            return {
                'normal': Color(0.1, 0.1, 0.2, 0.9),
                'hovered': Color(0.2, 0.1, 0.3, 0.9),
                'pressed': Color(0.05, 0.05, 0.15, 0.9),
                'text': Color(0.0, 1.0, 1.0, 1.0)
            }
        
        # Default fallback
        return {
            'normal': Color(0.2, 0.2, 0.2, 0.9),
            'hovered': Color(0.3, 0.3, 0.3, 0.9),
            'pressed': Color(0.1, 0.1, 0.1, 0.9),
            'text': Color(1.0, 1.0, 1.0, 1.0)
        }
    
    def cleanup(self):
        """Очистка ресурсов"""
        try:
            if hasattr(self, 'elements_buffer'):
                self.elements_buffer.release()
            if hasattr(self, 'text_buffer'):
                self.text_buffer.release()
            if hasattr(self, 'font_texture_buffer'):
                self.font_texture_buffer.release()
        except:
            pass

# Фабричные функции для быстрого создания UI элементов
def create_main_menu(gui: OpenCLGUI, width: int) -> Panel:
    """Создать главное меню приложения"""
    menu_panel = gui.create_panel("main_menu", 0, 0, width, 30, "Main Menu")
    
    # Кнопки меню
    gui.create_button("menu_file", 10, 5, 60, 20, "File")
    gui.create_button("menu_edit", 80, 5, 60, 20, "Edit") 
    gui.create_button("menu_view", 150, 5, 60, 20, "View")
    gui.create_button("menu_help", 220, 5, 60, 20, "Help")
    
    return menu_panel

def create_fps_display(gui: OpenCLGUI, x: float, y: float) -> Text:
    """Создать отображение FPS"""
    fps_text = gui.create_text("fps_display", x, y, "FPS: 60.0", 14.0)
    fps_text.colors['text'] = Color(0.0, 1.0, 0.0, 1.0)  # Зеленый цвет
    return fps_text

def create_camera_info_panel(gui: OpenCLGUI, x: float, y: float) -> Panel:
    """Создать панель информации о камере"""
    panel = gui.create_panel("camera_info", x, y, 250, 120, "Camera Info")
    
    # Текстовые поля для информации о камере
    gui.create_text("camera_pos", x + 10, y + 30, "Position: 0.0, 0.0, 5.0")
    gui.create_text("camera_angles", x + 10, y + 50, "Angles: 0.0, 0.0, 0.0")
    gui.create_text("camera_speed", x + 10, y + 70, "Speed: 1.0")
    
    return panel

def create_render_settings_panel(gui: OpenCLGUI, x: float, y: float) -> Panel:
    """Создать панель настроек рендера"""
    panel = gui.create_panel("render_settings", x, y, 200, 200, "Render Settings")
    
    # Слайдеры для настроек
    gui.create_slider("exposure_slider", x + 10, y + 40, 180, 20, 0.1, 5.0, 1.0)
    gui.create_text("exposure_label", x + 10, y + 65, "Exposure: 1.0")
    
    gui.create_slider("gamma_slider", x + 10, y + 85, 180, 20, 1.0, 3.0, 2.2)
    gui.create_text("gamma_label", x + 10, y + 110, "Gamma: 2.2")
    
    # Кнопки режимов tone mapping
    gui.create_button("tm_linear", x + 10, y + 130, 40, 20, "Lin")
    gui.create_button("tm_reinhard", x + 55, y + 130, 40, 20, "Rein")
    gui.create_button("tm_filmic", x + 100, y + 130, 40, 20, "Film")
    gui.create_button("tm_aces", x + 145, y + 130, 40, 20, "ACES")
    
    return panel
