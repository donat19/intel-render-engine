# OpenCL GUI System - Руководство разработчика

OpenCL GUI System - это полностью GPU-ускоренная система интерфейса, созданная для замены ImGui в Intel Render Engine. Все элементы интерфейса рендерятся на GPU через OpenCL как часть основного рендеринг пайплайна.

## 🎯 Архитектура

### Основные компоненты

1. **OpenCLGUI** - главный класс управления GUI системой
2. **GUIElement** - базовый класс для всех UI элементов  
3. **OpenCL Kernels** - GPU ядра для рендеринга элементов
4. **Theme System** - система тем оформления
5. **Event Handling** - обработка событий мыши и клавиатуры

### Преимущества OpenCL GUI

✅ **Полная GPU-ускорение** - весь рендеринг на GPU  
✅ **Интеграция с raymarcher** - общий OpenCL контекст  
✅ **Максимальная производительность** - нет CPU-GPU transfers  
✅ **Customizable** - полный контроль над рендерингом  
✅ **Minimal dependencies** - только PyOpenCL + NumPy  

## 🧩 Компоненты GUI

### Базовые элементы

```python
# Кнопка
button = gui.create_button("my_button", 100, 100, 80, 30, "Click Me", 
                          on_click=my_callback)

# Текст
text = gui.create_text("my_text", 10, 10, "Hello OpenCL!")

# Панель
panel = gui.create_panel("my_panel", 50, 50, 200, 150, "Panel Title")

# Слайдер
slider = gui.create_slider("my_slider", 10, 100, 180, 20, 0.0, 1.0, 0.5,
                          on_change=slider_callback)
```

### Продвинутые элементы

- **Button** - кнопки с hover эффектами
- **Text** - текстовые элементы с bitmap шрифтами
- **Panel** - контейнеры с заголовками и рамками
- **Slider** - слайдеры для числовых значений
- **Checkbox** - флажки (в разработке)
- **TextBox** - поля ввода (в разработке)

## 🎨 Система тем

### Доступные темы

```python
from src.gui.opencl_gui import GUITheme

# Темная тема (по умолчанию)
gui.set_theme(GUITheme.DARK)

# Светлая тема
gui.set_theme(GUITheme.LIGHT)

# Blender-style тема
gui.set_theme(GUITheme.BLENDER)

# Cyberpunk тема
gui.set_theme(GUITheme.CYBERPUNK)
```

### Настройка цветов

```python
from src.gui.opencl_gui import Color

# Создание custom цветов
red_color = Color(1.0, 0.0, 0.0, 1.0)  # RGBA
blue_color = Color(0.0, 0.5, 1.0, 0.8)  # Полупрозрачный синий

# Применение к элементу
button.colors['normal'] = red_color
button.colors['hovered'] = blue_color
```

## 🔧 OpenCL Kernels

### Структура ядер

Все GUI ядра находятся в `shaders/gui.cl`:

1. **render_gui_kernel** - основной рендеринг элементов
2. **render_text_kernel** - рендеринг текста
3. **composite_gui_kernel** - композитинг GUI поверх основного рендера
4. **gui_effects_kernel** - эффекты (размытие, тени)

### Добавление новых элементов

Для добавления нового типа элемента:

1. Создайте класс наследующий от `GUIElement`
2. Добавьте новый `GUIElementType` в enum
3. Реализуйте рендеринг в `render_gui_kernel`
4. Добавьте обработку событий

```python
class MyCustomElement(GUIElement):
    def __init__(self, element_id: str, rect: Rect):
        super().__init__(element_id, GUIElementType.CUSTOM, rect)
        # Дополнительные свойства
    
    def to_gpu_data(self) -> np.ndarray:
        # Конвертация данных для GPU
        data = super().to_gpu_data()
        # Добавить custom данные
        return data
```

## 🎮 Обработка событий

### События мыши

```python
def my_button_click(button: Button):
    print(f"Clicked button: {button.id}")

button.on_click = my_button_click
button.on_hover = lambda btn: print(f"Hovering: {btn.id}")
```

### События клавиатуры

```python
def handle_keyboard(key: int, pressed: bool):
    if key == pygame.K_SPACE and pressed:
        print("Space pressed!")

gui.handle_keyboard_event(pygame.K_SPACE, True)
```

