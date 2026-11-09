from src.interfaces import Patch, VertexTag
from src.pole1_mesh import DynamicMesh
import numpy as np


class Retriangulator:
    # Table de retriangulation selon les balises +/-.

    def plan_retriangulation(self, patch, tags):
        new_tri = []

        # Balises par défaut de la porte d'entrée (cf. guide) : v0 = +, v1 = -.
        tags_patch = [tags.get(v) for v in patch.border_vertices]
        if tags_patch[0] is None:
            tags_patch[0] = VertexTag.PLUS
        if tags_patch[1] is None:
            tags_patch[1] = VertexTag.MINUS

        # Cas triangle.
        if patch.valence == 3:
            new_tri.append(list(patch.border_vertices))
            tags_patch[2] = VertexTag.MINUS if tags_patch.count(VertexTag.PLUS) == 2 else VertexTag.PLUS

        # Cas quadrilatère.
        if patch.valence == 4:
            if tags_patch[1] == VertexTag.PLUS:
                new_tri.append([patch.border_vertices[0], patch.border_vertices[1], patch.border_vertices[3]])
                new_tri.append([patch.border_vertices[1], patch.border_vertices[2], patch.border_vertices[3]])
                tags_patch[3] = VertexTag.PLUS
                tags_patch[2] = VertexTag.MINUS
            else:
                new_tri.append([patch.border_vertices[0], patch.border_vertices[1], patch.border_vertices[2]])
                new_tri.append([patch.border_vertices[0], patch.border_vertices[2], patch.border_vertices[3]])
                tags_patch[2] = VertexTag.PLUS
                tags_patch[3] = VertexTag.MINUS



        # Cas pentagone.
        if patch.valence == 5:
            if tags_patch[0] == VertexTag.PLUS and tags_patch[1] == VertexTag.MINUS:
                new_tri.append([patch.border_vertices[0], patch.border_vertices[1], patch.border_vertices[2]])
                new_tri.append([patch.border_vertices[0], patch.border_vertices[2], patch.border_vertices[4]])
                new_tri.append([patch.border_vertices[4], patch.border_vertices[2], patch.border_vertices[3]])
                tags_patch[2] = VertexTag.PLUS
                tags_patch[3] = VertexTag.MINUS
                tags_patch[4] = VertexTag.PLUS
            elif tags_patch[0] == VertexTag.MINUS and tags_patch[1] == VertexTag.PLUS:
                new_tri.append([patch.border_vertices[0], patch.border_vertices[1], patch.border_vertices[4]])
                new_tri.append([patch.border_vertices[1], patch.border_vertices[2], patch.border_vertices[4]])
                new_tri.append([patch.border_vertices[2], patch.border_vertices[3], patch.border_vertices[4]])
                tags_patch[2] = VertexTag.PLUS
                tags_patch[3] = VertexTag.MINUS
                tags_patch[4] = VertexTag.PLUS

            elif tags_patch[0] == VertexTag.PLUS and tags_patch[1] == VertexTag.PLUS:
                new_tri.append([patch.border_vertices[0], patch.border_vertices[3], patch.border_vertices[4]])
                new_tri.append([patch.border_vertices[0], patch.border_vertices[1], patch.border_vertices[3]])
                new_tri.append([patch.border_vertices[1], patch.border_vertices[2], patch.border_vertices[3]])
                tags_patch[2] = VertexTag.MINUS
                tags_patch[3] = VertexTag.PLUS
                tags_patch[4] = VertexTag.MINUS
            elif tags_patch[0] == VertexTag.MINUS and tags_patch[1] == VertexTag.MINUS:
                new_tri.append([patch.border_vertices[0], patch.border_vertices[1], patch.border_vertices[2]])
                new_tri.append([patch.border_vertices[0], patch.border_vertices[2], patch.border_vertices[4]])
                new_tri.append([patch.border_vertices[2], patch.border_vertices[3], patch.border_vertices[4]])
                tags_patch[2] = VertexTag.PLUS
                tags_patch[3] = VertexTag.MINUS
                tags_patch[4] = VertexTag.PLUS

        if patch.valence == 6:
            if tags_patch[0] == VertexTag.PLUS and tags_patch[1] == VertexTag.MINUS:
                new_tri.append([patch.border_vertices[0], patch.border_vertices[1], patch.border_vertices[2]])
                new_tri.append([patch.border_vertices[0], patch.border_vertices[2], patch.border_vertices[4]])
                new_tri.append([patch.border_vertices[2], patch.border_vertices[3], patch.border_vertices[4]])
                new_tri.append([patch.border_vertices[0], patch.border_vertices[4], patch.border_vertices[5]])
                tags_patch[2] = VertexTag.PLUS
                tags_patch[3] = VertexTag.MINUS
                tags_patch[4] = VertexTag.PLUS
                tags_patch[5] = VertexTag.MINUS
            elif tags_patch[0] == VertexTag.MINUS and tags_patch[1] == VertexTag.PLUS:
                new_tri.append([patch.border_vertices[0], patch.border_vertices[1], patch.border_vertices[5]])
                new_tri.append([patch.border_vertices[1], patch.border_vertices[2], patch.border_vertices[3]])
                new_tri.append([patch.border_vertices[1], patch.border_vertices[3], patch.border_vertices[5]])
                new_tri.append([patch.border_vertices[5], patch.border_vertices[3], patch.border_vertices[4]])
                tags_patch[2] = VertexTag.MINUS
                tags_patch[3] = VertexTag.PLUS
                tags_patch[4] = VertexTag.MINUS
                tags_patch[5] = VertexTag.PLUS
            elif tags_patch[0] == VertexTag.PLUS and tags_patch[1] == VertexTag.PLUS:
                new_tri.append([patch.border_vertices[0], patch.border_vertices[1], patch.border_vertices[5]])
                new_tri.append([patch.border_vertices[1], patch.border_vertices[2], patch.border_vertices[3]])
                new_tri.append([patch.border_vertices[1], patch.border_vertices[3], patch.border_vertices[5]])
                new_tri.append([patch.border_vertices[3], patch.border_vertices[4], patch.border_vertices[5]])
                tags_patch[2] = VertexTag.MINUS
                tags_patch[3] = VertexTag.PLUS
                tags_patch[4] = VertexTag.MINUS
                tags_patch[5] = VertexTag.PLUS
            elif tags_patch[0] == VertexTag.MINUS and tags_patch[1] == VertexTag.MINUS:
                new_tri.append([patch.border_vertices[0], patch.border_vertices[1], patch.border_vertices[2]])
                new_tri.append([patch.border_vertices[0], patch.border_vertices[2], patch.border_vertices[4]])
                new_tri.append([patch.border_vertices[2], patch.border_vertices[3], patch.border_vertices[4]])
                new_tri.append([patch.border_vertices[0], patch.border_vertices[4], patch.border_vertices[5]])
                tags_patch[2] = VertexTag.PLUS
                tags_patch[3] = VertexTag.MINUS
                tags_patch[4] = VertexTag.PLUS
                tags_patch[5] = VertexTag.MINUS

        # Cas erreur : si la valence est supérieure à 6, on ne peut pas retrianguler.
        if patch.valence > 6:
            raise ValueError("Valence supérieure à 6, retriangulation non supportée.")

        # Une balise déjà attribuée n'est jamais modifiée (Section 3.5).
        new_tags = tags.copy()
        for i in range(len(patch.border_vertices)):
            if patch.border_vertices[i] not in new_tags:
                new_tags[patch.border_vertices[i]] = tags_patch[i]

        # print(new_tags)
        return new_tri, new_tags


