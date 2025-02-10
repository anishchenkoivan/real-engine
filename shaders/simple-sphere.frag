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
};

struct Material {
    float color[3];
    float refllose[3];
    float roughness[3];
};

struct Sphere {
    vec3 centre;
    float radius;
    Material mat;
};

struct Plane {
    float a;
    float b;
    float c;
    float d;

    Material mat;
};

struct Triangle {
    vec3 a;
    vec3 b;
    vec3 c;

    Material mat;
};

struct Reflection {
    Ray ray;
    float dist;
};

bool isBlackSquare(float x) {
    return int((x + 0.5) * 55) % 2 == 0;
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


float castRayWithSky(Ray ray) {
    float[] sunColor = float[](1.0, 1.0, 0.0);
    float[] skyColor = float[](0.67, 0.84, 0.89);

    if (distance(ray.dir, normalize(vec3(0.4, 0.3, 1.0))) < 0.05) {
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

    vec3 refvector = diffusedReflection(normal, ray.dir, plane.mat.roughness[ray.color], ray.start);
    return Reflection(Ray(intersection, refvector, ray.color), t * length(ray.dir));
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
        vec3 reflection = diffusedReflection(normal, ray.dir, tr.mat.roughness[ray.color], ray.start);
        vec3 intersection = ray.start + ray.dir * t;
        return Reflection(Ray(intersection, reflection, ray.color), dist);
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
    vec3 refvector = diffusedReflection(rvector, ray.dir, sph.mat.roughness[ray.color], ray.start);
    return Reflection(Ray(intersection, refvector, ray.color), t * length(ray.dir));
}

float castRay(Ray ray) {
    Reflection refl;
    Material mat;

    Material mt1 = Material(float[](1.0, 0.0, 1.0), float[](0.1, 0.1, 0.1), float[](0.05, 0.05, 0.05));
    Material mt2 = Material(float[](1.0, 0.0, 1.0), float[](0.3, 0.3, 0.3), float[](0.05, 0.05, 0.05));
    Material mt3 = Material(float[](0.4, 0.4, 0.4), float[](0.4, 0.4, 0.4), float[](0.01, 0.01, 0.01));

    Sphere spheres[] = Sphere[](
            Sphere(vec3(-2.0, 1.0, 13.0), 1.5, mt1),
            Sphere(vec3(1.0, -1.2, 13.0), 1.25, mt2)
        );

    Plane planes[] = Plane[](
            Plane(0.0, 1.0, 0.0, 2.0, mt3)
        );

    Triangle trs[] = Triangle[](
            Triangle(vec3(-1.0, 0.0, 10.0), vec3(-1.0, 1.0, 11.0), vec3(3.0, 1.0, 10.0), mt3),
            Triangle(vec3(-1.0, 1.0, 11.0), vec3(-1.0, 2.0, 10.0), vec3(3.0, 1.0, 10.0), mt3),
            Triangle(vec3(-1.0, 2.0, 10.0), vec3(-1.0, -1.0, 9.0), vec3(3.0, 1.0, 10.0), mt3),
            Triangle(vec3(-1.0, -1.0, 9.0), vec3(-1.0, 0.0, 10.0), vec3(3.0, 1.0, 10.0), mt3),
            Triangle(vec3(-1.0, 2.0, 10.0), vec3(-1.0, 1.0, 11.0), vec3(-1.0, -1.0, 9.0), mt3)
        );

    float res = 0.0;
    float brightness = 1.0;

    for (int i = 0; i < 10; ++i) {
        refl.dist = INFTY;

        #define PROCESS_PRIMITIVE(primitives, castFunction, count) \
                    for (int i = 0; i < count; ++i) { \
                        Reflection newrefl = castFunction(ray, primitives[i]); \
                        if (newrefl.dist < refl.dist) { \
                            refl = newrefl; \
                            mat = primitives[i].mat; \
                        } \
                    } \

        PROCESS_PRIMITIVE(spheres, castRayWithSphere, 2);
        PROCESS_PRIMITIVE(planes, castRayWithPlane, 1);
        PROCESS_PRIMITIVE(trs, castRayWithTriangle, 5);

        #undef PROCESS_PRIMITIVE

        if (refl.dist == INFTY) {
            return res + brightness * castRayWithSky(ray);
        }
        ray = refl.ray;

        res = brightness * mat.color[ray.color] * mat.refllose[ray.color];
        brightness *= 1.0 - mat.refllose[ray.color];
    }

    return res / brightness;
}

vec4 getColor(vec3 camera, vec3 dir) {
    vec4 res = vec4(0.0, 0.0, 0.0, 1.0);

    Ray ray = Ray(camera, dir, COLOR_RED);
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
