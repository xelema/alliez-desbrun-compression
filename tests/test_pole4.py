#!/usr/bin/env python3
"""
Script de test autonome pour le Pôle 4 (`src/pole4_obja_writer.py`).

Utilisation depuis la racine du dépôt :
    python tests/test_pole4.py
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import numpy as np
import demo.obja as obja
from src.interfaces import DecimationRecord
from src.pole4_obja_writer import DecimationHistory, GeometryPredictor, OBJAWriter


class MockBaseMesh(obja.Model):
    """
    Maillage synthétique (octaèdre dont le sommet supérieur 4 a été décimé)
    simulant le contrat du Pôle 1 (DynamicMesh) après décimation.
    """

    def __init__(self) -> None:
        super().__init__()
        # 4 sommets du carré équatorial (0, 1, 2, 3), sommet haut (4 décimé), sommet bas (5 actif)
        self.vertices = [
            np.array([1.0, 0.0, 0.0]),   # 0
            np.array([0.0, 1.0, 0.0]),   # 1
            np.array([-1.0, 0.0, 0.0]),  # 2
            np.array([0.0, -1.0, 0.0]),  # 3
            np.array([0.0, 0.0, 1.0]),   # 4 (sommet qui a été décimé lors de la passe A_1)
            np.array([0.0, 0.0, -1.0]),  # 5 (sommet bas du maillage de base)
        ]
        # Faces 0..3 : les 4 faces originales autour du sommet 4 (désactivées par la décimation)
        # Faces 4..7 : les 4 faces basses autour du sommet 5 (toujours actives)
        # Faces 8..9 : les 2 faces de re-triangulation du trou [0, 1, 2, 3] (actives dans le base_mesh)
        self.faces = [
            obja.Face(0, 1, 4, visible=False),  # 0
            obja.Face(1, 2, 4, visible=False),  # 1
            obja.Face(2, 3, 4, visible=False),  # 2
            obja.Face(3, 0, 4, visible=False),  # 3
            obja.Face(1, 0, 5, visible=True),   # 4
            obja.Face(2, 1, 5, visible=True),   # 5
            obja.Face(3, 2, 5, visible=True),   # 6
            obja.Face(0, 3, 5, visible=True),   # 7
            obja.Face(0, 1, 2, visible=True),   # 8 (re-triangulation temporaire)
            obja.Face(0, 2, 3, visible=True),   # 9 (re-triangulation temporaire)
        ]

    def get_active_vertices(self):
        return [0, 1, 2, 3, 5]

    def get_active_faces(self):
        return [4, 5, 6, 7, 8, 9]


def test_pole4() -> None:
    print("=== Test autonome du Pôle 4 (DecimationHistory, GeometryPredictor & OBJAWriter) ===")
    mesh = MockBaseMesh()

    # 1. Test de DecimationHistory
    history = DecimationHistory()
    record_a1 = DecimationRecord(
        layer_name="A_1",
        removed_vertex=4,
        removed_faces=[0, 1, 2, 3],
        added_faces=[(0, 1, 2), (0, 2, 3)],
        border_vertices=[0, 1, 2, 3],
        added_face_indices=[8, 9],
    )
    history.record_operation(record_a1)
    layers = history.get_layers()
    assert len(layers) == 1 and len(layers[0]) == 1 and layers[0][0].removed_vertex == 4
    print("[1/3] DecimationHistory (record_operation & get_layers) : OK")

    # 2. Test de GeometryPredictor (repère de Frenet et décomposition exacte)
    predictor = GeometryPredictor()
    bary, t1, t2, normal = predictor.compute_frenet_frame(
        mesh=mesh,
        border_vertices=record_a1.border_vertices,
        patch_triangles=record_a1.added_faces,
    )
    alpha, beta, gamma = predictor.decompose_residual(
        vertex_pos=mesh.vertices[4],
        barycenter=bary,
        t1=t1,
        t2=t2,
        normal=normal,
    )
    reconstructed_pos = bary + alpha * t1 + beta * t2 + gamma * normal
    assert np.allclose(reconstructed_pos, mesh.vertices[4], atol=1e-6), (
        f"Erreur de reconstruction Frenet : obtenu {reconstructed_pos}, attendu {mesh.vertices[4]}"
    )
    print(f"[2/3] GeometryPredictor Frenet (alpha={alpha:.3f}, beta={beta:.3f}, gamma={gamma:.3f}) : OK")

    # 3. Test de OBJAWriter.export et vérification avec le parseur officiel obja.py
    out_path = ROOT_DIR / "demo" / "example" / "test_pole4.obja"
    writer = OBJAWriter()
    writer.export(
        base_mesh=mesh,
        history=layers,
        output_path=str(out_path),
    )

    reconstructed = obja.parse_file(str(out_path))
    visible_faces = [f for f in reconstructed.faces if f.visible]
    assert len(reconstructed.vertices) == 6, f"Attendu 6 sommets, obtenu {len(reconstructed.vertices)}"
    assert len(visible_faces) == 8, f"Attendu 8 faces visibles finales, obtenu {len(visible_faces)}"
    print(f"[3/3] OBJAWriter.export -> fichier généré et validé : {out_path}")
    print("\nTous les tests du Pôle 4 sont passés avec succès !")
    print("Pour visualiser en 3D : `cd demo && python server.py` puis ouvre http://localhost:8000/?example/test_pole4.obja")


if __name__ == "__main__":
    test_pole4()
