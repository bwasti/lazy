import threading
import time
import pygraphviz
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams["figure.dpi"] = 300

_graph = nx.DiGraph()
debug = False
verbose = False
parallelize = False


def log(s):
    if verbose:
        print(s)


class Task(object):

    def __init__(self, iter_base=0.00001, iter_func=lambda x: x * 1.01):
        self.spins = []
        self.iter_base = iter_base
        self.iter_func = iter_func

    def spin(self):
        self.spins.append(0)
        i = self.iter_base
        while True:
            time.sleep(i)
            i = self.iter_func(i)
            self.spins[-1] += 1
            yield None


class Thread(threading.Thread):

    def __init__(self, func, *args, **kwargs):
        threading.Thread.__init__(self)
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.out = self.func(*self.args, **self.kwargs)


def _run_ops_in_parallel(ops):
    log("running in parallel {}".format(ops))
    threads = [Thread(op.run) for op in ops]
    [t.start() for t in threads]
    [t.join() for t in threads]


# Data acquisition
def _execute_graph(data):
    log("executing graph")
    nodes = nx.ancestors(_graph, data)
    nodes.add(data)
    needed = [n for n in nodes if n.type == "Data" and n.data == None]

    log("need to resolve {}".format(needed))

    controlflow = nx.DiGraph()
    for n in needed:
        for i in _graph.predecessors(n):
            log("running {} to resolve {}".format(i, n))
            controlflow.add_node(i)
            # Check if we draw an edge to a consumer
            # of the output of this node
            for s in _graph.successors(n):
                # Data output is data we need
                for d in _graph.successors(s):
                    if d in needed:
                        controlflow.add_edge(i, s)

    # fake a node to be root node (its a No-op)
    root_op = Operation(lambda: None)
    controlflow.add_node(root_op)
    for node in controlflow.nodes:
        if node == root_op:
            continue
        if len(controlflow.in_edges(node)) == 0:
            controlflow.add_edge(root_op, node)

    splits = []
    for n, idom in nx.immediate_dominators(controlflow, root_op).items():
        if n == idom:
            continue
        if n in controlflow.successors(idom):
            continue
        splits.append((idom, n))

    # Graph mode
    order = list(nx.topological_sort(controlflow))
    iteration = 0
    max_threads = 4
    while iteration < len(order):
        ops = []
        for i in range(max_threads):
            if iteration >= len(order):
                break
            next_op = order[iteration]
            if sum([op in nx.ancestors(controlflow, next_op) for op in ops]) > 0:
                break
            ops.append(order[iteration])
            iteration += 1
        _run_ops_in_parallel(ops)


class Data(object):

    @classmethod
    def getId(cls, _impl=[-1]):
        _impl[0] += 1
        return _impl[0]

    def __init__(self, d=None):
        self.data = d
        self.type = "Data"
        self.id = self.getId()
        log("creating {}".format(self))

    def __eq__(self, other):
        return self.id == other.id and self.type == other.type

    def __hash__(self):
        return hash(self.id)

    def get(self):
        if self.data is None:
            log("getting data")
        if parallelize and self.data is None:
            _execute_graph(self)
        else:  # Default execution
            if self.data is None:
                for p in _graph.predecessors(self):
                    p.run()
        return self.data

    def __repr__(self):
        return "Data_{}".format(self.id)


class Operation(object):

    @classmethod
    def getId(cls, _impl=[-1]):
        _impl[0] += 1
        return _impl[0]

    def __init__(self, f):
        self.func = f
        self.name = f.__name__
        self.type = "Operation"
        self.id = self.getId()
        args = f.__code__.co_argcount
        self.inputs = [Data() for d in range(args)]
        self.output = Data()
        log("creating {}".format(self))

    def __eq__(self, other):
        return self.id == other.id and self.type == other.type

    def __hash__(self):
        return hash(self.id)

    def run(self):
        log("running {}".format(self))
        inputs = [x.get() for x in self.inputs]
        self.output.data = self.func(*inputs)

    def __repr__(self):
        return "{}_{}".format(
            self.name, self.id, ", ".join([str(i) for i in self.inputs]), self.output
        )


# todo handle kwargs
def synchronous(fn):

    def wrapper(*args):
        op = Operation(fn)

        for i in range(len(op.inputs)):
            if not isinstance(args[i], Data):
                op.inputs[i].data = args[i]
            else:
                op.inputs[i] = args[i]

        _graph.add_node(op)
        for inp in op.inputs:
            _graph.add_node(inp)
            _graph.add_edge(inp, op)
        _graph.add_edge(op, op.output)

        return op.output

    return wrapper


def _draw(G):
    log("num nodes {}".format(len(G)))
    node_sizes = [400 for i in range(len(G))]
    pos = nx.nx_agraph.graphviz_layout(G, prog="dot")
    color = lambda x: "red" if x.type == "Operation" else "green" if x.data else "grey"
    colors = [color(node) for node in G.nodes()]
    nx.draw(G, pos, with_labels=True, node_size=node_sizes, node_color=colors)

    ax = plt.gca()
    ax.set_axis_off()
    plt.show()


def draw():
    _draw(_graph)
