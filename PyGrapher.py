#!/usr/bin/python2
# Import graphviz
from optparse import OptionParser
import sys
sys.path.append('..')
sys.path.append('/usr/lib/python2.7/site-packages/graphviz')
#sys.path.append('/usr/lib/graphviz/python/')
#sys.path.append('/usr/lib64/graphviz/python/')
import gv

from pygraph.classes.graph import graph
from pygraph.classes.digraph import digraph
from pygraph.algorithms.searching import breadth_first_search
from pygraph.readwrite.dot import write

class GraphContainer:
    def __init__(self, graph_csv_file):
        self.nodes = list()
        self.edges = list()
        self.max_weight = 0
        self._parseCSV(graph_csv_file)

    def _parseCSV(self, csv_file):
        f = open(csv_file, 'r')
        # get unique nodes and lode the vertices into tuples
        for line in f:
            # split on comma and strip any whitespace on the element
            elements = map(str.strip, line.split(','))

            print "FOUND: " + str(elements)

            elements.append('fillcolor = red')
            self.edges.append(elements)

            if float(elements[2]) > self.max_weight:
                self.max_weight = float(elements[2])

            #print str(elements)
            if elements[0] not in self.nodes:
                self.nodes.append(elements[0])

            if elements[1] not in self.nodes:
                self.nodes.append(elements[1])


class PyGrapher:
    def __init__(self, graph_container):
        self.graph_container = graph_container
        self.gr = graph()

        self.weight_thresh = 0

        # edge coloring
        self.e_hue = .5
        self.e_sat = 1.0
        self.e_val = 1.0

        self._buildGraph(self.graph_container)

    def _buildGraph(self, graph_container):
        for node in self.graph_container.nodes:
            self.gr.add_node(node)
            print "Adding Nodes: " + str(node)
            #gr.add_node_attribute(node, ('fillcolor', "red"))

        hue = .5
        sat = 1.0
        val = 1.0
        for edge in self.graph_container.edges:
            if float(edge[2]) > self.weight_thresh:
                norm_weight = float(edge[2]) / self.graph_container.max_weight
                self.gr.add_edge(edge[0:2], float(edge[2]), label=str(norm_weight))

                hue = 1.0 - norm_weight
                color_tuple = ('color', str(hue) + " " + " " + str(sat) + " " + str(val))
                penWidth_tuple = ('penwidth', str(norm_weight * 5))

                self.gr.add_edge_attribute((edge[0], edge[1]), color_tuple)
                self.gr.add_edge_attribute((edge[0], edge[1]), penWidth_tuple)

    def saveGraphPNG(self, png_filename):
        dot = write(self.gr)
        gvv = gv.readstring(dot)
        gv.layout(gvv, 'dot')
        gv.render(gvv, 'png', png_filename)

    def saveGraphSVG(self, svg_filename):
        dot = write(self.gr)
        gvv = gv.readstring(dot)
        gv.layout(gvv, 'dot')
        gv.render(gvv, 'svg', svg_filename)


#f = open('graph_1.csv', 'r')
#
#nodes = list()
#edges = list()
#max_weight = 0
## get unique nodes and lode the vertices into tuples
#for line in f:
#    # split on comma and strip any whitespace on the element
#    elements = map(str.strip, line.split(','))
#
#    elements.append('fillcolor = red')
#    edges.append(elements)
#
#    if int(elements[2]) > max_weight:
#        max_weight = int(elements[2])
#
#    #print str(elements)
#    if elements[0] not in nodes:
#        nodes.append(elements[0])
#
#    if elements[1] not in nodes:
#        nodes.append(elements[1])
#
#print str(nodes)
#
#gr = graph()
#
#for node in nodes:
#    #gr.add_node(node,[('fillcolor', 'red')])
#    gr.add_node(node)
#    gr.add_node_attribute(node, ('fillcolor', "red"))
#
#threshold = 0
#hue = .5
#sat = 1.0
#val = 1.0
#for edge in edges:
#    if int(edge[2]) > threshold:
#        print "Adding: " + str(edge[0:2]) + " with weight: " + str(edge[2])
#        norm_weight = float(edge[2])/max_weight
#        gr.add_edge(edge[0:2], int(edge[2]), label=str(norm_weight))
#        hue = 1.0 - norm_weight
#        color_tuple = ('color', str(hue)+ " "+ " " + str(sat) + " " + str(val))
#        penWidth_tuple = ('penwidth', str(norm_weight * 5))
#        gr.add_edge_attribute((edge[0],edge[1]), color_tuple)
#        gr.add_edge_attribute((edge[0],edge[1]), penWidth_tuple)
#
#
#
#dot = write(gr)
#print "DOT: " + str(dot)
#gvv = gv.readstring(dot)
#gv.layout(gvv,'dot')
#gv.render(gvv,'png','mpi.png')
#gv.render(gvv,'svg','mpi.svg')

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-s", "--svg-file", dest="svg_output", default = None,
                        help="File to save svg graph to")

    parser.add_option("-p", "--png-file", dest="png_output", default = None,
                        help="File to save png graph to")

    parser.add_option("-i", "--input-csv", dest="input_csv_file", default = None,
                        help="Path to a fie containing line delimited csv of <node>,<node>,<edge weight>")

#    parser.add_option("-l", "--listen-socks", dest="listen", action="store_true",default = False,
#                        help="Only monitor listening sockets ('-l' option in netstat)")

    parser.add_option("-d", "--debug", dest="debug_on", default=False,
                        action="store_true",
                        help="Print data verbosely to the screen")

    (options, args) = parser.parse_args()

    print "Making container..."
    graph_container = GraphContainer(options.input_csv_file)

    grapher = PyGrapher(graph_container)
    if options.svg_output is not None:
        grapher.saveGraphPNG(options.svg_output)

    if options.png_output is not None:
        grapher.saveGraphPNG(options.png_output)
