"""
Properties Editor - Редактор свойств объектов

Контекстный редактор, который показывает свойства выбранного объекта.
Включает вкладки для различных типов свойств (объект, материал, модификаторы и т.д.).
"""

import imgui
from .base_editor import BaseEditor
from .outliner import SceneObject, ObjectType
from typing import Dict, Any, Optional, List
from enum import Enum
import numpy as np

class PropertyTab(Enum):
    """Вкладки свойств"""
    RENDER = "render"           # 🎬 Настройки рендера
    SCENE = "scene"            # 🌍 Настройки сцены
    WORLD = "world"            # 🌌 Настройки мира/окружения
    OBJECT = "object"          # 📦 Свойства объекта
    MODIFIER = "modifier"      # 🔧 Модификаторы
    MATERIAL = "material"      # 🎨 Материалы
    TEXTURE = "texture"        # 🖼️ Текстуры
    PHYSICS = "physics"        # ⚽ Физика

class PropertiesEditor(BaseEditor):
    """Редактор свойств объектов"""
    
    def __init__(self, editor_id: str = "properties"):
        super().__init__(editor_id)
        
        # Текущая активная вкладка
        self.active_tab = PropertyTab.OBJECT
        
        # Текущий выбранный объект
        self.active_object: Optional[SceneObject] = None
        
        # Свойства рендера
        self.render_settings = {
            'resolution_x': 1920,
            'resolution_y': 1080,
            'samples': 128,
            'max_bounces': 12,
            'use_hdr': True,
            'exposure': 1.0,
            'tone_mapping': 'filmic'
        }
        
        # Свойства сцены
        self.scene_settings = {
            'frame_start': 1,
            'frame_end': 250,
            'frame_current': 1,
            'fps': 24
        }
        
        # Свойства мира
        self.world_settings = {
            'background_color': [0.05, 0.05, 0.1],
            'ambient_strength': 0.1,
            'fog_enabled': False,
            'fog_density': 0.01
        }
        
    def set_active_object(self, obj: Optional[SceneObject]):
        """Установить активный объект"""
        self.active_object = obj
        if obj:
            self.active_tab = PropertyTab.OBJECT
            
    def render_content(self):
        """Отрендерить содержимое редактора свойств"""
        # Вкладки свойств
        self._render_property_tabs()
        
        imgui.separator()
        
        # Содержимое выбранной вкладки
        self._render_active_tab_content()
        
    def _render_property_tabs(self):
        """Отрендерить вкладки свойств"""
        tab_icons = {
            PropertyTab.RENDER: "🎬",
            PropertyTab.SCENE: "🌍", 
            PropertyTab.WORLD: "🌌",
            PropertyTab.OBJECT: "📦",
            PropertyTab.MODIFIER: "🔧",
            PropertyTab.MATERIAL: "🎨",
            PropertyTab.TEXTURE: "🖼️",
            PropertyTab.PHYSICS: "⚽"
        }
        
        # Отображаем вкладки как кнопки
        for i, (tab, icon) in enumerate(tab_icons.items()):
            if i > 0:
                imgui.same_line()
                
            is_active = tab == self.active_tab
            if is_active:
                imgui.push_style_color(imgui.COLOR_BUTTON, 0.2, 0.6, 0.8, 1.0)
                
            if imgui.button(f"{icon}##{tab.value}", width=30, height=30):
                self.active_tab = tab
                
            if is_active:
                imgui.pop_style_color()
                
            # Подсказка при наведении
            if imgui.is_item_hovered():
                imgui.set_tooltip(tab.value.title())
                
    def _render_active_tab_content(self):
        """Отрендерить содержимое активной вкладки"""
        if self.active_tab == PropertyTab.RENDER:
            self._render_render_properties()
        elif self.active_tab == PropertyTab.SCENE:
            self._render_scene_properties()
        elif self.active_tab == PropertyTab.WORLD:
            self._render_world_properties()
        elif self.active_tab == PropertyTab.OBJECT:
            self._render_object_properties()
        elif self.active_tab == PropertyTab.MODIFIER:
            self._render_modifier_properties()
        elif self.active_tab == PropertyTab.MATERIAL:
            self._render_material_properties()
        elif self.active_tab == PropertyTab.TEXTURE:
            self._render_texture_properties()
        elif self.active_tab == PropertyTab.PHYSICS:
            self._render_physics_properties()
            
    def _render_render_properties(self):
        """Отрендерить настройки рендера"""
        imgui.text("Render Settings")
        imgui.separator()
        
        if imgui.collapsing_header("Resolution", ):
            changed, self.render_settings['resolution_x'] = imgui.input_int(
                "Width", self.render_settings['resolution_x'], step=1)
            changed, self.render_settings['resolution_y'] = imgui.input_int(
                "Height", self.render_settings['resolution_y'], step=1)
                
        if imgui.collapsing_header("Quality", ):
            changed, self.render_settings['samples'] = imgui.slider_int(
                "Samples", self.render_settings['samples'], 1, 512)
            changed, self.render_settings['max_bounces'] = imgui.slider_int(
                "Max Bounces", self.render_settings['max_bounces'], 1, 32)
                
        if imgui.collapsing_header("HDR", ):
            changed, self.render_settings['use_hdr'] = imgui.checkbox(
                "Enable HDR", self.render_settings['use_hdr'])
            
            if self.render_settings['use_hdr']:
                changed, self.render_settings['exposure'] = imgui.slider_float(
                    "Exposure", self.render_settings['exposure'], 0.1, 5.0)
                    
                tone_mapping_modes = ['linear', 'reinhard', 'filmic', 'aces']
                current_mode = self.render_settings['tone_mapping']
                if imgui.begin_combo("Tone Mapping", current_mode):
                    for mode in tone_mapping_modes:
                        clicked, selected = imgui.selectable(mode, mode == current_mode)
                        if clicked:
                            self.render_settings['tone_mapping'] = mode
                    imgui.end_combo()
                    
    def _render_scene_properties(self):
        """Отрендерить настройки сцены"""
        imgui.text("Scene Settings")
        imgui.separator()
        
        if imgui.collapsing_header("Animation", ):
            changed, self.scene_settings['frame_start'] = imgui.input_int(
                "Start Frame", self.scene_settings['frame_start'])
            changed, self.scene_settings['frame_end'] = imgui.input_int(
                "End Frame", self.scene_settings['frame_end'])
            changed, self.scene_settings['frame_current'] = imgui.slider_int(
                "Current Frame", self.scene_settings['frame_current'],
                self.scene_settings['frame_start'], self.scene_settings['frame_end'])
            changed, self.scene_settings['fps'] = imgui.input_int(
                "FPS", self.scene_settings['fps'])
                
    def _render_world_properties(self):
        """Отрендерить настройки мира"""
        imgui.text("World Settings")
        imgui.separator()
        
        if imgui.collapsing_header("Background", ):
            changed, self.world_settings['background_color'] = imgui.color_edit3(
                "Background Color", *self.world_settings['background_color'])
            changed, self.world_settings['ambient_strength'] = imgui.slider_float(
                "Ambient Strength", self.world_settings['ambient_strength'], 0.0, 1.0)
                
        if imgui.collapsing_header("Fog"):
            changed, self.world_settings['fog_enabled'] = imgui.checkbox(
                "Enable Fog", self.world_settings['fog_enabled'])
                
            if self.world_settings['fog_enabled']:
                changed, self.world_settings['fog_density'] = imgui.slider_float(
                    "Fog Density", self.world_settings['fog_density'], 0.001, 0.1)
                    
    def _render_object_properties(self):
        """Отрендерить свойства объекта"""
        if not self.active_object:
            imgui.text("No object selected")
            return
            
        imgui.text(f"Object: {self.active_object.name}")
        imgui.separator()
        
        # Общие свойства
        if imgui.collapsing_header("General", ):
            # Имя объекта
            if not hasattr(self.active_object, '_editing_name'):
                if imgui.button("Rename"):
                    self.active_object._editing_name = True
                    self.active_object._temp_name = self.active_object.name
            else:
                changed, self.active_object._temp_name = imgui.input_text(
                    "Name", self.active_object._temp_name)
                if imgui.button("OK"):
                    self.active_object.name = self.active_object._temp_name
                    delattr(self.active_object, '_editing_name')
                    delattr(self.active_object, '_temp_name')
                imgui.same_line()
                if imgui.button("Cancel"):
                    delattr(self.active_object, '_editing_name')
                    delattr(self.active_object, '_temp_name')
                    
            # Видимость и блокировка
            changed, self.active_object.visible = imgui.checkbox(
                "Visible", self.active_object.visible)
            changed, self.active_object.locked = imgui.checkbox(
                "Locked", self.active_object.locked)
                
        # Трансформация
        if imgui.collapsing_header("Transform", ):
            self._render_transform_properties()
            
        # Специфичные для типа свойства
        self._render_type_specific_properties()
        
    def _render_transform_properties(self):
        """Отрендерить свойства трансформации"""
        # Инициализируем transform если его нет
        if 'transform' not in self.active_object.properties:
            self.active_object.properties['transform'] = {
                'location': [0.0, 0.0, 0.0],
                'rotation': [0.0, 0.0, 0.0],
                'scale': [1.0, 1.0, 1.0]
            }
            
        transform = self.active_object.properties['transform']
        
        # Location
        imgui.text("Location:")
        changed, transform['location'] = imgui.input_float3("##location", *transform['location'])
        
        # Rotation (в градусах)
        imgui.text("Rotation:")
        rotation_deg = [np.degrees(r) for r in transform['rotation']]
        changed, rotation_deg = imgui.input_float3("##rotation", *rotation_deg)
        if changed:
            transform['rotation'] = [np.radians(r) for r in rotation_deg]
            
        # Scale
        imgui.text("Scale:")
        changed, transform['scale'] = imgui.input_float3("##scale", *transform['scale'])
        
    def _render_type_specific_properties(self):
        """Отрендерить свойства, специфичные для типа объекта"""
        obj_type = self.active_object.obj_type
        
        if obj_type == ObjectType.LIGHT:
            self._render_light_properties()
        elif obj_type == ObjectType.CAMERA:
            self._render_camera_properties()
        elif obj_type == ObjectType.MESH:
            self._render_mesh_properties()
            
    def _render_light_properties(self):
        """Отрендерить свойства источника света"""
        if imgui.collapsing_header("Light", ):
            if 'light' not in self.active_object.properties:
                self.active_object.properties['light'] = {
                    'type': 'point',
                    'color': [1.0, 1.0, 1.0],
                    'intensity': 1.0,
                    'range': 10.0
                }
                
            light = self.active_object.properties['light']
            
            # Тип света
            light_types = ['point', 'sun', 'spot', 'area']
            if imgui.begin_combo("Type", light['type']):
                for light_type in light_types:
                    clicked, selected = imgui.selectable(light_type, light_type == light['type'])
                    if clicked:
                        light['type'] = light_type
                imgui.end_combo()
                
            # Цвет
            changed, light['color'] = imgui.color_edit3("Color", *light['color'])
            
            # Интенсивность
            changed, light['intensity'] = imgui.slider_float("Intensity", light['intensity'], 0.0, 10.0)
            
            # Дальность
            changed, light['range'] = imgui.slider_float("Range", light['range'], 0.1, 100.0)
            
    def _render_camera_properties(self):
        """Отрендерить свойства камеры"""
        if imgui.collapsing_header("Camera", ):
            if 'camera' not in self.active_object.properties:
                self.active_object.properties['camera'] = {
                    'fov': 50.0,
                    'near_clip': 0.1,
                    'far_clip': 1000.0,
                    'type': 'perspective'
                }
                
            camera = self.active_object.properties['camera']
            
            # Тип камеры
            camera_types = ['perspective', 'orthographic']
            if imgui.begin_combo("Type", camera['type']):
                for cam_type in camera_types:
                    clicked, selected = imgui.selectable(cam_type, cam_type == camera['type'])
                    if clicked:
                        camera['type'] = cam_type
                imgui.end_combo()
                
            # FOV (только для perspective)
            if camera['type'] == 'perspective':
                changed, camera['fov'] = imgui.slider_float("FOV", camera['fov'], 10.0, 120.0)
                
            # Clipping
            changed, camera['near_clip'] = imgui.input_float("Near Clip", camera['near_clip'])
            changed, camera['far_clip'] = imgui.input_float("Far Clip", camera['far_clip'])
            
    def _render_mesh_properties(self):
        """Отрендерить свойства меша"""
        if imgui.collapsing_header("Mesh", ):
            if 'mesh' not in self.active_object.properties:
                self.active_object.properties['mesh'] = {
                    'primitive_type': 'sphere',
                    'size': 1.0,
                    'subdivisions': 2
                }
                
            mesh = self.active_object.properties['mesh']
            
            # Тип примитива
            primitives = ['sphere', 'cube', 'cylinder', 'torus', 'plane']
            if imgui.begin_combo("Primitive", mesh['primitive_type']):
                for primitive in primitives:
                    clicked, selected = imgui.selectable(primitive, primitive == mesh['primitive_type'])
                    if clicked:
                        mesh['primitive_type'] = primitive
                imgui.end_combo()
                
            # Размер
            changed, mesh['size'] = imgui.slider_float("Size", mesh['size'], 0.1, 10.0)
            
            # Подразделения
            changed, mesh['subdivisions'] = imgui.slider_int("Subdivisions", mesh['subdivisions'], 1, 6)
            
    def _render_modifier_properties(self):
        """Отрендерить свойства модификаторов"""
        imgui.text("Modifiers")
        imgui.separator()
        
        if not self.active_object:
            imgui.text("No object selected")
            return
            
        # TODO: Implement modifiers system
        imgui.text("Modifier system not implemented yet")
        
    def _render_material_properties(self):
        """Отрендерить свойства материалов"""
        imgui.text("Material Properties")
        imgui.separator()
        
        if not self.active_object:
            imgui.text("No object selected")
            return
            
        # TODO: Implement material system
        imgui.text("Material system not implemented yet")
        
    def _render_texture_properties(self):
        """Отрендерить свойства текстур"""
        imgui.text("Texture Properties")
        imgui.separator()
        
        # TODO: Implement texture system
        imgui.text("Texture system not implemented yet")
        
    def _render_physics_properties(self):
        """Отрендерить свойства физики"""
        imgui.text("Physics Properties")
        imgui.separator()
        
        # TODO: Implement physics system
        imgui.text("Physics system not implemented yet")
        
    def get_render_settings(self) -> Dict[str, Any]:
        """Получить настройки рендера"""
        return self.render_settings.copy()
        
    def get_scene_settings(self) -> Dict[str, Any]:
        """Получить настройки сцены"""
        return self.scene_settings.copy()
        
    def get_world_settings(self) -> Dict[str, Any]:
        """Получить настройки мира"""
        return self.world_settings.copy()
