import math
from typing import Tuple, List, Set

from .SequentialItemset import SequentialItemset


class SequentialDatabase(List[Tuple[int, SequentialItemset]]):
    def __init__(self, *args: Tuple[int, SequentialItemset]):
        super().__init__(args)

    def project(self, *prefix: str) -> 'SequentialDatabase':
        return SequentialDatabase(*(
            (tid, projected_transaction)
            for tid, projected_transaction in (
                (tid, transaction.project(*prefix))
                for tid, transaction in self
            )
            if projected_transaction is not None
        ))

    @property
    def items(self) -> Set[SequentialItemset]:
        return set(
            SequentialItemset(x)
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
    def item_powerset(self) -> 'SequentialDatabase':
        items = list(self.items)

        def generate(l: int):
            if l == 0:
                return

            for i in items:
                yield i
                for k in generate(l - 1):
                    if i[0] not in k:
                        yield i + k

        return SequentialDatabase(*enumerate(sorted(generate(self.max_length))))

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
