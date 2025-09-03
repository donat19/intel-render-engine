// Advanced HDR Procedural Clouds Shader
// Implements volumetric rendering with physically correct lighting
// Author: AI Assistant, based on procedural cloud theory

// ===== MATHEMATICAL FUNCTIONS =====

float3 fract3(float3 x) {
    return x - floor(x);
}

float fract1(float x) {
    return x - floor(x);
}

// Improved hash function for better noise quality
float hash13(float3 p3) {
    p3 = fract3(p3 * 0.1031f);
    p3 += dot(p3, p3.yzx + 33.33f);
    return fract1((p3.x + p3.y) * p3.z);
}

float3 hash33(float3 p3) {
    p3 = fract3(p3 * (float3)(0.1031f, 0.1030f, 0.0973f));
    p3 += dot(p3, p3.yxz + 33.33f);
    return fract3((p3.xxy + p3.yxx) * p3.zyx);
}

// ===== NOISE FUNCTIONS =====

// Gradient noise (Perlin-like)
float gradientNoise(float3 x) {
    float3 i = floor(x);
    float3 f = fract3(x);
    
    // Quintic interpolation for smoothness
    f = f * f * f * (f * (f * 6.0f - 15.0f) + 10.0f);
    
    return mix(
        mix(mix(hash13(i + (float3)(0,0,0)), hash13(i + (float3)(1,0,0)), f.x),
            mix(hash13(i + (float3)(0,1,0)), hash13(i + (float3)(1,1,0)), f.x), f.y),
        mix(mix(hash13(i + (float3)(0,0,1)), hash13(i + (float3)(1,0,1)), f.x),
            mix(hash13(i + (float3)(0,1,1)), hash13(i + (float3)(1,1,1)), f.x), f.y), f.z);
}

// Curl noise for turbulence (simplified version)
float3 curlNoise(float3 p) {
    const float e = 0.1f;
    float3 dx = (float3)(e, 0.0f, 0.0f);
    float3 dy = (float3)(0.0f, e, 0.0f);
    float3 dz = (float3)(0.0f, 0.0f, e);
    
    float3 p_x0 = hash33(p - dx);
    float3 p_x1 = hash33(p + dx);
    float3 p_y0 = hash33(p - dy);
    float3 p_y1 = hash33(p + dy);
    float3 p_z0 = hash33(p - dz);
    float3 p_z1 = hash33(p + dz);
    
    float x = p_y1.z - p_y0.z - p_z1.y + p_z0.y;
    float y = p_z1.x - p_z0.x - p_x1.z + p_x0.z;
    float z = p_x1.y - p_x0.y - p_y1.x + p_y0.x;
    
    const float divisor = 1.0f / (2.0f * e);
    return normalize((float3)(x, y, z) * divisor);
}

// Fractal Brownian Motion with proper weights
float fbmNoise(float3 x, int octaves, float lacunarity, float gain) {
    float value = 0.0f;
    float amplitude = 0.5f;
    float frequency = 1.0f;
    float maxValue = 0.0f;
    
    for (int i = 0; i < octaves; i++) {
        value += amplitude * gradientNoise(x * frequency);
        maxValue += amplitude;
        amplitude *= gain;
        frequency *= lacunarity;
    }
    
    return value / maxValue; // Normalization
}

// Billowy noise for cloud masses
float billowNoise(float3 x, int octaves) {
    float value = 0.0f;
    float amplitude = 0.5f;
    float frequency = 1.0f;
    
    for (int i = 0; i < octaves; i++) {
        value += amplitude * fabs(gradientNoise(x * frequency));
        amplitude *= 0.5f;
        frequency *= 2.0f;
    }
    
    return value;
}

// Ridged noise for cloud edge details
float ridgedNoise(float3 x, int octaves) {
    float value = 0.0f;
    float amplitude = 0.5f;
    float frequency = 1.0f;
    
    for (int i = 0; i < octaves; i++) {
        float n = gradientNoise(x * frequency);
        n = 1.0f - fabs(n);
        n = n * n;
        value += amplitude * n;
        amplitude *= 0.5f;
        frequency *= 2.0f;
    }
    
    return value;
}

// ===== CLOUD DENSITY =====

// Cloud height function (stratosphere)
float cloudHeightGradient(float height, float cloudBase, float cloudTop) {
    float bottomFade = smoothstep(cloudBase - 1.0f, cloudBase + 1.0f, height);
    float topFade = 1.0f - smoothstep(cloudTop - 2.0f, cloudTop + 1.0f, height);
    return bottomFade * topFade;
}

