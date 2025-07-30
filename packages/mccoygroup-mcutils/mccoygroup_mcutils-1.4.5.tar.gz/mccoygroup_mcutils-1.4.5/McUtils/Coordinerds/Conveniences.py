"""
Convenience functions that are inefficient, but are maybe a bit easier to work with?
"""

from .. import Iterators as itut
from .. import Numputils as nput
from .. import Devutils as dev

import itertools
from collections import namedtuple
import numpy as np

from .CoordinateSystems import *

__all__ = [
    "cartesian_to_zmatrix",
    "zmatrix_to_cartesian",
    "zmatrix_unit_convert",
    "zmatrix_indices",
    "canonicalize_internal",
    "num_zmatrix_coords",
    "zmatrix_embedding_coords",
    "set_zmatrix_embedding",
    "enumerate_zmatrices",
    "extract_zmatrix_internals",
    "parse_zmatrix_string",
    "format_zmatrix_string",
    "validate_zmatrix",
    "chain_zmatrix",
    "attached_zmatrix_fragment",
    "functionalized_zmatrix",
    "reindex_zmatrix",
    "is_coordinate_list_like",
    "is_valid_coordinate",
    "get_stretch_angles",
    "get_angle_dihedrals",
    "get_angle_stretches",
    "get_dihedral_stretches",
    "get_stretch_angle_dihedrals",
    "get_stretch_coordinate_system",
    "get_coordinate_label"
]

zm_type = namedtuple("zms", ["coords", "ordering"])
def cartesian_to_zmatrix(coords, ordering=None, use_rad=True):
    """
    Converts Cartesians to Z-Matrix coords and returns the underlying arrays

    :param coords: input Cartesians
    :type coords: np.ndarray
    :param ordering: the Z-matrix ordering as a list of lists
    :type ordering:
    :return: Z-matrix coords
    :rtype: Iterable[np.ndarray | list]
    """

    zms = CoordinateSet(coords, system=CartesianCoordinates3D).convert(ZMatrixCoordinates, ordering=ordering, use_rad=use_rad)
    return zm_type(np.asarray(zms), zms.converter_options['ordering'])

def zmatrix_to_cartesian(coords, ordering=None, origins=None, axes=None, use_rad=True):
    """
    Converts Z-maztrix coords to Cartesians

    :param coords:
    :type coords: np.ndarray
    :param ordering:
    :type ordering:
    :param origins:
    :type origins:
    :param axes:
    :type axes:
    :param use_rad:
    :type use_rad:
    :return:
    :rtype:
    """
    carts = CoordinateSet(coords, ZMatrixCoordinates).convert(CartesianCoordinates3D,
                                                            ordering=ordering, origins=origins, axes=axes, use_rad=use_rad)
    return np.asarray(carts)

def zmatrix_unit_convert(zmat, distance_conversion, angle_conversion=None, rad2deg=False, deg2rad=False):
    zm2 = np.asanyarray(zmat)
    if zm2 is zmat: zm2 = zm2.copy()

    zm2[..., :, 0] *= distance_conversion
    if angle_conversion is None:
        if deg2rad:
            zm2[..., :, 1] = np.deg2rad(zm2[..., :, 1])
            zm2[..., :, 2] = np.deg2rad(zm2[..., :, 2])
        elif rad2deg:
            zm2[..., :, 1] = np.rad2deg(zm2[..., :, 1])
            zm2[..., :, 2] = np.rad2deg(zm2[..., :, 2])
    else:
        zm2[..., :, 1] *= angle_conversion
        zm2[..., :, 2] *= angle_conversion

    return zm2



def canonicalize_internal(coord):
    dupes = len(np.unique(coord)) < len(coord)
    if dupes: return None
    if len(coord) == 2:
        i, j = coord
        if i > j:
            coord = (j, i)
    elif len(coord) == 3:
        i, j, k = coord
        if i > k:
            coord = (k, j, i)
    elif len(coord) == 4:
        i, j, k, l = coord
        if i > l:
            coord = (l, k, j, i)
    elif coord[0] > coord[-1]:
        coord = tuple(reversed(coord))
    return coord

def zmatrix_indices(zmat, coords):
    base_coords = [canonicalize_internal(c) for c in extract_zmatrix_internals(zmat)]
    return [
        base_coords.index(canonicalize_internal(c))
        for c in coords
    ]

