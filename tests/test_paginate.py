import pytest
from app.utils import paginate

def test_paginate():
    assert paginate(1, 10) == [1, 2, 3, 4, 5]
    assert paginate(2, 10) == [1, 2, 3, 4, 5]
    assert paginate(3, 10) == [1, 2, 3, 4, 5]
    assert paginate(4, 10) == [2, 3, 4, 5, 6]
    assert paginate(5, 10) == [3, 4, 5, 6, 7]
    assert paginate(6, 10) == [4, 5, 6, 7, 8]
    assert paginate(7, 10) == [5, 6, 7, 8, 9]
    assert paginate(8, 10) == [6, 7, 8, 9, 10]
    assert paginate(9, 10) == [6, 7, 8, 9, 10]
    assert paginate(10, 10) == [6, 7, 8, 9, 10]

    assert paginate(1, 1) == [1]
    assert paginate(1, 2) == [1, 2]
    assert paginate(2, 2) == [1, 2]
    assert paginate(1, 3) == [1, 2, 3]
    assert paginate(2, 3) == [1, 2, 3]
    assert paginate(3, 3) == [1, 2, 3]
    assert paginate(1, 4) == [1, 2, 3, 4]
    assert paginate(2, 4) == [1, 2, 3, 4]
    assert paginate(3, 4) == [1, 2, 3, 4]
    assert paginate(4, 4) == [1, 2, 3, 4]
    assert paginate(1, 5) == [1, 2, 3, 4, 5]
    assert paginate(1, 6) == [1, 2, 3, 4, 5]

def test_paginate_outofrange():
    with pytest.raises(ValueError):
        paginate(0, 10)
    with pytest.raises(ValueError):
        paginate(-5, 10)
    with pytest.raises(ValueError):
        paginate(11, 10)