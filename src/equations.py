import numpy as np


def tokenizer(string: str) -> list:
    """
    Splits the string in meaningful units (lexical analysis).\n
    Splits at the symbols: \n\t' '   +   -   *   /   ^   (   )   ,
    :param string: the string that should be tokenized
    :return: the tokens of string as a list
    """
    stop = [' ', '+', '-', '*', '/', '^', '(', ')', ',']
    tokens = []
    is_num: bool = False
    t_start: int = 0
    t_length: int = 0
    i: int = 0  # replacing for with while for recalculating current loop
    while i < len(string):
        if string[i] in stop:
            is_num = False
            if t_length > 0:
                tokens.append(string[t_start: i])
                if not string[i] == ' ':
                    tokens.append(string[i])
                t_start = i + 1
                t_length = 0
            else:
                if string[i] == ' ':
                    t_start += 1
                else:
                    tokens.append(string[i])
                    t_start += 1
        else:
            t_length += 1
            try:
                float(string[t_start:i+1])
                is_num = True
            except ValueError:
                if is_num:
                    is_num = False
                    tokens.append(string[t_start:i])
                    tokens.append("*")
                    t_start = i
                    t_length = 0
                    continue
            if i == len(string)-1:
                tokens.append(string[t_start: i+1])
        i += 1
    return tokens


def polish_str(res: str):
    """
    does some formatting of a string\n\t- removes the zeros of complex numbers
    \n\t- remove unneeded parentheses and merges plus and minus\n\t- remove unneeded .0
    :param res: the string that should be formatted
    :return: the formatted string
    """
    # remove zeros of imaginary numbers
    tmp = res.find("0j")
    if tmp != -1:
        zeros: list = [tmp]
        while tmp != -1:
            if zeros[-1] + 1 > len(res) - 1:
                break
            tmp = res.find("0j", zeros[-1] + 1)
            zeros.append(tmp)
        del zeros[-1]
        c = 0
        for i in zeros:
            if i - c == 0:
                res = res[i - c + 1:]
                c += 2
            elif res[i - 1 - c] in ["+", "-"]:
                tmp = res
                res = tmp[:i - c - 1]
                if not i - c + 2 == len(tmp):
                    res += tmp[i - c + 2:]
                c += 3
            elif res[i - 1 - c] == " " and res[i - 2 - c] in ["+", "-"]:
                res = res[:i - c - 2]
                if not i - c + 1 == len(res):
                    res += res[:i - c + 1]
                c += 4
    # remove unneeded parentheses and merges plus and minus
    tmp = res.find("-")
    if tmp != -1:
        minus: list = [tmp]
        while tmp != -1:
            if minus[-1] + 1 > len(res) - 1:
                break
            tmp = res.find("-", minus[-1] + 1)
            minus.append(tmp)
        del minus[-1]
        c = 0
        for i in minus:
            if i >= 1:
                if (i == 1 and res[i - 1 - c] == "(") or (res[i - 1 - c] == "(" == res[i - 2 - c]):
                    for k in range(i, len(res)):
                        if res[k] == ")":
                            res = res[:i - 1 - c] + res[i - c:k] + res[k + 1:]
                            c += 2
                            break
                        elif res[k] not in [str(m) for m in range(10)] + ["-", ".", "e"]:
                            break
                elif i - c > 3 and res[i - c - 1] == "(" and res[i - c - 3] == "+":
                    for k in range(i, len(res)):
                        if res[k] == ")":
                            res = res[:i - 3 - c] + "-" + res[i - 2 - c:i - 1 - c] + res[i - c + 1:k] + res[k + 1:]
                            c += 3
                            break
                        elif res[k] not in [str(m) for m in range(10)] + ["-", ".", "e", "j"]:
                            break
    # remove unneeded .0
    tmp = res.find(".0")
    if tmp != -1:
        dots: list = [tmp]
        while tmp != -1:
            if dots[-1] + 1 > len(res) - 1:
                break
            tmp = res.find(".0", dots[-1] + 1)
            dots.append(tmp)
        del dots[-1]
        c = 0
        for i in dots:
            if i - c == len(res) - 2:
                res = res[:i - c]
                c += 2
            elif res[i + 2 - c] not in [str(k) for k in range(10)]:
                res = res[:i - c] + res[i + 2 - c:]
                c += 2
    return res


