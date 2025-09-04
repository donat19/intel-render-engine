#!/usr/bin/env python3
"""
Level Editor Launcher

Лаунчер для запуска редактора уровней с проверкой зависимостей.
Автоматически устанавливает необходимые пакеты если они отсутствуют.
"""

import sys
import os
import subprocess
import argparse

def check_dependencies():
    """Проверка и установка зависимостей"""
    print("🔍 Проверка зависимостей Level Editor...")
    
    required_packages = [
        'imgui[glfw,opengl,pygame]',
        'PyOpenGL',
        'PyOpenGL_accelerate',
        'pygame',
        'numpy'
    ]
    
    missing_packages = []
    
    # Проверяем каждый пакет
    for package in required_packages:
        package_name = package.split('[')[0]  # Убираем extras из имени
        try:
            if package_name == 'imgui':
                import imgui
                # Проверяем pygame integration
                try:
                    from imgui.integrations.pygame import PygameRenderer
                except ImportError:
                    missing_packages.append(package)
            elif package_name == 'PyOpenGL':
                import OpenGL.GL
            elif package_name == 'PyOpenGL_accelerate':
                try:
                    import OpenGL_accelerate
                except ImportError:
                    pass  # Это опциональный пакет
            elif package_name == 'pygame':
                import pygame
            elif package_name == 'numpy':
                import numpy
                
        except ImportError:
            missing_packages.append(package)
            
    if missing_packages:
        print(f"❌ Отсутствуют пакеты: {', '.join(missing_packages)}")
        print("📦 Устанавливаем недостающие зависимости...")
        
        for package in missing_packages:
            try:
                print(f"   Устанавливаем {package}...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"   ✅ {package} установлен")
            except subprocess.CalledProcessError as e:
                print(f"   ❌ Ошибка установки {package}: {e}")
                return False
                
        print("✅ Все зависимости установлены!")
    else:
        print("✅ Все зависимости уже установлены")
        
    return True

def check_opengl_support():
    """Проверка поддержки OpenGL"""
    try:
        import pygame
        pygame.init()
        
        # Создаем тестовое окно с OpenGL контекстом
        pygame.display.set_mode((100, 100), pygame.OPENGL | pygame.HIDDEN)
        
        import OpenGL.GL as gl
        version = gl.glGetString(gl.GL_VERSION)
        renderer = gl.glGetString(gl.GL_RENDERER)
        
        pygame.quit()
        
        print(f"🎮 OpenGL версия: {version.decode()}")
        print(f"🎮 Рендерер: {renderer.decode()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка поддержки OpenGL: {e}")
        return False

def launch_level_editor(debug=False):
    """Запуск Level Editor"""
    print("🚀 Запуск Intel Render Engine - Level Editor")
    
    # Добавляем текущую директорию в Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
    
    sys.path.insert(0, project_root)
    sys.path.insert(0, os.path.join(project_root, 'src'))
    
    try:
        if debug:
            print("🐛 Режим отладки включен")
            
        # Импортируем и запускаем Level Editor
        from src.level_editor.level_editor import LevelEditor
        
        print("✨ Инициализация Level Editor...")
        editor = LevelEditor()
        
        print("🎯 Level Editor готов к работе!")
        print("\n📋 Управление:")
        print("   F12 - Показать/скрыть ImGui Demo")
        print("   Tab - Переключение типа редактора в активной области")
        print("   Меню File -> Exit или закрытие окна для выхода")
        print()
        
        editor.run()
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("💡 Попробуйте переустановить зависимости")
        return False
        
    except Exception as e:
        print(f"❌ Ошибка запуска Level Editor: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        return False
        
    return True

def main():
    """Главная функция лаунчера"""
    parser = argparse.ArgumentParser(
        description='Level Editor Launcher для Intel Render Engine',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python level_editor_launcher.py                # Обычный запуск
  python level_editor_launcher.py --debug        # Запуск с отладкой
  python level_editor_launcher.py --check-deps   # Только проверка зависимостей
  python level_editor_launcher.py --force-install # Принудительная переустановка

Level Editor Features:
  🎨 Модульный интерфейс в стиле Blender
  🏗️ Система областей (Areas) с различными редакторами
  👀 3D Viewport с real-time raymarching
  📁 Outliner для управления иерархией сцены
  ⚙️ Properties editor для настройки объектов
  💾 Сохранение и загрузка раскладки интерфейса
  🎬 HDR рендеринг и настройки материалов
        """
    )
    
    parser.add_argument('--debug', action='store_true',
                       help='Запуск в режиме отладки')
    parser.add_argument('--check-deps', action='store_true',
                       help='Только проверить зависимости')
    parser.add_argument('--force-install', action='store_true',
                       help='Принудительно переустановить все зависимости')
    parser.add_argument('--skip-opengl-check', action='store_true',
                       help='Пропустить проверку OpenGL')
    
    args = parser.parse_args()
    
    print("🏗️ Intel Render Engine - Level Editor Launcher")
    print("=" * 50)
    
    # Принудительная установка зависимостей
    if args.force_install:
        print("🔄 Принудительная переустановка зависимостей...")
        required_packages = [
            'imgui[glfw,opengl,pygame]',
            'PyOpenGL',
            'PyOpenGL_accelerate', 
            'pygame',
            'numpy'
        ]
        
        for package in required_packages:
            try:
                print(f"   Переустанавливаем {package}...")
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', 
                    '--upgrade', '--force-reinstall', package
                ])
            except subprocess.CalledProcessError as e:
                print(f"   ❌ Ошибка установки {package}: {e}")
        
        print("✅ Переустановка завершена!")
        
    # Проверка зависимостей
    if not check_dependencies():
        print("❌ Не удалось установить зависимости")
        sys.exit(1)
        
    if args.check_deps:
        print("✅ Проверка зависимостей завершена")
        sys.exit(0)
        
    # Проверка OpenGL
    if not args.skip_opengl_check:
        if not check_opengl_support():
            print("⚠️ Проблемы с поддержкой OpenGL")
            print("💡 Попробуйте запустить с --skip-opengl-check")
            response = input("Продолжить запуск? (y/N): ")
            if response.lower() != 'y':
                sys.exit(1)
                
    # Запуск Level Editor
    success = launch_level_editor(debug=args.debug)
    
    if success:
        print("👋 Level Editor завершен")
    else:
        print("❌ Level Editor завершен с ошибкой")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Запуск прерван пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Критическая ошибка лаунчера: {e}")
        sys.exit(1)
