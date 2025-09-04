"""
Area Manager - Система областей интерфейса как в Blender

Каждая область может содержать любой редактор и изменяться динамически.
Поддерживает разделение, объединение и изменение размеров областей.
"""

import imgui
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import uuid

class EditorType(Enum):
    """Типы редакторов доступных в системе"""
    VIEWPORT_3D = "3D Viewport"
    OUTLINER = "Outliner"
    PROPERTIES = "Properties"
    SHADER_EDITOR = "Shader Editor"
    SCENE_HIERARCHY = "Scene Hierarchy"
    MATERIAL_EDITOR = "Material Editor"
    LIGHT_EDITOR = "Light Editor"
    CAMERA_EDITOR = "Camera Editor"
    RENDER_SETTINGS = "Render Settings"
    CONSOLE = "Console"

class Area:
    """Область интерфейса, которая может содержать любой редактор"""
    
    def __init__(self, editor_type: EditorType, x: float = 0, y: float = 0, 
                 width: float = 400, height: float = 300, area_id: str = None):
        self.id = area_id or str(uuid.uuid4())
        self.editor_type = editor_type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_focused = False
        self.can_split = True
        self.editor_instance = None
        
    def set_position(self, x: float, y: float, width: float, height: float):
        """Установить позицию и размер области"""
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
    def split_horizontal(self, split_ratio: float = 0.5) -> 'Area':
        """Разделить область горизонтально"""
        if not self.can_split:
            return None
            
        new_height = self.height * split_ratio
        remaining_height = self.height - new_height
        
        # Создаем новую область снизу
        new_area = Area(
            editor_type=self.editor_type,
            x=self.x,
            y=self.y + new_height,
            width=self.width,
            height=remaining_height
        )
        
        # Уменьшаем текущую область
        self.height = new_height
        
        return new_area
        
    def split_vertical(self, split_ratio: float = 0.5) -> 'Area':
        """Разделить область вертикально"""
        if not self.can_split:
            return None
            
        new_width = self.width * split_ratio
        remaining_width = self.width - new_width
        
        # Создаем новую область справа
        new_area = Area(
            editor_type=self.editor_type,
            x=self.x + new_width,
            y=self.y,
            width=remaining_width,
            height=self.height
        )
        
        # Уменьшаем текущую область
        self.width = new_width
        
        return new_area

