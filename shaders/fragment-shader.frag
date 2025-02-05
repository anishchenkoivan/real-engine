#version 330 core
out vec4 color;

uniform vec2 resolution;

vec2 fragCoord = gl_FragCoord.xy;

vec3 reflect(vec3 v, vec3 axis) {
    axis = normalize(axis);
    vec3 proj = dot(v, axis) * axis;
    vec3 diff = v - proj;
    return v - 2 * diff;
}

vec2 castRayWithSky(vec3 start, vec3 dir) {
    return vec2((dir.x + 3 * dir.y + 2 * dir.z) / 6, 1.0 / 0.0);
}

vec2 castRayWithSphere(vec3 O, vec3 D, vec3 C, float R) {
    vec3 OC = O - C;
    float k1 = dot(D, D);
    float k2 = 2 * dot(OC, D);
    float k3 = dot(OC, OC) - R * R;
    float discr = k2 * k2 - 4 * k1 * k3;

    if (discr <= 0) {
        return castRayWithSky(O, D);
    }

    discr = sqrt(discr);

    float t1 = (-k2 - discr) / (2 * k1);
    float t2 = (-k2 + discr) / (2 * k1);

    vec3 intersection = O + D * t1;
    vec3 rvector = intersection - O;
    vec3 reflection = reflect(D, rvector);
    return castRayWithSky(intersection, reflection) * 0.5 + 0.5;
}

vec4 castRay(vec3 start, vec3 dir) {
    vec2 cst = castRayWithSphere(start, dir, vec3(0.0, 0.0, 10.0), 1.0);
    return vec4(cst.x, cst.x, cst.x, 1.0);
}

void main() {
    fragCoord -= resolution / 2;
    float d = max(resolution.x, resolution.y);
    vec2 uv = fragCoord / d;
    vec3 start = vec3(0.0, 0.0, -1.0);
    vec3 dir = vec3(uv, 1.0);
    color = castRay(start, dir);
}