#version 460 core
out vec4 color;

uniform vec2 resolution;

vec2 fragCoord = gl_FragCoord.xy;

#define INFTY 1E9
#define EPS   1E-3

#define COLOR_RED   0
#define COLOR_GREEN 1
#define COLOR_BLUE  2

#define ARRLEN(x)  (sizeof(x) / sizeof((x)[0]))

struct Ray {
    vec3 start;
    vec3 dir;
    int color;
};

struct Material {
    float color[3];
    float refllose[3];
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

struct Reflection {
    Ray ray;
    float dist;
};

vec3 reflect(vec3 v, vec3 axis) {
    axis *= dot(axis, v);
    return normalize(v - 2 * axis);
}

bool isBlackSquare(float x) {
    return int((x + 0.5) * 55) % 2 == 0;
}

float castRayWithSky(Ray ray) {
    return 0.8;
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

    vec3 refvector = reflect(ray.dir, normal);
    return Reflection(Ray(intersection, refvector, ray.color), t * length(ray.dir));
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
    vec3 refvector = reflect(ray.dir, rvector);
    return Reflection(Ray(intersection, refvector, ray.color), t * length(ray.dir));
}

float castRay(Ray ray) {
    Reflection refl;
    Material mat;

    Material mt1 = Material(float[](1.0, 0.0, 1.0), float[](0.1, 0.1, 0.1));
    Material mt2 = Material(float[](1.0, 0.0, 1.0), float[](0.3, 0.3, 0.3));
    Material mt3 = Material(float[](0.4, 0.4, 0.4), float[](0.4, 0.4, 0.4));

    Sphere spheres[] = Sphere[](
            Sphere(vec3(-2.0, 1.0, 13.0), 1.5, mt1),
            Sphere(vec3(1.0, -1.2, 13.0), 1.25, mt2)
        );

    Plane planes[] = Plane[](
            Plane(0.0, 1.0, 0.0, 2.0, mt3)
        );

    float res = 0.0;
    float brightness = 1.0;

    for (int i = 0; i < 10; ++i) {
        refl.dist = INFTY;

        for (int i = 0; i < 2; ++i) {
            Reflection newrefl = castRayWithSphere(ray, spheres[i]);
            if (newrefl.dist < refl.dist) {
                refl = newrefl;
                mat = spheres[i].mat;
            }
        }

        for (int i = 0; i < 1; ++i) {
            Reflection newrefl = castRayWithPlane(ray, planes[i]);
            if (newrefl.dist < refl.dist) {
                refl = newrefl;
                mat = planes[i].mat;
            }
        }

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
    vec3 camera = vec3(0.0, 0.0, -1.0);
    vec3 dir = normalize(vec3(uv, 0.0) - camera);
    color = getColor(camera, dir);
}
