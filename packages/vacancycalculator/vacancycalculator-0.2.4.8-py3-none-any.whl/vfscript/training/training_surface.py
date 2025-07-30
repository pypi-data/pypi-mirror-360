import os
import json
import numpy as np
from scipy.spatial import ConvexHull
from vfscript.training.utils import resolve_input_params_path

from ovito.io import import_file, export_file
from ovito.modifiers import (
    ExpressionSelectionModifier,
    InvertSelectionModifier,
    DeleteSelectedModifier
)

class HSM:
    """
    Lee un dump de LAMMPS, centra las coordenadas, calcula hull y genera expresión Ovito.
    Puede alinear el hull al origen de un dump de referencia y aplicar la expresión.
    """
    def __init__(self, dump_path: str, ref_dump_path: str = None):
        # Rutas de input
        self.dump_path = resolve_input_params_path(dump_path)
        self.ref_dump_path = resolve_input_params_path(ref_dump_path) if ref_dump_path else None

        # Atributos de coordenadas
        self.coords_originales = None
        self.center_of_mass = None
        self.reference_center = None
        self.ovito_expr = None

        # Si hay referencia, calcular centro de masa de referencia
        if self.ref_dump_path:
            self._compute_reference_center()

    def _compute_reference_center(self):
        """
        Lee el dump de referencia y calcula su centro de masa.
        """
        coords = []
        with open(self.ref_dump_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        start = next((i for i,line in enumerate(lines)
                      if line.strip().startswith("ITEM: ATOMS")), None)
        if start is None:
            raise ValueError(f"No 'ITEM: ATOMS' en referencia: {self.ref_dump_path}")
        for line in lines[start+1:]:
            parts = line.split()
            if not parts or parts[0] == 'ITEM:': break
            if len(parts) < 5: continue
            try:
                x,y,z = float(parts[2]), float(parts[3]), float(parts[4])
                coords.append((x,y,z))
            except ValueError:
                continue
        if not coords:
            raise ValueError(f"No hay coords válidas en referencia: {self.ref_dump_path}")
        arr = np.array(coords)
        self.reference_center = arr.mean(axis=0)

    def read_and_translate(self):
        """
        Lee el dump y calcula el centro de masa del cluster.
        Guarda coords_originales y center_of_mass.
        """
        if not os.path.isfile(self.dump_path):
            raise FileNotFoundError(f"No encontrado: {self.dump_path}")
        coords = []
        with open(self.dump_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        start = next((i for i,line in enumerate(lines)
                      if line.strip().startswith("ITEM: ATOMS")), None)
        if start is None:
            raise ValueError(f"No 'ITEM: ATOMS' en {self.dump_path}")
        for line in lines[start+1:]:
            parts = line.split()
            if not parts or parts[0]=='ITEM:': break
            if len(parts) < 5: continue
            try:
                x,y,z = float(parts[2]), float(parts[3]), float(parts[4])
                coords.append((x,y,z))
            except ValueError:
                continue
        if not coords:
            raise ValueError(f"No coords tras 'ITEM: ATOMS' en {self.dump_path}")
        self.coords_originales = np.array(coords)
        self.center_of_mass = self.coords_originales.mean(axis=0)

    def compute_hull_expression(self, strict: bool = True) -> str:
        """
        Construye el hull a partir de coords_originales (alineado si hay referencia)
        y genera la expresión Ovito con < o > estrictos.
        """
        if self.coords_originales is None:
            raise RuntimeError("Llama primero a read_and_translate()")
        # Shift coords: move cluster center to reference center (o al origen si no hay)
        if self.reference_center is not None:
            pts = self.coords_originales - self.center_of_mass + self.reference_center
        else:
            pts = self.coords_originales
        hull = ConvexHull(pts)

        conditions = []
        seen = set()
        for a,b,c,d in hull.equations:
            if abs(c) < 1e-8: continue
            key = tuple(np.round([a,b,c,d],6))
            if key in seen: continue
            seen.add(key)
            coef_x = -a / c
            coef_y = -b / c
            const  = -d / c
            rhs = f"({coef_x:.6f})*Position.X + ({coef_y:.6f})*Position.Y + ({const:.6f})"
            if strict:
                cond = f"Position.Z < {rhs}" if c>0 else f"Position.Z > {rhs}"
            else:
                cond = f"Position.Z <= {rhs}" if c>0 else f"Position.Z >= {rhs}"
            conditions.append(cond)
        self.ovito_expr = " && ".join(conditions)
        return self.ovito_expr

    def apply_to_reference(self, output_path: str):
        """
        Aplica la expresión al dump de referencia (si se inicializó con ref_dump_path)
        y exporta el resultado filtrado.
        """
        if self.ovito_expr is None:
            raise RuntimeError("Primero compute_hull_expression()")
        if not self.ref_dump_path:
            raise RuntimeError("No se proporcionó referencia en __init__")
        pipe = import_file(self.ref_dump_path)
        pipe.modifiers.append(ExpressionSelectionModifier(expression=self.ovito_expr))
        pipe.modifiers.append(InvertSelectionModifier())
        pipe.modifiers.append(DeleteSelectedModifier())
        export_file(
            pipe,
            output_path,
            'lammps/dump',
            columns=[
                'Particle Identifier', 'Particle Type',
                'Position.X', 'Position.Y', 'Position.Z'
            ]
        )

if __name__ == "__main__":
    # Leer configuración
    cfg_path = resolve_input_params_path('outputs/json/key_archivos.json')
    with open(cfg_path, 'r') as f:
        cfg = json.load(f)

    ref = 'inputs/relax_structure.dump'   # sistema de referencia
    for path in cfg.get('clusters_final', []):
        proc = HSM(path, ref_dump_path=ref)
        proc.read_and_translate()
        expr = proc.compute_hull_expression(strict=True)
        print(f"Expresión para {path}:\n{expr}\n")
        base = os.path.splitext(os.path.basename(path))[0]
        outp = f'outputs/dump/{base}_inside.dump'
        proc.apply_to_reference(outp)
        print(f"→ Archivo filtrado: {outp}\n")
