#! /usr/bin/python3

import sys


class Read:
    def __init__(self, lines):
        self.name = lines[0].strip()[1:]
        self.bases = "".join([x.strip() for x in lines[1:]]).upper()

    def get_kmers(self, kmersize):
        res = {}
        for pos in range(0, len(self.bases) - kmersize + 1):
            kmer = self.bases[pos:(pos + kmersize)]
            if kmer not in res:
                res[kmer] = 0
            res[kmer] += 1
        return res

    def __str__(self):
        return self.name + ": " + self.bases[:20] + "..."

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if not isinstance(other, Read):
            return False
        if other.name == self.name and other.bases == self.bases:
            return True
        return False


class DBGnode:
    def __init__(self, seq):
        self.seq = seq
        self.eto = dict()
        self.efrom = dict()

    def add_edge_to(self, eto):
        if eto not in self.eto:
            self.eto[eto] = 0
        self.eto[eto] += 1

    def add_edge_from(self, efrom):
        if efrom not in self.efrom:
            self.efrom[efrom] = 0
        self.efrom[efrom] += 1

    def get_potential_from(self):
        res = []
        for x in "AGTC":
            res += [x + self.seq[:-1]]
        return res

    def get_potential_to(self):
        res = []
        for x in "AGTC":
            res += [self.seq[1:] + x]
        return res

    def get_edge_to_weight(self, other):
        if not other in self.eto:
            return 0
        return self.eto[other]

    def get_edge_from_weight(self, other):
        if not other in self.efrom:
            return 0
        return self.efrom[other]

    def extend_next(self):
        return None

    def extend_prev(self):
        return None

    def can_extend_next(self):
        return False

    def can_extend_prev(self):
        return False

class DBGraph:
    def __init__(self):
        self.nodes = {}
        self.kmerlen = None

    def add_kmers(self, kmers):
        if len(kmers) == 0:
            return
        ## Falls kmer-L??nge (Dimension) des Graphen noch nicht gesetzt ist,
        ## auf den Wert von irgendeinem k-mer aus der ??bergebenen dictionary
        ## setzen.
        if self.kmerlen is None:
            self.kmerlen = len(next(iter(kmers.keys())))
        for kmer_s in kmers.keys():
            if len(kmer_s) != self.kmerlen:
                raise ValueError("Incompatible k-mer lengths: " + str(self.kmerlen) + " and " + str(len(kmer_s)))
            if kmer_s not in self.nodes.keys():
                self.nodes[kmer_s] = DBGnode(kmer_s)
            kmer = self.nodes[kmer_s]
            ## F??r jedes m??gliche k-mer, von/zu dem es eine Kante geben k??nnte,
            ## die entsprechenden Kanten hinzuf??gen, falls dieses k-mer auch im
            ## Graphen ist (vorsicht: wenn es eine Kante A -> B gibt, sowohl in
            ## A eine kante nach B als auch in B eine Kante von A hinzuf??gen)
            for pto in kmer.get_potential_to():
                if pto in self.nodes.keys():
                    self.nodes[pto].add_edge_from(kmer)
                    kmer.add_edge_to(self.nodes[pto])
            for pfrom in kmer.get_potential_from():
                if pfrom in self.nodes.keys():
                    self.nodes[pfrom].add_edge_to(kmer)
                    kmer.add_edge_from(self.nodes[pfrom])

    def count_edges(self):
        edges = 0
        for kmer, node in self.nodes.items():
            edges += len(node.eto)
        return edges

    def count_nodes(self):
        return len(self.nodes)

    def simplify(self):
        pass

    def get_FASTA(self):
        return ""

    def __str__(self):
        return "DBG(" + str(self.kmerlen) + ") with " + str(self.count_nodes()) + " nodes and " + str(
            self.count_edges()) + " edges"


def read_fasta(readfile):
    f = open(readfile, "r")
    readlines = []
    reads = []
    for line in f:
        readlines += [line]
        if len(readlines) == 2:
            reads += [Read(readlines)]
            readlines = []
    f.close()
    return reads


def build_graph(filename, kmersize):
    reads = read_fasta(filename)
    graph = DBGraph()
    for read in reads:
        graph.add_kmers(read.get_kmers(kmersize))
    return graph

if __name__ == "__main__":
    dbg = build_graph("data/virus_perfectreads.fasta", 18)
    print(dbg)
    dbg.simplify()
    print(dbg)
    print(dbg.get_FASTA())