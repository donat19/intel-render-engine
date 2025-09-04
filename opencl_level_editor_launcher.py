#!/usr/bin/env python3
"""
OpenCL Level Editor Launcher

Лаунчер для запуска Level Editor с полностью OpenCL GUI системой.
Автоматически проверяет зависимости и создает необходимые директории.
"""
import sys
import os
import argparse
import subprocess
import time
from typing import List, Dict, Any

def check_dependencies() -> bool:
    """Проверка и установка зависимостей"""
    print("🔍 Проверка зависимостей OpenCL Level Editor...")
    
    required_packages = [
        'pyopencl',
        'numpy', 
        'pygame',
        'Pillow'
    ]
    
    missing_packages = []
    
    # Проверяем каждый пакет
    for package in required_packages:
        try:
            if package == 'pyopencl':
                import pyopencl
                print(f"✅ {package}: {pyopencl.get_platforms()}")
            elif package == 'numpy':
                import numpy
                print(f"✅ {package}: {numpy.__version__}")
            elif package == 'pygame':
                import pygame
                pygame.init()
                print(f"✅ {package}: {pygame.version.ver}")
                pygame.quit()
            elif package == 'Pillow':
                from PIL import Image
                print(f"✅ {package}: available")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}: не найден")
    
    if missing_packages:
        print(f"\n📦 Устанавливаем недостающие пакеты: {', '.join(missing_packages)}")
        
        for package in missing_packages:
            try:
                print(f"📥 Устанавливаем {package}...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✅ {package} установлен")
            except subprocess.CalledProcessError as e:
                print(f"❌ Ошибка установки {package}: {e}")
                return False
    
    print("✅ Все зависимости готовы")
    return True

def check_opencl_support() -> bool:
    """Проверка поддержки OpenCL"""
    print("🔍 Проверка поддержки OpenCL...")
    
    try:
        import pyopencl as cl
        
        # Получаем список платформ
        platforms = cl.get_platforms()
        if not platforms:
            print("❌ OpenCL платформы не найдены")
            return False
        
        print(f"✅ Найдено OpenCL платформ: {len(platforms)}")
        
        # Проверяем устройства на каждой платформе
        total_devices = 0
        for i, platform in enumerate(platforms):
            try:
                devices = platform.get_devices()
                device_count = len(devices)
                total_devices += device_count
                
                print(f"  Платформа {i+1}: {platform.name.strip()} ({device_count} устройств)")
                
                for j, device in enumerate(devices):
                    device_type = "GPU" if device.type & cl.device_type.GPU else "CPU"
                    print(f"    Устройство {j+1}: {device.name.strip()} ({device_type})")
                    
            except Exception as e:
                print(f"  Платформа {i+1}: ошибка получения устройств - {e}")
        
        if total_devices == 0:
            print("❌ OpenCL устройства не найдены")
            return False
        
        # Создаем тестовый контекст
        try:
            context = cl.create_some_context(interactive=False)
            queue = cl.CommandQueue(context)
            print("✅ OpenCL контекст создан успешно")
            return True
        except Exception as e:
            print(f"❌ Ошибка создания OpenCL контекста: {e}")
            return False
            
    except ImportError:
        print("❌ PyOpenCL не установлен")
        return False
    except Exception as e:
        print(f"❌ Ошибка проверки OpenCL: {e}")
        return False

