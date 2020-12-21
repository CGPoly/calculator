from equations import *


def n_solve_naive(a: (Expression, float, int), b: (Expression, float, int), var: str, x: float = 0, s_exp: int = 0, e_exp: int = -16, **kwargs) -> float:
    """
    This is a method to solve the equation a = b.\n
    The methode is primitive and there will be an alternative with binary search one day.
    
    :param a: the first Expression
    :param b: the second Expression
    :param var: the value, which should be solved for
    :param x: the start value
    :param s_exp: the start exponent (should have the same order as the expected solution)
    :param e_exp: the minimal (maximal negative) Exponent to which should be searched
    :param kwargs: a parameter for the Expressions
    :return: the solution for x
    """
    inp: dict = dict(kwargs, **{var: x})
    if s_exp < e_exp:
        return x
    if type(a) == float:
        if type(b) == float:
            raise Exception("all values for x are possible")
        while a < b(**inp):
            x += 10**s_exp
            inp = dict(kwargs, **{var: x})
        while a > b(**inp):
            x -= 10**s_exp
            inp = dict(kwargs, **{var: x})
    elif type(b) == float:
        while a(**inp) < b:
            x += 10 ** s_exp
            inp = dict(kwargs, **{var: x})
        while a(**inp) > b:
            x -= 10 ** s_exp
            inp = dict(kwargs, **{var: x})
    else:
        while a(**inp) < b(**inp):
            x += 10**s_exp
            inp = dict(kwargs, **{var: x})
        while a(**inp) > b(**inp):
            x -= 10**s_exp
            inp = dict(kwargs, **{var: x})
    return n_solve_naive(a, b, var, x, s_exp-1, e_exp, **kwargs)
