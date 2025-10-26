# test_connection.py
from core.db_config import Neo4jConnection

if __name__ == "__main__":
    conn = Neo4jConnection()
    conn.verify()      # should print "Connected to Neo4j AuraDB ..."
    conn.close()