emb_pos_map = [
    (0,1),
    (0,2),
    (0,3),
    None,
    (1,2),
    (1,3),
    None,
    None,
    (2,3)
]
def zmatrix_embedding_coords(zmat_or_num_atoms, array_inds=False):
    if array_inds:
        base_inds = zmatrix_embedding_coords(zmat_or_num_atoms, array_inds=False)
        return [emb_pos_map[i] for i in base_inds]
    else:
        if not nput.is_int(zmat_or_num_atoms):
            zmat_or_num_atoms = len(zmat_or_num_atoms) + (1 if len(zmat_or_num_atoms[0]) == 3 else 0)
        n: int = zmat_or_num_atoms

        if n < 1:
            return []
        elif n == 1:
            return [0, 1, 2]
        elif n == 2:
            return [0, 1, 2, 4, 5]
        else:
            return [0, 1, 2, 4, 5, 8]

def num_zmatrix_coords(zmat_or_num_atoms, strip_embedding=True):
    if not nput.is_int(zmat_or_num_atoms):
        zmat_or_num_atoms = len(zmat_or_num_atoms) + (1 if len(zmat_or_num_atoms[0]) == 3 else 0)
    n: int = zmat_or_num_atoms

    return (n*3) - (
        0
            if not strip_embedding else
        len(zmatrix_embedding_coords(n))
    )

def _zmatrix_iterate(coords, natoms=None,
                     include_origins=False,
                     canonicalize=True,
                     deduplicate=True,
                     allow_completions=False
                     ):
    # TODO: this fixes an atom ordering, to change that up we'd need to permute the initial coords...
    if canonicalize:
        coords = [tuple(reversed(canonicalize_internal(s))) for s in coords]

    if deduplicate:
        dupes = set()
        _ = []
        for c in coords:
            if c in dupes: continue
            _.append(c)
            dupes.add(c)
        coords = _

    if include_origins:
        if (1, 0) not in coords:
            coords = [(1, 0)] + coords
        if (2, 1) not in coords and (2, 0) not in coords:
            if (2, 1, 0) in coords:
                coords = [(2, 1)] + coords
            else:
                coords = [(2, 0)] + coords
        if (2, 0) in coords and (2, 0, 1) not in coords: # can this happen?
            coords.append((2,1,0))

    if natoms is None:
        all_atoms = {i for s in coords for i in s}
        natoms = len(all_atoms)

    dihedrals = [k for k in coords if len(k) == 4]
    all_dihedrals = [
        (i, j, k, l)
        for (i, j, k, l) in dihedrals
        if i > j and i > k and i > l
    ]

    # need to iterate over all N-2 choices of dihedrals (in principle)...
    # should first reduce over consistent sets
    if not allow_completions:
        dihedrals = [
            (i,j,k,l) for i,j,k,l in dihedrals
            if (i,j) in coords and (i,j,k) in coords
            # if (
            #         any(x in coords or tuple(reversed(x)) in coords for x in [(i,j), (l,k)])
            #         and any(x in coords or tuple(reversed(x)) in coords for x in [(i,j,k), (l,k,j)])
            # )
        ]

    embedding = [
        x for x in [(2, 0, 1), (2, 1, 0)]
        if x in coords
    ]

    # we also will want to sample from dihedrals that provide individual atoms
    atom_diheds = [[] for _ in range(natoms)]
    for n,(i,j,k,l) in enumerate(dihedrals):
        atom_diheds[i].append((i,j,k,l))

    # completions = []
    # if allow_completions:
    #     for d in all_dihedrals:
    #         if d in dihedrals: continue
    #         completions.extend([d[:2], d[:3]])
    #
    #     c_set = set()
    #     for d in dihedrals:
    #         c_set.add(d[:2])
    #         c_set.add(d[:3])
    #     coord_pairs = [
    #         (c[:2],c[:3])
    #         for
    #     ]
    #     for d in all_dihedrals:
    #         if d in dihedrals: continue
    #         completions.extend([d[:2], d[:3]])

    for dihed_choice in itertools.product(embedding, *atom_diheds[3:]):
        emb, dis = dihed_choice[0], dihed_choice[1:]
        yield (
            (0, -1, -1, -1),
            (1, 0, -1, -1),
            emb + (-1,)
        ) + dis

