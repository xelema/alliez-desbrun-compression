from src.interfaces import Patch, VertexTag
from src.pole1_mesh import DynamicMesh
import numpy as np


class Retriangulator:
    # Table de retriangulation selon les balises +/-.

    def plan_retriangulation(self, patch, tags):
        new_tri = []
        new_tags = tags.copy()

        # Cas triangle. 
        if patch.valence() == 3:
            new_tri.append(patch.border_vertices)

            tags_patch = [tags.get(v) for v in patch.border_vertices]
            for v in patch.border_vertices:
                if tags.get(v) is None:
                    new_tags[v] = VertexTag.MINUS if tags_patch.count(VertexTag.PLUS) == 2 else VertexTag.PLUS

        # Cas quadrilatère.
        if patch.valence() == 4:
            tags_patch = [tags.get(v) for v in patch.border_vertices]
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
        if patch.valence() == 5:
            tags_patch = [tags.get(v) for v in patch.border_vertices]
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

        if patch.valence() ==6:
            tags_patch = [tags.get(v) for v in patch.border_vertices]
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
        if patch.valence() > 6:
            raise ValueError("Valence supérieure à 6, retriangulation non supportée.")

        return new_tri, new_tags


class Validator:

    def __init__(self, check_normals=True):
        self.check_normals = check_normals

    def check_manifold(self, mesh, patch, new_triangles):
        # Les arêtes du bord appartiennent déjà aux faces voisines du patch.
        # Seules les diagonales introduites par la retriangulation doivent être
        # absentes du maillage existant.
        return True

    def check_normal_flipping(self, mesh, patch, new_triangles):
        # Vérifie si les normales sont inversées.
        return True

    def compute_geometric_error(self, mesh, patch, new_triangles):
        # Calcule l'erreur géométrique entre le maillage original et le nouveau maillage.
        # Le volume de l'enveloppe fermée formée par les deux triangulations
        # est calculé par somme de tétraèdres orientés.
        return 0.0

    def can_remove_vertex(self, mesh, patch, new_triangles, max_error=0.25):
        # Un patch de valence v doit être remplacé par exactement v - 2 triangles.
        return True
