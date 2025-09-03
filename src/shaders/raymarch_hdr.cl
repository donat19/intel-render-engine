// HDR Raymarching Shader with Tone Mapping
// Enhanced version of raymarch.cl with HDR support

// Distance functions for primitives
float sdSphere(float3 p, float r) {
    return length(p) - r;
}

float sdBox(float3 p, float3 b) {
    float3 q = fabs(p) - b;
    return length(fmax(q, 0.0f)) + fmin(fmax(q.x, fmax(q.y, q.z)), 0.0f);
}

float sdTorus(float3 p, float2 t) {
    float2 q = (float2)(length(p.xz) - t.x, p.y);
    return length(q) - t.y;
}

// Scene SDF
float map(float3 pos, float time) {
    // Animated sphere
    float3 sphere_pos = pos - (float3)(sin(time) * 2.0f, 0.0f, 0.0f);
    float sphere = sdSphere(sphere_pos, 1.0f);
    
    // Static box
    float3 box_pos = pos - (float3)(0.0f, -2.0f, 0.0f);
    float box = sdBox(box_pos, (float3)(2.0f, 0.1f, 2.0f));
    
    // Rotating torus
    float3 torus_pos = pos - (float3)(0.0f, 1.0f, 3.0f);
    float c = cos(time);
    float s = sin(time);
    torus_pos.xz = (float2)(c * torus_pos.x - s * torus_pos.z, s * torus_pos.x + c * torus_pos.z);
    float torus = sdTorus(torus_pos, (float2)(1.0f, 0.3f));
    
    return fmin(fmin(sphere, box), torus);
}

// Calculate normal using finite differences
float3 calcNormal(float3 pos, float time) {
    const float h = 0.0001f;
    const float2 k = (float2)(1.0f, -1.0f);
    return normalize(k.xyy * map(pos + k.xyy * h, time) +
                    k.yyx * map(pos + k.yyx * h, time) +
                    k.yxy * map(pos + k.yxy * h, time) +
                    k.xxx * map(pos + k.xxx * h, time));
}

// Raymarching function
float raymarch(float3 ro, float3 rd, float time) {
    float dO = 0.0f;
    
    for (int i = 0; i < 100; i++) {
        float3 p = ro + rd * dO;
        float dS = map(p, time);
        dO += dS;
        if (dO > 100.0f || dS < 0.001f) break;
    }
    
    return dO;
}

// HDR lighting with physically based values
float3 hdr_lighting(float3 pos, float3 normal, float3 lightPos, float3 viewDir, float time) {
    float3 lightDir = normalize(lightPos - pos);
    float lightDistance = length(lightPos - pos);
    
    // Physically based light attenuation
    float attenuation = 1.0f / (1.0f + 0.1f * lightDistance + 0.01f * lightDistance * lightDistance);
    
    // Enhanced diffuse lighting
    float ndotl = fmax(dot(normal, lightDir), 0.0f);
    
    // Enhanced specular with energy conservation
    float3 reflectDir = -lightDir - 2.0f * dot(-lightDir, normal) * normal;
    float spec = pow(fmax(dot(viewDir, reflectDir), 0.0f), 64.0f);
    
    // HDR ambient lighting (simulating sky bounce)
    float3 ambient = (float3)(0.02f, 0.03f, 0.05f) * 2.0f;
    
    // HDR light colors (sun-like)
    float3 lightColor = (float3)(15.0f, 12.0f, 8.0f); // High intensity sun
    float3 diffuse = lightColor * (float3)(0.8f, 0.6f, 0.4f) * ndotl * attenuation;
    float3 specular = lightColor * (float3)(1.0f, 0.95f, 0.9f) * spec * attenuation;
    
    // Add rim lighting for better edge definition
    float rim = 1.0f - fmax(dot(viewDir, normal), 0.0f);
    rim = pow(rim, 3.0f);
    float3 rimLight = (float3)(0.5f, 0.7f, 1.0f) * rim * 0.5f;
    
    return ambient + diffuse + specular + rimLight;
}

// HDR sky with proper sun disk
float3 hdr_sky(float3 rd, float3 lightDir, float time) {
    float cosTheta = dot(rd, lightDir);
    
    // Sun disk with proper brightness
    float sun = smoothstep(0.9995f, 0.9999f, cosTheta);
    float3 sunColor = (float3)(100.0f, 95.0f, 80.0f) * sun;
    
    // Atmospheric gradient
    float t = rd.y * 0.5f + 0.5f;
    t = fmax(t, 0.0f);
    
    // HDR sky colors
    float3 zenith = (float3)(0.3f, 0.6f, 1.2f);    // Bright blue at zenith
    float3 horizon = (float3)(2.0f, 1.5f, 1.0f);   // Warm horizon
    
    float3 skyCol = mix(horizon, zenith, pow(t, 0.7f));
    
    // Sun halo
    float halo = pow(fmax(cosTheta, 0.0f), 8.0f);
    float3 haloColor = (float3)(3.0f, 2.5f, 2.0f) * halo * (1.0f - sun);
    
    // Atmospheric scattering near horizon
    float scattering = pow(1.0f - t, 3.0f);
    skyCol += (float3)(1.0f, 0.7f, 0.4f) * scattering * 0.5f;
    
    return skyCol + sunColor + haloColor;
}