def enumerate_zmatrices(coords, natoms=None,
                        allow_permutation=True,
                        include_origins=False,
                        canonicalize=True,
                        deduplicate=True,
                        preorder_atoms=True,
                        allow_completions=False
                        ):
    if canonicalize:
        coords = [tuple(reversed(canonicalize_internal(s))) for s in coords]

    if deduplicate:
        dupes = set()
        _ = []
        for c in coords:
            if c in dupes: continue
            _.append(c)
            dupes.add(c)
        coords = _

    if natoms is None:
        all_atoms = {i for s in coords for i in s}
        natoms = len(all_atoms)

    if preorder_atoms:
        counts = itut.counts(itertools.chain(*coords))
        max_order = list(sorted(range(natoms), key=lambda k:-counts[k]))
    else:
        max_order = np.arange(natoms)

    for atoms in (
            itertools.permutations(max_order)
                if allow_permutation else
            [max_order]
    ):
        atom_perm = np.argsort(atoms)
        perm_coords = [
            tuple(reversed(canonicalize_internal([atom_perm[c] for c in crd])))
            for crd in coords
        ]
        for zm in _zmatrix_iterate(perm_coords,
                                   natoms=natoms,
                                   include_origins=include_origins,
                                   canonicalize=False,
                                   deduplicate=False,
                                   allow_completions=allow_completions
                                   ):
            yield [
                [atoms[c] if c >= 0 else c for c in z]
                for z in zm
            ]

def extract_zmatrix_internals(zmat, strip_embedding=True):
    specs = []
    for n,row in enumerate(zmat):
        if strip_embedding and n == 0: continue
        specs.append(tuple(row[:2]))
        if strip_embedding and n == 1: continue
        specs.append(tuple(row[:3]))
        if strip_embedding and n == 2: continue
        specs.append(tuple(row[:4]))
    return specs

def parse_zmatrix_string(zmat, units="Angstroms", in_radians=False,):
    from ..Data import AtomData, UnitsData
    # we have to reparse the Gaussian Z-matrix...

    possible_atoms = {d["Symbol"][:2] for d in AtomData.data.values()}

    atoms = []
    ordering = []
    coords = []
    # vars = {}

    if "Variables:" in zmat:
        zmat, vars_block = zmat.split("Variables:", 1)
    else:
        zmat = zmat.split("\n\n", 1)
        if len(zmat) == 1:
            zmat = zmat[0]
            vars_block = ""
        else:
            zmat, vars_block = zmat
    bits = [b.strip() for b in zmat.split() if len(b.strip()) > 0]

    coord = []
    ord = []
    complete = False
    last_complete = -1
    last_idx = len(bits) - 1
    for i, b in enumerate(bits):
        d = (i - last_complete) - 1
        m = d % 2
        if d == 0:
            atoms.append(b)
        elif m == 1:
            b = int(b)
            if b > 0: b = b - 1
            ord.append(b)
        elif m == 0:
            coord.append(b)

        terminal = (
                i == last_idx
                or i in {0, 3, 8}
                or (i > 8 and (i - 9) % 7 == 6)
        )
        # atom_q = bits[i + 1][:2] in possible_atoms
        if terminal:
            last_complete = i
            ord = ord + [-1] * (4 - len(ord))
            coord = coord + [0] * (3 - len(coord))
            ordering.append(ord)
            coords.append(coord)
            ord = []
            coord = []

    split_pairs = [
        (vb.strip().split("=", 1) if "=" in vb else vb.strip().split())
        for vb in vars_block.split("\n")
    ]
    split_pairs = [s for s in split_pairs if len(s) == 2]

    vars = {k.strip(): float(v) for k, v in split_pairs}
    coords = [
        [vars.get(x, x) for x in c]
        for c in coords
    ]

    ordering = [
        [i] + o
        for i, o in enumerate(ordering)
    ]
    # convert book angles into sensible dihedrals...
    # actually...I think I don't need to do anything for this?
    ordering = np.array(ordering)[:, :4]

    coords = np.array(coords)
    coords[:, 0] *= UnitsData.convert(units, "BohrRadius")
    coords[:, 1] = coords[:, 1] if in_radians else np.deg2rad(coords[:, 1])
    coords[:, 2] = coords[:, 2] if in_radians else np.deg2rad(coords[:, 2])

    return (atoms, ordering, coords)

