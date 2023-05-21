import wx
import itertools
import numpy as np
import pandas as pd
import networkx as x
import datetime as dt
import matplotlib.pyplot as plt

import bokeh.io as bkio
import bokeh.plotting as bkp
import bokeh.models as bkm
import bokeh.palettes as bkpal
from bokeh.palettes import Dark2_5 as palette
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigureCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar


class GraphLN(wx.Frame):
    def __init__(self, edges_nodes, type_model, path, *args, **kwargs):
        super(GraphLN, self).__init__(*args, **kwargs, size=(1000, 1000))

        self.panel = MainPanel(edges_nodes[0], edges_nodes[1], edges_nodes[2], type_model, self)
        if type_model == "static":
            self.Show()
        elif type_model == "path" and path:
            self.panel.path_nodes(path)
            self.Show()


class MainPanel(wx.Panel):
    def __init__(self, nodes, edges, num_nodes, type_model, parent):
        # wx.Panel.__init__(self, parent)
        wx.Panel.__init__(self, parent, -1, size=(500, 500))
        self.nodes = nodes
        self.edges = edges
        self.numNodes = num_nodes

        if type_model == "static":
            # mainSplitter = wx.SplitterWindow(self)
            self.static_model(self)

            '''sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(mainSplitter, 1, wx.EXPAND)
            self.SetSizer(sizer)'''
        elif type_model == "interactive":
            self.interactive_model(self)

    def draw_network_x(self):
        G = x.DiGraph(directed=True)
        labels = {}
        node_colors = []
        count = 0
        for nodePub1, valNode in self.nodes.items():
            G.add_node(nodePub1, alias=("node " if valNode['alias'] == 'node' else valNode['alias']).replace(':', ''),
                       node_color='#2b83ba')
            if count < self.numNodes:
                labels[nodePub1] = valNode['alias']
                node_alias_pub1 = "node " if valNode['alias'] == 'node' else valNode['alias']
                node_colors.append(valNode['color'])
                if nodePub1 in self.edges:
                    for nodePub2, valueEdge in self.edges[nodePub1].items():
                        node_alias_pub2 = "node " if self.nodes[nodePub2]['alias'] == 'node' else \
                            self.nodes[nodePub2]['alias']
                        channel_id = policy1 = policy2 = last_update = ""
                        free_rate1 = time_lock_delta1 = free_rate2 = time_lock_delta2 = ''
                        weight = 0
                        flag = False
                        try:
                            if valueEdge['node1_policy'] and valueEdge['node1_policy']['disabled']:
                                policy1 = 'NODE1'
                                weight = valueEdge['node1_policy']['fee_rate_milli_msat']
                                free_rate1 = valueEdge['node1_policy']['fee_rate_milli_msat']
                                time_lock_delta1 = str(valueEdge['node1_policy']['time_lock_delta'])
                            if valueEdge['node2_policy'] and valueEdge['node2_policy']['disabled']:
                                policy2 = 'NODE2'
                                weight = valueEdge['node2_policy']['fee_rate_milli_msat']
                                free_rate2 = valueEdge['node2_policy']['fee_rate_milli_msat']
                                time_lock_delta2 = str(valueEdge['node2_policy']['time_lock_delta'])
                            flag = True if policy1 or policy2 else False
                            channel_id = valueEdge['channel_id']
                            capacity = valueEdge['capacity']
                            last_update = dt.datetime.utcfromtimestamp(valueEdge['last_update']) \
                                .strftime('%Y-%m-%d %H:%M:%S')
                        except TypeError:
                            wx.MessageBox(valueEdge['channel_id'])
                        if flag:
                            G.add_edge(nodePub1, nodePub2, channel_id=channel_id, last_update=self.surround(last_update),
                                       policy1=policy1, policy2=policy2,
                                       nodeAliasPub1=node_alias_pub1.replace(':', ""), nodeAliasPub2=node_alias_pub2
                                       .replace(':', ""),
                                       capacity=capacity, weight=weight, free_rate1=free_rate1,
                                       time_lock_delta1=time_lock_delta1, free_rate2=free_rate2,
                                       time_lock_delta2=time_lock_delta2)
                        else:
                            G.add_node(nodePub1)
                else:
                    G.add_node(nodePub1)
                count += 1
            else:
                if nodePub1 in G.nodes(data=True):
                    G.remove_node(nodePub1)

        pos = x.spring_layout(G)
        edge_attrs = {}
        index = 0
        for start_node, end_node, _ in G.edges(data=True):
            index += 1
            edge_attrs[(start_node, end_node)] = str(self.create_color(index))

        x.set_edge_attributes(G, edge_attrs, "edge_color")
        edge_labels = dict([((u, v,), d['capacity'])
                            for u, v, d in G.edges(data=True)])
        colors = range(20)
        plt.title('LIGHTNING NETWORK\nMODEL')
        options = {
            'labels': labels,
            'with_labels': True,
            'width': 2,
            'arrows': True,
            'node_color': node_colors
        }
        x.draw(G, pos, **options)
        x.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

        plt.axis('off')

        return G, x, labels

    def interactive_model(self, parent):
        engine = 'dot'
        nodes_size = .009
        arrow_size = .008
        palette = None
        graph_x = self.draw_network_x()[0]

        nodes = pd.DataFrame.from_dict(x.nx_pydot.pydot_layout(graph_x, prog=engine),
                                       orient="index", columns=["x", "y"])
        nodes.fillna('')

        for coord in ["x", "y"]:
            nodes[coord] -= np.asarray(nodes[coord].min())
            nodes[coord] /= np.asarray(nodes[coord].max())

        nodes["alias"] = ["".join(str(alias) for alias in graph_x.nodes[node]["alias"])
                          for node in nodes.index]

        idx = nodes.to_dict(orient="index")
        edges = pd.DataFrame(((src, idx[src]["x"], idx[src]["y"],
                               tgt, idx[tgt]["x"], idx[tgt]["y"],
                               "".join(self.surround(channel_id) for channel_id in val['channel_id']),
                               "".join(self.surround(last_update) for last_update in val['last_update']),
                               "".join(self.surround(node_alias_pub1) for node_alias_pub1 in val['nodeAliasPub1']),
                               "".join(self.surround(node_alias_pub2) for node_alias_pub2 in val['nodeAliasPub2']),
                               "".join(self.surround(capacity) for capacity in val['capacity']),
                               "".join(self.surround(policy1) for policy1 in val['policy1']),
                               "".join(self.surround(free_rate1) for free_rate1 in val['free_rate1']),
                               "".join(self.surround(time_lock_delta1) for time_lock_delta1 in val['time_lock_delta1']),
                               "".join(self.surround(policy2) for policy2 in val['policy2']),
                               "".join(self.surround(free_rate2) for free_rate2 in val['free_rate2']),
                               "".join(self.surround(time_lock_delta2) for time_lock_delta2 in val['time_lock_delta2']),
                               "".join(self.surround(edge_color) for edge_color in val['edge_color']))
                              for src, tgt, val in graph_x.edges(data=True)),
                             columns=["start", "x_start", "y_start",
                                      "end", "x_end", "y_end",
                                      "channel_id", "last_update",
                                      "nodeAliasPub1", "nodeAliasPub2",
                                      "capacity", "policy1", "free_rate1",
                                      "time_lock_delta1", "policy2", "free_rate2",
                                      "time_lock_delta2", "edge_color"])

        edges["slope"] = np.arctan2(edges["y_end"] - edges["y_start"],
                                    edges["x_end"] - edges["x_start"])

        edges["x_start"] += np.cos(edges["slope"]) * nodes_size
        edges["y_start"] += np.sin(edges["slope"]) * nodes_size
        edges["x_end"] -= np.cos(edges["slope"]) * nodes_size
        edges["y_end"] -= np.sin(edges["slope"]) * nodes_size
        edges["size"] = np.full(len(edges), arrow_size)

        pal = getattr(bkpal, palette or "Spectral4", bkpal.Spectral4)
        plot = bkp.figure(title="LN Modeling",
                          x_range=(-1.5 * nodes_size, 1 + 1.5 * nodes_size),
                          y_range=(-1.5 * nodes_size, 1 + 1.5 * nodes_size),
                          x_axis_location=None, y_axis_location=None,
                          outline_line_dash="dotted", width=1400, height=800, )
        plot.grid.visible = False

        graph = bkm.GraphRenderer()
        nodes_dict = {k: nodes[k] for k in nodes.columns}
        nodes_dict["index"] = nodes.index
        nodes_data = bkm.ColumnDataSource(data=nodes_dict)
        graph.node_renderer.data_source.data = dict(nodes_data.data)
        edges_dict = {k: edges[k] for k in edges.columns}
        edges_dict["xs"] = [(edges["x_start"][e], edges["x_end"][e])
                            for e in edges.index]
        edges_dict["ys"] = [(edges["y_start"][e], edges["y_end"][e])
                            for e in edges.index]
        edges_data = bkm.ColumnDataSource(data=edges_dict)
        graph.edge_renderer.data_source.data = dict(edges_data.data)

        layout = {i: [nodes["x"][n], nodes["y"][n]]
                  for i, n in enumerate(nodes.index)}
        graph.layout_provider = bkm.StaticLayoutProvider(graph_layout=layout)

        arrows = bkm.Arrow(end=bkm.NormalHead(size=arrow_size * 1000),
                           x_start="x_start",
                           y_start="y_start",
                           x_end="x_end",
                           y_end="y_end",
                           source=edges_data)
        plot.add_layout(arrows)

        graph.node_renderer.glyph = bkm.Circle(radius=nodes_size,
                                               fill_color=pal[0], line_color="#3288bd", line_width=3,
                                               fill_alpha=.5)
        graph.node_renderer.selection_glyph = bkm.Circle(radius=nodes_size,
                                                         fill_color=pal[2],
                                                         fill_alpha=.5)
        graph.node_renderer.hover_glyph = bkm.Circle(radius=nodes_size,
                                                     fill_color=pal[1],
                                                     fill_alpha=.5)
        graph.edge_renderer.glyph = bkm.MultiLine(line_color="edge_color",
                                                  line_alpha=0.8, line_width=2.5)
        graph.edge_renderer.selection_glyph = bkm.MultiLine(line_color=pal[2],
                                                            line_width=2.5)
        graph.edge_renderer.hover_glyph = bkm.MultiLine(line_color=pal[1],
                                                        line_width=2.5)

        graph.selection_policy = bkm.NodesAndLinkedEdges()
        graph.inspection_policy = bkm.EdgesAndLinkedNodes()
        plot.renderers.append(graph)
        plot.add_tools(bkm.TapTool(),
                       bkm.LassoSelectTool(),
                       bkm.BoxSelectTool(),
                       bkm.HoverTool(tooltips=[("Channel ID:", "@channel_id"),
                                               ("Last Update:", "@last_update"),
                                               ("Node AliasPub1:", "@nodeAliasPub1"),
                                               ("Node AliasPub2:", "@nodeAliasPub2"),
                                               ("Capacity:", "@capacity"),
                                               ("Policy:", "@policy1"),
                                               ("Free Rate:", "@free_rate1"),
                                               ("Time Lock Delta:", "@time_lock_delta1"),
                                               ("Policy:", "@policy2"),
                                               ("Free Rate:", "@free_rate2"),
                                               ("Time Lock Delta:", "@time_lock_delta2")]))
        bkio.output_file("LN.html", title="LN Modeling")
        bkio.show(plot)
        wx.MessageBox("Graph generated!!!")

    def static_model(self, parent):
        self.fig = plt.figure()
        canvas = FigureCanvas(self, -1, self.fig)
        graph = self.draw_network_x()

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        toolbar = NavigationToolbar(canvas)
        vbox.Add(toolbar, 0, wx.EXPAND)
        self.SetSizer(vbox)
        vbox.Fit(self)

    @staticmethod
    def create_color(index):
        val = ''
        colors = itertools.cycle(palette)
        for color in zip(range(index), colors):
            val = color

        return val[1]

    def path_nodes(self, path):
        graph = self.draw_network_x()
        if path[0] in graph[0] and path[1] in graph[0]:
            try:
                path = x.shortest_path(graph[0], path[0], path[1])
                message = ""
                for node in path:
                    # message = message + node + ' - ' + self.nodes[node]['alias'] + '\n'
                    message = message + ' - ' + self.nodes[node]['alias'] + '\n'

                # wx.MessageBox(message)
                self.fig = plt.figure()
                canvas = FigureCanvas(self, -1, self.fig)

                path_edges = list(zip(path, path[1:]))
                pos = x.spring_layout(graph[0])
                plt.title('LIGHTNING NETWORK\nMODEL')
                plt.text(-1, -1, message, dict(size=10), wrap=True, color='g')
                options = {
                    'labels': graph[2],
                    'with_labels': True,
                    'width': 2,
                    'arrows': True
                }
                x.draw(graph[0], pos, node_color='k', **options)
                x.draw_networkx_nodes(graph[0], pos, nodelist=path, node_color='r')
                x.draw_networkx_edges(graph[0], pos, edgelist=path_edges, edge_color='r', width=2)
                plt.axis('equal')

                vbox = wx.BoxSizer(wx.VERTICAL)
                vbox.Add(canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
                toolbar = NavigationToolbar(canvas)
                vbox.Add(toolbar, 0, wx.EXPAND)
                self.SetSizer(vbox)
                vbox.Fit(self)
            except x.NetworkXNoPath:
                wx.MessageBox("There is no path between two nodes: %s - %s " % (path[0], path[1]))
        else:
            wx.MessageBox("No nodes in the graph")

    @staticmethod
    def surround(value):
        value = str(value)
        if value.find(":"):
            return '"' + value + '"'
        return value
