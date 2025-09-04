/*
OpenCL GUI Rendering Kernels - Рендеринг GUI элементов на GPU

Этот файл содержит все ядра для рендеринга GUI элементов:
- Базовые формы (прямоугольники, круги, линии)
- Текст и шрифты
- Композитинг GUI поверх основного рендера
- Эффекты (тени, градиенты, размытие)
*/

// Структура данных для GUI элементов
typedef struct {
    float type;          // Тип элемента (enum)
    float4 rect;         // x, y, width, height
    float4 color;        // r, g, b, a
    float state_flags;   // Флаги состояния (visible, enabled, hovered, etc.)
    float z_order;       // Порядок рендеринга
    float2 padding;      // Резерв для расширений
} GUIElement;

// Вспомогательные функции для работы с цветом
float4 unpack_color(uint color_packed) {
    float r = (float)((color_packed      ) & 0xFF) / 255.0f;
    float g = (float)((color_packed >>  8) & 0xFF) / 255.0f;
    float b = (float)((color_packed >> 16) & 0xFF) / 255.0f;
    float a = (float)((color_packed >> 24) & 0xFF) / 255.0f;
    return (float4)(r, g, b, a);
}

uint pack_color(float4 color) {
    uint r = (uint)(clamp(color.x, 0.0f, 1.0f) * 255.0f);
    uint g = (uint)(clamp(color.y, 0.0f, 1.0f) * 255.0f);
    uint b = (uint)(clamp(color.z, 0.0f, 1.0f) * 255.0f);
    uint a = (uint)(clamp(color.w, 0.0f, 1.0f) * 255.0f);
    return r | (g << 8) | (b << 16) | (a << 24);
}

// Функция для смешивания цветов (alpha blending)
float4 blend_colors(float4 src, float4 dst) {
    float src_alpha = src.w;
    float inv_alpha = 1.0f - src_alpha;
    
    return (float4)(
        src.x * src_alpha + dst.x * inv_alpha,
        src.y * src_alpha + dst.y * inv_alpha,
        src.z * src_alpha + dst.z * inv_alpha,
        src_alpha + dst.w * inv_alpha
    );
}

// Функция для рендеринга прямоугольника с закругленными углами
float rounded_rect_sdf(float2 pos, float2 rect_pos, float2 rect_size, float radius) {
    float2 q = fabs(pos - rect_pos - rect_size * 0.5f) - rect_size * 0.5f + radius;
    return length(fmax(q, 0.0f)) + fmin(fmax(q.x, q.y), 0.0f) - radius;
}

// Функция для рендеринга кнопки
float4 render_button(float2 pos, float4 rect, float4 color, uint state_flags) {
    bool hovered = (state_flags & 4) != 0;
    bool pressed = (state_flags & 8) != 0;
    
    // Позиция относительно кнопки
    float2 local_pos = pos - rect.xy;
    
    // Проверяем, находимся ли мы внутри кнопки
    if (local_pos.x >= 0.0f && local_pos.x <= rect.z && 
        local_pos.y >= 0.0f && local_pos.y <= rect.w) {
        
        // Закругленные углы
        float corner_radius = 4.0f;
        float d = rounded_rect_sdf(pos, rect.xy, rect.zw, corner_radius);
        
        if (d <= 0.0f) {
            // Внутри кнопки
            float4 button_color = color;
            
            // Эффекты в зависимости от состояния
            if (pressed) {
                button_color.xyz *= 0.8f;  // Затемнение при нажатии
            } else if (hovered) {
                button_color.xyz *= 1.2f;  // Осветление при hover
            }
            
            // Градиент для объемного эффекта
            float gradient = 1.0f - (local_pos.y / rect.w) * 0.3f;
            button_color.xyz *= gradient;
            
            // Рамка
            if (d > -2.0f) {
                float4 border_color = (float4)(0.6f, 0.6f, 0.6f, 1.0f);
                float border_factor = smoothstep(-2.0f, 0.0f, d);
                button_color = mix(button_color, border_color, border_factor);
            }
            
            return button_color;
        }
    }
    
    return (float4)(0.0f, 0.0f, 0.0f, 0.0f);  // Прозрачный
}