def format_zmatrix_string(atoms, zmat, ordering=None, units="Angstroms",
                          in_radians=False,
                          float_fmt="{:11.8f}",
                          index_padding=1
                          ):
    from ..Data import UnitsData
    zmat = np.asanyarray(zmat).copy()
    zmat[:, 0] *= UnitsData.convert("BohrRadius", units)
    zmat[:, 1] = zmat[:, 1] if in_radians else np.rad2deg(zmat[:, 1])
    zmat[:, 2] = zmat[:, 2] if in_radians else np.rad2deg(zmat[:, 2])

    if ordering is None:
        if len(zmat) == len(atoms):
            zmat = zmat[1:]
        ordering = [
            [z[0], z[2], z[4]]
            if i > 1 else
            [z[0], z[2], -1]
            if i > 0 else
            [z[0], -1, -1]
            for i, z in enumerate(zmat)
        ]
        zmat = [
            [z[1], z[3], z[5]]
            if i > 1 else
            [z[1], z[3], -1]
            if i > 0 else
            [z[1], -1, -1]
            for i, z in enumerate(zmat)
        ]
    includes_atom_list = len(ordering[0]) == 4
    if not includes_atom_list:
        if len(ordering) < len(atoms):
            ordering = [[-1, -1, -1]] + list(ordering)
        if len(zmat) < len(atoms):
            zmat = [[-1, -1, -1]] + list(zmat)

    zmat = [
        ["", "", ""]
        if i == 0 else
        [z[0], "", ""]
        if i == 1 else
        [z[0], z[1], ""]
        if i == 2 else
        [z[0], z[1], z[2]]
        for i, z in enumerate(zmat)
    ]
    zmat = [
        [
            float_fmt.format(x)
                if not isinstance(x, str) else
            x
            for x in zz
        ]
        for zz in zmat
    ]
    if includes_atom_list:
        ord_list = [o[0] for o in ordering]
        atom_order = np.argsort(ord_list)
        atoms = [atoms[o] for o in ord_list]
        ordering = [
            ["", "", ""]
              if i == 0 else
            [atom_order[z[1]], "", ""]
              if i == 1 else
            [atom_order[z[1]], atom_order[z[2]], ""]
              if i == 2 else
            [atom_order[z[1]], atom_order[z[2]], atom_order[z[3]]]
              for i, z in enumerate(ordering)
        ]
    else:
        ordering = [
            ["", "", ""]
            if i == 0 else
                [z[0], "", ""]
            if i == 1 else
                [z[0], z[1], ""]
            if i == 2 else
                [z[0], z[1], z[2]]
            for i, z in enumerate(ordering)
        ]
    ordering = [
        ["{:.0f}".format(x + index_padding) if not isinstance(x, str) else x for x in zz]
        for zz in ordering
    ]

    max_at_len = max(len(a) for a in atoms)

    nls = [
        max([len(xyz[i]) for xyz in ordering])
        for i in range(3)
    ]
    zls = [
        max([len(xyz[i]) for xyz in zmat])
        for i in range(3)
    ]
    fmt_string = f"{{a:<{max_at_len}}} {{n[0]:>{nls[0]}}} {{r[0]:>{zls[0]}}} {{n[1]:>{nls[1]}}} {{r[1]:>{zls[1]}}} {{n[2]:>{nls[2]}}} {{r[2]:>{zls[2]}}}"
    return "\n".join(
        fmt_string.format(
            a=a,
            n=n,
            r=r
        )
        for a, n, r in zip(atoms, ordering, zmat)
    )

def validate_zmatrix(ordering,
                     allow_reordering=True,
                     ensure_nonnegative=True,
                     # raise_exception=False
                     ):
    proxy_order = np.array([o[0] for o in ordering])
    if allow_reordering:
        order_sorting = np.argsort(proxy_order)
        proxy_order = proxy_order[order_sorting,]
        if ensure_nonnegative and proxy_order[0] < 0:
            return False
        new_order = [
            [
                [order_sorting[i] if i >= 0 else i for i in row]
                for row in ordering
            ]
        ]
        return validate_zmatrix(new_order, allow_reordering=False)
    if ensure_nonnegative and proxy_order[0] < 0:
        # if raise_exception:
        #     raise ValueError("Z-matrix atom spec {} is non-zero")
        return False

    for n,row in enumerate(ordering):
        if (
                any(i > n for i in row)
                or any(i > row[0] for i in row[1:])
        ):
            return False

    return True

