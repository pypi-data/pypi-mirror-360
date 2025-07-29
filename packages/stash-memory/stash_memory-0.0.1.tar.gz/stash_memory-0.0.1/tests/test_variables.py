#-------------------- Imports --------------------

from src.stash import Stash

import pytest

#-------------------- Testing Variables --------------------

def test_variables():

    @Stash(freeze=False)
    class TestExample():
        name: str
        age: int
        is_villain: bool

    example2 = TestExample(
        name="Diana Prince",
        age=35,
        is_villain=False
    )

    assert example2.name == "Diana Prince"
    assert example2.age == 35
    assert example2.is_villain is False

if __name__ == "__main__":
    pytest.main()