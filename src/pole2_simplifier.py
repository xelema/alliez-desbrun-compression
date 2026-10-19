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
            seed_gate.v1 = StateFlag.CONQUERED
            seed_gate.v2 = StateFlag.CONQUERED
            self.vertex_tags[seed_gate.v1] = VertexTag.PLUS
            self.vertex_tags[seed_gate.v2] = VertexTag.MINUS

            queue.append(seed_gate)

            while not queue.count == 0 : 

                seed_gate_loop = queue.pop
                gate = self.mesh.get_gate_info(seed_gate_loop.v1, seed_gate_loop.v2)
                gate_flag = self.mesh.get_face_state(gate.front_face) 

                if gate is None or gate_flag != StateFlag.FREE : 
                    pass

                patch = self.mesh.extract_patch(gate)

                front_vertex = gate.front_vertex 
                if self.mesh.get_vertex_state(front_vertex) == StateFlag.FREE and not self.mesh.is_boundary_vertex(w) and 3 <= self.mesh.get_valence(w) <= 6 and patch is not None  :
                    # à voir avec mathis pour la sortie 
                    new_triangles, updated_tags = triangularisation( ..... ) #à recup 
                    
                    if self.validator.can_remove(self.mesh, patch, new_triangles, max_error):
                        
                        self.vertex_tags = updated_tags
                        patch.border_vertices = StateFlag.CONQUERED # à voir si ça marche c'est un liste je sais pas si c'est comme en matlab
                        
                        for k in range(1, patch.valence): 
                            queue.append((patch.border_vertices[(k + 1) % patch.valence], patch.border_vertices[k]))

                        added_face_indices = self.mesh.apply_patch_decimation(patch, new_triangles)
                        
                        self.history.record_operation(...) = DecimationRecord(""" à remplir avec les truc précédent """) # je sais pas si on le garde comme ça c'est bancale 

                        removed_count += 1
                else : 
                    gate.front_face = StateFlag.CONQUERED
                    queue.append(front_vertex, gate.v2)
                    queue.append(gate.v1, front_vertex)



    def run_cleaning_pass(self, layer_index, max_error=None):
        # Exécute la conquête de nettoyage Bi pour les valences 3.
        return 0

    def simplify(self, min_vertices=4, max_layers=None, max_error=None):
        # Boucle principale qui enchaîne les couches Ai et Bi.
        pass