class Validator:

    def __init__(self, check_normals=True):
        self.check_normals = check_normals

    def check_manifold(self, mesh, patch, new_triangles):
        # Les arêtes du bord appartiennent déjà aux faces voisines du patch.
        # Seules les diagonales introduites par la retriangulation doivent être
        # absentes du maillage existant.
        border = patch.border_vertices
        border_edges = {
            tuple(sorted((border[i], border[(i + 1) % len(border)])))
            for i in range(len(border))
        }

        for tri in new_triangles:
            print(f"Vérification de la triangle {tri} dans le maillage...")
            v1, v2, v3 = tri
            if len({v1, v2, v3}) != 3:
                print(f"Triangle dégénéré {tri}.")
                return False

            for edge in ((v1, v2), (v2, v3), (v3, v1)):
                if tuple(sorted(edge)) in border_edges:
                    continue
                if mesh.has_edge(*edge):
                    print(f"Edge {edge} existe déjà dans le maillage.")
                    return False
        return True

    def check_normal_flipping(self, mesh, patch, new_triangles):
        # Vérifie si les normales sont inversées.
        def triangle_normal(triangle):
            a, b, c = mesh.vertices[triangle[0]], mesh.vertices[triangle[1]], mesh.vertices[triangle[2]]
            return np.cross(b - a, c - a)

        ref_normal = triangle_normal([patch.border_vertices[0], patch.border_vertices[1], patch.border_vertices[2]])
        for tri in new_triangles:
            new_normal = triangle_normal(tri)
            if np.dot(ref_normal, new_normal) < 0:
                print(f"Normal flipping détecté pour le triangle {tri}.")
                return False
        return True

    def compute_geometric_error(self, mesh, patch, new_triangles):
        # Calcule l'erreur géométrique entre le maillage original et le nouveau maillage.
        # Le volume de l'enveloppe fermée formée par les deux triangulations
        # est calculé par somme de tétraèdres orientés.
        def signed_tetra_volume(a, b, c):
            pa, pb, pc = (
                np.asarray(mesh.vertices[index], dtype=float)
                for index in (a, b, c)
            )
            center = np.asarray(mesh.vertices[patch.center_vertex], dtype=float)
            return abs(np.dot(pa - center, np.cross(pb - center, pc - center))) / 6.0

        original_volume = sum(
            signed_tetra_volume(
                face.a,
                face.b,
                face.c,
            )
            for index, face in enumerate(mesh.faces)
            if index in patch.incident_faces and getattr(face, "visible", True)
        )
        new_volume = sum(
            signed_tetra_volume(triangle[0], triangle[1], triangle[2])
            for triangle in new_triangles
        )
        volume = abs(original_volume - new_volume)

        border_points = [
            np.asarray(mesh.vertices[index], dtype=float)
            for index in patch.border_vertices
        ]
        perimeter = sum(
            np.linalg.norm(border_points[i] - border_points[(i + 1) % len(border_points)])
            for i in range(len(border_points))
        )
        if perimeter == 0 or patch.valence == 0:
            return 0.0
        return volume ** (1.0 / 3.0) / (perimeter / patch.valence)

    def can_remove_vertex(self, mesh, patch, new_triangles, max_error=0.25):
        # Un patch de valence v doit être remplacé par exactement v - 2 triangles.
        if len(new_triangles) != patch.valence - 2:
            return False
        if not self.check_manifold(mesh, patch, new_triangles):
            return False
        if self.check_normals and not self.check_normal_flipping(mesh, patch, new_triangles):
            return False
        if max_error is not None and not self.compute_geometric_error(mesh, patch, new_triangles) <= max_error:
            return False
        return True
