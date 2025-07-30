import itertools
import math
from typing import Tuple, List, Set, Callable

from .Itemset import Itemset


class TransactionDatabase(List[Tuple[int, Itemset]]):
    def __init__(self, *args: Tuple[int, Itemset]):
        super().__init__(args)

    @property
    def items(self) -> Set[Itemset]:
        return set(
            Itemset(x)
            for _, transaction in self
            for x in transaction
        )

    @property
    def max_length(self) -> int:
        return max(
            len(transaction)
            for _, transaction in self
        )

    @property
    def powerset(self) -> 'TransactionDatabase':
        s = [x[0] for x in self.items]

        return TransactionDatabase(
            *enumerate(
                sorted(
                    map(
                        lambda x: Itemset(*x),
                        filter(
                            len,
                            itertools.chain.from_iterable(
                                itertools.combinations(s, r)
                                for r in range(len(s) + 1)
                            )
                        )
                    )
                )
            )
        )

    def __repr__(self) -> str:
        tid_len = max(len('TID'), int(math.log10(max(tid for tid, _ in self))) + 1 if len(self) > 0 else 0)
        transaction_len = max(len('Transaktion'), max(len(str(t)) for _, t in self) if len(self) > 0 else 0)

        return (
                f'{"TID":<{tid_len}}  |  Transaktion\n' +
                f'{"-" * (tid_len + 2)}|{"-" * (transaction_len + 2)}\n' +
                '\n'.join(
                    f'{tid:>{tid_len}}  |  {transaction}'
                    for tid, transaction in self
                )
        )

    def __str__(self) -> str:
        return self.__repr__()

    def map(self, func: Callable[[Itemset], Itemset]) -> 'TransactionDatabase':
        return TransactionDatabase(*(
            (tid, func(transaction))
            for tid, transaction in self
        ))
