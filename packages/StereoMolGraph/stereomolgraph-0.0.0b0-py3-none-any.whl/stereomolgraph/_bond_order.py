#
# highly inspired in partially copied from https://github.com/jensengroup/xyz2mol
# Jensen Group
# Jan H. Jensen Research Group of the Department of Chemistry,
# University of Copenhagen
# License: MIT License (see at end of file)
#
# This code is based on the work of DOI: 10.1002/bkcs.10334
# Yeonjoon Kim and Woo Youn Kim
# "Universal Structure Conversion Method for Organic Molecules:
# From Atomic Connectivity to Three-Dimensional Geometry"
# Bull. Korean Chem. Soc.
# 2015, Vol. 36, 1769-1777
from __future__ import annotations

import copy
import itertools
import warnings
from collections import defaultdict
from collections.abc import Sequence

import numpy as np

from stereomolgraph import Element

#import networkx as nx

atomic_valence:dict[int, list[int]] = defaultdict(lambda: [0,1,2,3,4,5,6,7,8])
atomic_valence[1] = [1]
atomic_valence[5] = [3, 4]
atomic_valence[6] = [4]
atomic_valence[7] = [3, 4]
atomic_valence[8] = [2, 1, 3]
atomic_valence[9] = [1]
atomic_valence[14] = [4]
atomic_valence[15] = [5, 3]  # [5,4,3]
atomic_valence[16] = [6, 3, 2]  # [6,4,2]
atomic_valence[17] = [1]
atomic_valence[32] = [4]
atomic_valence[35] = [1]
atomic_valence[53] = [1]

atomic_valence_electrons = {}
atomic_valence_electrons[1] = 1
atomic_valence_electrons[5] = 3
atomic_valence_electrons[6] = 4
atomic_valence_electrons[7] = 5
atomic_valence_electrons[8] = 6
atomic_valence_electrons[9] = 7
atomic_valence_electrons[14] = 4
atomic_valence_electrons[15] = 5
atomic_valence_electrons[16] = 6
atomic_valence_electrons[17] = 7
atomic_valence_electrons[32] = 4
atomic_valence_electrons[35] = 7
atomic_valence_electrons[53] = 7


def connectivity2bond_orders(
    atom_types: Sequence[Element],
    connectivity_matrix: np.typing.ArrayLike,
    allow_charged_fragments=False,
    charge: int = 0,
) -> np.ndarray:
    """
    Calculates Bond orders from atom connectivity.
    Bond orders can be assigned automatically using the algorithm from
    DOI: 10.1002/bkcs.10334
    Yeonjoon Kim and Woo Youn Kim
    "Universal Structure Conversion Method for Organic Molecules:
    From Atomic Connectivity to Three-Dimensional Geometry"
    Bull. Korean Chem. Soc.
    2015, Vol. 36, 1769-1777
    :param atom_types: list of atom types
    :param connectivity_matrix: Adjacency matrix. Has to be symmetric square
                                matrix. Behaveour is not defined for values
                                other than 1 and 0.
    :param allow_charged_fragments: If false radicals are formed and if True
                                ions are preferred, defaults to False.
                                bond_orders has to be set to true to be able to
                                assign charges to fragments.
    :param charge: charge of the whole molecule, defaults to 0, only possible
                    if allow_charged_fragments is True, because only rdkit
                    allows only atoms to be charged and the charge of the
                    molecule is calculated based on them.
    :return: bond orders matrix
    """

    atom_types_strings = [elem.atomic_nr for elem in atom_types]

        # convert AC matrix to bond order (BO) matrix
    BO_matrix, atomic_valence_electrons = _AC2BO(
            np.array(connectivity_matrix),
            atom_types_strings,
            charge,
            allow_charged_fragments=allow_charged_fragments,
            use_graph=False,
        )

    return BO_matrix # radical_matrix, charge_matrix


def _get_UA(maxValence_list, valence_list):
    UA = []
    DU = []
    for i, (maxValence, valence) in enumerate(
        zip(maxValence_list, valence_list)
    ):
        if not maxValence - valence > 0:
            continue
        UA.append(i)
        DU.append(maxValence - valence)
    return UA, DU