class Expression:
    """
    A class that stores expressions
    """
    def __init__(self, plus: bool):
        """
        creates a member of the class Expression
        :param plus: true if this Expression is added onto another Expression, false if it is subtracted
        """
        self.plus: bool = plus  # True: +; False: - for expression before it (+ or - of first expr is irrelevant)
        self.next: (Expression, None) = None  # next Expression to be added; stops chain if None
        self.term: (Term, None) = None
    
    def add(self, plus: bool):
        """
        Adds an Expression onto this Expression\n
        Adds onto the next expression, if there is a next one
        :param plus: is the Expression added or subtracted
        """
        if self.next is None:
            self.next = Expression(plus)
        else:
            self.next.add(plus)
    
    def change_term(self, multiply):
        """
        changes the saved Term to the given one
        :param multiply: the given Term
        """
        self.term = Term(multiply)
    
    @staticmethod
    def parse(tokens: list):
        """
        translates a list of tokens to an Expression
        :param tokens: the list of Tokens
        :return: the corresponding Expression
        """
        tmp: list = [Expression(True)]
        tmp[0].term = Term.parse(tokens)
        if len(tokens) == 0:
            return tmp[0]
        t: str = tokens[0]
        while len(tokens) > 0 and (t == "+" or t == "-"):
            del tokens[0]
            tmp.append(Expression(t == "+"))
            tmp[-1].term = Term.parse(tokens)
            if len(tokens) > 0:
                t = tokens[0]
        for i in range(len(tmp) - 2, -1, -1):
            tmp[i].next = tmp[i + 1]
        return tmp[0]
    
    def give_all_var(self, var: (set, None) = None) -> list:
        """
        returns the names of all contained variables
        :param var: the already found variables
        :return: the already found variables together with the new ones
        """
        if var is None:
            var = set()
        if self.next is not None:
            self.next.give_all_var(var)
        self.term.give_all_var(var)
        return var
    
    def give_loc_var(self, var: (set, None) = None) -> list:
        """
        returns the names of all local variables (no function variables)
        :param var: the already found variables
        :return: the already found variables together with the new ones
        """
        if var is None:
            var = set()
        if self.next is not None:
            self.next.give_loc_var(var)
        self.term.give_loc_var(var)
        return var
    
    def give_all_func(self, var: (set, None) = None) -> list:
        """
        returns the names of all contained functions
        :param var: the already found functions
        :return: the already found functions together with the new ones
        """
        if var is None:
            var = set()
        if self.next is not None:
            self.next.give_all_func(var)
        self.term.give_all_func(var)
        return var
    
    def __call__(self, **kwargs):
        """
        calls the Expression
        :param kwargs: the variables, which should be replaced
        :return: the new Expression / the resulting number
        """
        ter = self.term(**kwargs)
        nex = None
        if self.next is not None:
            nex = self.next(**kwargs)
        if isinstance(ter, Term):
            res = Expression(self.plus)
            res.term = ter
            if nex is not None:
                if isinstance(nex, Expression):
                    res.next = nex
                elif isinstance(nex, (float, int, complex)):
                    if nex != 0:
                        res.next = Expression.apply_val(nex)
                else:
                    raise Exception("unexpected Type")
            return res
        if not isinstance(ter, (float, int, complex)):
            raise Exception("unexpected Type")
        if nex is not None:
            if isinstance(nex, Expression):
                if ter == 0:
                    if not self.next.plus:
                        nex.term.factor.positive = not nex.term.factor.positive
                    return nex
                res = Expression.apply_val(ter)
                res.next = nex
                return res
            elif isinstance(nex, (float, int, complex)):
                if self.next.plus:
                    ter += nex
                else:
                    ter -= nex
            else:
                raise Exception("unexpected Type")
        return ter
    
    @staticmethod
    def apply_val(val):
        """
        applies an Value onto the Expression
        :param val: the value
        :return: the resulting Expression
        """
        tmp = Expression(True)
        tmp.term = Term.apply_val(val)
        return tmp
    
    def __str__(self) -> str:
        """
        a polished string representation of the Expression
        :return: the string representation
        """
        tmp = self.str()
        return polish_str(tmp)
    
    def str(self) -> str:
        """
        a blank string representation of the Expression
        :return: the string representation
        """
        return self.term.str() + (((" + " if self.next.plus else " - ") + self.next.str()) if self.next is not None else "")


