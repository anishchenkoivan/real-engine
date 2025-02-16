import pyassimp
from scene import Triangle, Vector

def triangulate(filePath, centerX, centerY, modelHeight, material):
    with pyassimp.load(filePath, processing=pyassimp.postprocess.aiProcess_Triangulate) as scene:
        if not scene.meshes:
            raise ValueError("Unable to parse the file")

        triangles = []
        maxZ = -float("inf")
        minZ = float("inf")

        for mesh in scene.meshes:
            for face in mesh.faces:
                if len(face) == 3:
                    v1, v2, v3 = mesh.vertices[face[0]], mesh.vertices[face[1]], mesh.vertices[face[2]]

                    maxZ = max(maxZ, v1[2], v2[2], v3[2])
                    minZ = min(minZ, v1[2], v2[2], v3[2])

                    triangles.append((v1, v2, v3))

        height = maxZ - minZ
        scale = modelHeight / height if height != 0 else 1

        convertedTriangles = []

        for v1, v2, v3 in triangles:
            v1 = Vector(v1[0] * scale + centerX, v1[1] * scale + centerY, v1[2] * scale)
            v2 = Vector(v2[0] * scale + centerX, v2[1] * scale + centerY, v2[2] * scale)
            v3 = Vector(v3[0] * scale + centerX, v3[1] * scale + centerY, v3[2] * scale)

            convertedTriangles.append(Triangle(v1, v2, v3, material))

        return convertedTriangles
