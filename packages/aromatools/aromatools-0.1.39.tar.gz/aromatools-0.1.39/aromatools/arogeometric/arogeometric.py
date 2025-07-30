#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import math
import glob
import google.colab
import numpy as np
import pandas as pd
import networkx as nx
import plotly.io as pio
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from art import text2art
from ase.data import covalent_radii, atomic_numbers, chemical_symbols
from IPython.display import display
from google.colab import output

# Diccionarios de parámetros
R_opt = {'HOMA': {'CC': 1.388, 'CN': 1.334, 'NN': 1.309, 'CO': 1.265},
         'HOMER': {'CC': 1.437, 'CN': 1.39, 'NN': 1.375, 'CO': 1.379},
         'HOMAC': {'CC': 1.392, 'CN': 1.333, 'NN': 1.318, 'CO': 1.315, 'SiSi': 2.163, 'CSi': 1.752}}

alpha = {'HOMA': {'CC': 257.7, 'CN': 93.52, 'NN': 130.33, 'CO': 157.38},
         'HOMER': {'CC': 950.74, 'CN': 506.43, 'NN': 187.36, 'CO': 164.96},
         'HOMAC': {'CC': 153.37, 'CN': 111.83, 'NN': 98.99, 'CO': 335.16, 'SiSi': 325.6, 'CSi': 115.41}}

def detect_environment():
    try:
        return "colab"
    except ImportError:
        try:
            shell = get_ipython().__class__.__name__
            if shell == 'ZMQInteractiveShell':
                return "jupyter"
        except NameError:
            pass
    return "other"

env = detect_environment()

if env == "colab":
    pio.renderers.default = "colab"
elif env == "jupyter":
    pio.renderers.default = "notebook_connected"
else:
    pio.renderers.default = "browser"

def arogeometric():
    text_ascci = text2art("AROGEOMETRIC 1.0", font='old banner')
    print("\n" + text_ascci)
    welcome = """
    Welcome to AroGeometric — Geometric Aromaticity Index Calculator
    Authors: Fernando Martinez-Villarino and Gabriel Merino
    Cinvestav Mérida, 2024

    This tool allows you to compute geometric-based aromaticity indices for a set of molecules in .xyz files.
    You can choose among three different indices:

    • HOMA (HOMA93): 0 = non-aromatic, 1 = aromatic.
    • HOMAc:       -1 = antiaromatic, 0 = non-aromatic, 1 = aromatic.
    • HOMER:       Excited-state version of HOMAc.

    Use as: aroegeometric.py [HOMA|HOMER|HOMAc]
    """
    print(welcome)

