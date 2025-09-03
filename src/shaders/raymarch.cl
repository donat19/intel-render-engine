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

// Simple lighting
float3 lighting(float3 pos, float3 normal, float3 lightPos, float3 viewDir) {
    float3 lightDir = normalize(lightPos - pos);
    float diff = fmax(dot(normal, lightDir), 0.0f);
    
    // Manual reflection calculation: r = d - 2 * (d · n) * n
    float3 reflectDir = -lightDir - 2.0f * dot(-lightDir, normal) * normal;
    float spec = pow(fmax(dot(viewDir, reflectDir), 0.0f), 32.0f);
    
    float3 ambient = (float3)(0.1f, 0.1f, 0.2f);
    float3 diffuse = (float3)(0.8f, 0.6f, 0.4f) * diff;
    float3 specular = (float3)(1.0f, 1.0f, 1.0f) * spec;
    
    return ambient + diffuse + specular;
}

__kernel void raymarch_kernel(__global uchar4* output,
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
    
    // Apply camera rotation (simplified - using first 3x3 of matrix)
    float3 rd_rotated;
    rd_rotated.x = rd.x * camera_matrix.s0 + rd.y * camera_matrix.s1 + rd.z * camera_matrix.s2;
    rd_rotated.y = rd.x * camera_matrix.s4 + rd.y * camera_matrix.s5 + rd.z * camera_matrix.s6;
    rd_rotated.z = rd.x * camera_matrix.s8 + rd.y * camera_matrix.s9 + rd.z * camera_matrix.sa;
    rd = normalize(rd_rotated);
    
    // Raymarch
    float d = raymarch(camera_pos, rd, time);
    
    float3 color = (float3)(0.0f, 0.0f, 0.0f);
    
    if (d < 100.0f) {
        float3 pos = camera_pos + rd * d;
        float3 normal = calcNormal(pos, time);
        float3 lightPos = (float3)(5.0f, 5.0f, 5.0f);
        color = lighting(pos, normal, lightPos, -rd);
    } else {
        // Background gradient
        float t = uv.y * 0.5f + 0.5f;
        color = (float3)(0.1f, 0.2f, 0.4f) * (1.0f - t) + (float3)(0.8f, 0.9f, 1.0f) * t;
    }
    
    // Gamma correction
    color = pow(color, 1.0f / 2.2f);
    
    // Convert to RGBA
    uchar4 pixel = (uchar4)(
        (uchar)(clamp(color.x * 255.0f, 0.0f, 255.0f)),
        (uchar)(clamp(color.y * 255.0f, 0.0f, 255.0f)),
        (uchar)(clamp(color.z * 255.0f, 0.0f, 255.0f)),
        255
    );
    
    output[y * width + x] = pixel;
}
