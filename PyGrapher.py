#!/usr/bin/python2
# Import graphviz
from optparse import OptionParser
import sys
#sys.path.append('..')
#sys.path.append('/usr/lib/python2.7/site-packages/graphviz')
#sys.path.append('/usr/lib/graphviz/python/')
#sys.path.append('/usr/lib64/graphviz/python/')
import gv

from pygraph.classes.graph import graph
from pygraph.classes.digraph import digraph
from pygraph.algorithms.searching import breadth_first_search
from pygraph.readwrite.dot import write

class GraphContainer:
    def __init__(self, graph_csv_file, threshold = -1):
        self.nodes = list()
        self.edges = list()
        self.threshold = threshold
        self.max_weight = 0
        self._parseCSV(graph_csv_file)

    def _parseCSV(self, csv_file):
        f = open(csv_file, 'r')
        # get unique nodes and lode the vertices into tuples
        for line in f:
            # split on comma and strip any whitespace on the element
            elements = map(str.strip, line.split(','))

            # keep track of max weight for normalizing later
            if float(elements[2]) > self.max_weight:
                self.max_weight = float(elements[2])

            elements.append('fillcolor = red')
            self.edges.append(elements)

            #print str(elements)
            if elements[0] not in self.nodes:
                self.nodes.append(elements[0])

            if elements[1] not in self.nodes:
                self.nodes.append(elements[1])

    def nodeNamesToAlpha(self):
        start_char = 'A'

        # keep mapping of original node names
        name_to_alpha_map = dict()
        new_nodes = list()
        for node in self.nodes:
            #store name mapping and increment the alpha
            new_name = start_char
            name_to_alpha_map[node] = new_name
            new_nodes.append( new_name )
            start_char = chr(ord(start_char) + 1)

        self.nodes = new_nodes

        #go through edges and replace the names
        for edge in self.edges:
            edge[0] = name_to_alpha_map[edge[0]]
            edge[1] = name_to_alpha_map[edge[1]]
        #print str(self.edges)
        print str(self.nodes)
        #print str(name_to_alpha_map)


class PyGrapher:
    def __init__(self, graph_container, threshold = 0):
        self.graph_container = graph_container
        self.gr = graph()

        self.weight_thresh = float(threshold)

        print "weight threshold set:: " + str(self.weight_thresh)
        self._buildGraph(self.graph_container)

    def _buildGraph(self, graph_container):
        sat = 1.0
        val = 1.0
        for node in self.graph_container.nodes:
            self.gr.add_node(node)
            #print "Adding Nodes: " + str(node)

        for edge in self.graph_container.edges:
            # normalize
            norm_weight = float(edge[2]) / self.graph_container.max_weight

            #only add the edge if the weight is above the threshold
            if norm_weight > self.weight_thresh:

                # add the edge with a label
                #self.gr.add_edge(edge[0:2], float(edge[2]), label=str(norm_weight))
                self.gr.add_edge(edge[0:2], float(edge[2]), label="{0:.3f}".format(norm_weight))

                # calculate the color and thickniss of the pen
                hue = 1.0 - norm_weight
                color_tuple = ('color', str(hue) + " " + " " + str(sat) + " " + str(val))
                penWidth_tuple = ('penwidth', str(norm_weight * 5))

                # set edge attributes (color and width)
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

def parseArguments(inputs, pngs, svgs):

    png_outs = None
    svg_outs = None
    ins = map(str.strip, inputs.split(','))
    if pngs is not None:
        png_outs = map(str.strip, pngs.split(','))

    if svgs is not None:
        svg_outs = map(str.strip, svgs.split(','))

    file_tuples = list()
    count = 0

    for _in in ins:
        file_tuples.append( (_in,
                             png_outs[count] if png_outs != None else None,
                             svg_outs[count] if svg_outs != None else None) )
        count += 1

    return file_tuples


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-s", "--svg-file", dest="svg_output", default = None,
                        help="File to save svg graph to")

    parser.add_option("-p", "--png-file", dest="png_output", default = None,
                        help="File to save png graph to")

    parser.add_option("-i", "--input-csv", dest="input_csv_file", default = None,
                        help="Path to a fie containing line delimited csv of <node>,<node>,<edge weight>")

    parser.add_option("-t", "--threshold", dest="norm_threshold", default = 0,
                        help="Threshold for weight, if below threshold, the edge will not be drawn")

    parser.add_option("-a", "--alpha-names", dest="alpha_names_set", default = False,
                        action="store_true", help="Replace node names in file with letters")


    parser.add_option("-d", "--debug", dest="debug_on", default=False,
                        action="store_true",
                        help="Print data verbosely to the screen")

    (options, args) = parser.parse_args()

    file_tuples = parseArguments(options.input_csv_file, options.png_output, options.svg_output)


    for file_tuple in file_tuples:
        print "Parsing input file " + file_tuple[0] + "..."
        graph_container = GraphContainer(file_tuple[0], float(options.norm_threshold))

        if options.alpha_names_set:
            graph_container.nodeNamesToAlpha()

        print "\tBuilding graph..."
        grapher = PyGrapher(graph_container, float(options.norm_threshold))
        if options.svg_output is not None:
            grapher.saveGraphSVG(file_tuple[2])

        if options.png_output is not None:
            grapher.saveGraphPNG(file_tuple[1])
