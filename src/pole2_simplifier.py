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

        liste_faces = self.mesh.get_active_faces()

        if not liste_faces:
            return None
        
        for id in liste_faces:
            if self.mesh.get_face_state(id) == StateFlag.FREE : 
                face = self.mesh.faces[id]
                return self.mesh.get_gate_info(face.a,face.b)
            
        return None



    def run_decimation_pass(self, layer_index, max_error=None):
        # on reset les flag 
        self.mesh.reset_state_flags()
        self.vertex_tags.clear()

        removed_count = 0
        queue = deque()

        seed_gate = self.select_seed_gate()
        while seed_gate is not None :
            self.mesh.set_vertex_state(seed_gate.v1, StateFlag.CONQUERED)
            self.mesh.set_vertex_state(seed_gate.v2, StateFlag.CONQUERED)
            self.vertex_tags[seed_gate.v1] = VertexTag.PLUS
            self.vertex_tags[seed_gate.v2] = VertexTag.MINUS

            queue.append(seed_gate)

            while queue : 

                seed_gate_loop = queue.popleft()
                gate = self.mesh.get_gate_info(seed_gate_loop.v1, seed_gate_loop.v2)

                # cas 1 : la porte n'existe plus ou sa face avant est deja traitee
                if gate is None or self.mesh.get_face_state(gate.front_face) != StateFlag.FREE : 
                    continue

                front_vertex = gate.front_vertex 
                patch = None
                can_delete = False

                if self.mesh.get_vertex_state(front_vertex) == StateFlag.FREE and not self.mesh.is_boundary_vertex(front_vertex) and 3 <= self.mesh.get_valence(front_vertex) <= 6 :
                    patch = self.mesh.extract_patch(gate)

                if patch is not None :
                    new_triangles, updated_tags = self.retriangulator.plan_retriangulation(patch, self.vertex_tags)
                    can_delete = self.validator.can_remove_vertex(self.mesh, patch, new_triangles, max_error)

                if can_delete :
                    # cas 2 : on supprime le sommet
                    self.vertex_tags = updated_tags
                    for v in patch.border_vertices :
                        self.mesh.set_vertex_state(v, StateFlag.CONQUERED)

                    # les v-1 portes de sortie (on saute la porte d'entree k=0)
                    for k in range(1, patch.valence): 
                        exit_gate = self.mesh.get_gate_info(patch.border_vertices[(k + 1) % patch.valence], patch.border_vertices[k])
                        if exit_gate is not None :
                            queue.append(exit_gate)

                    added_face_indices = self.mesh.apply_patch_decimation(patch, new_triangles)

                    self.history.record_operation(DecimationRecord(
                        f"A_{layer_index}",
                        patch.center_vertex,
                        list(patch.incident_faces),
                        new_triangles,
                        list(patch.border_vertices),
                        added_face_indices))

                    removed_count += 1
                else : 
                    # cas 3 : null patch, on ne supprime rien mais on avance
                    self.mesh.set_face_state(gate.front_face, StateFlag.CONQUERED)
                    for exit_gate in (self.mesh.get_gate_info(front_vertex, gate.v2), self.mesh.get_gate_info(gate.v1, front_vertex)) :
                        if exit_gate is not None :
                            queue.append(exit_gate)

            # file vide : on cherche une autre graine (autre composante connexe)
            seed_gate = self.select_seed_gate()

        return removed_count



    def run_cleaning_pass(self, layer_index, max_error=None):
        # Exécute la conquête de nettoyage Bi pour les valences 3.
        return 0

    def simplify(self, min_vertices=4, max_layers=None, max_error=None):
        # Boucle principale qui enchaîne les couches Ai et Bi.
        pass