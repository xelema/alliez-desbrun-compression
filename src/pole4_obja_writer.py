import numpy as np
import demo.obja as obja

from src.interfaces import DecimationRecord
from src.pole1_mesh import DynamicMesh


class DecimationHistory:
    # Stocke l'historique des opérations de décimation par couche.

    def __init__(self):
        self.layers = []

    def record_operation(self, record):
        # Ajoute une opération dans la couche courante.
        pass

    def get_layers(self):
        # Retourne la liste des couches.
        return self.layers


class GeometryPredictor:
    # Prédiction géométrique avec repère de Frenet.

    def compute_frenet_frame(self, mesh, border_vertices, patch_triangles):
        # Calcule le barycentre et la base locale (t1, t2, normale).

        return np.zeros(3), np.zeros(3), np.zeros(3), np.zeros(3)

    def decompose_residual(self, vertex_pos, barycenter, t1, t2, normal):
        # Calcule les coordonnées du résidu (alpha, beta, gamma).
        return 0.0, 0.0, 0.0


class OBJAWriter:
    # Écriture du fichier .obja final en inversant les couches.

    def export(self, base_mesh, history, output_path):
        # Exporte le maillage grossier puis rejoue les couches à l'envers.
        pass