// Функция для рендеринга панели
float4 render_panel(float2 pos, float4 rect, float4 color, uint state_flags) {
    float2 local_pos = pos - rect.xy;
    
    if (local_pos.x >= 0.0f && local_pos.x <= rect.z && 
        local_pos.y >= 0.0f && local_pos.y <= rect.w) {
        
        float4 panel_color = color;
        
        // Заголовок панели (первые 24 пикселя)
        if (local_pos.y <= 24.0f) {
            panel_color.xyz *= 1.3f;  // Осветление заголовка
            
            // Линия разделения
            if (local_pos.y >= 22.0f && local_pos.y <= 24.0f) {
                panel_color = (float4)(0.5f, 0.5f, 0.5f, 1.0f);
            }
        }
        
        // Рамка панели
        if (local_pos.x <= 1.0f || local_pos.x >= rect.z - 1.0f ||
            local_pos.y <= 1.0f || local_pos.y >= rect.w - 1.0f) {
            panel_color = (float4)(0.4f, 0.4f, 0.4f, 1.0f);
        }
        
        return panel_color;
    }
    
    return (float4)(0.0f, 0.0f, 0.0f, 0.0f);
}

// Функция для рендеринга слайдера
float4 render_slider(float2 pos, float4 rect, float4 color, uint state_flags, float value) {
    float2 local_pos = pos - rect.xy;
    
    if (local_pos.x >= 0.0f && local_pos.x <= rect.z && 
        local_pos.y >= 0.0f && local_pos.y <= rect.w) {
        
        float4 slider_color = color;
        
        // Дорожка слайдера
        float track_height = 4.0f;
        float track_y = rect.w * 0.5f - track_height * 0.5f;
        
        if (local_pos.y >= track_y && local_pos.y <= track_y + track_height) {
            slider_color = (float4)(0.3f, 0.3f, 0.3f, 1.0f);
            
            // Заполненная часть
            float filled_width = value * rect.z;
            if (local_pos.x <= filled_width) {
                slider_color = (float4)(0.2f, 0.6f, 1.0f, 1.0f);  // Синий цвет
            }
        }
        
        // Ручка слайдера
        float handle_width = 16.0f;
        float handle_x = value * (rect.z - handle_width);
        
        if (local_pos.x >= handle_x && local_pos.x <= handle_x + handle_width &&
            local_pos.y >= 2.0f && local_pos.y <= rect.w - 2.0f) {
            
            bool hovered = (state_flags & 4) != 0;
            bool pressed = (state_flags & 8) != 0;
            
            slider_color = (float4)(0.8f, 0.8f, 0.8f, 1.0f);
            
            if (pressed) {
                slider_color.xyz *= 0.7f;
            } else if (hovered) {
                slider_color.xyz *= 1.1f;
            }
        }
        
        return slider_color;
    }
    
    return (float4)(0.0f, 0.0f, 0.0f, 0.0f);
}

// Основное ядро для рендеринга GUI элементов
__kernel void render_gui_kernel(__global uchar4* framebuffer,
                               __global float16* elements,
                               const int element_count,
                               const int width,
                               const int height) {
    
    int x = get_global_id(0);
    int y = get_global_id(1);
    
    if (x >= width || y >= height) return;
    
    int pixel_index = y * width + x;
    float2 pos = (float2)((float)x, (float)y);
    
    // Получаем текущий цвет пикселя
    uchar4 current_pixel = framebuffer[pixel_index];
    float4 current_color = (float4)(
        (float)current_pixel.x / 255.0f,
        (float)current_pixel.y / 255.0f,
        (float)current_pixel.z / 255.0f,
        (float)current_pixel.w / 255.0f
    );
    
    float4 final_color = current_color;
    
    // Проходим по всем GUI элементам
    for (int i = 0; i < element_count; i++) {
        __global float16* element_data = &elements[i];
        
        float element_type = element_data->s0;
        float4 rect = (float4)(element_data->s1, element_data->s2, 
                              element_data->s3, element_data->s4);
        float4 color = (float4)(element_data->s5, element_data->s6, 
                               element_data->s7, element_data->s8);
        uint state_flags = (uint)element_data->s9;
        
        // Проверяем видимость
        if ((state_flags & 1) == 0) continue;  // Не видимый
        
        float4 element_color = (float4)(0.0f, 0.0f, 0.0f, 0.0f);
        
        // Рендерим в зависимости от типа элемента
        if (element_type == 0.0f) {  // BUTTON
            element_color = render_button(pos, rect, color, state_flags);
        } else if (element_type == 2.0f) {  // PANEL
            element_color = render_panel(pos, rect, color, state_flags);
        } else if (element_type == 4.0f) {  // SLIDER
            float value = element_data->sa;  // Используем дополнительное поле для значения
            element_color = render_slider(pos, rect, color, state_flags, value);
        } else {
            // Простой прямоугольник для остальных типов
            float2 local_pos = pos - rect.xy;
            if (local_pos.x >= 0.0f && local_pos.x <= rect.z && 
                local_pos.y >= 0.0f && local_pos.y <= rect.w) {
                element_color = color;
            }
        }
        
        // Смешиваем с текущим цветом
        if (element_color.w > 0.0f) {
            final_color = blend_colors(element_color, final_color);
        }
    }
    
    // Записываем результат обратно в framebuffer
    framebuffer[pixel_index] = (uchar4)(
        (uchar)(clamp(final_color.x * 255.0f, 0.0f, 255.0f)),
        (uchar)(clamp(final_color.y * 255.0f, 0.0f, 255.0f)),
        (uchar)(clamp(final_color.z * 255.0f, 0.0f, 255.0f)),
        (uchar)(clamp(final_color.w * 255.0f, 0.0f, 255.0f))
    );
}

