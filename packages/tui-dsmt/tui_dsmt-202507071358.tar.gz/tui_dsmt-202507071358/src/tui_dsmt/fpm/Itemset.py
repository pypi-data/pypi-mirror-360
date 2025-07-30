import itertools
from typing import Callable, Any


class Itemset(tuple):
    def __new__(cls, *args, key: Callable[[str], Any] = None, reverse: bool = False, modify: bool = True):
        if modify:
            return super().__new__(cls, sorted(set(args), key=key, reverse=reverse))
        else:
            return super().__new__(cls, args)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return Itemset(*super().__getitem__(key), modify=False)
        else:
            return super().__getitem__(key)

    def __add__(self, other):
        return Itemset(*self, *other)

    def __sub__(self, other):
        return Itemset(*(i for i in self if i not in other))

    def __repr__(self, lp: str = '(', rp: str = ')') -> str:
        return f'{lp}{", ".join(map(str, self))}{rp}'

    def __str__(self):
        return self.__repr__()

    def __format__(self, format_spec: str):
        return f'{str(self):{format_spec}}'

    @property
    def set(self):
        return set(self)

    def is_subset(self, transaction):
        return self.set.issubset(transaction)

    def count_in(self, transactions):
        c = 0
        for _, items in transactions:
            if self.is_subset(items):
                c += 1

        return c

    def support_in(self, transactions):
        return self.count_in(transactions) / len(transactions)

    def matches(self, other, length):
        return self[:length] == other[:length] and self[length:] != other[length:]

    def union(self, other):
        return Itemset(*self, *other)

    def subsets(self, length):
        for combination in itertools.combinations(self, length):
            yield Itemset(*combination)

    @property
    def real_nonempty_subsets(self):
        for i in range(1, len(self)):
            yield from self.subsets(i)

    def sort(self, key: Callable[[str], Any] = None, reverse: bool = False):
        return Itemset(*self, key=key, reverse=reverse)

    def filter(self, key: Callable[[str], bool]):
        return Itemset(*filter(key, self))