class Term:
    """
    A class that stores Terms
    """
    def __init__(self, multiply: bool):
        self.multiply: bool = multiply  # True: *; False: / for expression before it (* or / of wirst expr is irrelevant)
        self.next: (Term, None) = None  # next Term to be multiplyed; stops chain if None
        self.factor: (Factor, None) = None
    
    def mul(self, multiply):
        if self.next is None:
            self.next = Term(multiply)
        else:
            self.next.mul(multiply)
    
    def change_factor(self, positive):
        self.factor = Factor(positive)
    
    @staticmethod
    def parse(tokens: list):
        tmp: list = [Term(True)]
        tmp[0].factor = Factor.parse(tokens)
        if len(tokens) == 0:
            return tmp[0]
        t: str = tokens[0]
        while len(tokens) > 0 and (t == "*" or t == "/"):
            del tokens[0]
            tmp.append(Term(t == "*"))
            tmp[-1].factor = Factor.parse(tokens)
            if len(tokens) > 0:
                t = tokens[0]
        for i in range(len(tmp) - 2, -1, -1):
            tmp[i].next = tmp[i + 1]
        return tmp[0]
    
    def give_all_var(self, var: (set, None) = None) -> list:
        if var is None:
            var = set()
        if self.next is not None:
            self.next.give_all_var(var)
        self.factor.give_all_var(var)
        return var
    
    def give_loc_var(self, var: (set, None) = None) -> list:
        if var is None:
            var = set()
        if self.next is not None:
            self.next.give_loc_var(var)
        self.factor.give_loc_var(var)
        return var
    
    def give_all_func(self, var: (set, None) = None) -> list:
        if var is None:
            var = set()
        if self.next is not None:
            self.next.give_all_func(var)
        self.factor.give_all_func(var)
        return var
    
    def __call__(self, **kwargs):
        fac = self.factor(**kwargs)
        nex = None
        if self.next is not None:
            nex = self.next(**kwargs)
        if isinstance(fac, (float, int, complex)) and isinstance(nex, (float, int, complex)) and fac == nex == 0:
            return 0
        if isinstance(fac, Factor):
            res = Term(self.multiply)
            res.factor = fac
            if nex is not None:
                if isinstance(nex, Term):
                    res.next = nex
                elif isinstance(nex, (float, int, complex)):
                    res.next = Term.apply_val(nex)
                else:
                    raise Exception("unexpected Type")
            return res
        if not isinstance(fac, (float, int, complex)):
            raise Exception("unexpected Type")
        if nex is not None:
            if isinstance(nex, Term):
                res = Term.apply_val(fac)
                res.next = nex
                return res
            elif isinstance(nex, (float, int, complex)):
                if self.next.multiply:
                    fac *= nex
                else:
                    fac /= nex
            else:
                raise Exception("unexpected Type")
        return fac
    
    @staticmethod
    def apply_val(val):
        tmp = Term(True)
        tmp.factor = Factor.apply_val(val)
        return tmp
    
    def __str__(self) -> str:
        return self.str()
    
    def str(self) -> str:
        return self.factor.str() + ((("*" if self.next.multiply else "/") + self.next.str()) if self.next is not None else "")


