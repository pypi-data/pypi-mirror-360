from generalutils import coneSearchHTMCassandra
from cassandra.cluster import Cluster

keyspace = 'test01'
host = ['localhost']
table = 'atlasdophot'

ra = 83.20546
dec = -20.70055
radius = 2.0

cluster = Cluster(host)
session = cluster.connect()
session.set_keyspace(keyspace)

data = coneSearchHTMCassandra(session, ra, dec, radius, table)
print(data)

cluster.shutdown()

