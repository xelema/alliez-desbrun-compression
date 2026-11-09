from typing import Dict

import demo.obja as obja

from src.interfaces import Gate, Patch, StateFlag


class DynamicMesh(obja.Model):
    # Maillage dynamique pour gérer les suppressions de patches et retriangulations.

    def __init__(self):
        self.half_edges =  dict()
        self.vertex_faces = dict()
        self.active_vertices = set()
        self.active_faces = set()
        self.vertex_states = dict()
        self.face_states = dict()
        super().__init__()

    def parse_file(self, path):
        super().parse_file(path)
        self.build_adjacency()

    def build_adjacency(self):
        for face_index, face in enumerate(self.faces):

            self.active_faces.add(face_index)
            self.face_states[face_index] = StateFlag.FREE

            v1, v2, v3 = face.a, face.b, face.c
            self.half_edges[(v1, v2)] = face_index
            self.half_edges[(v2, v3)] = face_index
            self.half_edges[(v3, v1)] = face_index

            for vertex in (v1, v2, v3):
                if vertex not in self.vertex_faces:
                    self.vertex_faces[vertex] = set()
                self.vertex_faces[vertex].add(face_index)

                self.active_vertices.add(vertex)
                self.vertex_states[vertex] = StateFlag.FREE

        pass

    def get_valence(self, vertex_index):
        if self.is_boundary_vertex(vertex_index):
            return len(self.vertex_faces[vertex_index]) + 1
        return len(self.vertex_faces[vertex_index])

    def is_boundary_vertex(self, vertex_index):
        for face_index in self.vertex_faces.get(vertex_index, []):
            face = self.faces[face_index]
            verts = (face.a, face.b, face.c)
            for i in range(3):
                v1 = verts[i]
                v2 = verts[(i + 1) % 3]
                if (v1, v2) not in self.half_edges or (v2, v1) not in self.half_edges:
                    return True
        return False

    def has_edge(self, v1, v2):
        return (v1, v2) in self.half_edges

    def get_active_vertices(self):
        return list(self.active_vertices)

    def get_active_faces(self):
        return list(self.active_faces)

    def get_vertex_state(self, vertex_index):
        return self.vertex_states.get(vertex_index, StateFlag.FREE)

    def set_vertex_state(self, vertex_index, state):
        self.vertex_states[vertex_index] = state

    def get_face_state(self, face_index):
        return self.face_states.get(face_index, StateFlag.FREE)

    def set_face_state(self, face_index, state):
        self.face_states[face_index] = state

    def reset_state_flags(self):
        for vertex in self.active_vertices:
            self.vertex_states[vertex] = StateFlag.FREE
        for face in self.active_faces:
            self.face_states[face] = StateFlag.FREE

    def get_gate_info(self, v1, v2):
        # Récupère les informations de la porte orientée.
        if (v1, v2) in self.half_edges:
            face_index = self.half_edges[(v1, v2)]
            face = self.faces[face_index]
            front_vertex = next(v for v in (face.a, face.b, face.c) if v != v1 and v != v2)
            return Gate(v1, v2, face_index, front_vertex)
        return None

    def extract_patch(self, gate):
        if not self.is_boundary_vertex(gate.v1):
            border_vertices = []
            u_curr, u_next, center = gate.v1, gate.v2, gate.front_vertex
            incident_faces = [gate.front_face]
            while True:
                gate_next = self.get_gate_info(center, u_next)
                border_vertices.append(u_curr)
                u_curr, u_next = u_next, gate_next.front_vertex

                if u_curr == gate.v1:
                    break
                incident_faces.append(gate_next.front_face)
            if len(border_vertices) != len(self.vertex_faces[center]):
                return None
            return Patch(center, len(border_vertices), border_vertices, incident_faces, gate)

        return None

    def apply_patch_decimation(self, patch, new_triangles):
        return []
