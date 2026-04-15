"""Tests for peyote.sizing."""

import pytest

from peyote.sizing import PRESETS, BeadConfig


class TestBeadConfigDefaults:
    def test_defaults(self):
        cfg = BeadConfig()
        assert cfg.columns == 10
        assert cfg.rows == 72
        assert cfg.bead_width == 22
        assert cfg.bead_height == 22
        assert cfg.bead_margin == 1
        assert cfg.corner_radius == 5

    def test_frozen_dataclass(self):
        cfg = BeadConfig()
        with pytest.raises(Exception):
            cfg.columns = 20  # type: ignore[misc]


class TestBeadConfigValidation:
    def test_odd_columns_raises(self):
        with pytest.raises(ValueError, match="even"):
            BeadConfig(columns=5)

    def test_columns_one_raises(self):
        with pytest.raises(ValueError):
            BeadConfig(columns=1)

    def test_even_columns_accepted(self):
        BeadConfig(columns=4)
        BeadConfig(columns=100)


class TestBeadConfigGeometry:
    def test_slot_default(self):
        # 22 + 1*2 = 24
        assert BeadConfig().slot == 24

    def test_slot_custom(self):
        cfg = BeadConfig(bead_width=10, bead_margin=3)
        assert cfg.slot == 16

    def test_half(self):
        assert BeadConfig(columns=10).half == 5
        assert BeadConfig(columns=20).half == 10


class TestActiveColumns:
    def test_odd_cols_for_10(self):
        assert BeadConfig(columns=10).odd_cols() == [0, 2, 4, 6, 8]

    def test_even_cols_for_10(self):
        assert BeadConfig(columns=10).even_cols() == [1, 3, 5, 7, 9]

    def test_cols_for_row_alternates(self):
        cfg = BeadConfig(columns=6)
        # row 0 → N=1 → odd → even-indexed cols
        assert cfg.cols_for_row(0) == [0, 2, 4]
        # row 1 → N=2 → even → odd-indexed cols
        assert cfg.cols_for_row(1) == [1, 3, 5]
        # row 2 → N=3 → odd
        assert cfg.cols_for_row(2) == [0, 2, 4]
        # row 3 → N=4 → even
        assert cfg.cols_for_row(3) == [1, 3, 5]

    def test_active_cols_cover_all(self):
        cfg = BeadConfig(columns=8)
        union = set(cfg.cols_for_row(0)) | set(cfg.cols_for_row(1))
        assert union == set(range(8))


class TestPresets:
    def test_presets_nonempty(self):
        assert len(PRESETS) > 0

    @pytest.mark.parametrize("name", list(PRESETS.keys()))
    def test_all_presets_valid(self, name):
        cfg = PRESETS[name]
        assert isinstance(cfg, BeadConfig)
        assert cfg.columns % 2 == 0
        assert cfg.rows > 0

    def test_known_presets_present(self):
        for name in ('ring', 'bracelet', 'bookmark'):
            assert name in PRESETS
