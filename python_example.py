# Main pattern-matching code segment from the new Laplace Transform in sympy
# see https://github.com/sympy/sympy/pull/22376
    k, func = f.as_independent(t, as_Add=False)
    for t_dom, s_dom, check, plane, prep in simple_rules:
        ma = prep(func).match(t_dom)
        if ma:
            if check.xreplace(ma):
                return self._cr(k*s_dom.xreplace(ma),
                                plane.xreplace(ma), S.true, **hints)