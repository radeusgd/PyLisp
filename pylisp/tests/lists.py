from pylisp.interpreter import python_list_to_lisp, lisp_list_to_python, lisp_list_length, lisp_list_is_valid, ConsCell


def test_lisp_list():
    assert lisp_list_to_python(None) == []

    def inverse(py):
        lisp = python_list_to_lisp(py)
        assert lisp_list_to_python(lisp) == py
        assert len(py) == lisp_list_length(lisp)
        assert lisp_list_is_valid(lisp)

    inverse([])
    inverse(["a"])
    inverse([3, 2, 2, 5])
    assert not lisp_list_is_valid(ConsCell(2, 3))