// Ядро для рендеринга текста
__kernel void render_text_kernel(__global uchar4* framebuffer,
                                __global uchar* text_data,
                                __global uchar* font_bitmap,
                                const float text_x,
                                const float text_y,
                                const int text_length,
                                const int text_offset,
                                const float4 text_color,
                                const int width,
                                const int height) {
    
    int local_x = get_global_id(0);
    int local_y = get_global_id(1);
    
    // Размеры символа в bitmap
    const int char_width = 8;
    const int char_height = 12;
    const int chars_per_row = 16;
    
    // Определяем, какой символ и какой пиксель внутри символа
    int char_index = local_x / char_width;
    int pixel_x = local_x % char_width;
    int pixel_y = local_y;
    
    if (char_index >= text_length || pixel_y >= char_height) return;
    
    // Получаем код символа
    int char_code = text_data[text_offset + char_index];
    if (char_code < 32 || char_code > 127) char_code = 32;  // Заменяем на пробел
    
    // Вычисляем позицию в font bitmap
    int char_bitmap_x = ((char_code - 32) % chars_per_row) * char_width;
    int char_bitmap_y = ((char_code - 32) / chars_per_row) * char_height;
    
    int bitmap_index = (char_bitmap_y + pixel_y) * 512 + (char_bitmap_x + pixel_x);
    uchar font_pixel = font_bitmap[bitmap_index];
    
    // Если пиксель шрифта не пустой, рендерим его
    if (font_pixel > 128) {  // Порог для определения наличия пикселя
        int screen_x = (int)(text_x + local_x);
        int screen_y = (int)(text_y + local_y);
        
        if (screen_x >= 0 && screen_x < width && screen_y >= 0 && screen_y < height) {
            int pixel_index = screen_y * width + screen_x;
            
            // Получаем текущий цвет пикселя
            uchar4 current_pixel = framebuffer[pixel_index];
            float4 current_color = (float4)(
                (float)current_pixel.x / 255.0f,
                (float)current_pixel.y / 255.0f,
                (float)current_pixel.z / 255.0f,
                (float)current_pixel.w / 255.0f
            );
            
            // Смешиваем цвет текста с фоном
            float alpha = (float)font_pixel / 255.0f * text_color.w;
            float4 blended_color = (float4)(
                text_color.x * alpha + current_color.x * (1.0f - alpha),
                text_color.y * alpha + current_color.y * (1.0f - alpha),
                text_color.z * alpha + current_color.z * (1.0f - alpha),
                alpha + current_color.w * (1.0f - alpha)
            );
            
            framebuffer[pixel_index] = (uchar4)(
                (uchar)(clamp(blended_color.x * 255.0f, 0.0f, 255.0f)),
                (uchar)(clamp(blended_color.y * 255.0f, 0.0f, 255.0f)),
                (uchar)(clamp(blended_color.z * 255.0f, 0.0f, 255.0f)),
                (uchar)(clamp(blended_color.w * 255.0f, 0.0f, 255.0f))
            );
        }
    }
}