// Main cloud density function
float cloudDensity(float3 worldPos, float time) {
    // Cloud parameters
    const float cloudBase = 5.0f;
    const float cloudTop = 15.0f;
    const float cloudScale = 0.02f;
    
    // Wind animation
    float3 windDirection = normalize((float3)(1.0f, 0.0f, 0.3f));
    float3 windDisplacement = windDirection * time * 0.8f;
    
    // Position with wind
    float3 samplePos = worldPos + windDisplacement;
    
    // Height gradient
    float heightGradient = cloudHeightGradient(worldPos.y, cloudBase, cloudTop);
    if (heightGradient <= 0.0f) return 0.0f;
    
    // Main cloud shape (low frequency noise)
    float baseShape = fbmNoise(samplePos * cloudScale, 4, 2.0f, 0.5f);
    
    // Add billowy noise for volume
    float billowy = billowNoise(samplePos * cloudScale * 0.7f, 3);
    baseShape = mix(baseShape, billowy, 0.4f);
    
    // Threshold for cloud formation
    baseShape = smoothstep(0.4f, 0.8f, baseShape);
    
    if (baseShape <= 0.0f) return 0.0f;
    
    // High frequency details
    float detail = ridgedNoise(samplePos * cloudScale * 4.0f, 3);
    detail = mix(detail, fbmNoise(samplePos * cloudScale * 8.0f, 2, 2.0f, 0.5f), 0.5f);
    
    // Cloud edge erosion
    float erosion = 1.0f - smoothstep(0.1f, 0.9f, detail);
    baseShape *= erosion;
    
    // Turbulence with curl noise
    float3 curl = curlNoise(samplePos * cloudScale * 2.0f);
    float3 distortedPos = samplePos + curl * 0.5f;
    float turbulence = fbmNoise(distortedPos * cloudScale * 6.0f, 2, 2.0f, 0.5f);
    
    // Final density
    float density = baseShape * heightGradient;
    density *= (1.0f + turbulence * 0.3f);
    
    return clamp(density, 0.0f, 1.0f);
}

// ===== CLOUD LIGHTING =====

// Calculate cloud shadowing (Beer's law)
float cloudShadowing(float3 pos, float3 lightDir, float time, int samples) {
    float shadowStepSize = 2.0f;
    float lightTransmittance = 1.0f;
    
    for (int i = 0; i < samples; i++) {
        float3 shadowPos = pos + lightDir * shadowStepSize * (float)(i + 1);
        float shadowDensity = cloudDensity(shadowPos, time);
        
        // Beer's law for light absorption
        lightTransmittance *= exp(-shadowDensity * shadowStepSize * 0.8f);
        
        // Early exit if light is almost absorbed
        if (lightTransmittance < 0.01f) break;
    }
    
    return lightTransmittance;
}

// Henyey-Greenstein phase function for scattering
float henyeyGreensteinPhase(float cosTheta, float g) {
    float g2 = g * g;
    return (1.0f - g2) / (4.0f * 3.14159f * pow(1.0f + g2 - 2.0f * g * cosTheta, 1.5f));
}

// Multiple scattering (simplified model)
float multipleScattering(float density, float lightAttenuation) {
    // Approximation of multiple scattering influence
    return 0.2f + 0.8f * pow(lightAttenuation, 0.25f);
}

// ===== VOLUME RENDERING =====

float3 volumeRenderClouds(float3 rayOrigin, float3 rayDir, float tmin, float tmax, 
                         float time, float3 lightDir, float3 sunColor) {
    
    const int maxSamples = 80;
    const int shadowSamples = 6;
    
    float stepSize = (tmax - tmin) / (float)maxSamples;
    
    float3 scatteredLight = (float3)(0.0f);
    float transmittance = 1.0f;
    
    // Scattering parameters
    const float scatteringCoeff = 1.2f;
    const float absorptionCoeff = 0.8f;
    const float g = 0.3f; // Forward scattering
    
    for (int i = 0; i < maxSamples; i++) {
        float t = tmin + stepSize * ((float)i + 0.3f); // Jittering для сглаживания
        float3 samplePos = rayOrigin + rayDir * t;
        
        float density = cloudDensity(samplePos, time);
        
        if (density > 0.01f) {
            // Calculate illumination at point
            float lightAttenuation = cloudShadowing(samplePos, lightDir, time, shadowSamples);
            
            // Phase function
            float cosTheta = dot(rayDir, lightDir);
            float phase = henyeyGreensteinPhase(cosTheta, g);
            
            // Multiple scattering
            float multiScatter = multipleScattering(density, lightAttenuation);
            
            // Scattered light color
            float3 lightContribution = sunColor * lightAttenuation * phase * multiScatter;
            
            // Add ambient lighting
            float3 ambientColor = (float3)(0.3f, 0.4f, 0.6f);
            lightContribution += ambientColor * density;
            
            // Accumulate scattered light
            scatteredLight += transmittance * lightContribution * density * stepSize * scatteringCoeff;
            
            // Update light transmission (Beer's law)
            float extinction = (scatteringCoeff + absorptionCoeff) * density * stepSize;
            transmittance *= exp(-extinction);
            
            // Early exit with strong absorption
            if (transmittance < 0.01f) break;
        }
    }
    
    return scatteredLight;
}

