from pycallgraph2 import PyCallGraph, Config, GlobbingFilter
from pycallgraph2.output import GraphvizOutput
from pycallgraph2.tracer import TraceProcessor, SynchronousTracer
import os, inspect, time
from collections import defaultdict


# Modified classes based on : https://github.com/gak/pycallgraph/tree/master
# Graphviz language online visualiser : https://dreampuf.github.io/GraphvizOnline/
class CustomPyCallGraph(PyCallGraph):
    def get_tracer_class(self):
        if self.config.threaded:
            return CustomAsynchronousTracer
        else:
            return CustomSyncronousTracer


class CustomSyncronousTracer(SynchronousTracer):
    def __init__(self, outputs, config):
        super().__init__(outputs, config)
        self.processor = CustomTraceProcessor(outputs, config)


class CustomAsynchronousTracer(CustomSyncronousTracer):
    def start(self):
        self.processor.start()
        CustomSyncronousTracer.start(self)

    def tracer(self, frame, event, arg):
        self.processor.queue(frame, event, arg, self.memory())
        return self.tracer

    def done(self):
        self.processor.done()
        self.processor.join()


class CustomTraceProcessor(TraceProcessor):
    def init_trace_data(self):
        self.previous_event_return = False

        # A mapping of which function called which other function
        self.call_dict = defaultdict(lambda: defaultdict(int))

        # Current call stack
        self.call_stack = ["__main__"]
        self.filtered_call_stack = [True]

        # Counters for each function
        self.func_count = defaultdict(int)
        self.func_count_max = 0
        self.func_count["__main__"] = 1

        # Accumulative time per function
        self.func_time = defaultdict(float)
        self.func_time_max = 0

        # Accumulative memory addition per function
        self.func_memory_in = defaultdict(int)
        self.func_memory_in_max = 0

        # Accumulative memory addition per function once exited
        self.func_memory_out = defaultdict(int)
        self.func_memory_out_max = 0

        # Keeps track of the start time of each call on the stack
        self.call_stack_timer = []
        self.call_stack_memory_in = []
        self.call_stack_memory_out = []

    def process(self, frame, event, arg, memory=None):
        """This function processes a trace result. Keeps track of
        relationships between calls.
        """

        def last_unfiltered_call():
            for func_name, boolean in zip(reversed(self.call_stack), reversed(self.filtered_call_stack)):
                if boolean:
                    return func_name
            return ""

        if memory is not None and self.previous_event_return:
            self.previous_event_return = False

            if self.call_stack_memory_out:
                full_name, m = self.call_stack_memory_out.pop(-1)
            else:
                full_name, m = (None, None)

            if full_name and m:
                call_memory = memory - m

                self.func_memory_out[full_name] += call_memory
                self.func_memory_out_max = max(self.func_memory_out_max, self.func_memory_out[full_name])

        if event == "call":
            keep = True
            code = frame.f_code

            full_name_list = []

            module = inspect.getmodule(code)
            if module:
                module_name = module.__name__
                module_path = module.__file__

                if not self.config.include_stdlib and self.is_module_stdlib(module_path):
                    keep = False

                if module_name == "__main__":
                    module_name = ""
            else:
                module_name = ""

            if module_name:
                full_name_list.append(module_name)

            try:
                class_name = frame.f_locals["self"].__class__.__name__
                full_name_list.append(class_name)
            except (KeyError, AttributeError):
                class_name = ""

            func_name = code.co_name
            if func_name == "?":
                func_name = "__main__"
            full_name_list.append(func_name)

            full_name = ".".join(full_name_list)

            if len(self.call_stack) > self.config.max_depth:
                keep = False

            if keep and self.config.trace_filter:
                keep = self.config.trace_filter(full_name)

            if self.call_stack:
                src_func = self.call_stack[-1]
            else:
                src_func = None

            if keep:
                self.call_dict[last_unfiltered_call()][full_name] += 1
                self.func_count[full_name] += 1
                self.func_count_max = max(self.func_count_max, self.func_count[full_name])

                self.call_stack.append(full_name)
                self.call_stack_timer.append(time.time())
                self.filtered_call_stack.append(True)

                if memory is not None:
                    self.call_stack_memory_in.append(memory)
                    self.call_stack_memory_out.append([full_name, memory])

            else:
                self.call_stack.append(full_name)
                self.call_stack_timer.append(time.time())
                self.filtered_call_stack.append(False)

        if event == "return":
            self.previous_event_return = True

            if self.call_stack:
                full_name = self.call_stack.pop(-1)

                if self.call_stack_timer:
                    start_time = self.call_stack_timer.pop(-1)
                else:
                    start_time = None

                if start_time:
                    call_time = time.time() - start_time

                    self.func_time[full_name] += call_time
                    self.func_time_max = max(self.func_time_max, self.func_time[full_name])

                if memory is not None:
                    if self.call_stack_memory_in:
                        start_mem = self.call_stack_memory_in.pop(-1)
                    else:
                        start_mem = None

                    if start_mem:
                        call_memory = memory - start_mem
                        self.func_memory_in[full_name] += call_memory

                        self.func_memory_in_max = max(
                            self.func_memory_in_max,
                            self.func_memory_in[full_name],
                        )

            if self.filtered_call_stack:
                self.filtered_call_stack.pop(-1)


