#version 460 core
out vec4 color;

uniform vec2 resolution;

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
};

struct Sphere {
    vec3 centre;
    float radius;
    Material mat;
};

struct Reflection {
    Ray ray;
    float dist;
};

vec3 reflect(vec3 v, vec3 axis) {
    axis *= dot(axis, v);
    return (v - 2 * axis);
    return v - 2 * (v - axis);
}

bool isBlackSquare(float x) {
    return int((x + 0.5) * 55) % 2 == 0;
}

float castRayWithSky(Ray ray) {
    // if (ray.color == COLOR_RED) {
    //     return ray.dir.x;
    // }
    // if (ray.color == COLOR_BLUE) {
    //     return ray.dir.y;
    // }
    // return ray.dir.z * 0.4;
    if (ray.dir.y > -0.1) {
        if (ray.color == COLOR_BLUE) {
            return 0.3;
        } else {
            return 0.0;
        }
    }
    return 0.0;
    if (isBlackSquare(ray.dir.x) ^^ isBlackSquare(ray.dir.y)) {
        return 1.0;
    }
    return 0.0;
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

    Material mater1 = Material(float[](1.0, 0.0, 0.0), float[](0.1, 0.1, 0.1));
    Material mater2 = Material(float[](0.0, 0.0, 1.0), float[](0.1, 0.1, 0.1));
    Sphere sph1 = Sphere(vec3(-2.0, 1.0, 13.0), 1.5, mater1);
    Sphere sph2 = Sphere(vec3(1.0, -1.2, 13.0), 1.25, mater2);

    float res = 0.0;
    float brightness = 1.0;

    for (int i = 0; i < 10; ++i) {
        Reflection refl1 = castRayWithSphere(ray, sph1);
        Reflection refl2 = castRayWithSphere(ray, sph2);

        if (refl1.dist < refl2.dist) {
            refl = refl1;
            mat = sph1.mat;
        } else {
            refl = refl2;
            mat = sph2.mat;
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
