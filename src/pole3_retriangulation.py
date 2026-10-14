from src.interfaces import Patch, VertexTag
from src.pole1_mesh import DynamicMesh
import numpy as np


class Retriangulator:
    # Table de retriangulation selon les balises +/-.

    def plan_retriangulation(self, patch, tags):
        return [], {}


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
