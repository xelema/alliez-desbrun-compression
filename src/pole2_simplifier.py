from src.interfaces import DecimationRecord, Gate, StateFlag, VertexTag
from src.pole1_mesh import DynamicMesh
from src.pole3_retriangulation import Retriangulator, Validator
from src.pole4_obja_writer import DecimationHistory
from collections import deque


class MeshSimplifier:
    # Simplifie le maillage couche par couche (conquêtes de décimation Ai et de nettoyage Bi).

    def __init__(self, mesh, retriangulator, validator, history):
        self.mesh = mesh
        self.retriangulator = retriangulator
        self.validator = validator
        self.history = history
        self.vertex_tags = {}



    def select_seed_gate(self):
        # Choisit une premiere porte pour demarrer la conquete. ou pour la redemarrer

        return None



    def run_decimation_pass(self, layer_index, max_error=None):
        # Exécute la conquête de décimation Ai.
        return 0



    def run_cleaning_pass(self, layer_index, max_error=None):
        # Exécute la conquête de nettoyage Bi pour les valences 3.
        return 0

    def simplify(self, min_vertices=4, max_layers=None, max_error=None):
        # Boucle principale qui enchaîne les couches Ai et Bi.
        pass