def chain_zmatrix(n):
    return [
        list(range(i, i-4, -1))
        for i in range(n)
    ]

def attached_zmatrix_fragment(n, fragment, attachment_points):
    return [
        [attachment_points[-r-1] if r < 0 else n+r for r in row]
        for row in fragment
    ]

def set_zmatrix_embedding(zmat, embedding=None):
    zmat = np.array(zmat)
    if embedding is None:
        embedding = [-1, -2, -3, -1, -2, -1]
    emb_pos = zmatrix_embedding_coords(zmat, array_inds=True)
    for (i,j),v in zip(emb_pos, embedding):
        zmat[..., i,j] = v
    return zmat

def functionalized_zmatrix(
        base_zm,
        attachments:dict,
        single_atoms:list[int]=None # individual components, embedding doesn't matter
):
    if nput.is_numeric(base_zm):
        zm = chain_zmatrix(base_zm)
    else:
        zm = [
            list(x) for x in base_zm
        ]
    for attachment_points, fragment in attachments.items():
        if nput.is_numeric(fragment):
            fragment = chain_zmatrix(fragment)
        zm = zm + attached_zmatrix_fragment(
            len(zm),
            fragment,
            attachment_points
        )
    if single_atoms is not None:
        for atom in single_atoms:
            zm = zm + attached_zmatrix_fragment(
                len(zm),
                [[0, -1, -2, -3]],
                [
                    (atom - i) if i < 0 else i
                    for i in range(atom, atom - 4, -1)
                ]
            )
    return zm

def reindex_zmatrix(zm, perm):
    return [
        [perm[r] if r >= 0 else r for r in row]
        for row in zm
    ]

def is_valid_coordinate(coord):
    return (
        len(coord) > 1 and len(coord) < 5
        and all(nput.is_int(c) for c in coord)
    )

def is_coordinate_list_like(clist):
    return dev.is_list_like(clist) and all(
        is_valid_coordinate(c) for c in clist
    )

def get_stretch_angles(stretches):
    angles = []
    for i,(sa,sb) in enumerate(stretches):
        for sc,sd in stretches[i+1:]:
            if sa == sc:
                if sb == sd: continue
                angles.append((sb, sa, sd))
            elif sa == sd:
                if sb == sc: continue
                angles.append((sb, sa, sc))
            elif sb == sc:
                angles.append((sa, sb, sd))
            elif sb == sd:
                angles.append((sa, sb, sc))
    return angles
def get_stretch_angle_dihedrals(stretches, angles):
    dihedrals = []
    for sa,sb in stretches:
        for ba,bc,bd in angles:
            if sa in (ba,bc,bd) and sb in (ba,bc,bd): continue
            # enumerate for simplicity & avoiding try/except
            if sa == ba:
                dihedrals.append(
                    (sb, ba, bc, bd)
                )
            elif sa == bc:
                dihedrals.append(
                    (ba, sb, bc, bd)
                )
            elif sa == bd:
                dihedrals.append(
                    (ba, bc, bd, sb)
                )
            elif sb == ba:
                dihedrals.append(
                    (sa, ba, bc, bd)
                )
            elif sb == bc:
                dihedrals.append(
                    (ba, sa, bc, bd)
                )
            elif sb == bd:
                dihedrals.append(
                    (ba, bc, bd, sa)
                )
    return dihedrals
def get_angle_stretches(angles):
    return [
        s
        for a,b,c in angles
        for s in [(a, b), (b, c)]
    ]
def get_dihedral_stretches(dihedrals):
    return [
        s
        for a,b,c,d in dihedrals
        for s in [(a, b), (b, c), (c,d)]
    ]