def _get_BO(AC, UA, DU, valences, UA_pairs, use_graph=False):
    BO = AC.copy()
    DU_save = []

    while DU_save != DU:
        for i, j in UA_pairs:
            BO[i, j] += 1
            BO[j, i] += 1

        BO_valence = list(BO.sum(axis=1))
        DU_save = copy.copy(DU)
        UA, DU = _get_UA(valences, BO_valence)
        UA_pairs = _get_UA_pairs(UA, AC, use_graph=use_graph)[0]

    return BO


def _valences_not_too_large(BO, valences):
    """ """
    number_of_bonds_list = BO.sum(axis=1)
    for valence, number_of_bonds in zip(valences, number_of_bonds_list):
        if number_of_bonds > valence:
            return False

    return True


def _charge_is_OK(
    BO,
    AC,
    charge,
    DU,
    atomic_valence_electrons,
    atoms,
    valences,
    allow_charged_fragments=True,
):
    # total charge
    Q = 0

    # charge fragment list
    q_list = []

    if allow_charged_fragments:
        BO_valences = list(BO.sum(axis=1))
        for i, atom in enumerate(atoms):
            q = _get_atomic_charge(
                atom, atomic_valence_electrons[atom], BO_valences[i]
            )
            Q += q
            if atom == 6:
                number_of_single_bonds_to_C = list(BO[i, :]).count(1)
                if number_of_single_bonds_to_C == 2 and BO_valences[i] == 2:
                    Q += 1
                    q = 2
                if number_of_single_bonds_to_C == 3 and Q + 1 < charge:
                    Q += 2
                    q = 1

            if q != 0:
                q_list.append(q)

    return charge == Q


def _BO_is_OK(
    BO,
    AC,
    charge,
    DU,
    atomic_valence_electrons,
    atoms,
    valences,
    allow_charged_fragments=True,
):
    """
    Sanity of bond-orders

    args:
        BO -
        AC -
        charge -
        DU -


    optional
        allow_charges_fragments -


    returns:
        boolean - true of molecule is OK, false if not
    """

    if not _valences_not_too_large(BO, valences):
        return False

    check_sum = (BO - AC).sum() == sum(DU)
    check_charge = _charge_is_OK(
        BO,
        AC,
        charge,
        DU,
        atomic_valence_electrons,
        atoms,
        valences,
        allow_charged_fragments,
    )

    if check_charge and check_sum:
        return True

    return False


def _get_atomic_charge(atom, atomic_valence_electrons, BO_valence):
    """ """

    if atom == 1:
        charge = 1 - BO_valence
    elif atom == 5:
        charge = 3 - BO_valence
    elif atom == 15 and BO_valence == 5:
        charge = 0
    elif atom == 16 and BO_valence == 6:
        charge = 0
    else:
        charge = atomic_valence_electrons - 8 + BO_valence

    return charge


def _set_atomic_charges(
    mol, atoms, atomic_valence_electrons, BO_valences, BO_matrix, mol_charge
):
    """ """
    q = 0
    for i, atom in enumerate(atoms):
        a = mol.GetAtomWithIdx(i)
        charge = _get_atomic_charge(
            atom, atomic_valence_electrons[atom], BO_valences[i]
        )
        q += charge
        if atom == 6:
            number_of_single_bonds_to_C = list(BO_matrix[i, :]).count(1)
            if number_of_single_bonds_to_C == 2 and BO_valences[i] == 2:
                q += 1
                charge = 0
            if number_of_single_bonds_to_C == 3 and q + 1 < mol_charge:
                q += 2
                charge = 1

        if abs(charge) > 0:
            a.SetFormalCharge(int(charge))

    # mol = clean_charges(mol)

    return mol


def _set_atomic_radicals(mol, atoms, atomic_valence_electrons, BO_valences):
    """

    The number of radical electrons = absolute atomic charge

    """
    for i, atom in enumerate(atoms):
        a = mol.GetAtomWithIdx(i)
        charge = _get_atomic_charge(
            atom, atomic_valence_electrons[atom], BO_valences[i]
        )

        if abs(charge) > 0:
            a.SetNumRadicalElectrons(abs(int(charge)))

    return mol