def parse_xyz(file_xyz):
    with open(file_xyz, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    natoms = int(lines[0])
    atoms = []
    for i in range(2, 2 + natoms):
        parts = lines[i].split()
        if len(parts) < 4:
            continue
        symbol = parts[0].capitalize()
        if symbol == 'H':
            continue
        try:
            x, y, z = map(float, parts[1:4])
            atoms.append((symbol, x, y, z))
        except ValueError:
            print(f"Error: Invalid coordinates at line {i+1}.")
            sys.exit(1)
    return atoms

def build_graph(atoms, tol=0.15):
    G = nx.Graph()
    for idx, (sym, _, _, _) in enumerate(atoms):
        G.add_node(idx, element=sym)
    for i in range(len(atoms)):
        sym1, x1, y1, z1 = atoms[i]
        r1 = covalent_radii[atomic_numbers[sym1]]
        for j in range(i + 1, len(atoms)):
            sym2, x2, y2, z2 = atoms[j]
            r2 = covalent_radii[atomic_numbers[sym2]]
            dist = math.sqrt((x1 - x2)**2 + (y1 - y2)**2 + (z1 - z2)**2)
            if dist <= r1 + r2 + tol:
                bond_type = ''.join(sorted(sym1 + sym2))
                G.add_edge(i, j, length=dist, bond_type=bond_type)
    return G

def compute_index(G, atoms, index_type, filename, show_banner=True, verbose=True):

    if show_banner:
        ascci_title = text2art("AroGeometric", font='big')
        print()
        print(f"AroGeometric 2025, output file — {index_type}")
        print(ascci_title)
        print("Theoretical and Computational Chemistry Group")
        print("Centro de Investigacion y de Estudios Avanzados — Unidad Merida")
        print("Merida, Yucatan, Mexico\n")

        print("---------------------------------Cite this work as---------------------------------")
        print("AroGeometric 2025, Fernando Martinez-Villarino and G. Merino, Cinvestav, Merida, YUC, Mexico, 2025")
        print("-----------------------------------------------------------------------------------\n")

        print("Copyright (C) 1943, Cinvestav. All Rights Reserved")

    print(f"\nProcessing: {filename}")
    rings = nx.minimum_cycle_basis(G)
    print(f"Number of rings detected: {len(rings)}")
    ring_indices = []
    all_results = []

    for idx, ring in enumerate(rings, start=1):
        ring_atoms = ring + [ring[0]]
        ring_bonds = []

        for i in range(len(ring)):
            a1, a2 = ring_atoms[i], ring_atoms[i+1]
            if G.has_edge(a1, a2):
                data = G[a1][a2]
                bond_type = data['bond_type']
                dist = data['length']

                if bond_type not in R_opt[index_type]:
                    continue

                print(f"Ring {idx}: bond {bond_type} with distance {dist:.4f} Å")

                if bond_type == 'SiSi':
                    print(f"Ring {idx} contains Si-Si bond: distance = {dist:.4f} Å")

                Ropt = R_opt[index_type][bond_type]
                a = alpha[index_type][bond_type]
                ring_bonds.append((bond_type, dist, Ropt, a))

        if not ring_bonds:
            print(f"Ring {idx}: No valid bonds for index {index_type}.")
            continue

        n = len(ring_bonds)
        total = sum(a * (dist - Ropt)**2 for _, dist, Ropt, a in ring_bonds)
        index_value = 1.0 - (1.0 / n) * total
        ring_indices.append((idx, index_value))

        if verbose:
            print(f"{index_type.upper()} index for ring {idx}: {index_value:.4f}")

        all_results.append({
            "Ring": f"Ring {idx}",
            "Bonds": [round(b[1], 4) for b in ring_bonds],
            "Index": round(index_value, 4)
            })

    df = pd.DataFrame(all_results, columns=["Ring", "Bonds", "Index"])
    if not verbose:
        try:
            display(df)
        except ImportError:
            print(df)

    return rings, ring_indices, df

def draw_molecular_graph(G, atoms, rings, project_name, ring_indices):
    index_lookup = dict(ring_indices)
    pos = {}  # posiciones aproximadas basadas en coordenadas 2D proyectadas
    for idx, (_, x, y, z) in enumerate(atoms):
        pos[idx] = (x, y)  # solo tomamos x-y para un gráfico 2D

    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=False, node_size=300, node_color='lightblue', edge_color='gray')
    
    labels = {i: atoms[i][0] for i in range(len(atoms))}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=8)

    for i, ring in enumerate(rings, start=1):
        x_coords = [pos[a][0] for a in ring]
        y_coords = [pos[a][1] for a in ring]
        centroid = (sum(x_coords) / len(ring), sum(y_coords) / len(ring))
        index_value = index_lookup.get(i, None)
        if index_value is not None:
            label = f"{index_value:.3f}"
            plt.text(centroid[0], centroid[1], label, fontsize=10, fontweight='bold', color='red')

    # filename = f"molgraph_{project_name}.png"
    plt.title(f"Molecular Graph: {project_name}")
    plt.axis('off')
    # plt.savefig(filename)
    plt.close()