class Factor:
    def __init__(self, positive: bool):
        self.positive: bool = positive  # True: +; False: -
        self.item: (Item, None) = None
        self.exponent: (Factor, None) = None  # no exponentiation if exponent is None
    
    def change_positive(self, positive: bool):
        self.positive = positive
    
    def change_item(self, kind: int):
        self.item = Item(kind)
    
    def change_exponent(self, positive: bool):
        self.exponent = Factor(positive)
    
    @staticmethod
    def parse(tokens: list):
        res: Factor = Factor(True)
        if tokens[0] == "+":
            del tokens[0]
        elif tokens[0] == "-":
            del tokens[0]
            res.positive = False
        res.item = Item.parse(tokens)
        if len(tokens) > 0 and tokens[0] == "^":
            del tokens[0]
            res.exponent = Factor.parse(tokens)
        return res
    
    def give_all_var(self, var: (set, None) = None) -> list:
        if var is None:
            var = set()
        if self.exponent is not None:
            self.exponent.give_all_var(var)
        self.item.give_all_var(var)
        return var
    
    def give_loc_var(self, var: (set, None) = None) -> list:
        if var is None:
            var = set()
        if self.exponent is not None:
            self.exponent.give_loc_var(var)
        self.item.give_loc_var(var)
        return var
    
    def give_all_func(self, var: (set, None) = None) -> list:
        if var is None:
            var = set()
        if self.exponent is not None:
            self.exponent.give_all_func(var)
        self.item.give_all_func(var)
        return var
    
    def __call__(self, **kwargs):
        item = self.item(**kwargs)
        expo: (Factor, None) = None
        if self.exponent is not None:
            expo = self.exponent(**kwargs)
        if isinstance(item, Item):
            res = Factor(self.positive)
            res.item = item
            if expo is not None:
                if isinstance(expo, Factor):
                    res.exponent = expo
                elif isinstance(expo, (float, int, complex)):
                    res.exponent = Factor.apply_val(expo)
                else:
                    raise Exception("unexpected Type")
            return res
        if not isinstance(item, (float, int, complex)):
            raise Exception("unexpected Type")
        if not self.positive:
            item *= -1
        if expo is not None:
            if isinstance(expo, Factor):
                res = Factor.apply_val(item)
                res.exponent = expo
                return res
            elif isinstance(expo, (float, int, complex)):
                item **= expo
            else:
                raise Exception("unexpected Type")
        return item
    
    @staticmethod
    def apply_val(val):
        res = Factor(True)
        if not isinstance(val, complex) and val < 0:
            res.positive = False
            val *= -1
        tmp = Item(0)
        tmp.value = val
        res.item = tmp
        return res
    
    def __str__(self) -> str:
        return self.str()
    
    def str(self) -> str:
        if not self.positive:
            return "(-" + self.item.str() + ")" + ("^" + self.exponent.str() if self.exponent is not None else "")
        return self.item.str() + (("^" + self.exponent.str()) if self.exponent is not None else "")


