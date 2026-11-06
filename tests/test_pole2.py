#!/usr/bin/env python3
"""
Script de test autonome pour le Pôle 2 (`src/pole2_conquest.py`).

Ce script inclut des mocks légers simulant les Pôles 1, 3 et 4 sur un octaèdre
(6 sommets de valence 4, 8 faces triangulaires) afin que tu puisses tester
ton `ConquestEngine` sans attendre les 3 autres membres.

Utilisation depuis la racine du dépôt :
    python tests/test_pole2.py
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import numpy as np
import demo.obja as obja
from src.interfaces import Gate, Patch, StateFlag, VertexTag
from src.pole2_conquest import ConquestEngine


class MockOctahedronMesh(obja.Model):
    """Maillage octaédrique minimal simulant le contrat du Pôle 1 (DynamicMesh)."""

    def __init__(self) -> None:
        super().__init__()
        self.vertices = [
            np.array([1.0, 0.0, 0.0]),   # 0
            np.array([0.0, 1.0, 0.0]),   # 1
            np.array([-1.0, 0.0, 0.0]),  # 2
            np.array([0.0, -1.0, 0.0]),  # 3
            np.array([0.0, 0.0, 1.0]),   # 4 (sommet haut)
            np.array([0.0, 0.0, -1.0]),  # 5 (sommet bas)
        ]
        self.faces = [
            obja.Face(0, 1, 4, visible=True),
            obja.Face(1, 2, 4, visible=True),
            obja.Face(2, 3, 4, visible=True),
            obja.Face(3, 0, 4, visible=True),
            obja.Face(1, 0, 5, visible=True),
            obja.Face(2, 1, 5, visible=True),
            obja.Face(3, 2, 5, visible=True),
            obja.Face(0, 3, 5, visible=True),
        ]
        self.active_vertices = set(range(6))
        self.vertex_states = {v: StateFlag.FREE for v in range(6)}
        self.face_states = {f: StateFlag.FREE for f in range(8)}

    def get_active_vertices(self):
        return sorted(self.active_vertices)

    def get_active_faces(self):
        return [i for i, f in enumerate(self.faces) if f.visible]

    def reset_state_flags(self):
        for v in self.active_vertices:
            self.vertex_states[v] = StateFlag.FREE
        for f in self.get_active_faces():
            self.face_states[f] = StateFlag.FREE

    def get_vertex_state(self, v):
        return self.vertex_states[v]

    def set_vertex_state(self, v, state):
        self.vertex_states[v] = state

    def get_face_state(self, f):
        return self.face_states[f]

    def set_face_state(self, f, state):
        self.face_states[f] = state

    def is_boundary_vertex(self, v):
        return False

    def get_valence(self, v):
        return sum(1 for i, f in enumerate(self.faces) if f.visible and v in (f.a, f.b, f.c))

    def get_gate_info(self, v1, v2):
        for f_idx in self.get_active_faces():
            f = self.faces[f_idx]
            verts = (f.a, f.b, f.c)
            for k in range(3):
                if verts[k] == v1 and verts[(k + 1) % 3] == v2:
                    return Gate(v1=v1, v2=v2, front_face=f_idx, front_vertex=verts[(k + 2) % 3])
        return None

    def extract_patch(self, gate):
        center = gate.front_vertex
        border = []
        inc_faces = []
        curr_gate = gate
        v = self.get_valence(center)
        for _ in range(v):
            if curr_gate is None or curr_gate.front_vertex != center:
                return None
            border.append(curr_gate.v1)
            inc_faces.append(curr_gate.front_face)
            curr_gate = self.get_gate_info(center, curr_gate.v2)
            if curr_gate is not None:
                # Réoriente la porte sur le bord extérieur (v2 -> next_v)
                next_v = curr_gate.front_vertex
                curr_gate = Gate(v1= border[-1] if False else curr_gate.v2, v2=next_v,
                                 front_face=curr_gate.front_face, front_vertex=center)
        return Patch(
            center_vertex=center,
            valence=len(border),
            border_vertices=border,
            incident_faces=inc_faces,
            input_gate=gate,
        )

    def apply_patch_decimation(self, patch, new_triangles):
        for f_idx in patch.incident_faces:
            self.faces[f_idx].visible = False
            self.face_states[f_idx] = StateFlag.TO_BE_REMOVED
        self.active_vertices.discard(patch.center_vertex)
        self.vertex_states[patch.center_vertex] = StateFlag.TO_BE_REMOVED
        added_indices = []
        for a, b, c in new_triangles:
            new_idx = len(self.faces)
            self.faces.append(obja.Face(a, b, c, visible=True))
            self.face_states[new_idx] = StateFlag.CONQUERED
            added_indices.append(new_idx)
        return added_indices


class DummyRetriangulator:
    def plan_retriangulation(self, patch, tags):
        B = patch.border_vertices
        tris = [(B[0], B[i], B[i + 1]) for i in range(1, len(B) - 1)]
        updated = dict(tags)
        for idx, v in enumerate(B):
            updated.setdefault(v, VertexTag.PLUS if idx % 2 == 0 else VertexTag.MINUS)
        return tris, updated


class DummyValidator:
    def can_remove_vertex(self, mesh, patch, new_triangles, max_error=None):
        return len(mesh.get_active_vertices()) > 4


class DummyHistory:
    def __init__(self):
        self.records = []

    def record_operation(self, record):
        self.records.append(record)


def test_pole2() -> None:
    print("=== Test autonome du Pôle 2 (ConquestEngine) ===")
    mesh = MockOctahedronMesh()
    retri = DummyRetriangulator()
    validator = DummyValidator()
    history = DummyHistory()

    engine = ConquestEngine(
        mesh=mesh,
        retriangulator=retri,
        validator=validator,
        history=history,
    )

    # 1. Test de select_seed_gate
    seed = engine.select_seed_gate()
    assert seed is not None, "select_seed_gate doit trouver une porte graine sur un maillage FREE"
    print(f"[1/3] Porte graine sélectionnée : {seed} -> OK")

    # 2. Test d'une passe de décimation A_1
    removed_a1 = engine.run_decimation_pass(layer_index=1)
    assert removed_a1 >= 1, "Au moins un sommet de valence 4 de l'octaèdre doit être décimé"
    assert len(history.records) == removed_a1
    assert history.records[0].layer_name == "A_1"
    print(f"[2/3] Passe de décimation A_1 ({removed_a1} sommet(s) supprimé(s)) -> OK")

    # 3. Test de simplify sur un nouvel octaèdre
    mesh2 = MockOctahedronMesh()
    history2 = DummyHistory()
    engine2 = ConquestEngine(mesh2, retri, validator, history2)
    engine2.simplify(min_vertices=4, max_layers=2)
    assert len(mesh2.get_active_vertices()) <= 5
    print(
        f"[3/3] Boucle multi-couches simplify() terminée "
        f"({len(mesh2.get_active_vertices())} sommets restants, {len(history2.records)} opérations) -> OK"
    )
    print("\nTous les tests du Pôle 2 sont passés avec succès !")


if __name__ == "__main__":
    test_pole2()
