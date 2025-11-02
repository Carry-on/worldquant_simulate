from itertools import product



def ts_factory(op, field):
    output = []
    # days = [3, 5, 10, 20, 60, 120, 240]
    days = [5, 22, 66, 120, 240]
    for day in days:
        alpha = "%s(%s, %d) " %(op, field, day)
        output.append(alpha)
    return output


def ts_comp_factory(op, field, factor, paras):
    output = []
    # l1, l2 = [3, 5, 10, 20, 60, 120, 240], paras
    l1, l2 = [5, 22, 66, 240], paras
    comb = list(product(l1, l2))
    for day, para in comb:
        if type(para) == float:
            alpha = "%s(%s, %d, %s=%.1f)" % (op, field, day, factor, para)
        elif type(para) == int:
            alpha = "%s(%s, %d, %s=%d)" % (op, field, day, factor, para)
        output.append(alpha)
    return output


def vector_factory(op, field):
    output = []
    vectors = ["cap"]
    for vector in vectors:
        alpha = "%s(%s, %s)" % (op, field, vector)
        output.append(alpha)
    return output


def group_factory(op, field, region):
    pass


if __name__ == '__main__':
    l1, l2 = [5, 22, 66, 240], [1,2,4,5]
    comb = list(product(l1, l2))
    print(comb)

