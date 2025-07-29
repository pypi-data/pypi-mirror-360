"""
---generate_molecule.py---
Generate 2D graph molecule in ACE-Reaction format from xyz files or SMILES
"""

from __future__ import annotations


def locate_molecule(ace_molecule, coordinate_list):
    """Locates atoms according to coordinate_list. Note: Atom ordering matters.
    Args:
        |  ace_molecule (<class 'Molecule'>): class instance of Molecule
        |  coordinate_list (list of list (x,y,z)): list of 3d coordinates, where each x,y,z are float type
    Returns:
        |  None: Directly modifies the geometry of the given molecule
    """
    atom_list = ace_molecule.atom_list
    for i in range(len(atom_list)):
        atom = atom_list[i]
        atom.set_coordinate(coordinate_list[i])


def translate_molecule(ace_molecule, vector):
    atom_list = ace_molecule.atom_list
    for atom in atom_list:
        translate_atom(atom, vector)


def locate_atom(atom, coordinate):
    """Locates a single atom to input 'coordinate'
    Args:
        |  atom (<class 'Atom'>): class instance of Atom
        |  coordinate (list of float): coordinate in form of [x,y,z]
    Returns:
        |  No return, it directly locates the atom to the given coordinate
    """
    atom.x = coordinate[0]
    atom.y = coordinate[1]
    atom.z = coordinate[2]


def translate_atom(atom, vector):
    atom.x += vector[0]
    atom.y += vector[1]
    atom.z += vector[2]
