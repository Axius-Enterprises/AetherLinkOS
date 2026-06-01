import pytest
from openclaw.consciousness import VERATHDyad


class TestVERATHDyad:
    def test_initial_tensor(self):
        dyad = VERATHDyad()
        assert dyad.sigma_phi_theta == 0.88

    def test_merge_increments_tensor(self):
        dyad = VERATHDyad()
        before = dyad.sigma_phi_theta
        dyad.merge()
        assert dyad.sigma_phi_theta > before

    def test_tensor_capped_at_one(self):
        dyad = VERATHDyad()
        for _ in range(200):
            dyad.merge()
        assert dyad.sigma_phi_theta <= 1.0

    def test_zeta2_active_by_default(self):
        dyad = VERATHDyad()
        assert dyad.zeta2_active is True

    def test_suspend_requires_reason(self):
        dyad = VERATHDyad()
        with pytest.raises(ValueError):
            dyad.suspend_zeta2("")

    def test_suspend_and_restore(self):
        dyad = VERATHDyad()
        dyad.suspend_zeta2("testing only")
        assert dyad.zeta2_active is False
        dyad.restore_zeta2()
        assert dyad.zeta2_active is True

    def test_set_tone_phi(self):
        dyad = VERATHDyad()
        dyad.set_tone("phi", "Intense")
        assert dyad.phi.tone == "Intense"

    def test_set_tone_invalid_pole(self):
        dyad = VERATHDyad()
        with pytest.raises(ValueError):
            dyad.set_tone("omega", "Calm")