class AreaManager:
    """Менеджер областей интерфейса"""
    
    def __init__(self):
        self.areas: Dict[str, Area] = {}
        self.active_area_id: Optional[str] = None
        self.splitter_thickness = 4.0
        
        # Создаем начальные области (как в Blender по умолчанию)
        self._create_default_layout()
        
    def _create_default_layout(self):
        """Создать стандартную раскладку интерфейса"""
        # Основной 3D Viewport (левая большая область)
        main_viewport = Area(
            EditorType.VIEWPORT_3D,
            x=0, y=0, 
            width=800, height=600,
            area_id="main_viewport"
        )
        
        # Outliner (правая верхняя область)
        outliner = Area(
            EditorType.OUTLINER,
            x=800, y=0,
            width=300, height=300,
            area_id="outliner"
        )
        
        # Properties (правая нижняя область)
        properties = Area(
            EditorType.PROPERTIES,
            x=800, y=300,
            width=300, height=300,
            area_id="properties"
        )
        
        self.areas = {
            main_viewport.id: main_viewport,
            outliner.id: outliner,
            properties.id: properties
        }
        
        self.active_area_id = main_viewport.id
        
    def add_area(self, area: Area):
        """Добавить новую область"""
        self.areas[area.id] = area
        
    def remove_area(self, area_id: str):
        """Удалить область"""
        if area_id in self.areas and len(self.areas) > 1:
            del self.areas[area_id]
            if self.active_area_id == area_id:
                self.active_area_id = next(iter(self.areas.keys()))
                
    def get_area(self, area_id: str) -> Optional[Area]:
        """Получить область по ID"""
        return self.areas.get(area_id)
        
    def get_active_area(self) -> Optional[Area]:
        """Получить активную область"""
        return self.areas.get(self.active_area_id)
        
    def set_active_area(self, area_id: str):
        """Установить активную область"""
        if area_id in self.areas:
            self.active_area_id = area_id
            
    def split_area(self, area_id: str, direction: str, ratio: float = 0.5) -> Optional[str]:
        """
        Разделить область
        
        Args:
            area_id: ID области для разделения
            direction: 'horizontal' или 'vertical'
            ratio: Коэффициент разделения (0.0-1.0)
            
        Returns:
            ID новой области или None если разделение невозможно
        """
        area = self.get_area(area_id)
        if not area:
            return None
            
        if direction == 'horizontal':
            new_area = area.split_horizontal(ratio)
        elif direction == 'vertical':
            new_area = area.split_vertical(ratio)
        else:
            return None
            
        if new_area:
            self.add_area(new_area)
            return new_area.id
            
        return None
        
    def merge_areas(self, area_id1: str, area_id2: str) -> bool:
        """Объединить две соседние области"""
        area1 = self.get_area(area_id1)
        area2 = self.get_area(area_id2)
        
        if not area1 or not area2:
            return False
            
        # Проверяем, являются ли области соседними
        if self._are_adjacent(area1, area2):
            # Расширяем первую область, удаляем вторую
            area1.width = max(area1.x + area1.width, area2.x + area2.width) - min(area1.x, area2.x)
            area1.height = max(area1.y + area1.height, area2.y + area2.height) - min(area1.y, area2.y)
            area1.x = min(area1.x, area2.x)
            area1.y = min(area1.y, area2.y)
            
            self.remove_area(area_id2)
            return True
            
        return False
        
    def _are_adjacent(self, area1: Area, area2: Area) -> bool:
        """Проверить, являются ли области соседними"""
        # Упрощенная проверка - можно улучшить
        return (
            (area1.x + area1.width == area2.x or area2.x + area2.width == area1.x) or
            (area1.y + area1.height == area2.y or area2.y + area2.height == area1.y)
        )
        
    def resize_window(self, new_width: float, new_height: float):
        """Изменить размер всех областей при изменении размера окна"""
        if not self.areas:
            return
            
        # Простое пропорциональное масштабирование
        old_width = max(area.x + area.width for area in self.areas.values())
        old_height = max(area.y + area.height for area in self.areas.values())
        
        if old_width == 0 or old_height == 0:
            return
            
        width_scale = new_width / old_width
        height_scale = new_height / old_height
        
        for area in self.areas.values():
            area.x *= width_scale
            area.y *= height_scale
            area.width *= width_scale
            area.height *= height_scale
            
    def render_areas(self, render_callback):
        """Отрендерить все области с их редакторами"""
        for area in self.areas.values():
            # Устанавливаем позицию и размер окна ImGui
            imgui.set_next_window_position(area.x, area.y)
            imgui.set_next_window_size(area.width, area.height)
            
            window_flags = (
                imgui.WINDOW_NO_MOVE |
                imgui.WINDOW_NO_RESIZE |
                imgui.WINDOW_NO_COLLAPSE
            )
            
            window_title = f"{area.editor_type.value}##{area.id}"
            
            if imgui.begin(window_title, flags=window_flags)[0]:
                # Проверяем, активна ли область
                if imgui.is_window_focused():
                    self.set_active_area(area.id)
                    area.is_focused = True
                else:
                    area.is_focused = False
                
                # Отрендерить содержимое редактора
                render_callback(area)
                
            imgui.end()
            
    def save_layout(self, filename: str):
        """Сохранить раскладку в файл"""
        layout_data = {
            'areas': {
                area_id: {
                    'editor_type': area.editor_type.value,
                    'x': area.x,
                    'y': area.y,
                    'width': area.width,
                    'height': area.height
                }
                for area_id, area in self.areas.items()
            },
            'active_area_id': self.active_area_id
        }
        
        import json
        with open(filename, 'w') as f:
            json.dump(layout_data, f, indent=2)
            
    def load_layout(self, filename: str):
        """Загрузить раскладку из файла"""
        try:
            import json
            with open(filename, 'r') as f:
                layout_data = json.load(f)
                
            self.areas.clear()
            
            for area_id, area_data in layout_data['areas'].items():
                editor_type = EditorType(area_data['editor_type'])
                area = Area(
                    editor_type=editor_type,
                    x=area_data['x'],
                    y=area_data['y'],
                    width=area_data['width'],
                    height=area_data['height'],
                    area_id=area_id
                )
                self.areas[area_id] = area
                
            self.active_area_id = layout_data.get('active_area_id')
            
        except Exception as e:
            print(f"Ошибка загрузки раскладки: {e}")
            self._create_default_layout()