def get_3Dgraph(G, atoms, rings, ring_indices, title="Molecular Graph 3D"):

    node_xyz = [(x, y, z) for _, x, y, z in atoms]
    edges = []
    for u, v in G.edges():
        edges.append((u, v))

    # Coordenadas para enlaces
    x_edges = []
    y_edges = []
    z_edges = []
    for u, v in edges:
        x_edges += [node_xyz[u][0], node_xyz[v][0], None]
        y_edges += [node_xyz[u][1], node_xyz[v][1], None]
        z_edges += [node_xyz[u][2], node_xyz[v][2], None]

    # Coordenadas para nodos
    x_nodes = [x for x, y, z in node_xyz]
    y_nodes = [y for x, y, z in node_xyz]
    z_nodes = [z for x, y, z in node_xyz]
    symbols = [atoms[i][0] for i in range(len(atoms))]

    node_trace = go.Scatter3d(
        x=x_nodes,
        y=y_nodes,
        z=z_nodes,
        mode='markers+text',
        text=symbols,
        textposition='top center',
        marker=dict(size=5, color='lightblue'),
        name="Atoms"
    )

    edge_trace = go.Scatter3d(
        x=x_edges,
        y=y_edges,
        z=z_edges,
        mode='lines',
        line=dict(width=2, color='gray'),
        name="Bonds"
    )

    x_c_list = []
    y_c_list = []
    z_c_list = []
    text_list = []

    for i, ring in enumerate(rings, start=1):
        coords = [node_xyz[a] for a in ring]
        x_c = sum(coord[0] for coord in coords) / len(coords)
        y_c = sum(coord[1] for coord in coords) / len(coords)
        z_c = sum(coord[2] for coord in coords) / len(coords)
        value = ring_indices.get(i, None)
        if value is not None:
            x_c_list.append(x_c)
            y_c_list.append(y_c)
            z_c_list.append(z_c)
            text_list.append(f"{value:.3f}")

    centroid_trace = go.Scatter3d(
        x=x_c_list,
        y=y_c_list,
        z=z_c_list,
        mode='text',
        text=text_list,
        textfont=dict(size=10, color='red'),
        textposition='middle center',
        name="Indices"

    )

    fig = go.Figure(data=[edge_trace, node_trace, centroid_trace])
    fig.update_layout(
        title=title,
        margin=dict(l=0, r=0, b=0, t=30),
        showlegend=False,
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False)
        )
    )
    return fig

def atoms_from_ase(ase_atoms):
    data = [(atom.symbol, *atom.position) for atom in ase_atoms]
    df = pd.DataFrame(data, columns=["Element", "X", "Y", "Z"])
    return df

def extract_atoms_from_output(fileout):
    atoms = []
    with open(fileout, 'r') as f:
        lines = f.readlines()

    if any("Entering Gaussian System" in line for line in lines):
        for i in range(len(lines) - 5):
            if "Standard orientation" in lines[i]:
                atoms = []
                j = i + 5
                while not "---" in lines[j]:
                    parts = lines[j].split()
                    atomic_number = int(parts[1])
                    symbol = chemical_symbols[atomic_number]
                    x, y, z = map(float, parts[3:6])
                    atoms.append((symbol, x, y, z))
                    j += 1

    elif any("O   R   C   A" in line for line in lines):
        atoms = []
        start = False
        for line in lines:
            if "CARTESIAN COORDINATES (ANGSTROEM)" in line:
                atoms = []
                start = True
                continue
            if start:
                if "---" in line or not line.strip():
                    start = False
                    continue
                parts = line.strip().split()
                if len(parts) == 4:
                    symbol = parts[0]
                    x, y, z = map(float, parts[1:])
                    atoms.append((symbol, x, y, z))

    df = pd.DataFrame(atoms, columns=["Element", "X", "Y", "Z"])
    return df

def main():
    if len(sys.argv) != 2:
        arogeometric()
        sys.exit(1)

    index_type = sys.argv[1].upper()
    if index_type not in R_opt:
        print("Error: Invalid index type. Choose from HOMA, HOMER, HOMAC.")
        sys.exit(1)

    xyz_files = sorted(glob.glob("*.xyz"))
    if not xyz_files:
        print("No .xyz files found in the current directory.")
        sys.exit(1)

    ascci_title = text2art("AroGeometric", font='big')

    print()
    print(f"AroGeometric 2025, output file — {index_type}")
    print(ascci_title)
    print("Theoretical and Computational Chemistry Group")
    print("Centro de Investigacion y de Estudios Avanzados — Unidad Merida")
    print("Merida, Yucatan, Mexico\n")

    print("---------------------------------Cite this work as---------------------------------")
    print("AroGeometric 2025, Fernando Martinez-Villarino and G. Merino, Cinvestav, Merida, YUC, Mexico, 2025")
    print("-----------------------------------------------------------------------------------\n")

    print("Copyright (C) 1943, Cinvestav. All Rights Reserved")

    print(f"Total XYZ files found: {len(xyz_files)}\n")

    for file_xyz in xyz_files:
        atoms = parse_xyz(file_xyz)
        G = build_graph(atoms)
        rings, ring_indices, df_index = compute_index(G, atoms, index_type, file_xyz)
        
        base_name = os.path.splitext(os.path.basename(file_xyz))[0]
        draw_molecular_graph(G, atoms, rings, base_name, ring_indices)

        fig = get_3Dgraph(G, atoms, rings, dict(ring_indices))

        try:
            display(fig)
        except:
            fig.show()

    print("\n")
    print("************************************ AroGeometric terminated normally! ************************************\n")