def get_angle_dihedrals(angles):
    dihedrals = []
    for i, (aa, ab, ac) in enumerate(angles):
        for ad, ae, af in angles[i + 1:]:
            if ae == ac:
                if ad == ab:
                    if af == aa: continue
                    dihedrals.append((aa, ab, ac, af))
                elif af == ab:
                    if ad == aa: continue
                    dihedrals.append((aa, ab, ac, ad))
            elif ae == aa:
                if ad == ab:
                    if af == ac: continue
                    dihedrals.append((af, aa, ab, ac))
                elif af == ab:
                    if ad == ac: continue
                    dihedrals.append((ad, aa, ab, ac))
    return dihedrals

def get_stretch_coordinate_system(stretches):
    angles = get_stretch_angles(stretches)
    dihedrals = get_angle_dihedrals(angles)
    return stretches,angles,dihedrals

atom_sort_order = ['C', 'O', 'N', 'H', 'F', 'Cl', 'Br', 'I']
coordinate_label = namedtuple('coordinate_label', ['ring', 'group', 'atoms', 'type'])
def get_coordinate_label(coord, atom_labels, atom_order=None):
    ring_lab = None
    group_lab = None
    # motif_lab = ""
    tag = None
    if atom_order is None:
        atom_order = atom_sort_order
    if not isinstance(atom_order, dict):
        atom_order = {a:i for i,a in enumerate(atom_order)}

    if isinstance(coord, dict):
        coord, tag = next(iter(coord.items()))
    if len(coord) == 2:
        if tag is None:
            tag = "stretch"

        a,b = coord
        atom_1 = atom_labels[a]
        atom_2 = atom_labels[b]
        r1 = atom_1.ring
        r2 = atom_2.ring
        if r1 is not None:
            if r2 is None or r1 == r2:
                ring_lab = r1
        elif r2 is not None:
            if r1 is None:
                ring_lab = r2

        g1 = atom_1.group
        g2 = atom_2.group
        if g1 is not None:
            if g2 is None or g1 == g2:
                group_lab = g1
        elif g2 is not None:
            if g1 is None:
                ring_lab = g2

        a1 = atom_1.atom
        a2 = atom_2.atom
        a,b = sorted([a1,a2], key=lambda c:atom_order.get(c, len(atom_order)))
        motif_lab = a+b

    elif len(coord) == 3:
        if tag is None:
            tag = "bend"

        a,b,c = coord
        atom_1 = atom_labels[a]
        atom_2 = atom_labels[b]
        atom_3 = atom_labels[c]

        r1 = atom_1.ring
        r2 = atom_2.ring
        r3 = atom_3.ring
        if (
                r1 is not None and r2 is not None and r3 is not None
                and r1 == r2 and r1 == r3 and r2 == r3
        ):
            ring_lab = r1

        g1 = atom_1.group
        g2 = atom_2.group
        g3 = atom_3.group
        if (
                g1 is not None and g2 is not None and g3 is not None
                and g1 == g2 and g1 == g3 and g2 == g3
        ):
            group_lab = g1

        a1 = atom_1.atom
        a2 = atom_2.atom
        a3 = atom_3.atom
        if atom_order.get(a1, len(atom_order)) > atom_order.get(a3, len(atom_order)):
            a1, a2, a3 = a3, a2, a1
        motif_lab = a1 + a2 + a3
    else:
        if tag is None:
            tag = "dihedral"

        a, b, c, d = coord
        atom_1 = atom_labels[a]
        atom_2 = atom_labels[b]
        atom_3 = atom_labels[c]
        atom_4 = atom_labels[d]

        rings = [atom_1.ring, atom_2.ring, atom_3.ring, atom_4.ring]
        if (
            all(r is not None for r in rings)
            and all(r1 == r2 for r1,r2 in itertools.combinations(rings, 2))
        ):
            ring_lab = rings[0]

        groups = [atom_1.group, atom_2.group, atom_3.group, atom_4.group]
        if (
                all(r is not None for r in groups)
                and all(r1 == r2 for r1, r2 in itertools.combinations(groups, 2))
        ):
            group_lab = groups[0]

        a1 = atom_1.atom
        a2 = atom_2.atom
        a3 = atom_3.atom
        a4 = atom_4.atom
        if atom_order.get(a1, len(atom_order)) > atom_order.get(a4, len(atom_order)):
            a1, a2, a3, a4 = a4, a3, a2, a1
        motif_lab = a1 + a2 + a3 + a4

    return coordinate_label(ring_lab, group_lab, motif_lab, tag)