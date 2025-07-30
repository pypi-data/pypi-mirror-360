from .FordFulkerson import FordFulkerson


class EdmondsKarp(FordFulkerson):
    @staticmethod
    def sort_paths(paths):
        return sorted(paths, key=len, reverse=False)
