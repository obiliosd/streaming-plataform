CREATE KEYSPACE sparkstreaming 
WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : '1'} ;