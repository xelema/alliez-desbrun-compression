#!/usr/bin/env python3
"""
Script de test autonome pour le Pôle 1 (`src/pole1_mesh.py`).

Utilisation depuis la racine du dépôt :
    python tests/test_pole1.py
"""

import sys
from pathlib import Path

# Permet d'exécuter `python tests/test_pole1.py` directement
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.interfaces import StateFlag
from src.pole1_mesh import DynamicMesh


def test_pole1() -> None:
    print("=== Test autonome du Pôle 1 (DynamicMesh) ===")
    mesh = DynamicMesh()
    mesh.parse_file(str(ROOT_DIR / "demo" / "example" / "suzanne.obj"))

    active_v = mesh.get_active_vertices()
    active_f = mesh.get_active_faces()
    print(f"[1/4] Maillage chargé : {len(active_v)} sommets actifs, {len(active_f)} faces actives.")
    assert len(active_v) > 0 and len(active_f) > 0

    # Test des drapeaux d'état
    v0 = active_v[0]
    assert mesh.get_vertex_state(v0) == StateFlag.FREE
    mesh.set_vertex_state(v0, StateFlag.CONQUERED)
    assert mesh.get_vertex_state(v0) == StateFlag.CONQUERED
    mesh.reset_state_flags()
    assert mesh.get_vertex_state(v0) == StateFlag.FREE
    print("[2/4] Gestion des drapeaux d'état (StateFlag) : OK")

    # Test de get_gate_info
    f0 = mesh.faces[active_f[0]]
    gate = mesh.get_gate_info(f0.a, f0.b)
    assert gate is not None, "get_gate_info ne doit pas retourner None sur une face active"
    assert gate.front_face == active_f[0] and gate.front_vertex == f0.c
    assert mesh.has_edge(f0.a, f0.b) and mesh.has_edge(f0.b, f0.a)
    print(f"[3/4] Navigation Gate sur la face 0 ({gate}) : OK")

    # Test de extract_patch et apply_patch_decimation sur un sommet intérieur de valence <= 6
    target_patch = None
    for f_idx in active_f:
        f = mesh.faces[f_idx]
        g = mesh.get_gate_info(f.a, f.b)
        if g and not mesh.is_boundary_vertex(g.front_vertex):
            v_val = mesh.get_valence(g.front_vertex)
            if 3 <= v_val <= 6:
                patch = mesh.extract_patch(g)
                if patch is not None:
                    target_patch = patch
                    break

    assert target_patch is not None, "Aucun patch intérieur de valence <= 6 trouvé"
    assert target_patch.border_vertices[0] == target_patch.input_gate.v1
    assert target_patch.border_vertices[1] == target_patch.input_gate.v2
    assert len(target_patch.border_vertices) == target_patch.valence
    assert len(target_patch.incident_faces) == target_patch.valence

    # Simulation d'une re-triangulation en éventail pour tester apply_patch_decimation
    B = target_patch.border_vertices
    new_triangles = [(B[0], B[i], B[i + 1]) for i in range(1, len(B) - 1)]
    new_face_indices = mesh.apply_patch_decimation(target_patch, new_triangles)

    assert len(new_face_indices) == target_patch.valence - 2
    assert target_patch.center_vertex not in mesh.get_active_vertices()
    print(
        f"[4/4] Extraction et décimation du patch autour du sommet {target_patch.center_vertex} "
        f"(valence {target_patch.valence} -> {len(new_face_indices)} triangles créés) : OK"
    )
    print("\nTous les tests du Pôle 1 sont passés avec succès !")


if __name__ == "__main__":
    test_pole1()
