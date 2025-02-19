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
    bool isInside;
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

struct Lens {
    Sphere sphere;
    Plane plane;
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

layout(LAYOUT, binding = 4) buffer LensesBuffer {
    Lens lenses[];
};

uniform vec3 sunPosition;
uniform float sunRadius;
uniform vec3 sunColor;
uniform vec3 skyColor;

struct Reflection {
    // Ray ray;
    vec3 intersection;
    vec3 normal;
    float dist;
};
#define NONE_REFLECTION Reflection(vec3(0.0, 0.0, 0.0), vec3(0.0, 0.0, 0.0), INFTY)

Reflection new_reflection(Ray ray, vec3 normal, float t) {
    return Reflection(ray.start + ray.dir * t, normal, length(ray.dir) * t);
}

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

vec3 reflectOrRefract(inout Ray ray, Material material, vec3 normal) {
    if (material.transparent) {
        if (dot(ray.dir, normal) > 0.0) {
            normal = -normal;
        }
        float theta = ray.opticalDensity / material.opticalDensity;
        if (ray.isInside) {
            theta = 1 / theta;
            ray.opticalDensity = 1;
        } else {
            ray.opticalDensity = material.opticalDensity;
        }
        ray.isInside = !ray.isInside;
        return normalize(refract(ray.dir, normal, theta));
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
        return NONE_REFLECTION;
    }

    float t = -(dot(normal, ray.start) + plane.d) / denom;

    if (t < EPS) {
        return NONE_REFLECTION;
    }

    return new_reflection(ray, normal, t);
}

// https://en.wikipedia.org/wiki/M%C3%B6ller%E2%80%93Trumbore_intersection_algorithm
Reflection castRayWithTriangle(Ray ray, Triangle tr) {
    vec3 edge1 = tr.b - tr.a;
    vec3 edge2 = tr.c - tr.a;
    vec3 ray_cross_e2 = cross(ray.dir, edge2);
    float det = dot(edge1, ray_cross_e2);

    if (det > -EPS && det < EPS) {
        return NONE_REFLECTION;
    }

    float inv_det = 1.0 / det;
    vec3 s = ray.start - tr.a;
    float u = inv_det * dot(s, ray_cross_e2);

    if ((u < 0 && abs(u) > EPS) || (u > 1 && abs(u - 1) > EPS)) {
        return NONE_REFLECTION;
    }

    vec3 s_cross_e1 = cross(s, edge1);
    float v = inv_det * dot(ray.dir, s_cross_e1);

    if ((v < 0 && abs(v) > EPS) || (u + v > 1 && abs(u + v - 1) > EPS)) {
        return NONE_REFLECTION;
    }

    float t = inv_det * dot(edge2, s_cross_e1);

    if (t > EPS) // ray intersection
    {
        vec3 normal = normalize(cross(edge1, edge2));
        return new_reflection(ray, normal, t);
    }
    else { // This means that there is a line intersection but not a ray intersection.
        return NONE_REFLECTION;
    }
}

Reflection castRayWithSphere(Ray ray, Sphere sph) {
    vec3 OC = ray.start - sph.centre;
    float k1 = dot(ray.dir, ray.dir);
    float k2 = 2 * dot(OC, ray.dir);
    float k3 = dot(OC, OC) - sph.radius * sph.radius;
    float discr = k2 * k2 - 4 * k1 * k3;

    if (discr <= 0) {
        return NONE_REFLECTION;
    }

    discr = sqrt(discr);

    float t1 = (-k2 - discr) / (2 * k1);
    float t2 = (-k2 + discr) / (2 * k1);

    float t_min = min(t1, t2);
    float t_max = max(t1, t2);

    float t = t_min;

    if (t_min < EPS) {
        if (t_max < EPS) {
            return NONE_REFLECTION;
        }
        t = t_max;
    }

    vec3 intersection = ray.start + ray.dir * t;
    vec3 rvector = normalize(intersection - sph.centre);
    return new_reflection(ray, rvector, t);
}

Reflection castRayWithLens(Ray ray, Lens lens) {
    vec3 OC = ray.start - lens.sphere.centre;
    float k1 = dot(ray.dir, ray.dir);
    float k2 = 2.0 * dot(OC, ray.dir);
    float k3 = dot(OC, OC) - lens.sphere.radius * lens.sphere.radius;
    float discr = k2 * k2 - 4.0 * k1 * k3;

    if (discr <= 0.0) {
        return NONE_REFLECTION;
    }

    discr = sqrt(discr);
    float t1 = (-k2 - discr) / (2.0 * k1);
    float t2 = (-k2 + discr) / (2.0 * k1);

    float t = INFTY;
    vec3 intersection;
    vec3 normal;

    for (int i = 0; i < 2; i++) {
        float ti = (i == 0) ? t1 : t2;
        if (ti < EPS) continue;
        vec3 lensDirection = vec3(lens.plane.a, lens.plane.b, lens.plane.c);

        vec3 candidateIntersection = ray.start + ray.dir * ti;
        vec3 candidateNormal = normalize(candidateIntersection - lens.sphere.centre);

        float planeSide = dot(vec3(lens.plane.a, lens.plane.b, lens.plane.c), candidateIntersection) + lens.plane.d;
        bool validSide = dot(vec3(lens.plane.a, lens.plane.b, lens.plane.c), lensDirection) > 0.0;

        if ((planeSide > 0.0) == validSide) {
            t = ti;
            intersection = candidateIntersection;
            normal = candidateNormal;
            break;
        }
    }

    if (t == INFTY) {
        return NONE_REFLECTION;
    }

    return new_reflection(ray, normal, t);
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
    Reflection refl = NONE_REFLECTION;
    int material = 0;

    float res = 1.0;

    for (int i = 0; i < 10; ++i) {
        refl.dist = INFTY;
        material = 0;

        PROCESS_PRIMITIVE(spheres, castRayWithSphere);
        PROCESS_PRIMITIVE(planes, castRayWithPlane);
        PROCESS_PRIMITIVE(trs, castRayWithTriangle);
        PROCESS_PRIMITIVE(lenses, castRayWithLens);

        if (refl.dist == INFTY) {
            return res * castRayWithSky(ray);
        }

        vec3 refvector = reflectOrRefract(ray, materials[material], refl.normal);
        ray = Ray(refl.intersection, refvector, ray.color, ray.opticalDensity, ray.isInside);
        res *= materials[material].color[ray.color];
    }

    return res;
}

#undef PROCESS_PRIMITIVE

vec4 getColor(vec3 camera, vec3 dir) {
    vec4 res = vec4(0.0, 0.0, 0.0, 1.0);

    Ray ray = Ray(camera, dir, COLOR_RED, 1.0, false);
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
}
