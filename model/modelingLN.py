import wx
import os
import json

from graphLN import GraphLN as stat


def on_about(event):
    wx.MessageBox("Lightning Network", "Modeling of LIGHTNING NETWORK", wx.OK | wx.ICON_INFORMATION)


class MainFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        # Parent's init invoked
        self.numNodeGraph = None
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        super(MainFrame, self).__init__(*args, **kwargs, size=(1250, 700))

        # Split Panels
        self.panel = MainPanel(self)

        # MenuBar
        self.create_menu_bar()

        # Status bar
        self.CreateStatusBar()
        self.SetStatusText("Lightning Network")

        self.Show()

    def create_menu_bar(self):
        file_menu = wx.Menu()
        items = file_menu.Append(-1, "&Load File ...\tCtrl-L", "Load File to populate the graph")
        file_menu.AppendSeparator()
        exit_item = file_menu.Append(wx.ID_EXIT)

        help_menu = wx.Menu()
        about_item = help_menu.Append(wx.ID_ABOUT)

        menu_bar = wx.MenuBar()
        menu_bar.Append(file_menu, "&File")
        menu_bar.Append(help_menu, "&Help")

        self.SetMenuBar(menu_bar)

        self.Bind(wx.EVT_MENU, self.on_open, items)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        self.Bind(wx.EVT_MENU, on_about, about_item)

    def on_exit(self, event):
        self.Close(True)

    def on_open(self, event):
        # wx.MessageBox("Load File here")
        wildcard = "JSON files (*.json)|*.json"
        dialog = wx.FileDialog(self, "Open Text Files", wildcard=wildcard,
                               style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if dialog.ShowModal() == wx.ID_CANCEL:
            return

        path = dialog.GetPath()

        if os.path.exists(path):
            try:
                self.panel.jsonData = json.loads(open(path).read())
                if self.panel.jsonData is not None:
                    index = 0
                    self.panel.node_list.DeleteAllItems()
                    self.panel.edges = self.panel.nodes = {}
                    for node in self.panel.jsonData['nodes']:
                        self.panel.node_list.InsertItem(index, node['pub_key'])
                        self.panel.node_list.SetItem(index, 1, node['alias'])
                        self.panel.nodes.update({node['pub_key']: node})
                        index += 1

                        self.panel.nodes_pub1.Append(node['alias'], node['pub_key'])
                        self.panel.nodes_pub2.Append(node['alias'], node['pub_key'])

                    self.panel.numNodes.SetMax(len(self.panel.nodes))
                    self.panel.numNodes.SetValue(len(self.panel.nodes))
                    self.numNodeGraph = len(self.panel.nodes)

                    self.panel.edges = {}
                    for edge in self.panel.jsonData['edges']:
                        self.populate_edges('node1_pub', 'node2_pub', edge)

                    self.panel.edge_list.DeleteAllItems()
                    self.panel.node_info.Clear()
                    self.panel.edge_info.Clear()

                    wx.MessageBox("File uploaded successfully", "JSON DATA", wx.OK | wx.ICON_INFORMATION)
            except ValueError:
                print(ValueError)
                wx.MessageBox("JSON data malformed", "JSON DATA", wx.OK | wx.ICON_STOP)

    def populate_edges(self, node_pub2, node_pub1, edge):
        val_child = {}
        if edge[node_pub1] in self.panel.edges:
            val_child = self.panel.edges[edge[node_pub1]]
            val_child.update({edge[node_pub2]: edge})

        if not val_child:
            val_child = {edge[node_pub2]: edge}
        self.panel.edges.update({edge[node_pub1]: val_child})
        '''print(edge[nodeP])'''


class MainPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        # DECLARATION OF VARIABLES
        self.currentItem = None
        self.jsonData = self.nodes = self.edges = None
        self.valueNodePub1 = self.valueNodePub2 = None
        self.numNodeGraph = 0

        # Add SplitterWindow panels
        main_splitter = wx.SplitterWindow(self)

        top_split = wx.Panel(main_splitter, style=wx.FIXED_LENGTH)
        bottom_split = wx.Panel(main_splitter, style=wx.FIXED_LENGTH)
        main_splitter.SplitHorizontally(top_split, bottom_split, 120)

        # TOP SPLIT WINDOW
        lbl_principal = wx.StaticText(top_split, -1, u"LOAD A JSON FILE BEFORE\nGENERATING A MODEL", size=(270, 40),
                                      pos=(560, 10),
                                      style=wx.ALIGN_CENTER)
        font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL)
        lbl_principal.SetFont(font)

        btn_interactive_model_ln = wx.Button(top_split, -1, "Graph Interactive Model", size=(200, 40), pos=(50, 60))
        btn_static_model_ln = wx.Button(top_split, -1, "Graph Static Model", size=(200, 40), pos=(300, 60))

        lbl_node_pub1 = wx.StaticText(top_split, -1, u"NODE PUB 1", size=(200, 20),
                                      pos=(550, 40), style=wx.ALIGN_CENTER)
        self.nodes_pub1 = wx.ComboBox(top_split, -1, "", pos=(550, 60), size=(200, 40), style=wx.CB_READONLY)

        lbl_node_pub2 = wx.StaticText(top_split, -1, u"NODE PUB 2", size=(200, 20),
                                      pos=(800, 40), style=wx.ALIGN_CENTER)
        self.nodes_pub2 = wx.ComboBox(top_split, -1, "", pos=(800, 60), size=(200, 40), style=wx.CB_READONLY)
        btn_path_nodes = wx.Button(top_split, -1, "Graph Path Nodes", size=(200, 40), pos=(1050, 60))

        self.numNodes = wx.Slider(top_split, value=10, minValue=1, maxValue=10, style=wx.SL_HORIZONTAL | wx.SL_LABELS,
                                  size=(200, 50))

        # BUTTON SPLIT WINDOW
        self.node_list = wx.ListCtrl(
            bottom_split,
            pos=(0, 0),
            size=(600, 300),
            style=wx.LC_REPORT | wx.BORDER_SUNKEN
        )
        self.node_list.InsertColumn(0, "NODES_PUB1", width=400)
        self.node_list.InsertColumn(1, "ALIAS", width=200)

        self.node_info = wx.TextCtrl(
            bottom_split,
            pos=(0, 300),
            size=(600, 200),
            value="NODE INFO",
            style=wx.TE_MULTILINE | wx.TE_READONLY
        )

        self.edge_list = wx.ListCtrl(
            bottom_split,
            pos=(600, 0),
            size=(600, 300),
            style=wx.LC_REPORT | wx.BORDER_SUNKEN
        )
        self.edge_list.InsertColumn(0, "NODE_PUB2", width=300)
        self.edge_list.InsertColumn(1, "ALIAS", width=150)
        self.edge_list.InsertColumn(2, 'CHANNEL ID', width=150)
        self.edge_list.InsertColumn(3, "NODE_PUB1", width=0)

        self.edge_info = wx.TextCtrl(
            bottom_split,
            pos=(600, 300),
            size=(600, 200),
            value="EDGE INFO",
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.EXPAND
        )

        # EVENTS OVER CONTROLS
        btn_interactive_model_ln.Bind(wx.EVT_BUTTON, self.generate_interactive_model_ln)
        btn_static_model_ln.Bind(wx.EVT_BUTTON, self.generate_static_model_ln)
        btn_path_nodes.Bind(wx.EVT_BUTTON, self.generate_path_nodes)

        self.node_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.show_node_info)
        self.edge_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.show_edge_info)
        self.nodes_pub1.Bind(wx.EVT_COMBOBOX, self.set_node_pub1)
        self.nodes_pub2.Bind(wx.EVT_COMBOBOX, self.set_node_pub2)
        self.numNodes.Bind(wx.EVT_SLIDER, self.get_num_nodes)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(main_splitter, 1, wx.EXPAND)
        self.SetSizer(sizer)

    def show_node_info(self, event):
        node = event.GetText().replace(" ", "-")
        self.node_info.Clear()
        self.edge_info.Clear()
        self.node_info.WriteText(json.dumps(self.nodes[node], indent=3, sort_keys=False))

        self.edge_list.DeleteAllItems()
        if node in self.edges:
            index = 0
            for node2, keyValue in self.edges[node].items():
                self.edge_list.InsertItem(index, node2)
                self.edge_list.SetItem(index, 1, self.nodes[node2]['alias'])
                self.edge_list.SetItem(index, 2, keyValue['channel_id'])
                self.edge_list.SetItem(index, 3, node)
                index += 1

    def show_edge_info(self, event):
        self.currentItem = event.Index
        '''print('OnItemSelected: "%s", "%s"\n' %
              (self.currentItem,
               self.edge_list.GetItemText(self.currentItem)))'''

        node = event.GetText().replace(" ", "-")
        self.edge_info.Clear()
        self.edge_info.WriteText(
            json.dumps(self.edges[self.edge_list.GetItemText(event.Index, 3)][node], indent=3, sort_keys=False))

    def set_node_pub1(self, event):
        self.valueNodePub1 = self.nodes_pub1.GetClientData(self.nodes_pub1.GetSelection())
        wx.MessageBox("NODE PUB1 SELECTED: " + self.valueNodePub1)

    def set_node_pub2(self, event):
        self.valueNodePub2 = self.nodes_pub2.GetClientData(self.nodes_pub2.GetSelection())
        wx.MessageBox("NODE PUB2 SELECTED: " + self.valueNodePub2)

    def get_num_nodes(self, event):
        self.numNodeGraph = event.GetEventObject().GetValue()

    def generate_interactive_model_ln(self, event):
        if self.jsonData is None:
            wx.MessageBox("First upload the file!!!")
        else:
            edges_nodes = [self.nodes, self.edges, self.numNodeGraph if self.numNodeGraph > 0 else len(self.nodes)]
            stat(edges_nodes, "interactive", None, None, title='LN Static Modeling')

    def generate_static_model_ln(self, event):
        if self.jsonData is None:
            wx.MessageBox("First upload the file!!!")
        else:
            edges_nodes = [self.nodes, self.edges, self.numNodeGraph if self.numNodeGraph > 0 else len(self.nodes)]
            stat(edges_nodes, "static", None, None, title='LN Static Modeling')

    def generate_path_nodes(self, event):
        if self.jsonData is None:
            wx.MessageBox("First upload the file!!!")
        else:
            if self.valueNodePub1 and self.valueNodePub2:
                edges_nodes = [self.nodes, self.edges, self.numNodeGraph if self.numNodeGraph > 0 else len(self.nodes)]
                path = [self.valueNodePub1, self.valueNodePub2]
                stat(edges_nodes, "path", path, None, title='LN Static Modeling')
            else:
                wx.MessageBox("Select both Node Pub1 and Pub2")


if __name__ == '__main__':
    app = wx.App()
    frm = MainFrame(None, title='LN Modeling')
    app.MainLoop()