// ===== SCENE AND RENDERING =====

// SDF for landscape
float sceneSDF(float3 pos) {
    // Mountain terrain
    float terrain = pos.y + 2.0f;
    terrain += fbmNoise(pos.xz * 0.01f, 4, 2.0f, 0.5f) * 8.0f;
    terrain += ridgedNoise(pos.xz * 0.05f, 3) * 2.0f;
    
    return terrain;
}

// Normal for landscape
float3 sceneNormal(float3 pos) {
    const float h = 0.01f;
    return normalize((float3)(
        sceneSDF(pos + (float3)(h, 0, 0)) - sceneSDF(pos - (float3)(h, 0, 0)),
        sceneSDF(pos + (float3)(0, h, 0)) - sceneSDF(pos - (float3)(0, h, 0)),
        sceneSDF(pos + (float3)(0, 0, h)) - sceneSDF(pos - (float3)(0, 0, h))
    ));
}

// Raymarching for solid objects
float raymarchTerrain(float3 ro, float3 rd) {
    float t = 0.0f;
    const float maxDist = 200.0f;
    
    for (int i = 0; i < 100; i++) {
        float3 pos = ro + rd * t;
        float d = sceneSDF(pos);
        
        if (d < 0.001f) return t;
        if (t > maxDist) break;
        
        t += d * 0.8f; // Relaxation factor
    }
    
    return maxDist;
}

// HDR sky
float3 getSkyColor(float3 rayDir, float3 lightDir, float3 sunColor) {
    float cosTheta = dot(rayDir, lightDir);
    
    // Sun disk
    float sunDisk = smoothstep(0.9995f, 0.9999f, cosTheta);
    float3 sun = sunColor * sunDisk * 8.0f;
    
    // Halo around sun
    float halo = pow(clamp(cosTheta, 0.0f, 1.0f), 8.0f);
    float3 haloColor = sunColor * 0.3f * halo;
    
    // Sky gradient
    float elevation = rayDir.y;
    float3 zenithColor = (float3)(0.2f, 0.5f, 1.0f);
    float3 horizonColor = (float3)(1.0f, 0.8f, 0.6f);
    
    float3 skyGradient = mix(horizonColor, zenithColor, smoothstep(-0.1f, 0.3f, elevation));
    
    // Rayleigh scattering
    float rayleigh = 1.0f + cosTheta * cosTheta;
    skyGradient *= rayleigh * 0.8f;
    
    return skyGradient + sun + haloColor;
}

// Landscape lighting
float3 shadeTerrain(float3 pos, float3 normal, float3 lightDir, float3 viewDir, float3 sunColor) {
    float ndotl = clamp(dot(normal, lightDir), 0.0f, 1.0f);
    
    // Diffuse lighting
    float3 diffuse = sunColor * ndotl * 0.8f;
    
    // Specular reflection
    float3 reflection = reflect(-lightDir, normal);
    float spec = pow(clamp(dot(viewDir, reflection), 0.0f, 1.0f), 16.0f);
    float3 specular = sunColor * spec * 0.3f;
    
    // Ambient lighting
    float3 ambient = (float3)(0.2f, 0.3f, 0.4f);
    
    // Material color (stone/earth)
    float3 albedo = mix((float3)(0.3f, 0.25f, 0.2f), (float3)(0.4f, 0.35f, 0.25f), 
                       fbmNoise(pos * 0.1f, 3, 2.0f, 0.5f));
    
    return albedo * (ambient + diffuse) + specular;
}

