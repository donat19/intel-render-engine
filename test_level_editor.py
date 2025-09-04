#!/usr/bin/env python3
"""
Simple Level Editor Test - Простой тест Level Editor

Минимальная версия для проверки работы ImGui с нашим движком.
"""

import sys
import os
import pygame
import imgui
from imgui.integrations.pygame import PygameRenderer

# Добавляем пути
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

def main():
    print("🚀 Запуск Level Editor Test...")
    
    try:
        pygame.init()
        print("✅ Pygame инициализирован")
        
        size = 1200, 800
        screen = pygame.display.set_mode(size, pygame.RESIZABLE)
        pygame.display.set_caption("Level Editor Test")
        print("✅ Окно создано")
        
        imgui.create_context()
        print("✅ ImGui контекст создан")
        
        renderer = PygameRenderer()
        print("✅ Renderer создан")
        
        io = imgui.get_io()
        io.display_size = size
        io.fonts.get_tex_data_as_rgba32()
        print("✅ ImGui настроен")
        
        clock = pygame.time.Clock()
        running = True
        show_demo = True
        
        print("🎯 Главный цикл...")
        frame_count = 0
        
        while running:
            frame_count += 1
            if frame_count % 60 == 0:  # Каждую секунду
                print(f"Frame {frame_count}, FPS: {clock.get_fps():.1f}")
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("❌ Получен сигнал QUIT")
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        print("❌ Нажата ESC")
                        running = False
                renderer.process_event(event)
                
            renderer.process_inputs()
            imgui.new_frame()
            
            # Главное меню
            if imgui.begin_main_menu_bar():
                if imgui.begin_menu("File"):
                    if imgui.menu_item("Exit")[0]:
                        print("❌ Exit из меню")
                        running = False
                    imgui.end_menu()
                if imgui.begin_menu("Window"):
                    clicked, show_demo = imgui.menu_item("ImGui Demo", selected=show_demo)
                    imgui.end_menu()
                imgui.end_main_menu_bar()
                
            # Demo окно
            if show_demo:
                show_demo = imgui.show_demo_window()
                
            # Простое окно
            if imgui.begin("Level Editor Test"):
                imgui.text("✅ ImGui работает!")
                imgui.text("✅ Pygame интеграция работает!")
                imgui.text("✅ OpenGL контекст активен!")
                
                if imgui.button("Тест кнопки"):
                    print("🔘 Кнопка нажата!")
                    
                if imgui.button("Выход"):
                    print("❌ Выход через кнопку")
                    running = False
                    
                imgui.separator()
                imgui.text("Следующие шаги:")
                imgui.bullet_text("Интеграция с raymarcher")
                imgui.bullet_text("Система областей")
                imgui.bullet_text("Редакторы сцены")
                
            imgui.end()
            
            # Информационное окно
            if imgui.begin("System Info"):
                imgui.text(f"Frame: {frame_count}")
                imgui.text(f"FPS: {clock.get_fps():.1f}")
                imgui.text(f"Window size: {size[0]}x{size[1]}")
                imgui.text(f"ImGui version: {imgui.get_version()}")
                
            imgui.end()
            
            # Рендеринг
            pygame.display.get_surface().fill((30, 30, 30))
            
            imgui.render()
            renderer.render(imgui.get_draw_data())
            
            pygame.display.flip()
            clock.tick(60)
            
        print("🔄 Выход из главного цикла")
        renderer.shutdown()
        pygame.quit()
        
    except Exception as e:
        print(f"❌ Критическая ошибка в main(): {e}")
        import traceback
        traceback.print_exc()
        return False
        
    return True

if __name__ == "__main__":
    print("🏗️ Intel Render Engine - Level Editor Test")
    print("=" * 50)
    
    try:
        success = main()
        if success:
            print("👋 Level Editor Test завершен успешно!")
        else:
            print("❌ Level Editor Test завершен с ошибками")
    except KeyboardInterrupt:
        print("\n🛑 Прервано пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