class Item:
    variables: dict = {
        "pi": np.pi,
        "e": np.e,
        "i": 1j
    }
    
    def __init__(self, kind: int):
        self.KIND: int = kind  # 0: Number; 1: ( Expression ); 2: Variable; 3: Function
        if self.KIND == 0:
            self.value: float = 0
        elif self.KIND == 1:
            self.value: (Expression, None) = None
        elif self.KIND == 2:
            self.value: str = ""
        elif self.KIND == 3:
            self.value: (Function, None) = None
        else:
            raise Exception("unknown kind")
    
    def change_value(self, value):
        self.value = value
    
    @staticmethod
    def define(name: str, value: (Expression, float, complex, int)):
        Item.variables[name] = value
    
    @staticmethod
    def parse(tokens: list):
        try:
            tmp = float(tokens[0])
            del tokens[0]
            res: Item = Item(0)
            res.value = tmp
            return res
        except ValueError:
            try:
                tmp = complex(tokens[0])
                del tokens[0]
                res: Item = Item(0)
                res.value = tmp
                return res
            except ValueError:
                if tokens[0] == "(":
                    del tokens[0]
                    index = Item.find_parenthesis(tokens)
                    if index == -1:
                        raise Exception("unmatched parenthesis!!!")
                    res: Item = Item(1)
                    res.value = Expression.parse(tokens[:index])
                    del tokens[:index + 1]
                    return res
            if tokens[0] == ")":
                raise Exception("unmatched parenthesis!!!")
            if len(tokens) > 1 and tokens[1] == "(":
                res: Item = Item(3)
                name = tokens[0]
                del tokens[:2]
                index = Item.find_parenthesis(tokens)
                if index == -1:
                    raise Exception("unmatched parenthesis!!!")
                res.value = Function.parse(name, tokens[:index])
                del tokens[:index + 1]
                return res
            res: Item = Item(2)
            res.value = tokens[0]
            del tokens[0]
            return res
    
    @staticmethod
    def find_parenthesis(tokens: list):
        parenthesis: int = 1
        for i in range(len(tokens)):
            if tokens[i] == "(":
                parenthesis += 1
            if tokens[i] == ")":
                parenthesis -= 1
            if parenthesis == 0:
                return i
        return -1
    
    def give_all_var(self, var: (set, None) = None) -> list:
        if var is None:
            var: set = set()
        if self.KIND == 2:
            var.add(self.value)
        elif self.KIND == 3:
            for i in self.value.vars:
                if isinstance(i, Expression):
                    i.give_all_var(var)
                elif isinstance(i, str):
                    var.add(i)
                else:
                    raise Exception("unknown Type")
        elif self.KIND == 1:
            self.value.give_all_var(var)
        return var
    
    def give_loc_var(self, var: (set, None) = None) -> list:
        if var is None:
            var: set = set()
        if self.KIND == 2:
            var.add(self.value)
        elif self.KIND == 1:
            self.value.give_loc_var(var)
        return var
    
    def give_all_func(self, var: (set, None) = None) -> list:
        if var is None:
            var: set = set()
        if self.KIND == 3:
            var.add(self.value.name)
        elif self.KIND == 1:
            self.value.give_all_func(var)
        return var
    
    def __call__(self, **kwargs):
        kwargs = {**kwargs, **self.variables}
        if self.KIND == 0:
            return self.value
        elif self.KIND == 1:
            tmp = self.value(**kwargs)
            if isinstance(tmp, Expression):
                res = Item(self.KIND)
                res.value = tmp
                return res
            return tmp
        elif self.KIND == 2:
            if self.value in kwargs:
                return kwargs[self.value]
            else:
                return self.copy()
        elif self.KIND == 3:
            tmp = self.value(**kwargs)
            if isinstance(tmp, Function):
                res = Item(self.KIND)
                res.value = tmp
                return res
            return tmp
        else:
            raise Exception("unknown type")
    
    def copy(self):
        tmp = Item(self.KIND)
        tmp.value = self.value
        return tmp
    
    def __str__(self) -> str:
        return self.str()
    
    def str(self) -> str:
        if self.KIND == 1:
            if self.value is None:
                return ""
            return "(" + self.value.str() + ")"
        return str(self.value)


