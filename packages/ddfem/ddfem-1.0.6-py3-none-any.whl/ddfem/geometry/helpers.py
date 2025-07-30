from ufl import conditional, dot, max_value, min_value, sqrt, ln, exp


# https://en.wikipedia.org/wiki/Smooth_maximum, https://en.wikipedia.org/wiki/LogSumExp
def smax_value(a, b, s):
    return 1 / s * ln(exp(s * a) + exp(s * b))


def smin_value(a, b, s):
    return smax_value(a, b, -s)


def ufl_length(p):
    return sqrt(dot(p, p) + 1e-10)
    # return max_value(sqrt(dot(p, p)), 1e-10)
    # return sqrt(dot(p, p))


def ufl_sign(p):
    if isinstance(p, (float, int)):
        return 1 if p > 0 else -1

    return conditional(p > 0, 1, -1)


def ufl_clamp(p, minimum, maximum):
    if isinstance(p, (float, int)):
        return min(max(p, minimum), maximum)

    # def ufl_max(p1, p2):
    #     return conditional(p2 < p1, p1, p2)

    # def ufl_min(p1, p2):
    #     return conditional(p1 < p2, p1, p2)

    # return ufl_min(ufl_max(p, minimum), maximum)
    # # using min_value/max_value, seems to break shape Pie?
    return min_value(max_value(p, minimum), maximum)


def ufl_cross(p1, p2):
    return p1[0] * p2[1] - p1[1] * p2[0]
