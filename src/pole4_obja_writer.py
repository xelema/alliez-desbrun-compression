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
        if len(self.layers) == 0:
            self.layers.append([record])
        else:
            derniere_couche = self.layers[-1]
            derniere_operation = derniere_couche[-1]

            if derniere_operation.layer_name == record.layer_name:
                # même couche que l'opération précédente.
                derniere_couche.append(record)
            else:
                # on commence une nouvelle couche.
                self.layers.append([record])

    def get_layers(self):
        # Retourne la liste des couches.
        return self.layers


class GeometryPredictor:
    # Prédiction géométrique avec repère de Frenet.

    def compute_frenet_frame(self, mesh, border_vertices, patch_triangles):
        # Calcule le barycentre et la base locale (t1, t2, normale).

        barycenter = np.mean([mesh.vertices[pos] for pos in border_vertices], axis=0)

        normales_triangle = []

        for t in patch_triangles:
            pa = mesh.vertices[t[0]]
            pb = mesh.vertices[t[1]]
            pc = mesh.vertices[t[2]]
            normales_triangle.append(np.cross(pb - pa, pc - pa))

        normale = np.sum(normales_triangle, axis=0)
        normale_norm = normale / np.linalg.norm(normale)

        n = barycenter + normale_norm

        g = (mesh.vertices[border_vertices[1]] - mesh.vertices[border_vertices[0]]) + barycenter
        g -= (np.dot(g, normale_norm) * normale_norm)

        t1 = g / np.linalg.norm(g)
        t2 = np.cross(normale_norm, t1)

        return barycenter, t1, t2, n

    def decompose_residual(self, vertex_pos, barycenter, t1, t2, normal):
        # Calcule les coordonnées du résidu (alpha, beta, gamma).
        residu = vertex_pos - barycenter

        alpha = np.dot(residu, t1)
        beta = np.dot(residu, t2)
        gamma = np.dot(residu, normal)

        return alpha, beta, gamma


class OBJAWriter:
    # Écriture du fichier .obja final en inversant les couches.

    def export(self, base_mesh, history, output_path):
        # Exporte le maillage grossier puis rejoue les couches à l'envers.
        for i, layer in enumerate(history):
            print(f"couche {i} ({len(layer)} records)")
            for record in layer:
                print(vars(record))

        with open(output_path, "w") as file:
            out = obja.Output(file, random_color=False)

            # écriture du maillage grossier
            for v_id in base_mesh.get_active_vertices():
                out.add_vertex(v_id, base_mesh.vertices[v_id])

            for f_id in base_mesh.get_active_faces():
                out.add_face(f_id, base_mesh.faces[f_id])

            # écriture des couches (à l'envers)
            # B_n, A_n, B_{n-1}, etc...
            for layer in reversed(history):
                for record in layer:
                    #ajout du sommet retiré
                    out.add_vertex(record.removed_vertex, base_mesh.vertices[record.removed_vertex])

                    for k in record.added_face_indices:
                        # il n'y pas out.remove_face
                        print('df {}'.format(out.face_mapping[k] + 1), file=file)

                    for orig in record.removed_faces:
                        out.add_face(orig, base_mesh.faces[orig])

        pass
