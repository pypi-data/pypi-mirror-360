import pytest
from naludaq import NaluDaq

class TestNaluDaq:
    @pytest.fixture
    def naludaq(self, tempdir):
        naludaq = NaluDaq("Mockboard", tempdir)

        return naludaq
    pass

