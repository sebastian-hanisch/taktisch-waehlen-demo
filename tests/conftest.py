"""Gemeinsame Fixtures: Mini-Profile, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def seven():
    """7 Wähler, 3 Kandidaten: 3 x A>B>C, 2 x B>C>A, 2 x C>B>A.
    Erststimmen A 3, B 2, C 2 (Mehrheitswahl: A); Borda A 6, B 9, C 6; Copeland A 0, B 2, C 1 (Condorcet-Sieger B)."""
    return np.array([[0, 1, 2]] * 3 + [[1, 2, 0]] * 2 + [[2, 1, 0]] * 2)


@pytest.fixture
def tb_ba():
    """Gleichstand: B vor A vor C."""
    return np.array([1, 0, 2])


@pytest.fixture
def tb_id():
    """Gleichstand: A vor B vor C."""
    return np.array([0, 1, 2])
