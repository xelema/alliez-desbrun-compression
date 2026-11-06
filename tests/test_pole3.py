#!/usr/bin/env python3
"""
Script de test autonome pour le Pôle 3 (`src/pole3_retriangulation.py`).

Utilisation depuis la racine du dépôt :
    python tests/test_pole3.py
"""

import math
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import numpy as np
import demo.obja as obja
from src.interfaces import Gate, Patch, VertexTag
from src.pole3_retriangulation import Retriangulator, Validator


class MockHexPatchMesh(obja.Model):
    """Mini-maillage hexagonal régulier autour d'un sommet central 6."""

    def __init__(self, existing_extra_edges=None) -> None:
        super().__init__()
        self.vertices = [
            np.array([math.cos(k * math.pi / 3.0), math.sin(k * math.pi / 3.0), 0.0])
            for k in range(6)
        ]
        # Sommet central 6 légèrement surélevé en z = 0.25
        self.vertices.append(np.array([0.0, 0.0, 0.25]))

        self.faces = [
            obja.Face(k, (k + 1) % 6, 6, visible=True) for k in range(6)
        ]
        self.extra_edges = set(existing_extra_edges or [])

    def has_edge(self, v1: int, v2: int) -> bool:
        if (v1, v2) in self.extra_edges or (v2, v1) in self.extra_edges:
            return True
        for f in self.faces:
            if f.visible:
                verts = (f.a, f.b, f.c)
                if v1 in verts and v2 in verts:
                    return True
        return False

    def get_valence(self, v: int) -> int:
        return sum(1 for f in self.faces if f.visible and v in (f.a, f.b, f.c))


def test_pole3() -> None:
    print("=== Test autonome du Pôle 3 (Retriangulator & Validator) ===")
    retri = Retriangulator()

    # 1. Test de la table Figure 9 pour les degrés v = 3, 4, 5, 6 et les 4 couples (+/-)
    for valence in (3, 4, 5, 6):
        border = list(range(valence))
        gate = Gate(v1=0, v2=1, front_face=0, front_vertex=valence)
        patch = Patch(
            center_vertex=valence,
            valence=valence,
            border_vertices=border,
            incident_faces=list(range(valence)),
            input_gate=gate,
        )
        for t0 in (VertexTag.MINUS, VertexTag.PLUS):
            for t1 in (VertexTag.MINUS, VertexTag.PLUS):
                tris, new_tags = retri.plan_retriangulation(patch, {0: t0, 1: t1})
                assert len(tris) == valence - 2, (
                    f"Degré {valence}, tags ({t0.value},{t1.value}) : "
                    f"attendu {valence - 2} triangles, obtenu {len(tris)}"
                )
                for v in border:
                    assert v in new_tags, f"Le sommet {v} du bord doit avoir une balise dans updated_tags"
    print("[1/4] Table de re-triangulation Figure 9 (degrés 3, 4, 5, 6 x 4 cas +/-) : OK")

    # 2. Test de Validator sur un patch hexagonal valide
    mesh = MockHexPatchMesh()
    gate6 = Gate(v1=0, v2=1, front_face=0, front_vertex=6)
    patch6 = Patch(
        center_vertex=6,
        valence=6,
        border_vertices=[0, 1, 2, 3, 4, 5],
        incident_faces=[0, 1, 2, 3, 4, 5],
        input_gate=gate6,
    )
    tris6, _ = retri.plan_retriangulation(patch6, {0: VertexTag.PLUS, 1: VertexTag.MINUS})

    validator = Validator(check_normals=True)
    assert validator.check_manifold(mesh, patch6, tris6) is True
    assert validator.check_normal_flipping(mesh, patch6, tris6) is True
    print("[2/4] Validation manifold et normal flipping sur patch hexagonal sain : OK")

    # 3. Test de détection d'une diagonale déjà existante (violation manifold)
    # On simule que toutes les diagonales internes existent déjà à l'extérieur du patch
    mesh_non_manifold = MockHexPatchMesh(
        existing_extra_edges=[(u, w) for u in range(6) for w in range(u + 2, 6)]
    )
    assert validator.check_manifold(mesh_non_manifold, patch6, tris6) is False
    print("[3/4] Détection d'arête doublon non-manifold (check_manifold == False) : OK")

    # 4. Test de la métrique d'erreur géométrique volumique et de can_remove_vertex
    err = validator.compute_geometric_error(mesh, patch6, tris6)
    assert err > 0.0
    assert validator.can_remove_vertex(mesh, patch6, tris6, max_error=err + 0.1) is True
    assert validator.can_remove_vertex(mesh, patch6, tris6, max_error=err * 0.1) is False
    print(f"[4/4] Métrique d'erreur volumique normalisée (error = {err:.4f}) et filtrage : OK")

    print("\nTous les tests du Pôle 3 sont passés avec succès !")


if __name__ == "__main__":
    test_pole3()
