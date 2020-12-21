from numeric import *
from equations import *
from complex_to_complex import *

import matplotlib.pyplot as plt
import numpy as np
import traceback


def parse_input(string: str) -> float:
    try:
        return float(string)
    except ValueError:
        try:
            return float(translate(string))
        except ValueError:
            raise Exception("unknown variable")


if __name__ == "__main__":
    format_c_plot = (3, 2.1)
    print('\033[35m'+"Hello World"+'\033[0m')
    l1: (Expression, Function, str, float, int, complex, None) = None
    l2: (Expression, Function, str, float, int, complex, None) = None
    debugging = False
    while True:
        _input = input()
        try:
            if _input == "stop":
                print('\033[35m' + "See you later" + '\033[0m')
                break
            elif _input == "debugging":
                debugging = not debugging
                print('\033[35m' + "Debugging is set to " + str(debugging) + '\033[0m')
            elif len(_input) != 0:
                if _input.startswith("plot("):
                    if _input[-1] == ")":
                        if _input[5:-1] == "help":
                            print("input(function, start, end, resolution, [type], {Parameters})")
                            continue
                        _input = _input[5:-1].replace(" ", "").split(",")
                        info = Function.give_info(_input[0])
                        ranges = []
                        for i in _input[1:4]:
                            ranges.append(parse_input(i))
                        if len(_input) > 4:
                            if _input[4] == "c":
                                """input(function, start, end, resolution, 'c', contour, angle)"""
                                dist = (abs(ranges[0]) + abs(ranges[1])) / 2
                                p = PlotterComplex(resolution=int(ranges[2]), distance=dist, format_of_image=format_c_plot)
                                contour = False
                                angle = False
                                if len(_input) == 7:
                                    contour = _input[5] in ["True", "true", "t", "1"]
                                    angle = _input[6] in ["True", "true", "t", "1"]
                                elif len(_input) == 6:
                                    contour = _input[5] in ["True", "true", "t", "1"]
                                elif len(_input) > 7:
                                    raise Exception("too many parameters for complex function")
                                func = lambda t: info[1](t + (float(ranges[0]) + float(ranges[1]))/2)
                                plot = p.plot_func(func, contour, angle)
                                plt.imshow(plot, interpolation='bicubic', origin="upper", extent=[-dist + (float(ranges[0]) + float(ranges[1]))/2,
                                                                                                  dist + (float(ranges[0]) + float(ranges[1]))/2,
                                                                                                  -dist * format_c_plot[1] / format_c_plot[0],
                                                                                                  dist * format_c_plot[1] / format_c_plot[0]])
                                plt.show()
                                print('\033[35m' + "done" + '\033[0m')
                            else:
                                raise Exception("unknown function type")
                        elif len(_input) == 4:
                            if info[0] == 1:
                                x = np.arange(ranges[0], ranges[1], 1/ranges[2])
                                y = [info[1](i) for i in x]
                                plt.plot(x, y)
                                plt.show()
                                print('\033[35m' + "done" + '\033[0m')
                            else:
                                raise Exception("to many var")
                        else:
                            raise Exception("unfitting parameters; ask help for clarification")
                    else:
                        raise Exception("unmatched parenthesis")
                elif _input[0] == "|":
                    _input = _input[1:]
                    if l1 is not None and l2 is not None:
                        if _input[0] == "(" and _input[-1] == ")":
                            paras: dict = {}
                            _input = _input[1:-1]
                            if _input.find(",") != -1:
                                _input = _input.split(",")
                                for i in _input:
                                    tmp = i.split("=")
                                    paras[tmp[0]] = translate(tmp[1])
                            else:
                                tmp = _input.split("=")
                                paras[tmp[0]] = translate(tmp[1])
                            if not isinstance(l1, (float, int, complex, Expression)):
                                l1 = translate(str(l1))
                            if not isinstance(l2, (float, int, complex, Expression)):
                                l2 = translate(str(l2))
                            if isinstance(l1, Expression):
                                l1 = l1(**paras)
                            if isinstance(l2, Expression):
                                l2 = l2(**paras)
                            if isinstance(l1, (int, float, complex)) and isinstance(l2, (int, float, complex)) and l1 == l2:
                                print(polish_str(str(l1)))
                            else:
                                print(polish_str(str(l1)) + " = " + polish_str(str(l2)))
                        elif "=" in _input:
                            i1, i2 = _input.split("=")
                            tmp = tokenizer(i1)
                            if len(tmp) != 1:
                                raise Exception("bad variable name")
                            Item.define(tmp[0], translate(i2))
                            print('\033[35m' + "done" + '\033[0m')
                        elif _input.startswith("solve"):
                            _input = _input[5:]
                            _input.replace(" ", "")
                            if len(_input) == 0:
                                if type(l1) == (Expression, Function) and len(l1.give_all_var()) == 1 and (type(l2) == (float, int) or len(l2.give_all_var()) == 0):
                                    print('\033[35m' + list(l1.give_all_var())[0] + ": " + str(n_solve_naive(l1, l2, list(l1.give_all_var())[0])))
                                elif type(l2) == (Expression, Function) and len(l2.give_all_var()) == 1 and (type(l1) == (float, int) or len(l1.give_all_var()) == 0):
                                    print('\033[35m' + list(l2.give_all_var())[0] + ": " + str(n_solve_naive(l1, l2, list(l2.give_all_var())[0])))
                                else:
                                    raise Exception("missing parameters")
                            elif _input[0] == "(" and _input[-1] == ")":
                                pass
                            else:
                                raise Exception("missing parameters")
                        else:
                            i1 = translate("(" + polish_str(str(l1)) + ")" + _input)
                            i2 = translate("(" + polish_str(str(l2)) + ")" + _input)
                            if isinstance(i1, (int, float, complex)) and isinstance(i2, (int, float, complex)) and i1 == i2:
                                print(polish_str(str(i1)))
                            else:
                                print(polish_str(str(i1)) + " = " + polish_str(str(i2)))
                            l1, l2 = i1, i2
                elif "=" in _input:
                    i1, i2 = _input.split("=")
                    tmp = tokenizer(i1)
                    if len(tmp) >= 4 and tmp[1] == "(" and all(tmp[i] == "," for i in range(3, len(tmp)-1, 2)) and tmp[-1] == ")":
                        Function.define(tmp[0], [tmp[i] for i in range(2, len(tmp)-1, 2)], translate(i2))
                        print('\033[35m'+"done"+'\033[0m')
                    else:
                        i1 = translate(i1)
                        i2 = translate(i2)
                        if isinstance(i1, (int, float, complex)) and isinstance(i2, (int, float, complex)) and i1 == i2:
                            print(polish_str(str(i1)))
                        else:
                            print(polish_str(str(i1)) + " = " + polish_str(str(i2)))
                        l1, l2 = i1, i2
                else:
                    tmp = translate(_input)
                    print(polish_str(str(tmp)))
                    l1 = tmp
                    l2 = None
            else:
                raise Exception("You need to write something")
        except Exception as e:
            if debugging:
                traceback.print_exc()
            else:
                print('\033[31m'+str(e)+'\033[0m')
