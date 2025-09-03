// Volumetric Cloud Raymarching Shader
// Implements realistic volumetric clouds with noise-based density

// Custom fract function for OpenCL compatibility
float3 fract3(float3 x) {
    return x - floor(x);
}

float fract1(float x) {
    return x - floor(x);
}

// Hash function for noise generation
float hash(float3 p) {
    p = fract3(p * 0.3183099f + 0.1f);
    p *= 17.0f;
    return fract1(p.x * p.y * p.z * (p.x + p.y + p.z));
}

// 3D noise function using interpolation
float noise(float3 x) {
    float3 p = floor(x);
    float3 f = fract3(x);
    f = f * f * (3.0f - 2.0f * f);
    
    return mix(mix(mix(hash(p + (float3)(0, 0, 0)), 
                      hash(p + (float3)(1, 0, 0)), f.x),
                  mix(hash(p + (float3)(0, 1, 0)), 
                      hash(p + (float3)(1, 1, 0)), f.x), f.y),
              mix(mix(hash(p + (float3)(0, 0, 1)), 
                      hash(p + (float3)(1, 0, 1)), f.x),
                  mix(hash(p + (float3)(0, 1, 1)), 
                      hash(p + (float3)(1, 1, 1)), f.x), f.y), f.z);
}

// Fractal noise (FBM - Fractional Brownian Motion)
float fbm(float3 x, int octaves) {
    float v = 0.0f;
    float a = 0.5f;
    float3 shift = (float3)(100.0f, 100.0f, 100.0f);
    
    for (int i = 0; i < octaves; ++i) {
        v += a * noise(x);
        x = x * 2.0f + shift;
        a *= 0.5f;
    }
    return v;
}

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

// Cloud density function
float cloudDensity(float3 pos, float time) {
    // Animate clouds by drifting them slowly
    float3 wind = (float3)(time * 0.02f, time * 0.01f, time * 0.015f);
    float3 p = pos + wind;
    
    // Base shape - ellipsoid
    float3 cloudCenter = (float3)(0.0f, 8.0f, 0.0f);
    float3 cloudSize = (float3)(15.0f, 6.0f, 10.0f);
    float3 q = (pos - cloudCenter) / cloudSize;
    float baseShape = 1.0f - smoothstep(0.3f, 1.0f, length(q));
    
    if (baseShape <= 0.0f) return 0.0f;
    
    // Multiple noise octaves for detail
    float density = 0.0f;
    
    // Large scale features
    density += fbm(p * 0.02f, 3) * 0.8f;
    
    // Medium scale features
    density += fbm(p * 0.05f, 4) * 0.6f;
    
    // Fine scale features
    density += fbm(p * 0.1f, 3) * 0.4f;
    
    // Apply base shape
    density *= baseShape;
    
    // Clamp and adjust
    density = clamp(density - 0.4f, 0.0f, 1.0f) * 0.3f;
    
    return density;
}

// Additional cloud volumes
float additionalClouds(float3 pos, float time) {
    float totalDensity = 0.0f;
    float3 wind = (float3)(time * 0.02f, time * 0.01f, time * 0.015f);
    
    // Second cloud cluster
    float3 cloudCenter2 = (float3)(-10.0f, 12.0f, -5.0f);
    float3 cloudSize2 = (float3)(8.0f, 4.0f, 8.0f);
    float3 q2 = (pos - cloudCenter2) / cloudSize2;
    float baseShape2 = 1.0f - smoothstep(0.4f, 1.0f, length(q2));
    
    if (baseShape2 > 0.0f) {
        float3 p2 = pos + wind * 1.3f;
        float density2 = fbm(p2 * 0.03f, 3) * 0.7f + fbm(p2 * 0.08f, 3) * 0.5f;
        density2 *= baseShape2;
        density2 = clamp(density2 - 0.5f, 0.0f, 1.0f) * 0.25f;
        totalDensity += density2;
    }
    
    // Third cloud cluster
    float3 cloudCenter3 = (float3)(12.0f, 10.0f, 5.0f);
    float3 cloudSize3 = (float3)(6.0f, 5.0f, 6.0f);
    float3 q3 = (pos - cloudCenter3) / cloudSize3;
    float baseShape3 = 1.0f - smoothstep(0.3f, 1.0f, length(q3));
    
    if (baseShape3 > 0.0f) {
        float3 p3 = pos + wind * 0.8f;
        float density3 = fbm(p3 * 0.04f, 4) * 0.8f + fbm(p3 * 0.12f, 2) * 0.3f;
        density3 *= baseShape3;
        density3 = clamp(density3 - 0.3f, 0.0f, 1.0f) * 0.4f;
        totalDensity += density3;
    }
    
    return totalDensity;
}

