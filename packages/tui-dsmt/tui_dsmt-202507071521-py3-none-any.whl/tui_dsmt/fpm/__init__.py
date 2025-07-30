from .apriori import apriori
from .BruteForceFI import BruteForceFI
from .FPTree import FPTree
from .HashTree import HashTree
from .Itemset import Itemset
from .ItemsetGrid import ItemsetGrid
from .ItemsetGridApriori import ItemsetGridApriori
from .ItemsetGridECLAT import ItemsetGridECLAT
from .NoneItemset import NoneItemset as NI
from .SequentialDatabase import SequentialDatabase
from .SequentialItemset import SequentialItemset
from .TransactionDatabase import TransactionDatabase

NoneItemset = NI()

receipts = TransactionDatabase(
    (1, Itemset('Brot', 'Milch')),
    (2, Itemset('Butter', 'Mehl')),
    (3, Itemset('Brot', 'Butter', 'Eier')),
    (4, Itemset('Brot', 'Milch', 'Eier')),
    (5, Itemset('Butter', 'Eier')),
)

receipts1 = TransactionDatabase(
    (1, Itemset('Brot', 'Butter', 'Milch', 'Zucker')),
    (2, Itemset('Butter', 'Mehl', 'Milch', 'Zucker')),
    (3, Itemset('Butter', 'Eier', 'Milch', 'Salz')),
    (4, Itemset('Eier')),
    (5, Itemset('Butter', 'Mehl', 'Milch', 'Salz', 'Zucker')),
)

sequential_receipts = SequentialDatabase(
    (1, SequentialItemset('Eier', 'Brot', 'Milch', 'Käse')),
    (2, SequentialItemset('Milch', 'Eier', 'Butter')),
    (3, SequentialItemset('Brot', 'Butter', 'Eier')),
    (4, SequentialItemset('Brot', 'Milch', 'Käse')),
    (5, SequentialItemset('Brot', 'Eier', 'Milch')),
    (6, SequentialItemset('Brot', 'Eier'))
    # (1, SequentialItemset('Brot', 'Milch', 'Eier')),
    # (2, SequentialItemset('Milch', 'Eier')),
    # (3, SequentialItemset('Brot', 'Butter', 'Eier')),
    # (4, SequentialItemset('Brot', 'Milch'))
)

numbers = TransactionDatabase(
    (100, Itemset(1, 3, 4)),
    (200, Itemset(2, 3, 5)),
    (300, Itemset(1, 2, 3, 5)),
    (400, Itemset(2, 5)),
)

extended_numbers = TransactionDatabase(
    (100, Itemset(1, 3, 4)),
    (200, Itemset(2, 3, 5)),
    (300, Itemset(1, 2, 3, 5)),
    (400, Itemset(2, 5)),
    (500, Itemset(1, 2, 3)),
    (600, Itemset(1, 2, 4)),
    (700, Itemset(1, 2, 4)),
)

characters = TransactionDatabase(
    (100, Itemset('f', 'a', 'c', 'd', 'g', 'i', 'm', 'p')),
    (200, Itemset('a', 'b', 'c', 'f', 'l', 'm', 'o')),
    (300, Itemset('b', 'f', 'm', 'h', 'j', 'o')),
    (400, Itemset('b', 'c', 'k', 's', 'p')),
    (500, Itemset('a', 'f', 'c', 'e', 'l', 'p', 'm', 'n')),
    (600, Itemset('f', 'c', 'p', 'n')),
)

characters2 = TransactionDatabase(
    (100, Itemset('f', 'a', 'c', 'd', 'g', 'i', 'm', 'p')),
    (200, Itemset('a', 'b', 'c', 'f', 'l', 'm', 'o')),
    (300, Itemset('b', 'f', 'h', 'j', 'o')),
    (400, Itemset('b', 'c', 'k', 's', 'p')),
    (500, Itemset('a', 'f', 'c', 'e', 'l', 'p', 'm', 'n')),
)

clothes = TransactionDatabase(
    (1, Itemset('Hemd')),
    (2, Itemset('Jacke', 'Bergstiefel')),
    (3, Itemset('Ski-Hose', 'Bergstiefel')),
    (4, Itemset('Straßenschuhe')),
    (5, Itemset('Straßenschuhe')),
    (6, Itemset('Jacke'))
)

dna = SequentialDatabase(
    (1, SequentialItemset(*'AGAAGT')),
    (2, SequentialItemset(*'TGACAG')),
    (3, SequentialItemset(*'GAAGT'))
)

orders = SequentialDatabase(
    (
        1,
        SequentialItemset(
            Itemset('Backofenreiniger'),
            Itemset('Backofenreiniger', 'Pizzastein', 'Pizzaschneider'),
            Itemset('Olivenöl')
        )
    ),
    (
        2,
        SequentialItemset(
            Itemset('Backofenreiniger'),
            Itemset('Backofenreiniger', 'Pizzastein'),
            Itemset('Wanderstiefel', 'Olivenöl')
        )
    ),
    (
        3,
        SequentialItemset(
            Itemset('Schwangerschaftstest', 'Pizzastein', 'Teigrolle'),
            Itemset('Vitamine', 'Zink'),
            Itemset('Babyphone', 'Windeln')
        )
    ),
    (
        4,
        SequentialItemset(
            Itemset('Schwangerschaftstest', 'Stift'),
            Itemset('Leinwand', 'Pinsel'),
            Itemset('Windeln')
        )
    )
)

gsp_nested_join_example = SequentialDatabase(
    (
        1,
        SequentialItemset(
            Itemset(1),
            Itemset(2, 3),
            Itemset(4),
        )
    ),
    (
        2,
        SequentialItemset(
            Itemset(2, 3),
            Itemset(4, 5),
        )
    ),
    (
        3,
        SequentialItemset(
            Itemset(2, 3),
            Itemset(4),
            Itemset(5),
        )
    )
)

prefixspan_nested_projection_example = SequentialDatabase(
    (
        1,
        SequentialItemset(
            Itemset('A'),
            Itemset('A', 'B', 'C'),
            Itemset('A', 'C'),
            Itemset('D'),
            Itemset('C', 'F'),
        )
    ),
    (
        2,
        SequentialItemset(
            Itemset('E', 'F'),
            Itemset('A', 'B'),
            Itemset('D', 'F'),
            Itemset('C'),
            Itemset('B'),
        )
    ),
    (
        3,
        SequentialItemset(
            Itemset('E', 'F'),
            Itemset('B'),
            Itemset('D', 'F'),
            Itemset('C'),
            Itemset('B')
        )
    )
)
