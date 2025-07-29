#-------------------- Imports --------------------

from src.stash import Stash, conserve

import pytest

#-------------------- Testing Preservation --------------------

def test_preservation():

    @Stash(freeze=False)
    class TestExample():
        name: str
        age: int
        is_villain: bool

        @conserve
        def preserved_method(self):
            return self.name
        
        def not_preserved_method(self):
            return self.name
        

    example3 = TestExample(
        name="Hank Pym",
        age=67,
        is_villain=False
    )

    assert example3.preserved_method() == "Hank Pym"

    with pytest.raises(AttributeError):
        example3.not_preserved_method()

    assert hasattr(example3, "preserved_method")
    assert not hasattr(example3, "not_preserved_method")