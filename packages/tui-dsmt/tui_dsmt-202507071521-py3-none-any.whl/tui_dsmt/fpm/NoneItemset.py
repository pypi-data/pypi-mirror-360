from .Itemset import Itemset

class NoneItemset(Itemset):
    def __new__(cls):
        return super().__new__(cls, None)
        
    def __add__(self, other):
        return Itemset(*self, *other, modify=False)
