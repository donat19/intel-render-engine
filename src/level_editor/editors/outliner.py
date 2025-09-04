"""
Outliner Editor - Редактор иерархии сцены

Отображает все объекты сцены в древовидной структуре.
Позволяет управлять видимостью, блокировкой и группировкой объектов.
"""

import imgui
from .base_editor import BaseEditor
from typing import Dict, List, Optional, Any
from enum import Enum

class ObjectType(Enum):
    """Типы объектов в сцене"""
    COLLECTION = "collection"
    MESH = "mesh"
    LIGHT = "light"
    CAMERA = "camera"
    EMPTY = "empty"
    MATERIAL = "material"

class SceneObject:
    """Объект сцены"""
    
    def __init__(self, name: str, obj_type: ObjectType, parent: Optional['SceneObject'] = None):
        self.name = name
        self.obj_type = obj_type
        self.parent = parent
        self.children: List['SceneObject'] = []
        
        # Состояние объекта
        self.visible = True
        self.locked = False
        self.selected = False
        
        # Дополнительные свойства
        self.properties = {}
        
        if parent:
            parent.add_child(self)
            
    def add_child(self, child: 'SceneObject'):
        """Добавить дочерний объект"""
        if child not in self.children:
            self.children.append(child)
            child.parent = self
            
    def remove_child(self, child: 'SceneObject'):
        """Удалить дочерний объект"""
        if child in self.children:
            self.children.remove(child)
            child.parent = None
            
    def get_full_path(self) -> str:
        """Получить полный путь к объекту"""
        if self.parent:
            return f"{self.parent.get_full_path()}/{self.name}"
        return self.name
        
    def is_ancestor_of(self, obj: 'SceneObject') -> bool:
        """Проверить, является ли этот объект предком другого"""
        current = obj.parent
        while current:
            if current == self:
                return True
            current = current.parent
        return False

