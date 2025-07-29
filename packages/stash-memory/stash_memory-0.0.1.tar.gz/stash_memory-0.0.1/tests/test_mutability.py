#-------------------- Imports --------------------

from src.stash import Stash

import pytest

#-------------------- Testing Mutability --------------------

def test_mutable_variables():

    @Stash(freeze=False)
    class TestExample():
        name: str
        age: int
        is_villain: bool

    example5 = TestExample(
        name="Viktor Von Doom",
        age=40,
        is_villain=True
    )

    example5.name = "Diana Prince"
    example5.is_villain = False

    assert example5.name == "Diana Prince"
    assert example5.is_villain is False

if __name__ == "__main__":
    pytest.main()
        