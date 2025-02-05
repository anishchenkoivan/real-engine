#version 330 core
out vec4 color;

uniform vec2 resolution;

vec2 fragCoord = gl_FragCoord.xy;

#define INFTY (1.0 / 0.0)

#define COLOR_RED   0
#define COLOR_GREEN 1
#define COLOR_BLUE  2
#define COLOR_GREY  3

struct Ray {
    vec3 start;
    vec3 dir;
    int color;
};

struct Sphere {
    vec3 centre;
    float radius;
};

struct Reflection {
    Ray ray;
    float dist;
};

vec3 reflect(vec3 v, vec3 axis) {
    axis = normalize(axis);
    vec3 proj = dot(v, axis) * axis;
    vec3 diff = v - proj;
    return v - 2 * diff;
}

bool isBlackSquare(float x) {
    return int((x + 0.5) * 55) % 2 == 0;
}

float castRayWithSky(Ray ray) {
    if (ray.dir.y > -0.1) {
        return 0.0;
    }
    ray.dir = normalize(ray.dir);
    if (isBlackSquare(ray.dir.x) ^^ isBlackSquare(ray.dir.y)) {
        return 1.0;
    }
    return 0.3;
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

    vec3 intersection = ray.start + ray.dir * t2;
    vec3 rvector = intersection - sph.centre;
    vec3 refvector = reflect(ray.dir, rvector);
    return Reflection(Ray(intersection, refvector, ray.color), t2);
}

vec4 castRay(Ray ray) {
    Sphere sph = Sphere(vec3(0.0, 0.0, 10.0), 0.5);
    Reflection refl = castRayWithSphere(ray, sph);
    ray = refl.ray;

    float brightness;
    if (refl.dist == INFTY) {
        brightness = castRayWithSky(ray);
    } else {
        brightness = castRayWithSky(ray) * 0.5 + 0.5;
    }
    return vec4(brightness, brightness, brightness, 1.0);
}

void main() {
    fragCoord -= resolution / 2;
    float d = max(resolution.x, resolution.y);
    vec2 uv = fragCoord / d;
    vec3 camera = vec3(0.0, 0.0, -1.0);
    vec3 dir = normalize(vec3(uv, 0.0) - camera);
    Ray ray = Ray(camera, dir, COLOR_GREY);
    color = castRay(ray);
}