## 📊 Производительность

### Оптимизации

- **Batch rendering** - все элементы рендерятся за один GPU вызов
- **Minimal CPU-GPU transfer** - данные копируются только при изменении
- **Efficient memory layout** - оптимизированная упаковка данных
- **Font caching** - bitmap шрифты в GPU памяти

### Мониторинг

```python
# FPS и время рендера
fps_display = create_fps_display(gui, 10, 10)

# Счетчики элементов
print(f"GUI elements: {len(gui.elements)}")
print(f"Render calls: {gui.render_call_count}")
```

## 🔌 Интеграция с Raymarcher

### Общий OpenCL контекст

```python
# Используем тот же контекст что и raymarcher
gui = OpenCLGUI(
    cl_context=raymarcher.context,
    cl_queue=raymarcher.queue,
    width=width,
    height=height
)
```

### Рендеринг поверх сцены

```python
def render_frame():
    # 1. Рендер основной сцены
    image_array = raymarcher.render()
    
    # 2. Рендер GUI поверх
    gui.render_to_buffer(raymarcher.output_buffer)
    
    # 3. Отображение результата
    display_image(image_array)
```

## 🛠️ Развитие системы

### Планируемые улучшения

- [ ] **Layout Manager** - автоматическое размещение элементов
- [ ] **Animation System** - анимации переходов и эффектов  
- [ ] **Advanced Text** - поддержка Unicode, разные шрифты
- [ ] **Vector Graphics** - SVG-подобные иконки и формы
- [ ] **3D GUI Elements** - объемные интерфейсы в 3D пространстве
- [ ] **Compute Shaders** - более сложные визуальные эффекты

### Extensibility

```python
# Кастомные ядра
custom_kernel_source = """
__kernel void my_custom_effect(...) {
    // Ваш OpenCL код
}
"""

gui.add_custom_kernel("my_effect", custom_kernel_source)
```

## 📖 Примеры использования

### Простой интерфейс

```python
# Создание GUI
gui = OpenCLGUI(cl_context, cl_queue, 800, 600)

# Главная панель
main_panel = gui.create_panel("main", 10, 10, 300, 200, "Settings")

# Элементы управления
speed_slider = gui.create_slider("speed", 20, 50, 200, 20, 0.1, 5.0, 1.0)
reset_button = gui.create_button("reset", 20, 80, 80, 30, "Reset")

# Callbacks
def on_speed_change(slider):
    print(f"Speed: {slider.value}")

def on_reset_click(button):
    speed_slider.set_value(1.0)

speed_slider.on_change = on_speed_change
reset_button.on_click = on_reset_click
```

### Level Editor интерфейс

```python
# Панель инструментов
tools = gui.create_panel("tools", 0, 0, 60, height, "Tools")

# Инструменты
select_btn = gui.create_button("select", 10, 30, 40, 40, "S")
move_btn = gui.create_button("move", 10, 75, 40, 40, "G") 
rotate_btn = gui.create_button("rotate", 10, 120, 40, 40, "R")

# Свойства объекта
props = gui.create_panel("properties", width-250, 0, 250, 300, "Properties")

# Слайдеры трансформации
pos_x = gui.create_slider("pos_x", width-240, 50, 200, 20, -10, 10, 0)
pos_y = gui.create_slider("pos_y", width-240, 75, 200, 20, -10, 10, 0)
pos_z = gui.create_slider("pos_z", width-240, 100, 200, 20, -10, 10, 0)
```

## 🐛 Отладка

### Debug режим

```python
# Запуск с отладкой
python opencl_level_editor_launcher.py --debug

# Отображение информации о элементах
gui.debug_mode = True
```

### Логирование

```python
# OpenCL ошибки
try:
    gui.render_to_buffer(framebuffer)
except cl.Error as e:
    print(f"OpenCL Error: {e}")

# Проверка элементов
for element_id, element in gui.elements.items():
    print(f"{element_id}: {element.visible}, {element.rect}")
```

---

**OpenCL GUI System** предоставляет мощную и гибкую платформу для создания высокопроизводительных интерфейсов, полностью интегрированных с GPU-ускоренным рендерингом Intel Render Engine.