class CustomGraphvizOutput(GraphvizOutput):
    def __init__(
        self,
        *args,
        simplified=True,
        graph_supp_attr={},
        node_supp_attr={},
        edge_supp_attr={},
        subgraph_supp_attr={},
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.graph_attributes["graph"].update(graph_supp_attr)
        self.graph_attributes["node"].update(node_supp_attr)
        self.graph_attributes["edge"].update(edge_supp_attr)

        if subgraph_supp_attr is not None:
            self.subgraph_attributes = subgraph_supp_attr

        self.simplified = simplified

    def rename_node(self, node):
        if node.name.startswith(node.group):
            node.name = node.name[len(node.group) + 1 :]
        return node

    def rename_edge(self, edge, groups):
        def rename_func(name):
            for group in groups:
                if name.startswith(group):
                    name = name[len(group) + 1 :]
                    return name
            return name

        edge.src_func = rename_func(edge.src_func)
        edge.dst_func = rename_func(edge.dst_func)

        return edge

    def generate(self):
        def nodes_modifier(nodes):
            def wrapper():
                for node in nodes():
                    if "__main__" in node.name and self.simplified:
                        continue
                    yield self.rename_node(node)

            return wrapper

        def edges_modifier(edges):
            def wrapper():
                for edge in edges():
                    nonlocal groups
                    if ("__main__" in edge.src_func or "__main__" in edge.dst_func) and self.simplified:
                        continue
                    yield self.rename_edge(edge, groups)

            return wrapper

        groups = set([node.group for node in self.processor.nodes()])

        self.processor.nodes = nodes_modifier(self.processor.nodes)
        self.processor.edges = edges_modifier(self.processor.edges)

        dot_code = super().generate()

        if self.simplified:  # just remove any line with __main__ in case there is still some
            new_dot_code = [line for line in dot_code.split("\n") if "__main__" not in line]
            dot_code = "\n".join(new_dot_code)

        self.dot_code = dot_code

        cmd = '"{0}" -T{1} -o{2} <temp_code_file>'.format(self.tool, self.output_type, self.output_file)

        self.shell_command = cmd

        return dot_code

    def node_label(self, node):
        if self.simplified:
            parts = ["{0.name}"]
        else:
            parts = [
                "{0.name}",
                "calls: {0.calls.value:n}",
                "time: {0.time.value:f}s",
            ]

        if self.processor.config.memory:
            parts += [
                "memory in: {0.memory_in.value_human_bibyte}",
                "memory out: {0.memory_out.value_human_bibyte}",
            ]
        return r"\n".join(parts).format(node)

    def edge_label(self, edge):
        if self.simplified:
            return ""
        return "{0}".format(edge.calls.value)

    def attrs_from_dict_semicolon(self, d):
        output = []
        for attr, val in d.items():
            output.append('%s = "%s"' % (attr, val))
        return "; ".join(output)

    def generate_groups(self):
        if not self.processor.config.groups:
            return ""

        output = []
        for group, nodes in self.processor.groups():
            funcs = [node.name for node in nodes]
            funcs = '" "'.join(funcs)
            group_color = self.group_border_color.rgba_web()
            group_font_size = self.group_font_size
            subgraph_attrs = self.attrs_from_dict_semicolon(self.subgraph_attributes)
            output.append(
                'subgraph "cluster_{group}" {{ '
                '"{funcs}"; '
                'label = "{group}"; '
                'fontsize = "{group_font_size}"; '
                'fontcolor = "black"; '
                'style = "bold"; '
                'color = "{group_color}"; '
                "{subgraph_attrs} "
                "}}".format(**locals())
            )

        return output


class PyCallGraphContext(CustomPyCallGraph):
    def __init__(
        self,
        output_file,
        include=[],
        exclude=[],
        simplified=True,
        graph_supp_attr={},
        node_supp_attr={},
        edge_supp_attr={},
        subgraph_supp_attr={},
    ):
        """Initialize a PyCallGraphContext class to capture function calls in a visual graph.

        Args:
            output_file (str): The name of the output file to store the generated graph.
            include (list, optional): A list of glob patterns to include in the trace. Defaults to [].
            exclude (list, optional): A list of glob patterns to exclude from the trace. Defaults to [].
            simplified (bool, optional): Set to True for a simplified Graphviz output. Defaults to True.
            graph_supp_attr (dict, optional): Additional attributes for modifying the overall graph appearance.
                Defaults to {}.
            node_supp_attr (dict, optional): Additional attributes for modifying the node appearance. Defaults to {}.
            edge_supp_attr (dict, optional): Additional attributes for modifying the edge appearance. Defaults to {}.
            subgraph_supp_attr (dict, optional): Additional attributes for modifying the subgraph appearance.
                Defaults to {}.

        You can use the :
          - dot_code attribute of the object returned by the context (using the 'as' keyword) to get the Graphviz
                DOT code used to make the graph.
          - shell_command attribute that contains the command that was used to call Graphviz
        """

        config = Config()
        if simplified:
            config.trace_filter = GlobbingFilter(
                include=["Inflow.*", "ResearchProjects.*"] + include,
                exclude=[
                    "*logging*",
                    "*__*__*",
                    "*<*>*",
                    "*decorator*",
                    "*wrapper*",
                ]
                + exclude,
            )

        self.graph_supp_attr = {
            "rankdir": "LR",
            "ranksep": "0.2",
            "nodesep": "0.2",
            "fontname": "arial",
            "concentrate": True,
            "label": "",
        }
        self.graph_supp_attr.update(graph_supp_attr)

        self.node_supp_attr = {"style": "rounded"}
        self.node_supp_attr.update(node_supp_attr)

        self.edge_supp_attr = {"fontname": "arial"}
        self.edge_supp_attr.update(edge_supp_attr)

        self.subgraph_supp_attr = {"rankdir": "TB", "style": "rounded"}
        self.subgraph_supp_attr.update(subgraph_supp_attr)

        output = CustomGraphvizOutput(
            output_file=output_file,
            simplified=simplified,
            graph_supp_attr=self.graph_supp_attr,
            node_supp_attr=self.node_supp_attr,
            edge_supp_attr=self.edge_supp_attr,
            subgraph_supp_attr=self.subgraph_supp_attr,
        )
        output.group_objects = True
        output.tool = "dot"
        output.output_type = os.path.splitext(output_file)[1].replace(".", "")

        self.output_obj = output

        super().__init__(output=output, config=config)

    def __enter__(self):
        super().__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        try:
            self.output_obj.dot_code
        except AttributeError:
            self.output_obj.dot_code = None
