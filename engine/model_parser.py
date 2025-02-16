import pymeshlab
from scene import Triangle, Vector


def triangulate(filePath, centerX, centerY, modelHeight, material):
    mesh_set = pymeshlab.MeshSet()
    mesh_set.load_new_mesh(filePath)

    mesh_obj = mesh_set.mesh(0)

    triangles = mesh_obj.face_matrix()

    vertices = mesh_obj.vertex_matrix()

    maxZ = -float("inf")
    minZ = float("inf")

    triangle_list = []

    for triangle in triangles:
        v1, v2, v3 = triangle

        v1_coords = vertices[v1]
        v2_coords = vertices[v2]
        v3_coords = vertices[v3]

        maxZ = max(maxZ, v1_coords[2], v2_coords[2], v3_coords[2])
        minZ = min(minZ, v1_coords[2], v2_coords[2], v3_coords[2])

        triangle_list.append((v1_coords, v2_coords, v3_coords))

    height = maxZ - minZ
    scale = modelHeight / height if height != 0 else 1

    converted_triangles = []
    for v1_coords, v2_coords, v3_coords in triangle_list:
        v1 = Vector(
            float(v1_coords[0] * scale + centerX),
            float(v1_coords[1] * scale + centerY),
            float(v1_coords[2] * scale),
        )
        v2 = Vector(
            float(v2_coords[0] * scale + centerX),
            float(v2_coords[1] * scale + centerY),
            float(v2_coords[2] * scale),
        )
        v3 = Vector(
            float(v3_coords[0] * scale + centerX),
            float(v3_coords[1] * scale + centerY),
            float(v3_coords[2] * scale),
        )

        converted_triangles.append(Triangle(v1, v2, v3, material))

    return converted_triangles
