#!/usr/bin/env python3
# Compression progressive d'un maillage OBJ en OBJA.

import argparse
import numpy as np

from src.pole1_mesh import DynamicMesh
from src.pole2_simplifier import MeshSimplifier
from src.pole3_retriangulation import Retriangulator, Validator
from src.pole4_obja_writer import DecimationHistory, OBJAWriter


def parse_args():
    parser = argparse.ArgumentParser(description="Compression progressive de maillages 3D")
    parser.add_argument("input", nargs="?", default="demo/example/suzanne.obj", help="Fichier .obj d'entrée")
    parser.add_argument("-o", "--output", default=None, help="Fichier .obja de sortie")
    parser.add_argument("--min-vertices", type=int, default=4, help="Nombre minimal de sommets")
    parser.add_argument("--max-layers", type=int, default=None, help="Nombre maximal de couches")
    parser.add_argument("--max-error", type=float, default=None, help="Seuil d'erreur géométrique")
    parser.add_argument("--no-normal-check", action="store_true", help="Désactive le test des normales")
    parser.add_argument("--face-method", choices=["ef", "df"], default="ef",
                        help="ef : recycle les faces temporaires (fichier plus léger), df : les cache puis ajoute")
    return parser.parse_args()


def main():
    np.seterr(invalid="raise")
    args = parse_args()

    input_path = args.input
    output_path = args.output
    if output_path is None:
        if input_path.endswith(".obj"):
            output_path = input_path[:-4] + ".obja"
        else:
            output_path = input_path + ".obja"

    mesh = DynamicMesh()
    mesh.parse_file(input_path)

    retriangulator = Retriangulator()
    validator = Validator(check_normals=not args.no_normal_check)
    history = DecimationHistory()

    simplifier = MeshSimplifier(mesh, retriangulator, validator, history)
    simplifier.simplify(
        min_vertices=args.min_vertices,
        max_layers=args.max_layers,
        max_error=args.max_error,
    )

    writer = OBJAWriter()
    writer.export(mesh, history.get_layers(), output_path, method=args.face_method)


if __name__ == "__main__":
    main()
