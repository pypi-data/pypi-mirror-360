from dhananjayan import naive
import pytest

def test_naive_dp():
    a, _ = naive.dot_product([1,0,0,1],[0, 0, 1, 1])
    assert a==1

    b, _ = naive.dot_product([3,4,3,4],[1, 1, 1, 1])
    assert b==14

if __name__ == '__main__': 
    pytest.main()