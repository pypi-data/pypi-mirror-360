#-------------------- Imports --------------------

from src.stash import Stash

import pytest

#-------------------- Testing Caching --------------------

def test_unique_caching():
    
    @Stash(freeze=False)
    class TestA():
        x: int = 5

    @Stash(freeze=False)
    class TestB():
        x: int = 10

    assert TestA != TestB
    assert TestA().__class__ is not TestB().__class__

if __name__ == "__main__":
    pytest.main()