// Scene SDF for solid objects
float mapSolid(float3 pos, float time) {
    // Ground plane
    float ground = sdBox(pos - (float3)(0.0f, -1.0f, 0.0f), (float3)(20.0f, 0.1f, 20.0f));
    
    // Mountain peaks
    float mountain1 = sdBox(pos - (float3)(-8.0f, 1.0f, -10.0f), (float3)(2.0f, 3.0f, 2.0f));
    float mountain2 = sdBox(pos - (float3)(5.0f, 2.0f, -8.0f), (float3)(1.5f, 4.0f, 1.5f));
    float mountain3 = sdBox(pos - (float3)(0.0f, 1.5f, -12.0f), (float3)(3.0f, 3.5f, 2.0f));
    
    return fmin(ground, fmin(mountain1, fmin(mountain2, mountain3)));
}

// Calculate normal for solid objects
float3 calcNormal(float3 pos, float time) {
    const float h = 0.0001f;
    const float2 k = (float2)(1.0f, -1.0f);
    return normalize(k.xyy * mapSolid(pos + k.xyy * h, time) +
                    k.yyx * mapSolid(pos + k.yyx * h, time) +
                    k.yxy * mapSolid(pos + k.yxy * h, time) +
                    k.xxx * mapSolid(pos + k.xxx * h, time));
}

// Raymarching for solid objects
float raymarch(float3 ro, float3 rd, float time) {
    float dO = 0.0f;
    
    for (int i = 0; i < 100; i++) {
        float3 p = ro + rd * dO;
        float dS = mapSolid(p, time);
        dO += dS;
        if (dO > 200.0f || dS < 0.001f) break;
    }
    
    return dO;
}

// Volume rendering for clouds
float3 volumeRender(float3 ro, float3 rd, float tmin, float tmax, float time, float3 lightDir) {
    const int samples = 64;
    const int shadowSamples = 8;
    float dt = (tmax - tmin) / (float)samples;
    
    float3 col = (float3)(0.0f, 0.0f, 0.0f);
    float transmittance = 1.0f;
    
    for (int i = 0; i < samples; i++) {
        float t = tmin + dt * ((float)i + 0.5f);
        float3 pos = ro + rd * t;
        
        // Sample density
        float density = cloudDensity(pos, time) + additionalClouds(pos, time);
        
        if (density > 0.0f) {
            // Light attenuation through cloud
            float lightAtten = 1.0f;
            for (int j = 0; j < shadowSamples; j++) {
                float3 shadowPos = pos + lightDir * (float)j * 0.5f;
                float shadowDensity = cloudDensity(shadowPos, time) + additionalClouds(shadowPos, time);
                lightAtten *= exp(-shadowDensity * 0.5f);
            }
            
            // Scattering calculations
            float cosTheta = dot(rd, lightDir);
            float phase = 0.25f / 3.14159f * (1.0f + cosTheta * cosTheta); // Rayleigh scattering
            
            // Cloud color - varies from white to gray
            float3 cloudColor = mix((float3)(0.6f, 0.6f, 0.7f), (float3)(1.0f, 0.95f, 0.9f), lightAtten);
            
            // Add scattered light
            float3 scattered = cloudColor * density * phase * lightAtten * transmittance;
            col += scattered * dt * 20.0f;
            
            // Update transmittance
            transmittance *= exp(-density * dt * 8.0f);
            
            if (transmittance < 0.01f) break;
        }
    }
    
    return col;
}