// ===== MAIN SHADER =====

__kernel void advanced_clouds_hdr_kernel(__global float4* hdr_output,
                                        const int width,
                                        const int height,
                                        const float time,
                                        const float16 camera_matrix,
                                        const float3 camera_pos) {
    
    int x = get_global_id(0);
    int y = get_global_id(1);
    
    if (x >= width || y >= height) return;
    
    // Normalized screen coordinates
    float2 uv = (float2)((float)x / (float)width, (float)y / (float)height);
    uv = uv * 2.0f - 1.0f;
    uv.x *= (float)width / (float)height;
    
    // Ray direction
    float3 rayDir = normalize((float3)(uv.x, uv.y, -1.5f));
    
    // Apply camera rotation
    rayDir = (float3)(
        dot(rayDir, (float3)(camera_matrix.s0, camera_matrix.s4, camera_matrix.s8)),
        dot(rayDir, (float3)(camera_matrix.s1, camera_matrix.s5, camera_matrix.s9)),
        dot(rayDir, (float3)(camera_matrix.s2, camera_matrix.s6, camera_matrix.sa))
    );
    rayDir = normalize(rayDir);
    
    // Lighting parameters
    float sunAngle = time * 0.1f;
    float3 lightDir = normalize((float3)(cos(sunAngle), 0.6f, sin(sunAngle)));
    float3 sunColor = (float3)(15.0f, 12.0f, 8.0f); // HDR intensity
    
    // Raymarching for landscape
    float terrainDist = raymarchTerrain(camera_pos, rayDir);
    
    float3 finalColor = (float3)(0.0f);
    
    if (terrainDist < 200.0f) {
        // Hit landscape
        float3 hitPos = camera_pos + rayDir * terrainDist;
        float3 normal = sceneNormal(hitPos);
        finalColor = shadeTerrain(hitPos, normal, lightDir, -rayDir, sunColor);
        
        // Clouds in front of landscape
        float cloudStart = 1.0f;
        float cloudEnd = min(terrainDist - 0.1f, 50.0f);
        
        if (cloudEnd > cloudStart) {
            float3 cloudColor = volumeRenderClouds(camera_pos, rayDir, cloudStart, cloudEnd, 
                                                  time, lightDir, sunColor);
            // Mix clouds with landscape
            float cloudAlpha = clamp(length(cloudColor) * 0.15f, 0.0f, 0.8f);
            finalColor = mix(finalColor, finalColor + cloudColor, cloudAlpha);
        }
    } else {
        // Only sky and clouds
        float3 skyColor = getSkyColor(rayDir, lightDir, sunColor);
        
        // Clouds in atmosphere
        float cloudStart = 1.0f;
        float cloudEnd = 80.0f;
        
        float3 cloudColor = volumeRenderClouds(camera_pos, rayDir, cloudStart, cloudEnd, 
                                              time, lightDir, sunColor);
        
        finalColor = skyColor + cloudColor;
    }
    
    // Atmospheric haze at distance
    if (terrainDist > 50.0f) {
        float fog = exp(-0.01f * (terrainDist - 50.0f));
        float3 fogColor = getSkyColor(rayDir, lightDir, sunColor) * 0.5f;
        finalColor = mix(fogColor, finalColor, fog);
    }
    
    // Write HDR color
    hdr_output[y * width + x] = (float4)(finalColor, 1.0f);
}

// ===== TONE MAPPING (identical to other shaders) =====

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
    
    float3 ldr_color;
    switch (tone_mapping_mode) {
        case 0: ldr_color = linear_tonemap(hdr_color, exposure); break;
        case 1: ldr_color = reinhard_tonemap(hdr_color, exposure); break;
        case 2: ldr_color = filmic_tonemap(hdr_color, exposure); break;
        case 3: ldr_color = aces_tonemap(hdr_color, exposure); break;
        default: ldr_color = reinhard_tonemap(hdr_color, exposure); break;
    }
    
    ldr_color = pow(fmax(ldr_color, 0.0f), 1.0f / gamma);
    
    uchar4 pixel = (uchar4)(
        (uchar)(clamp(ldr_color.x * 255.0f, 0.0f, 255.0f)),
        (uchar)(clamp(ldr_color.y * 255.0f, 0.0f, 255.0f)),
        (uchar)(clamp(ldr_color.z * 255.0f, 0.0f, 255.0f)),
        255
    );
    
    ldr_output[idx] = pixel;
}
