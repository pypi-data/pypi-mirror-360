import collections

import numpy as np
from . import Misc as misc
from . import SetOps as sets
from . import VectorOps as vec_ops

__all__ = [
    "permutation_sign",
    "levi_cevita_maps",
    "levi_cevita_tensor",
    "levi_cevita3",
    "levi_cevita_dot",
    "normalize_commutators",
    "commutator_terms",
    "commutator_evaluate"
]


def permutation_sign(perm, check=True):
    # essentially a swap sort on perm
    # https://stackoverflow.com/a/73511014
    parity = 1
    perm = np.asanyarray(perm)
    if check:
        perm = np.argsort(np.argsort(perm))
    else:
        perm = perm.copy()
    for i in range(len(perm)):
        while perm[i] != i: # ensure subblock is sorted
            parity *= -1
            j = perm[i]
            perm[i], perm[j] = perm[j], perm[i]
    return parity
def levi_cevita_maps(k):
    perms = sets.permutation_indices(k, k)
    signs = np.array([permutation_sign(p, check=False) for p in perms])
    return perms, signs
def levi_cevita_tensor(k, sparse=False):
    pos, vals = levi_cevita_maps(k)
    if sparse:
        from .Sparse import SparseArray
        a = SparseArray.from_data(
            (
                pos.T,
                vals
            ),
            shape=(k,)*k
        )
    else:
        a = np.zeros((k,)*k, dtype=int)
        a[tuple(pos.T)] = vals
    return a
# levi_cevita3 = levi_cevita_tensor(3)
levi_cevita3 = np.array([
    [[0, 0, 0],
     [0, 0, 1],
     [0, -1, 0]],

    [[0, 0, -1],
     [0, 0, 0],
     [1, 0, 0]],

    [[0, 1, 0],
     [-1, 0, 0],
     [0, 0, 0]]
])

def levi_cevita_dot(k, a, /, axes, shared=None):
    pos, vals = levi_cevita_maps(k)
    return vec_ops.semisparse_tensordot((tuple(pos.T), vals, (k,) * k), a, axes, shared=shared)

def _flatten_comstr(cs):
    for o in cs:
        if isinstance(o, (int, np.integer)):
            yield o
        else:
            for f in _flatten_comstr(o):
                yield f

def normalize_commutators(commutator_string):
    a, b = commutator_string
    a_int = isinstance(a, (int, np.integer))
    b_int = isinstance(b, (int, np.integer))
    if b_int and a_int:
        return [1], [commutator_string], [a, b]
    elif a_int:
        ps, bs, ts = normalize_commutators(b)
        return [-p for p in ps], [
            [b, a]
            for b in bs
        ], ts + [a]
    elif b_int:
        ps, as_, ts = normalize_commutators(a)
        return [p for p in ps], [
            [a, b]
            for a in as_
        ], ts + [b]
    else:
        aa, bb = a
        aa_int = isinstance(aa, (int, np.integer))
        bb_int = isinstance(bb, (int, np.integer))
        cc, dd = b
        cc_int = isinstance(cc, (int, np.integer))
        dd_int = isinstance(dd, (int, np.integer))

        if aa_int and bb_int:
            if cc_int and dd_int:
                forms = [
                    [[[aa, bb], cc], dd],
                    [[[dd, aa], bb], cc],
                    [[[cc, dd], aa], bb],
                    [[[bb, cc], dd], aa]
                ]
                phases = [1, 1, 1, 1]
                terms = [aa, bb, cc, dd]
                return phases, forms, terms
            else:
                pb, bs_, tb = normalize_commutators(b)
                return [-p for p in pb], [
                    [b, a]
                    for b in bs_
                ], tb + [aa, bb]
        elif cc_int and dd_int:
            pa, as_, ta = normalize_commutators(a)
            return [p for p in pa], [
                [a, b]
                for a in as_
            ], ta + [cc, dd]
        else:
            pa, as_, ta = normalize_commutators(a)
            pb, bs_, tb = normalize_commutators(b)
            if len(tb) > len(ta):
                return [
                    -p1 * p2
                    for p2 in pb
                    for p1 in pa
                ], [
                    [b, a]
                    for b in bs_
                    for a in as_
                ], tb + ta
            else:
                return [
                    p1 * p2
                    for p1 in pa
                    for p2 in pb
                ], [
                    [a, b]
                    for a in as_
                    for b in bs_
                ], ta + tb

