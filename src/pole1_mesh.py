from typing import Dict

import demo.obja as obja

from src.interfaces import Gate, Patch, StateFlag


class DynamicMesh(obja.Model):
    # Maillage dynamique pour gérer les suppressions de patches et retriangulations.

    def __init__(self):
        super().__init__()

    def parse_file(self, path):
        super().parse_file(path)
        self.build_adjacency()

    def build_adjacency(self):
        pass

    def get_valence(self, vertex_index):
        return 0

    def is_boundary_vertex(self, vertex_index):
        return False

    def has_edge(self, v1, v2):
        return False

    def get_active_vertices(self):
        return []

    def get_active_faces(self):
        return []

    def get_vertex_state(self, vertex_index):
        return StateFlag.FREE

    def set_vertex_state(self, vertex_index, state):
        pass

    def get_face_state(self, face_index):
        return StateFlag.FREE

    def set_face_state(self, face_index, state):
        pass

    def reset_state_flags(self):
        pass

    def get_gate_info(self, v1, v2):
        # Récupère les informations de la porte orientée.
        return None

    def extract_patch(self, gate):
        return None

    def apply_patch_decimation(self, patch, new_triangles):
        return []