class OutlinerEditor(BaseEditor):
    """Редактор Outliner для управления иерархией сцены"""
    
    def __init__(self, editor_id: str = "outliner"):
        super().__init__(editor_id)
        
        # Корневые объекты сцены
        self.root_objects: List[SceneObject] = []
        
        # Настройки отображения
        self.show_collections = True
        self.show_meshes = True
        self.show_lights = True
        self.show_cameras = True
        self.show_empties = True
        
        # Состояние UI
        self.search_filter = ""
        self.expanded_objects = set()  # ID развернутых объектов
        
        # Выбранные объекты
        self.selected_objects: List[SceneObject] = []
        self.last_selected: Optional[SceneObject] = None
        
        # Drag & Drop
        self.dragged_object: Optional[SceneObject] = None
        
        # Создаем тестовую иерархию
        self._create_test_hierarchy()
        
    def _create_test_hierarchy(self):
        """Создать тестовую иерархию объектов"""
        # Создаем коллекции
        scene_collection = SceneObject("Scene Collection", ObjectType.COLLECTION)
        lights_collection = SceneObject("Lights", ObjectType.COLLECTION, scene_collection)
        objects_collection = SceneObject("Objects", ObjectType.COLLECTION, scene_collection)
        
        # Добавляем объекты
        cube = SceneObject("Cube", ObjectType.MESH, objects_collection)
        sphere = SceneObject("Sphere", ObjectType.MESH, objects_collection)
        torus = SceneObject("Torus", ObjectType.MESH, objects_collection)
        
        # Добавляем источники света
        sun_light = SceneObject("Sun", ObjectType.LIGHT, lights_collection)
        point_light = SceneObject("Point Light", ObjectType.LIGHT, lights_collection)
        
        # Добавляем камеру
        camera = SceneObject("Camera", ObjectType.CAMERA, scene_collection)
        
        self.root_objects = [scene_collection]
        
    def render_content(self):
        """Отрендерить содержимое Outliner"""
        # Поиск
        self._render_search_bar()
        
        # Настройки фильтрации
        self._render_filter_options()
        
        imgui.separator()
        
        # Дерево объектов
        self._render_object_tree()
        
    def _render_search_bar(self):
        """Отрендерить строку поиска"""
        imgui.text("Search:")
        changed, self.search_filter = imgui.input_text("##search", self.search_filter)
        
    def _render_filter_options(self):
        """Отрендерить опции фильтрации"""
        if imgui.collapsing_header("Filters"):
            changed, self.show_collections = imgui.checkbox("Collections", self.show_collections)
            imgui.same_line()
            changed, self.show_meshes = imgui.checkbox("Meshes", self.show_meshes)
            
            changed, self.show_lights = imgui.checkbox("Lights", self.show_lights)
            imgui.same_line()
            changed, self.show_cameras = imgui.checkbox("Cameras", self.show_cameras)
            
            changed, self.show_empties = imgui.checkbox("Empties", self.show_empties)
            
    def _render_object_tree(self):
        """Отрендерить дерево объектов"""
        imgui.begin_child("object_tree", height=0)
        
        for obj in self.root_objects:
            self._render_object_node(obj)
            
        imgui.end_child()
        
    def _render_object_node(self, obj: SceneObject, level: int = 0):
        """Отрендерить узел объекта"""
        # Проверяем фильтр
        if not self._object_passes_filter(obj):
            return
            
        # Отступ для иерархии
        indent = level * 20
        imgui.indent(indent)
        
        # Иконка типа объекта
        icon = self._get_object_icon(obj.obj_type)
        
        # Флаги для узла дерева
        node_flags = 0  # Базовые флаги
        
        if obj.selected:
            # Выделенный объект
            pass
            
        if not obj.children:
            # Листовой узел
            pass
            
        # Отображаем узел
        object_id = id(obj)
        is_expanded = imgui.tree_node(f"{icon} {obj.name}##{object_id}")
        
        # Обработка клика
        if imgui.is_item_clicked():
            self._handle_object_selection(obj)
            
        # Контекстное меню
        if imgui.begin_popup_context_item():
            self._render_context_menu(obj)
            imgui.end_popup()
            
        # Кнопки видимости и блокировки
        imgui.same_line()
        self._render_object_buttons(obj)
        
        # Если узел развернут, отображаем детей
        if is_expanded and obj.children:
            for child in obj.children:
                self._render_object_node(child, level + 1)
            imgui.tree_pop()
        elif not obj.children and is_expanded:
            # Для листьев без детей
            pass
            
        imgui.unindent(indent)
        
    def _get_object_icon(self, obj_type: ObjectType) -> str:
        """Получить иконку для типа объекта"""
        icons = {
            ObjectType.COLLECTION: "📁",
            ObjectType.MESH: "🟦",
            ObjectType.LIGHT: "💡",
            ObjectType.CAMERA: "📷",
            ObjectType.EMPTY: "⭕",
            ObjectType.MATERIAL: "🎨"
        }
        return icons.get(obj_type, "❓")
        
    def _render_object_buttons(self, obj: SceneObject):
        """Отрендерить кнопки управления объектом"""
        # Кнопка видимости
        eye_icon = "👁" if obj.visible else "🙈"
        if imgui.small_button(f"{eye_icon}##{id(obj)}_vis"):
            obj.visible = not obj.visible
            
        imgui.same_line()
        
        # Кнопка блокировки
        lock_icon = "🔒" if obj.locked else "🔓"
        if imgui.small_button(f"{lock_icon}##{id(obj)}_lock"):
            obj.locked = not obj.locked
            
    def _render_context_menu(self, obj: SceneObject):
        """Отрендерить контекстное меню объекта"""
        if imgui.menu_item("Select")[0]:
            self.select_object(obj)
            
        if imgui.menu_item("Duplicate")[0]:
            self.duplicate_object(obj)
            
        if imgui.menu_item("Delete")[0]:
            self.delete_object(obj)
            
        imgui.separator()
        
        if imgui.menu_item("Rename")[0]:
            self.start_rename(obj)
            
        imgui.separator()
        
        if imgui.begin_menu("Add Child"):
            if imgui.menu_item("Empty")[0]:
                self.add_child_object(obj, ObjectType.EMPTY)
            if imgui.menu_item("Mesh")[0]:
                self.add_child_object(obj, ObjectType.MESH)
            if imgui.menu_item("Light")[0]:
                self.add_child_object(obj, ObjectType.LIGHT)
            imgui.end_menu()
            
    def _object_passes_filter(self, obj: SceneObject) -> bool:
        """Проверить, проходит ли объект фильтр"""
        # Проверка типа объекта
        type_filters = {
            ObjectType.COLLECTION: self.show_collections,
            ObjectType.MESH: self.show_meshes,
            ObjectType.LIGHT: self.show_lights,
            ObjectType.CAMERA: self.show_cameras,
            ObjectType.EMPTY: self.show_empties
        }
        
        if not type_filters.get(obj.obj_type, True):
            return False
            
        # Проверка поискового фильтра
        if self.search_filter and self.search_filter.lower() not in obj.name.lower():
            return False
            
        return True
        
    def _handle_object_selection(self, obj: SceneObject):
        """Обработать выбор объекта"""
        io = imgui.get_io()
        
        if io.key_ctrl:
            # Ctrl + клик = добавить/убрать из выбора
            if obj in self.selected_objects:
                self.deselect_object(obj)
            else:
                self.select_object(obj, add_to_selection=True)
        elif io.key_shift and self.last_selected:
            # Shift + клик = выбрать диапазон
            self.select_range(self.last_selected, obj)
        else:
            # Обычный клик = выбрать только этот объект
            self.select_object(obj)
            
    def select_object(self, obj: SceneObject, add_to_selection: bool = False):
        """Выбрать объект"""
        if not add_to_selection:
            self.clear_selection()
            
        if obj not in self.selected_objects:
            self.selected_objects.append(obj)
            obj.selected = True
            
        self.last_selected = obj
        
    def deselect_object(self, obj: SceneObject):
        """Отменить выбор объекта"""
        if obj in self.selected_objects:
            self.selected_objects.remove(obj)
            obj.selected = False
            
    def clear_selection(self):
        """Очистить выбор"""
        for obj in self.selected_objects:
            obj.selected = False
        self.selected_objects.clear()
        self.last_selected = None
        
    def select_range(self, start_obj: SceneObject, end_obj: SceneObject):
        """Выбрать диапазон объектов"""
        # TODO: Implement range selection
        self.select_object(end_obj, add_to_selection=True)
        
    def duplicate_object(self, obj: SceneObject):
        """Дублировать объект"""
        new_name = f"{obj.name}.001"
        new_obj = SceneObject(new_name, obj.obj_type, obj.parent)
        new_obj.properties = obj.properties.copy()
        
    def delete_object(self, obj: SceneObject):
        """Удалить объект"""
        if obj.parent:
            obj.parent.remove_child(obj)
        else:
            if obj in self.root_objects:
                self.root_objects.remove(obj)
                
        if obj in self.selected_objects:
            self.deselect_object(obj)
            
    def add_child_object(self, parent: SceneObject, obj_type: ObjectType):
        """Добавить дочерний объект"""
        type_names = {
            ObjectType.EMPTY: "Empty",
            ObjectType.MESH: "Mesh",
            ObjectType.LIGHT: "Light",
            ObjectType.CAMERA: "Camera",
            ObjectType.COLLECTION: "Collection"
        }
        
        name = type_names.get(obj_type, "Object")
        new_obj = SceneObject(name, obj_type, parent)
        
    def start_rename(self, obj: SceneObject):
        """Начать переименование объекта"""
        # TODO: Implement inline renaming
        pass
        
    def get_selected_objects(self) -> List[SceneObject]:
        """Получить выбранные объекты"""
        return self.selected_objects.copy()
        
    def find_object_by_name(self, name: str) -> Optional[SceneObject]:
        """Найти объект по имени"""
        def search_recursive(objects):
            for obj in objects:
                if obj.name == name:
                    return obj
                result = search_recursive(obj.children)
                if result:
                    return result
            return None
            
        return search_recursive(self.root_objects)
