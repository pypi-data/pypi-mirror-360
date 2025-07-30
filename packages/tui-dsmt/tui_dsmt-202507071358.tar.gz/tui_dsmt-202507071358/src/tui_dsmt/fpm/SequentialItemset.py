from typing import Callable, Any, Optional

from .Itemset import Itemset


class SequentialItemset(Itemset):
    def __new__(cls, *args, key: Callable[[str], Any] = None, reverse: bool = False):
        return super().__new__(cls, *args, modify=False)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return SequentialItemset(*super().__getitem__(key))
        else:
            return super().__getitem__(key)

    def __add__(self, other):
        return SequentialItemset(*self, *other)

    def __repr__(self, lp: str = '<', rp: str = '>') -> str:
        return super().__repr__(lp, rp)

    def __format__(self, format_spec: str):
        return f'{str(self):{format_spec}}'

    @property
    def total_len(self) -> int:
        return sum(
            len(c) if isinstance(c, Itemset) else 1
            for c in self
        )

    @staticmethod
    def _build_subsets(transaction, length, prefix):
        if length == 0:
            yield prefix
            return

        if len(transaction) == 0:
            return

        # remove first element from transaction
        next_prefix = prefix + Itemset(transaction[0])
        transaction = transaction[1:]

        # pick element
        yield from SequentialItemset._build_subsets(transaction, length - 1, next_prefix)

        # skip element
        yield from SequentialItemset._build_subsets(transaction, length, prefix)

    def subsets(self, length):
        yield from self._build_subsets(self, length, SequentialItemset())

    @staticmethod
    def _build_nested_subsets(transaction, length, prefix):
        if length == 0:
            yield prefix
            return

        if len(transaction[0]) > 0:
            i = 0
            element = transaction[0]
        elif len(transaction) >= 2:
            i = 1
            element = transaction[1]
        else:
            return

        if len(transaction[0]) == 0 and len(prefix[-1]) > 0:
            prefix += SequentialItemset(Itemset())

        k = 0
        event = element[0]

        remaining_elements = transaction[i + 1:]
        remaining_events = SequentialItemset(element[k + 1:])
        remaining = remaining_events + remaining_elements

        # pick event
        next_prefix = prefix[:-1] + SequentialItemset(prefix[-1] + Itemset(event))
        yield from SequentialItemset._build_nested_subsets(remaining, length - 1, next_prefix)

        # skip event
        yield from SequentialItemset._build_nested_subsets(remaining, length, prefix)

    def nested_subsets(self, length):
        yield from self._build_nested_subsets(self, length, SequentialItemset(Itemset()))

    def count_in(self, transactions):
        count = 0

        for _, transaction in transactions:
            pos = 0
            for el in transaction:
                if self[pos] == el:
                    pos += 1

                    if pos == len(self):
                        count += 1
                        break

        return count

    def count_in_nested(self, transactions):
        count = 0

        for _, transaction in transactions:
            for subset in transaction.nested_subsets(self.total_len):
                if subset == self:
                    count += 1

        return count

    def project(self, *prefix: str) -> Optional['SequentialItemset']:
        i = 0

        for k, e in enumerate(self, start=1):
            if e == prefix[i]:
                i += 1

            if i == len(prefix):
                return SequentialItemset(*self[k:])