// Ядро для композитинга GUI поверх основного рендера
__kernel void composite_gui_kernel(__global uchar4* main_framebuffer,
                                  __global uchar4* gui_framebuffer,
                                  const int width,
                                  const int height,
                                  const float gui_alpha) {
    
    int x = get_global_id(0);
    int y = get_global_id(1);
    
    if (x >= width || y >= height) return;
    
    int pixel_index = y * width + x;
    
    uchar4 main_pixel = main_framebuffer[pixel_index];
    uchar4 gui_pixel = gui_framebuffer[pixel_index];
    
    // Конвертируем в float для расчетов
    float4 main_color = (float4)(
        (float)main_pixel.x / 255.0f,
        (float)main_pixel.y / 255.0f,
        (float)main_pixel.z / 255.0f,
        (float)main_pixel.w / 255.0f
    );
    
    float4 gui_color = (float4)(
        (float)gui_pixel.x / 255.0f,
        (float)gui_pixel.y / 255.0f,
        (float)gui_pixel.z / 255.0f,
        (float)gui_pixel.w / 255.0f * gui_alpha
    );
    
    // Alpha blending
    float4 final_color = blend_colors(gui_color, main_color);
    
    // Записываем результат
    main_framebuffer[pixel_index] = (uchar4)(
        (uchar)(clamp(final_color.x * 255.0f, 0.0f, 255.0f)),
        (uchar)(clamp(final_color.y * 255.0f, 0.0f, 255.0f)),
        (uchar)(clamp(final_color.z * 255.0f, 0.0f, 255.0f)),
        (uchar)(clamp(final_color.w * 255.0f, 0.0f, 255.0f))
    );
}

// Ядро для эффектов GUI (тени, размытие)
__kernel void gui_effects_kernel(__global uchar4* framebuffer,
                                __global uchar4* temp_buffer,
                                const int width,
                                const int height,
                                const int effect_type,
                                const float effect_strength) {
    
    int x = get_global_id(0);
    int y = get_global_id(1);
    
    if (x >= width || y >= height) return;
    
    int pixel_index = y * width + x;
    
    if (effect_type == 0) {  // Размытие
        float4 color_sum = (float4)(0.0f, 0.0f, 0.0f, 0.0f);
        int sample_count = 0;
        
        int blur_radius = (int)(effect_strength * 3.0f);
        
        for (int dy = -blur_radius; dy <= blur_radius; dy++) {
            for (int dx = -blur_radius; dx <= blur_radius; dx++) {
                int sample_x = x + dx;
                int sample_y = y + dy;
                
                if (sample_x >= 0 && sample_x < width && 
                    sample_y >= 0 && sample_y < height) {
                    
                    int sample_index = sample_y * width + sample_x;
                    uchar4 sample_pixel = framebuffer[sample_index];
                    
                    color_sum.x += (float)sample_pixel.x;
                    color_sum.y += (float)sample_pixel.y;
                    color_sum.z += (float)sample_pixel.z;
                    color_sum.w += (float)sample_pixel.w;
                    sample_count++;
                }
            }
        }
        
        if (sample_count > 0) {
            color_sum /= (float)sample_count;
            
            temp_buffer[pixel_index] = (uchar4)(
                (uchar)clamp(color_sum.x, 0.0f, 255.0f),
                (uchar)clamp(color_sum.y, 0.0f, 255.0f),
                (uchar)clamp(color_sum.z, 0.0f, 255.0f),
                (uchar)clamp(color_sum.w, 0.0f, 255.0f)
            );
        } else {
            temp_buffer[pixel_index] = framebuffer[pixel_index];
        }
    } else if (effect_type == 1) {  // Тень
        // Простая реализация теней - смещение и затемнение
        int shadow_offset_x = 2;
        int shadow_offset_y = 2;
        
        int shadow_x = x - shadow_offset_x;
        int shadow_y = y - shadow_offset_y;
        
        if (shadow_x >= 0 && shadow_x < width && 
            shadow_y >= 0 && shadow_y < height) {
            
            int shadow_index = shadow_y * width + shadow_x;
            uchar4 shadow_pixel = framebuffer[shadow_index];
            
            // Затемняем для создания тени
            temp_buffer[pixel_index] = (uchar4)(
                (uchar)((float)shadow_pixel.x * 0.3f),
                (uchar)((float)shadow_pixel.y * 0.3f),
                (uchar)((float)shadow_pixel.z * 0.3f),
                shadow_pixel.w
            );
        } else {
            temp_buffer[pixel_index] = (uchar4)(0, 0, 0, 0);
        }
    } else {
        // Без эффектов - просто копируем
        temp_buffer[pixel_index] = framebuffer[pixel_index];
    }
}