// HDR rendering kernel
__kernel void raymarch_hdr_kernel(__global float4* hdr_output,
                                 const int width,
                                 const int height,
                                 const float time,
                                 const float16 camera_matrix,
                                 const float3 camera_pos) {
    
    int x = get_global_id(0);
    int y = get_global_id(1);
    
    if (x >= width || y >= height) return;
    
    // Convert to normalized coordinates
    float2 uv = (float2)((float)x / (float)width, (float)y / (float)height);
    uv = uv * 2.0f - 1.0f;
    uv.x *= (float)width / (float)height;
    
    // Ray direction
    float3 rd = normalize((float3)(uv.x, uv.y, -1.0f));
    
    // Apply camera rotation
    float3 rd_rotated;
    rd_rotated.x = rd.x * camera_matrix.s0 + rd.y * camera_matrix.s1 + rd.z * camera_matrix.s2;
    rd_rotated.y = rd.x * camera_matrix.s4 + rd.y * camera_matrix.s5 + rd.z * camera_matrix.s6;
    rd_rotated.z = rd.x * camera_matrix.s8 + rd.y * camera_matrix.s9 + rd.z * camera_matrix.sa;
    rd = normalize(rd_rotated);
    
    // Raymarch
    float d = raymarch(camera_pos, rd, time);
    
    float3 hdr_color = (float3)(0.0f, 0.0f, 0.0f);
    float3 lightPos = (float3)(5.0f, 5.0f, 5.0f);
    float3 lightDir = normalize(lightPos);
    
    if (d < 100.0f) {
        // Hit solid object
        float3 pos = camera_pos + rd * d;
        float3 normal = calcNormal(pos, time);
        hdr_color = hdr_lighting(pos, normal, lightPos, -rd, time);
    } else {
        // Sky
        hdr_color = hdr_sky(rd, lightDir, time);
    }
    
    // Store HDR color (no tone mapping here)
    hdr_output[y * width + x] = (float4)(hdr_color.x, hdr_color.y, hdr_color.z, 1.0f);
}

// Tone mapping operators
float3 linear_tonemap(float3 color, float exposure) {
    return color * exposure;
}

float3 reinhard_tonemap(float3 color, float exposure) {
    color *= exposure;
    return color / (1.0f + color);
}

float3 filmic_tonemap(float3 color, float exposure) {
    color *= exposure;
    float3 x = fmax((float3)(0.0f), color - 0.004f);
    return (x * (6.2f * x + 0.5f)) / (x * (6.2f * x + 1.7f) + 0.06f);
}

float3 aces_tonemap(float3 color, float exposure) {
    color *= exposure;
    float a = 2.51f;
    float b = 0.03f;
    float c = 2.43f;
    float d = 0.59f;
    float e = 0.14f;
    return clamp((color * (a * color + b)) / (color * (c * color + d) + e), 0.0f, 1.0f);
}

// Tone mapping kernel
__kernel void tone_map_kernel(__global float4* hdr_input,
                             __global uchar4* ldr_output,
                             const int width,
                             const int height,
                             const float exposure,
                             const int tone_mapping_mode,
                             const float gamma) {
    
    int x = get_global_id(0);
    int y = get_global_id(1);
    
    if (x >= width || y >= height) return;
    
    int idx = y * width + x;
    float4 hdr_pixel = hdr_input[idx];
    float3 hdr_color = hdr_pixel.xyz;
    
    // Apply tone mapping
    float3 ldr_color;
    switch (tone_mapping_mode) {
        case 0: // Linear
            ldr_color = linear_tonemap(hdr_color, exposure);
            break;
        case 1: // Reinhard
            ldr_color = reinhard_tonemap(hdr_color, exposure);
            break;
        case 2: // Filmic
            ldr_color = filmic_tonemap(hdr_color, exposure);
            break;
        case 3: // ACES
            ldr_color = aces_tonemap(hdr_color, exposure);
            break;
        default:
            ldr_color = reinhard_tonemap(hdr_color, exposure);
            break;
    }
    
    // Gamma correction
    ldr_color = pow(fmax(ldr_color, 0.0f), 1.0f / gamma);
    
    // Convert to LDR
    uchar4 pixel = (uchar4)(
        (uchar)(clamp(ldr_color.x * 255.0f, 0.0f, 255.0f)),
        (uchar)(clamp(ldr_color.y * 255.0f, 0.0f, 255.0f)),
        (uchar)(clamp(ldr_color.z * 255.0f, 0.0f, 255.0f)),
        255
    );
    
    ldr_output[idx] = pixel;
}