// Sky color
float3 getSkyColor(float3 rd, float3 lightDir) {
    float cosTheta = dot(rd, lightDir);
    float sun = smoothstep(0.995f, 0.999f, cosTheta);
    
    // Gradient from horizon to zenith
    float t = rd.y * 0.5f + 0.5f;
    float3 skyCol = mix((float3)(0.8f, 0.9f, 1.0f), (float3)(0.4f, 0.7f, 1.0f), t);
    
    // Add sun
    skyCol += (float3)(1.0f, 0.9f, 0.7f) * sun * 10.0f;
    
    // Atmospheric scattering near horizon
    skyCol = mix(skyCol, (float3)(1.0f, 0.8f, 0.6f), pow(1.0f - t, 4.0f) * 0.3f);
    
    return skyCol;
}

// Simple lighting for solid objects
float3 lighting(float3 pos, float3 normal, float3 lightDir, float3 viewDir) {
    float diff = fmax(dot(normal, lightDir), 0.0f);
    
    float3 reflectDir = -lightDir - 2.0f * dot(-lightDir, normal) * normal;
    float spec = pow(fmax(dot(viewDir, reflectDir), 0.0f), 32.0f);
    
    float3 ambient = (float3)(0.2f, 0.3f, 0.4f);
    float3 diffuse = (float3)(0.7f, 0.6f, 0.5f) * diff;
    float3 specular = (float3)(0.3f, 0.3f, 0.3f) * spec;
    
    return ambient + diffuse + specular;
}

__kernel void volumetric_clouds_kernel(__global uchar4* output,
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
    
    // Light direction (sun)
    float3 lightDir = normalize((float3)(0.5f, 0.8f, 0.3f));
    
    // Raymarch solid objects first
    float solidDist = raymarch(camera_pos, rd, time);
    
    float3 color = (float3)(0.0f, 0.0f, 0.0f);
    
    // Determine volume rendering bounds
    float tmin = 1.0f;
    float tmax = (solidDist < 200.0f) ? solidDist : 100.0f;
    
    // Render solid objects if hit
    if (solidDist < 200.0f) {
        float3 pos = camera_pos + rd * solidDist;
        float3 normal = calcNormal(pos, time);
        color = lighting(pos, normal, lightDir, -rd);
    }
    
    // Render clouds
    if (tmax > tmin) {
        float3 cloudCol = volumeRender(camera_pos, rd, tmin, tmax, time, lightDir);
        
        if (solidDist < 200.0f) {
            // Clouds in front of solid object
            color = mix(color, cloudCol, clamp(length(cloudCol) * 2.0f, 0.0f, 1.0f));
        } else {
            // Get sky color
            float3 skyCol = getSkyColor(rd, lightDir);
            color = skyCol + cloudCol;
        }
    } else if (solidDist >= 200.0f) {
        // Only sky visible
        color = getSkyColor(rd, lightDir);
    }
    
    // Tone mapping and gamma correction
    color = color / (color + 1.0f); // Simple tone mapping
    color = pow(color, 1.0f / 2.2f); // Gamma correction
    
    // Convert to RGBA
    uchar4 pixel = (uchar4)(
        (uchar)(clamp(color.x * 255.0f, 0.0f, 255.0f)),
        (uchar)(clamp(color.y * 255.0f, 0.0f, 255.0f)),
        (uchar)(clamp(color.z * 255.0f, 0.0f, 255.0f)),
        255
    );
    
    output[y * width + x] = pixel;
}