def _setup_com_terms(full_phases, storage, i0, idx, j0, j, term):
    a,b = term
    if isinstance(a, (int, np.integer)): # simple swap, nothing more needed
        prev = storage[i0:i0+idx]
        n = idx * 2
        new = storage[i0+idx:i0+n]
        new[:, :j0] = prev[:, :j0]
        new[:, j0], new[:, j0+1:j+j0+1] = prev[:, j0+j], prev[:, j0:j0+j]
        full_phases[i0+idx:i0+n] = -full_phases[i0:i0+idx]
        j = j + 1
    else:
        idx, j = _setup_com_terms(full_phases, storage, i0, idx, j0, j, a)
        if isinstance(b, (int, np.integer)): # swap all priors
            n = idx * 2
            prev = storage[i0:i0+idx]
            new = storage[i0 + idx:i0 + n]
            new[:, :j0] = prev[:, :j0]
            new[:, j0], new[:, j0 + 1:j + j0 + 1] = prev[:, j0 + j], prev[:, j0:j0 + j]
            full_phases[i0+idx:i0+n] = -full_phases[i0:i0+idx]
            j = j + 1
        else:
            n, j1 = _setup_com_terms(full_phases, storage, i0, idx, j, 1, b)
            idx = n
            n = 2 * n
            prev = storage[i0:i0+idx]
            new = storage[i0+idx:i0+n]
            new[:, j0:j0+j1], new[:, j0+j1:j0+j1+j] = prev[:, j0+j:j0+j+j1], prev[:, j0:j0+j]
            full_phases[i0+idx:i0+n] = -full_phases[i0:i0+idx]
    return n, j

def commutator_terms(commutator_strings):
    phases, normal_forms, symbols = normalize_commutators(commutator_strings)
    storage = np.full((2**(len(symbols)-1), len(symbols)), symbols)
    full_phases = np.ones(len(storage), dtype=int)
    idx = 0
    for base_phase,term in zip(phases, normal_forms):
        nx, _ = _setup_com_terms(full_phases, storage, idx, 1, 0, 1, term)
        full_phases[idx:idx+nx] *= base_phase
        idx += nx

    return full_phases, storage

def commutator_evaluate(commutator, expansion_terms, normalized=False, direct=None, recursive=False):
    if recursive:
        a,b = commutator
        if not isinstance(a, (int, np.integer)):
            a = commutator_evaluate(a, expansion_terms, recursive=True)
        else:
            a = expansion_terms[a]
        if not isinstance(b, (int, np.integer)):
            b = commutator_evaluate(b, expansion_terms, recursive=True)
        else:
            b = expansion_terms[b]
        return a@b - b@a

    if direct is None:
        test_phases, test_terms = commutator
        direct = (
                isinstance(test_phases, (int, np.integer))
                or not isinstance(test_phases[0], (int, np.integer))
                or not (abs(test_phases[-1]) == 1 and abs(test_phases[0]) == 1)
        )
    if direct:
        terms = collections.deque()
        terms.append([(0,), commutator])
        exprs = {}
        while terms:
            idx, (a,b) = terms.pop()
            ta = exprs.pop(idx + (0,), None)
            tb = exprs.pop(idx + (1,), None)
            if ta is None and isinstance(a, (int, np.integer)):
                ta = expansion_terms[a]
            if tb is None and isinstance(b, (int, np.integer)):
                tb = expansion_terms[b]
            if ta is not None and tb is not None:
                exprs[idx] = ta @ tb - tb @ ta
            else:
                terms.append([idx,(None, None)]) # by the time this comes back up we expect those to be filled in
                if tb is None:
                    terms.append([idx+(1,), b])
                else:
                    exprs[idx+(1,)] = tb
                if ta is None:
                    terms.append([idx+(0,), a])
                else:
                    exprs[idx+(0,)] = ta
        return exprs[(0,)]
    else:
        if not normalized:
            commutator = commutator_terms(commutator)
        phases, terms = commutator
        comm = 0
        for p,t in zip(phases, terms):
            res = expansion_terms[t[0]]
            for i in t[1:]:
                res = res @ expansion_terms[i]
            if p < 0:
                comm -= res
            else:
                comm += res
        return comm

