# -*- coding: utf-8 -*-
from functools import reduce
from collections import Iterator
from itertools import chain,groupby,product


class CollectionsHelper:
    def __init__(self, src=None):
        self.src=src

    def toList(self):
        return list(self.src)

    def toSet(self):
        return set(self.src)

    def toTuple(self):
        return tuple(self.src)

    def getSource(self):
        return self.src

    def map(self,func):
        return CollectionsHelper(list(map(func, self.src)))

    def filter(self,predicate):
        return CollectionsHelper(list(filter(predicate, self.src)))

    def reduce(self,func,identity=None):
        if identity is None:
            return reduce(func,self.src)
        else:
            return reduce(func,self.src,identity)

    def chain(self):
        return CollectionsHelper(chain.from_iterable(self.src))

    def groupby(self,func=None):
        return CollectionsHelper([(it[0], list(it[1])) for it in groupby(self.src, func)])

    def product(self,tag):
        return CollectionsHelper(product(self.src, tag))

    def all(self,predicate):
        return all([predicate(it) for it in self.src])

    def any(self,predicate):
        return any([predicate(it) for it in self.src])

    def first(self,predicate=None):
        if predicate is None:
            if isinstance(self.src,Iterator):
                return next(self.src)
            return next(iter(self.src))
        else :
            return next(list(filter(predicate,self.src)))

    def firstOrNone(self,predicate=None):
        try:
            if predicate is None:
                if isinstance(self.src,Iterator):
                    return next(self.src)
                return next(iter(self.src))
            else :
                return next(list(filter(predicate,self.src)))
        except StopIteration:
            return None


if __name__ == '__main__':
    testgroupdata=[{"id":1,"name":"wwb"},{"id":1,"name":"wxa"},{"id":1,"name":"wxb"},{"id":2,"name":"wxc"},{"id":2,"name":"wxd"}]
    print((CollectionsHelper(testgroupdata).groupby(lambda it:it['id']).toList()))