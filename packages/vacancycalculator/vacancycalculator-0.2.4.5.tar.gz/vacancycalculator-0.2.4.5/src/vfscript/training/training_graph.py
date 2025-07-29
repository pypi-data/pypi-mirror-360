import json
import copy
import numpy as np
import networkx as nx
from scipy.spatial import ConvexHull
from ovito.io import import_file, export_file
from ovito.modifiers import (
    ExpressionSelectionModifier,
    DeleteSelectedModifier,
    ClusterAnalysisModifier,
    ConstructSurfaceModifier,
    InvertSelectionModifier
)

from vfscript.training.utils import resolve_input_params_path
class AtomicGraphGenerator:
    def __init__(self,json_params_path: str = None):
       
        if json_params_path is None:
            json_params_path = resolve_input_params_path("input_params.json")


        
        with open(json_params_path, "r", encoding="utf-8") as f:
            all_params = json.load(f)
        if "CONFIG" not in all_params or not isinstance(all_params["CONFIG"], list) or len(all_params["CONFIG"]) == 0:
            raise KeyError("input_params.json debe contener la clave 'CONFIG' como lista no vacía.")
        cfg = all_params["CONFIG"][0]
        self.input_path = cfg['relax']
        self.cutoff = cfg['cutoff']
        self.radius = cfg['radius']
        self.smoothing_level_training = cfg['smoothing_level_training']
        self.num_iterations = cfg['max_graph_variations'] 
        self.max_nodes = cfg['max_graph_size']
        self.pipeline = import_file(self.input_path, multiple_frames=True)
        self.metrics = {
            'surface_area': [],
            'filled_volume': [],
            'vacancys': [],
            'cluster_size': []
        }

    def run(self):
        for iteration in range(1, self.num_iterations + 1):
            for length in range(2, self.max_nodes + 1):
                ids, coords = self._generate_graph(length)
                expr = " || ".join(f"ParticleIdentifier=={pid}" for pid in ids)
                area, volume, count = self._export_graph(expr)
                self.metrics['surface_area'].append(area)
                self.metrics['filled_volume'].append(volume)
                self.metrics['vacancys'].append(len(ids))
                self.metrics['cluster_size'].append(count)
        with open('outputs/json/training_graph.json', 'w') as f:
            json.dump(self.metrics, f, indent=4)
        print('Exported metrics to results.json')

    def _generate_graph(self, length: int):
        data = self.pipeline.compute()
        pos = data.particles.positions.array
        ids_arr = data.particles['Particle Identifier'].array
        N = len(pos)
        start = np.random.choice(N)
        coords = [pos[start]]
        ids = [int(ids_arr[start])]
        current = coords[0]
        remaining = set(range(N))
        remaining.remove(start)
        while len(coords) < length and remaining:
            rem = np.array(list(remaining))
            dists = np.linalg.norm(pos[rem] - current, axis=1)
            order = np.argsort(dists)
            top2 = order[:2] if len(order) >= 2 else order
            cands = rem[top2]
            choice = np.random.choice(cands)
            coords.append(pos[choice])
            ids.append(int(ids_arr[choice]))
            current = pos[choice]
            remaining.remove(choice)
        return ids, coords

    def _export_graph(self, expr: str):
        p = copy.deepcopy(self.pipeline)
        p.modifiers.append(ExpressionSelectionModifier(expression=expr))
        p.modifiers.append(DeleteSelectedModifier())
        p.modifiers.append(ConstructSurfaceModifier(
            radius=self.radius,
            smoothing_level=self.smoothing_level_training,
            select_surface_particles=True
        ))
        p.modifiers.append(InvertSelectionModifier())
        p.modifiers.append(DeleteSelectedModifier())
        p.modifiers.append(ClusterAnalysisModifier(cutoff=self.cutoff, unwrap_particles=True))
        data = p.compute()
        points = data.particles.positions.array
        count = len(points)
        if count >= 4:
            hull = ConvexHull(points)
            area = hull.area
            volume = hull.volume
        else:
            area = 0.0
            volume = 0.0
        export_file(
            p,
            f'outputs/dump/graph_{count}.dump',
            'lammps/dump',
            columns=[
                'Particle Identifier', 'Particle Type',
                'Position.X','Position.Y','Position.Z'
            ]
        )
        p.modifiers.clear()
        return area, volume, count

if __name__ == '__main__':
    generator = AtomicGraphGenerator()
    generator.run()