def _get_bonds(UA, AC):
    """ """
    bonds = []

    for k, i in enumerate(UA):
        for j in UA[k + 1 :]:
            if AC[i, j] == 1:
                bonds.append(tuple(sorted([i, j])))

    return bonds


def _get_UA_pairs(UA, AC, use_graph=False):
    """ """

    bonds = _get_bonds(UA, AC)

    if len(bonds) == 0:
        return [()]

    #if use_graph:
    #    G = nx.Graph()
    #    G.add_edges_from(bonds)
    #    UA_pairs = [list(nx.max_weight_matching(G))]
    #    return UA_pairs

    max_atoms_in_combo = 0
    UA_pairs = [()]
    for combo in list(itertools.combinations(bonds, int(len(UA) / 2))):
        flat_list = [item for sublist in combo for item in sublist]
        atoms_in_combo = len(set(flat_list))
        if atoms_in_combo > max_atoms_in_combo:
            max_atoms_in_combo = atoms_in_combo
            UA_pairs = [combo]

        elif atoms_in_combo == max_atoms_in_combo:
            UA_pairs.append(combo)

    return UA_pairs


def _AC2BO(AC, atoms, charge, allow_charged_fragments=True, use_graph=False):
    """

    implemenation of algorithm shown in Figure 2

    UA: unsaturated atoms

    DU: degree of unsaturation (u matrix in Figure)

    best_BO: Bcurr in Figure

    """

    global atomic_valence
    global atomic_valence_electrons

    # make a list of valences, e.g. for CO: [[4],[2,1]]
    valences_list_of_lists = []
    AC_valence = list(AC.sum(axis=1))

    for i, (atomicNum, valence) in enumerate(zip(atoms, AC_valence)):
        # valence can't be smaller than number of neighbourgs
        possible_valence = [
            x for x in atomic_valence[atomicNum] if x >= valence
        ]
        if not possible_valence:
            warnings.warn(
                f"Valence of atom {i},is {valence}, which bigger than allowed "
                f"max {max(atomic_valence[atomicNum])}. Continuing"
            )
            # sys.exit()
        valences_list_of_lists.append(possible_valence)

    # convert [[4],[2,1]] to [[4,2],[4,1]]
    valences_list = itertools.product(*valences_list_of_lists)

    best_BO = AC.copy()

    for valences in valences_list:
        UA, DU_from_AC = _get_UA(valences, AC_valence)

        check_len = len(UA) == 0
        if check_len:
            check_bo = _BO_is_OK(
                AC,
                AC,
                charge,
                DU_from_AC,
                atomic_valence_electrons,
                atoms,
                valences,
                allow_charged_fragments=allow_charged_fragments,
            )
        else:
            check_bo = None

        if check_len and check_bo:
            return AC, atomic_valence_electrons

        UA_pairs_list = _get_UA_pairs(UA, AC, use_graph=use_graph)
        for UA_pairs in UA_pairs_list:
            BO = _get_BO(
                AC, UA, DU_from_AC, valences, UA_pairs, use_graph=use_graph
            )
            status = _BO_is_OK(
                BO,
                AC,
                charge,
                DU_from_AC,
                atomic_valence_electrons,
                atoms,
                valences,
                allow_charged_fragments=allow_charged_fragments,
            )
            charge_OK = _charge_is_OK(
                BO,
                AC,
                charge,
                DU_from_AC,
                atomic_valence_electrons,
                atoms,
                valences,
                allow_charged_fragments=allow_charged_fragments,
            )

            if status:
                return BO, atomic_valence_electrons
            elif (
                BO.sum() >= best_BO.sum()
                and _valences_not_too_large(BO, valences)
                and charge_OK
            ):
                best_BO = BO.copy()

    return best_BO, atomic_valence_electrons



# MIT License

# Copyright (c) 2018 Jensen Group

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