def check_gui_files() -> bool:
    """Проверка наличия необходимых файлов GUI"""
    print("🔍 Проверка файлов OpenCL GUI...")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    required_files = [
        'opencl_level_editor.py',
        'src/gui/opencl_gui.py',
        'shaders/gui.cl',
        'src/core/raymarcher.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        full_path = os.path.join(current_dir, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path}: не найден")
    
    if missing_files:
        print(f"\n❌ Отсутствуют важные файлы:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        
        # Пытаемся создать недостающие директории
        directories_to_create = [
            'src/gui',
            'src/core', 
            'shaders'
        ]
        
        for dir_path in directories_to_create:
            full_dir_path = os.path.join(current_dir, dir_path)
            if not os.path.exists(full_dir_path):
                try:
                    os.makedirs(full_dir_path, exist_ok=True)
                    print(f"📁 Создана директория: {dir_path}")
                except Exception as e:
                    print(f"❌ Ошибка создания директории {dir_path}: {e}")
        
        return False
    
    print("✅ Все необходимые файлы найдены")
    return True

def setup_python_path():
    """Настройка Python путей"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    paths_to_add = [
        current_dir,
        os.path.join(current_dir, 'src'),
        os.path.join(current_dir, 'src', 'core'),
        os.path.join(current_dir, 'src', 'gui')
    ]
    
    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    print(f"🐍 Python paths настроены: {len(paths_to_add)} путей добавлено")

def launch_opencl_level_editor(debug: bool = False, theme: str = "blender") -> bool:
    """Запуск OpenCL Level Editor"""
    print("🚀 Запуск OpenCL Level Editor...")
    
    setup_python_path()
    
    try:
        # Импортируем и запускаем Level Editor
        from opencl_level_editor import OpenCLLevelEditor, GUITheme
        
        # Определяем тему
        theme_map = {
            'dark': GUITheme.DARK,
            'light': GUITheme.LIGHT,
            'blender': GUITheme.BLENDER,
            'cyberpunk': GUITheme.CYBERPUNK
        }
        
        selected_theme = theme_map.get(theme.lower(), GUITheme.BLENDER)
        
        print(f"🎨 Тема интерфейса: {selected_theme.value}")
        print(f"🐛 Режим отладки: {'включен' if debug else 'выключен'}")
        
        # Создаем и запускаем редактор
        editor = OpenCLLevelEditor(width=1400, height=900)
        if editor.gui:
            editor.gui.set_theme(selected_theme)
            print(f"🎨 Применена тема: {selected_theme.value}")
        
        print("\n" + "="*60)
        print("🎮 УПРАВЛЕНИЕ:")
        print("  WASD - движение камеры")
        print("  Мышь - поворот камеры (при зажатой ЛКМ)")
        print("  Стрелки - поворот камеры")
        print("  Q/E - вверх/вниз")
        print("  F11 - полноэкранный режим")
        print("  F1 - справка")
        print("  ESC - выход")
        print("="*60)
        print("🎛️ GUI: Используйте OpenCL GUI панели для управления")
        print("🎬 Raymarching работает на GPU через OpenCL")
        print("✨ Все UI элементы рендерятся на GPU")
        print("="*60 + "\n")
        
        editor.run()
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("🔧 Проверьте, что все файлы на месте")
        return False
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        return False

def run_system_info():
    """Отображение информации о системе"""
    print("💻 ИНФОРМАЦИЯ О СИСТЕМЕ")
    print("="*50)
    
    # Python info
    print(f"🐍 Python: {sys.version}")
    print(f"📁 Рабочая директория: {os.getcwd()}")
    
    # OpenCL info
    try:
        import pyopencl as cl
        platforms = cl.get_platforms()
        print(f"🔧 OpenCL платформ: {len(platforms)}")
        
        for platform in platforms:
            try:
                devices = platform.get_devices()
                print(f"   {platform.name.strip()}: {len(devices)} устройств")
            except:
                print(f"   {platform.name.strip()}: ошибка получения устройств")
    except:
        print("❌ OpenCL недоступен")
    
    # Memory info
    try:
        import psutil
        memory = psutil.virtual_memory()
        print(f"💾 RAM: {memory.total // (1024**3)} GB (доступно: {memory.available // (1024**3)} GB)")
    except:
        print("💾 RAM: информация недоступна")
    
    print("="*50)

def main():
    """Главная функция лаунчера"""
    parser = argparse.ArgumentParser(
        description='OpenCL Level Editor Launcher для Intel Render Engine',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ:
  python opencl_level_editor_launcher.py                    # Обычный запуск
  python opencl_level_editor_launcher.py --debug            # С отладкой
  python opencl_level_editor_launcher.py --theme cyberpunk  # Cyberpunk тема
  python opencl_level_editor_launcher.py --check-only       # Только проверка
  python opencl_level_editor_launcher.py --system-info      # Информация о системе

ОСОБЕННОСТИ OPENCL LEVEL EDITOR:
  🎨 Полностью GPU-ускоренный интерфейс на OpenCL
  🚀 Все UI элементы рендерятся на GPU 
  🎬 Интеграция с raymarching движком
  🎛️ Профессиональные инструменты редактирования
  ⚡ Максимальная производительность
  🎭 Множественные темы интерфейса
  
ТРЕБОВАНИЯ:
  ✅ Python 3.8+
  ✅ OpenCL 1.2+
  ✅ GPU с поддержкой OpenCL (рекомендуется)
  ✅ 4GB+ RAM
        """
    )
    
    parser.add_argument('--debug', action='store_true',
                       help='Запуск в режиме отладки')
    parser.add_argument('--theme', choices=['dark', 'light', 'blender', 'cyberpunk'],
                       default='blender', help='Тема интерфейса')
    parser.add_argument('--check-only', action='store_true',
                       help='Только проверка зависимостей')
    parser.add_argument('--system-info', action='store_true',
                       help='Показать информацию о системе')
    parser.add_argument('--force-install', action='store_true',
                       help='Принудительная переустановка зависимостей')
    
    args = parser.parse_args()
    
    print("🏗️ Intel Render Engine - OpenCL Level Editor Launcher")
    print("🎨 Полностью GPU-ускоренный интерфейс на OpenCL")
    print("=" * 60)
    
    # Информация о системе
    if args.system_info:
        run_system_info()
        return
    
    # Принудительная установка
    if args.force_install:
        print("🔄 Принудительная переустановка зависимостей...")
        packages = ['pyopencl', 'numpy', 'pygame', 'Pillow']
        for package in packages:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', package])
                print(f"✅ {package} переустановлен")
            except Exception as e:
                print(f"❌ Ошибка переустановки {package}: {e}")
    
    # Проверка зависимостей
    if not check_dependencies():
        print("❌ Ошибка проверки зависимостей")
        sys.exit(1)
    
    # Проверка OpenCL
    if not check_opencl_support():
        print("❌ OpenCL недоступен")
        print("💡 Убедитесь, что:")
        print("   - Установлены драйверы GPU")
        print("   - Установлен OpenCL runtime")
        print("   - GPU поддерживает OpenCL")
        sys.exit(1)
    
    # Проверка файлов
    if not check_gui_files():
        print("❌ Отсутствуют необходимые файлы")
        print("💡 Убедитесь, что проект полностью скопирован")
        if not args.check_only:
            sys.exit(1)
    
    # Только проверка
    if args.check_only:
        print("✅ Все проверки пройдены успешно!")
        print("🚀 Level Editor готов к запуску")
        return
    
    # Запуск Level Editor
    print("\n🎬 Все проверки пройдены, запускаем Level Editor...")
    time.sleep(1)  # Небольшая пауза для читаемости
    
    success = launch_opencl_level_editor(debug=args.debug, theme=args.theme)
    
    if success:
        print("\n👋 OpenCL Level Editor завершен успешно!")
    else:
        print("\n❌ Ошибка запуска OpenCL Level Editor")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Прервано пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
