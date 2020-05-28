from pyspark import SparkContext
from pyspark.sql import SQLContext
from pyspark.sql import functions
from graphframes import *
from pyspark.sql.functions import explode

sc=SparkContext("local", "degree.py")
sqlContext = SQLContext(sc)

def closeness(g):
	
	# Get list of vertices. We'll generate all the shortest paths at
	# once using this list.
	vert_list = list(g.vertices.map(lambda x: x[0]).collect())

	# first get all the path lengths.
	path_lengths = g.shortestPaths(landmarks = vert_list)

	# Break up the map and group by ID for summing
	path_lengths = path_lengths.select(functions.explode('distances')).groupBy('key')

	# Sum by ID
	summation = path_lengths.agg(functions.sum('value').alias('summation'))

	# Get the inverses and generate desired dataframe.
	closeness_df = summation.map(lambda x: (x.key, 1/float(x.summation)))
	return sqlContext.createDataFrame(closeness_df, ['id', 'closeness'])



print("Reading in graph for problem 2.")
graph = sc.parallelize([('A','B'),('A','C'),('A','D'),
	('B','A'),('B','C'),('B','D'),('B','E'),
	('C','A'),('C','B'),('C','D'),('C','F'),('C','H'),
	('D','A'),('D','B'),('D','C'),('D','E'),('D','F'),('D','G'),
	('E','B'),('E','D'),('E','F'),('E','G'),
	('F','C'),('F','D'),('F','E'),('F','G'),('F','H'),
	('G','D'),('G','E'),('G','F'),
	('H','C'),('H','F'),('H','I'),
	('I','H'),('I','J'),
	('J','I')])
	
e = sqlContext.createDataFrame(graph,['src','dst'])
v = e.selectExpr('src as id').unionAll(e.selectExpr('dst as id')).distinct()
print("Generating GraphFrame.")
g = GraphFrame(v,e)

print("Calculating closeness.")
Closeness = closeness(g).sort('closeness',ascending=False)
Closeness.show()
print("Writing output to file centrality_out.csv")
Closeness.toPandas().to_csv("centrality_out.csv")