class Function:
    PRE_DEFINED: dict = {
        "sin": (1, lambda *args: np.sin(*args), lambda **kwargs: np.sin(**kwargs), ["x"]),
        "cos": (1, lambda *args: np.cos(*args), lambda **kwargs: np.cos(**kwargs), ["x"]),
        "tan": (1, lambda *args: np.tan(*args), lambda **kwargs: np.tan(**kwargs), ["x"]),
    }
    
    new_defined: dict = {}
    
    def __init__(self, name: str):
        self.loc_defined: dict = {}
        self.name: str = name
        self.vars: list = []
    
    @staticmethod
    def __translate(__var_names: list, __values: list):
        if len(__values) != len(__var_names):
            print(1, __var_names, __values)
            raise Exception("length not fitting")
        res: dict = {}
        for i in range(len(__var_names)):
            res[__var_names[i]] = __values[i]
        return res
    
    def define_local(self, name: str, var_names: list, func: Expression):
        if set(var_names) != func.give_all_var():
            raise Exception("var names not fitting")
        self.loc_defined[name] = (len(var_names), lambda *args: func(**self.__translate(var_names, args)))
    
    @staticmethod
    def define(name: str, var_names: list, func: Expression):
        if set(var_names) != func.give_all_var():
            raise Exception("var names not fitting")
        Function.new_defined[name] = (len(var_names), lambda *args: func(**Function.__translate(var_names, args)), lambda **kwargs: func(**kwargs), var_names)
    
    @staticmethod
    def parse(name: str, variables: list):
        res = Function(name)
        while len(variables) > 0:
            try:
                index = variables.index(",")
                if index == 1:
                    try:
                        res.vars.append(float(variables[0]))
                    except ValueError:
                        try:
                            res.vars.append(complex(variables[0]))
                        except ValueError:
                            res.vars.append(variables[0])
                    del variables[:2]
                elif index == -1:
                    if len(variables) == 1:
                        try:
                            res.vars.append(float(variables[0]))
                        except ValueError:
                            try:
                                res.vars.append(complex(variables[0]))
                            except ValueError:
                                res.vars.append(Expression.parse(variables))
                        del variables[0]
                    else:
                        res.vars.append(Expression.parse(variables))
                elif index == 0:
                    raise Exception("double comma")
                else:
                    res.vars.append(Expression.parse(variables))
                    del variables[0]
            except ValueError:
                if len(variables) == 1:
                    try:
                        res.vars.append(float(variables[0]))
                    except ValueError:
                        try:
                            res.vars.append(complex(variables[0]))
                        except ValueError:
                            res.vars.append(Expression.parse(variables))
                    del variables[:2]
                else:
                    res.vars.append(Expression.parse(variables))
        return res
    
    def __call__(self, **kwargs):
        pack: list = self.vars.copy()
        for i in range(len(pack)):
            if isinstance(pack[i], Expression):
                pack[i] = pack[i](**kwargs)
            if isinstance(pack[i], str):
                raise Exception
        if all(isinstance(i, (float, int, complex)) for i in pack):
            if self.name in self.PRE_DEFINED:
                if len(self.vars) == self.PRE_DEFINED[self.name][0]:
                    return self.PRE_DEFINED[self.name][1](*pack)
            if self.name in self.new_defined:
                if len(self.vars) == self.new_defined[self.name][0]:
                    return self.new_defined[self.name][1](*pack)
            if self.name in self.loc_defined:
                if len(self.vars) == self.loc_defined[self.name][0]:
                    return self.loc_defined[self.name][1](*pack)
        for i in range(len(pack)):
            if i in kwargs:
                if isinstance(kwargs[pack[i]], Expression):
                    pack[i] = kwargs[pack[i]]
                else:
                    pack[i] = Expression.apply_val(kwargs[pack[i]])
        tmp_f: Function = Function(self.name)
        tmp_f.vars = pack
        return tmp_f
    
    @staticmethod
    def call(name: str, *args, **kwargs):
        if kwargs is not None and args is None:
            if name in Function.PRE_DEFINED and len(kwargs) == Function.PRE_DEFINED[name][0]:
                return Function.PRE_DEFINED[name][2](**kwargs)
            if name in Function.new_defined and len(kwargs) == Function.new_defined[name][0]:
                return Function.new_defined[name][3](**kwargs)
            raise Exception("undefined function call")
        if args is not None:
            if name in Function.PRE_DEFINED and len(args) == Function.PRE_DEFINED[name][0]:
                return Function.PRE_DEFINED[name][1](*args)
            if name in Function.new_defined and len(args) == Function.new_defined[name][0]:
                return Function.new_defined[name][1](*args)
            raise Exception("undefined function call")
        if args is not None and kwargs is not None:
            raise Exception("named and unnamed parameters given")
        raise Exception("no parameters given")
    
    @staticmethod
    def give_info(name: str):
        if name in Function.PRE_DEFINED:
            return Function.PRE_DEFINED[name]
        if name in Function.new_defined:
            return Function.new_defined[name]
        raise Exception("undefined function call")
    
    def __str__(self) -> str:
        return self.str()
    
    def str(self) -> str:
        res: str = self.name + "("
        for i in self.vars:
            res += str(i) + ", "
        return res[:-2] + ")"


def parser(tokens: list) -> Expression:
    """
    creates an expression of an given token list.
    :param tokens: the list of tokens
    :return: the Expression
    """
    return Expression.parse(tokens)()


def translate(string: str) -> Expression:
    """
    translates an string into an Expression
    :param string: the string, that should be translated
    :return: the Expression of that string
    """
    return parser(tokenizer(string))
