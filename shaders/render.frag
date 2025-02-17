#version 460 core
out vec4 color;

uniform vec2 resolution;
uniform mat3 rotationMatrix = mat3(1.0);
uniform vec3 position = vec3(0.0, 0.0, -1.0);
uniform float rand1;
uniform float rand2;

vec2 fragCoord = gl_FragCoord.xy;

#define INFTY 1E9
#define EPS   1E-3

#define COLOR_RED   0
#define COLOR_GREEN 1
#define COLOR_BLUE  2

struct Ray {
    vec3 start;
    vec3 dir;
    int color;
    float opticalDensity;
};

struct Material {
    vec3 color;
    float roughness;
    float opticalDensity;
    bool transparent;
};

struct Sphere {
    vec3 centre;
    float radius;
    int material;
};

struct Plane {
    float a;
    float b;
    float c;
    float d;

    int material;
};

struct Triangle {
    vec3 a;
    vec3 b;
    vec3 c;

    int material;
};

#define LAYOUT std430

layout(LAYOUT, binding = 0) buffer MaterialsBuffer {
    Material materials[];
};

layout(LAYOUT, binding = 1) buffer SpheresBuffer {
    Sphere spheres[];
};

layout(LAYOUT, binding = 2) buffer PlanesBuffer {
    Plane planes[];
};

layout(LAYOUT, binding = 3) buffer TrianglesBuffer {
    Triangle trs[];
};

uniform vec3 sunPosition;
uniform float sunRadius;
uniform vec3 sunColor;
uniform vec3 skyColor;

struct Reflection {
    Ray ray;
    float dist;
};

float hash(vec3 seed) {
    return fract(sin(dot(seed, vec3(12.9898, 78.233, 45.164))) * 43758.5453 * rand1);
}

vec3 diffusedReflection(vec3 normal, vec3 incidentDir, float roughness, vec3 rayOrigin) {
    float rand1 = hash(rayOrigin + incidentDir);
    float rand2 = hash(rayOrigin - incidentDir);

    float theta = 2.0 * 3.14159265359 * rand1;
    float phi = acos(mix(1.0, 2.0 * rand2 - 1.0, roughness));

    vec3 randDir = vec3(
            sin(phi) * cos(theta),
            sin(phi) * sin(theta),
            cos(phi)
        );

    vec3 perfectReflection = reflect(incidentDir, normal);

    vec3 up = abs(perfectReflection.y) < 0.999 ? vec3(0, 1, 0) : vec3(1, 0, 0);
    vec3 tangent = normalize(cross(up, perfectReflection));
    vec3 bitangent = cross(perfectReflection, tangent);

    vec3 randomReflection = normalize(
            tangent * randDir.x +
                bitangent * randDir.y +
                perfectReflection * randDir.z
        );

    return normalize(mix(perfectReflection, randomReflection, roughness));
}

vec3 advancedReflection(Ray ray, Material material, vec3 normal) {
    if (material.transparent) {
        if (dot(ray.dir, normal) > 0.0) {
            normal = -normal;
        }
        return normalize(refract(ray.dir, normal, ray.opticalDensity / material.opticalDensity));
    }
    return diffusedReflection(normal, ray.dir, material.roughness, ray.start);
}

float castRayWithSky(Ray ray) {
    if (distance(ray.dir, normalize(sunPosition)) < sunRadius) {
        return sunColor[ray.color];
    }
    return skyColor[ray.color];
}

Reflection castRayWithPlane(Ray ray, Plane plane) {
    vec3 normal = normalize(vec3(plane.a, plane.b, plane.c));
    float denom = dot(normal, ray.dir);

    if (abs(denom) < EPS) {
        return Reflection(ray, INFTY);
    }

    float t = -(dot(normal, ray.start) + plane.d) / denom;

    if (t < EPS) {
        return Reflection(ray, INFTY);
    }

    vec3 intersection = ray.start + ray.dir * t;

    // vec3 refvector = diffusedReflection(normal, ray.dir, materials[plane.material].roughness, ray.start);
    vec3 refvector = advancedReflection(ray, materials[plane.material], normal);
    return Reflection(Ray(intersection, refvector, ray.color, ray.opticalDensity), t * length(ray.dir));
}

