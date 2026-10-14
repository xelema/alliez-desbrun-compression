from enum import Enum


class StateFlag(str, Enum):
    # Drapeaux d'état pour les sommets et faces.
    FREE = "FREE"
    CONQUERED = "CONQUERED"
    TO_BE_REMOVED = "TO_BE_REMOVED"


class VertexTag(str, Enum):
    # Balises de retriangulation.
    MINUS = "-"
    PLUS = "+"


class Gate:
    # Porte orientée avec son arête et son sommet avant.
    def __init__(self, v1, v2, front_face, front_vertex):
        self.v1 = v1
        self.v2 = v2
        self.front_face = front_face
        self.front_vertex = front_vertex


class Patch:
    # Voisinage autour d'un sommet à supprimer.
    def __init__(self, center_vertex, valence, border_vertices, incident_faces, input_gate):
        self.center_vertex = center_vertex
        self.valence = valence
        self.border_vertices = border_vertices
        self.incident_faces = incident_faces
        self.input_gate = input_gate


class DecimationRecord:
    # Enregistrement d'une décimation pour l'inversion OBJA.
    def __init__(self, layer_name, removed_vertex, removed_faces, added_faces, border_vertices, added_face_indices=None):
        self.layer_name = layer_name
        self.removed_vertex = removed_vertex
        self.removed_faces = removed_faces
        self.added_faces = added_faces
        self.border_vertices = border_vertices
        self.added_face_indices = added_face_indices if added_face_indices is not None else []
