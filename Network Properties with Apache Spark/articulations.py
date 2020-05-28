import sys
import time
import networkx as nx
from pyspark import SparkContext
from pyspark.sql import SQLContext
from pyspark.sql import functions
from graphframes import *
from copy import deepcopy

sc=SparkContext("local", "degree.py")
sqlContext = SQLContext(sc)

def articulations(g, usegraphframe=False):
	# Get the starting count of connected components
	components_count = g.connectedComponents().select('component').distinct().count()
	print(components_count)

	# Default version sparkifies the connected components process 
	# and serializes node iteration.
	if usegraphframe:
		# Get vertex list for serial iteration
		vert_list = list(g.vertices.map(lambda x: x[0]).collect())
		output_list = []

		# For each vertex, generate a new graphframe missing that vertex
		# and calculate connected component count. Then append count to
		# the output
		for vertex in vert_list:
			v = g.filter('id != "' + vertex + '"')
			e = g.filter('src != "' + vertex + '"').filter('dst != "' + vertex + '"')
			g2 = GraphFrame(v,e)
			new_count = g2.connectedComponents().select('component').distinct().count()
			if new_count > components_count:
				output_list.append((vertex,1))
			else:
				output_list.append((vertex,0))
		output_df = sqlContext.createDataFrame(sc.parallelize(output_list), ['id','articulation'])
		return output_df
	# Non-default version sparkifies node iteration and uses networkx 
	# for connected components count.
	else:
		g2 = nx.Graph()
		vert_list = list(g.vertices.map(lambda x: x[0]).collect())
		g2.add_nodes_from(vert_list)
		edge_list = list(g.edges.map(lambda x: (x.src,x.dst)).collect())
		g2.add_edges_from(edge_list)

		output_list = []
		for i in range(len(vert_list)):
			g = deepcopy(g2)
			g.remove_node(vert_list[i])
			new_count = nx.number_connected_components(g)
			if new_count > components_count:
				output_list.append((vert_list[i],1))
			else:
				output_list.append((vert_list[i],0))
		output_df = sqlContext.createDataFrame(sc.parallelize(output_list), ['id','articulation'])
		return output_df
		

filename = sys.argv[1]
lines = sc.textFile(filename)

pairs = lines.map(lambda s: s.split(","))
e = sqlContext.createDataFrame(pairs,['src','dst'])
e = e.unionAll(e.selectExpr('src as dst','dst as src')).distinct() # Ensure undirectedness 	

# Extract all endpoints from input file and make a single column frame.
v = e.selectExpr('src as id').unionAll(e.selectExpr('dst as id')).distinct()	

# Create graphframe from the vertices and edges.
g = GraphFrame(v,e)

#Runtime approximately 5 minutes
print("---------------------------")
print("Processing graph using Spark iteration over nodes and serial (networkx) connectedness calculations")
init = time.time()
df = articulations(g, False)
print("Execution time: %s seconds" % (time.time() - init))
print("Articulation points:")
df.filter('articulation = 1').show(truncate=False)
df.filter('articulation = 1').toPandas().to_csv("articulations_out.csv")
print("---------------------------")

#Runtime for below is more than 2 hours
print("Processing graph using serial iteration over nodes and GraphFrame connectedness calculations")
init = time.time()
df = articulations(g, True)
print("Execution time: %s seconds" % (time.time() - init))
print("Articulation points:")
df.filter('articulation = 1').show(truncate=False)
df.filter('articulation = 1').toPandas().to_csv("articulations_out_false.csv")