// https://en.wikipedia.org/wiki/M%C3%B6ller%E2%80%93Trumbore_intersection_algorithm
Reflection castRayWithTriangle(Ray ray, Triangle tr) {
    vec3 edge1 = tr.b - tr.a;
    vec3 edge2 = tr.c - tr.a;
    vec3 ray_cross_e2 = cross(ray.dir, edge2);
    float det = dot(edge1, ray_cross_e2);

    if (det > -EPS && det < EPS)
        return Reflection(ray, INFTY);

    float inv_det = 1.0 / det;
    vec3 s = ray.start - tr.a;
    float u = inv_det * dot(s, ray_cross_e2);

    if ((u < 0 && abs(u) > EPS) || (u > 1 && abs(u - 1) > EPS))
        return Reflection(ray, INFTY);

    vec3 s_cross_e1 = cross(s, edge1);
    float v = inv_det * dot(ray.dir, s_cross_e1);

    if ((v < 0 && abs(v) > EPS) || (u + v > 1 && abs(u + v - 1) > EPS))
        return Reflection(ray, INFTY);

    // At this stage we can compute t to find out where the intersection point is on the line.
    float t = inv_det * dot(edge2, s_cross_e1);

    if (t > EPS) // ray intersection
    {
        float dist = length(ray.dir) * t;
        vec3 normal = normalize(cross(edge1, edge2));
        // vec3 reflection = diffusedReflection(normal, ray.dir, materials[tr.material].roughness, ray.start);
        vec3 reflection = advancedReflection(ray, materials[tr.material], normal);
        vec3 intersection = ray.start + ray.dir * t;
        return Reflection(Ray(intersection, reflection, ray.color, ray.opticalDensity), dist);
    }
    else // This means that there is a line intersection but not a ray intersection.
        return Reflection(ray, INFTY);
}

Reflection castRayWithSphere(Ray ray, Sphere sph) {
    vec3 OC = ray.start - sph.centre;
    float k1 = dot(ray.dir, ray.dir);
    float k2 = 2 * dot(OC, ray.dir);
    float k3 = dot(OC, OC) - sph.radius * sph.radius;
    float discr = k2 * k2 - 4 * k1 * k3;

    if (discr <= 0) {
        return Reflection(ray, INFTY);
    }

    discr = sqrt(discr);

    float t1 = (-k2 - discr) / (2 * k1);
    float t2 = (-k2 + discr) / (2 * k1);

    float t_min = min(t1, t2);
    float t_max = max(t1, t2);

    float t = t_min;

    if (t_min < EPS) {
        if (t_max < EPS) {
            return Reflection(ray, INFTY);
        }
        t = t_max;
    }

    vec3 intersection = ray.start + ray.dir * t;
    vec3 rvector = normalize(intersection - sph.centre);
    // vec3 refvector = diffusedReflection(rvector, ray.dir, materials[sph.material].roughness, ray.start);
    vec3 refvector = advancedReflection(ray, materials[sph.material], rvector);
    return Reflection(Ray(intersection, refvector, ray.color, ray.opticalDensity), t * length(ray.dir));
}

#define PROCESS_PRIMITIVE(primitives, castFunction) \
    for (int i = 0; i < primitives.length(); ++i) { \
        Reflection newrefl = castFunction(ray, primitives[i]); \
        if (newrefl.dist < refl.dist) { \
            refl = newrefl; \
            material = primitives[i].material; \
        } \
    } \

float castRay(Ray ray) {
    Reflection refl = Reflection(ray, INFTY);
    int material = 0;

    float res = 1.0;

    for (int i = 0; i < 10; ++i) {
        refl.dist = INFTY;
        material = 0;

        PROCESS_PRIMITIVE(spheres, castRayWithSphere);
        PROCESS_PRIMITIVE(planes, castRayWithPlane);
        PROCESS_PRIMITIVE(trs, castRayWithTriangle);

        if (refl.dist == INFTY) {
            return res * castRayWithSky(ray);
        }
        ray = refl.ray;

        res *= materials[material].color[ray.color];
        ray.opticalDensity = materials[material].opticalDensity;
    }

    return res;
}

#undef PROCESS_PRIMITIVE

vec4 getColor(vec3 camera, vec3 dir) {
    vec4 res = vec4(0.0, 0.0, 0.0, 1.0);

    Ray ray = Ray(camera, dir, COLOR_RED, 1.0);
    res.x = castRay(ray);

    ray.color = COLOR_GREEN;
    res.y = castRay(ray);

    ray.color = COLOR_BLUE;
    res.z = castRay(ray);

    return res;
}

void main() {
    fragCoord -= resolution / 2;
    float d = max(resolution.x, resolution.y);
    vec2 uv = fragCoord / d;
    vec3 camera = position;
    vec3 dir = normalize(vec3(uv, 1.0));
    dir = rotationMatrix * dir;
    color = getColor(camera, dir);
    // for (int i = 0; i < materials.length(); i++) {
    //     if (materials[i].transparent) {
    //         color = vec4(0, 0, 1, 1);
    //     }
    // }
    // vec3 normalizedVector = normalize(vec3(1, 2, 3));
    // if (normalizedVector != normalize(refract(normalizedVector, normalize(vec3(1, 1, 1)), 1.0))) {
    //     color = vec4(1, 0, 0, 1);
    // }
}
