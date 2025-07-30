from typing import Optional, Dict, Any, List
from psycopg import Connection


# AGE-specific operations
def execute_cypher(conn: Connection, graph_name: str, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict]:
    """Execute a Cypher query and return results."""
    # Prepare the AGE query
    age_query = f"SELECT * FROM cypher('{graph_name}', $${query}$$) as (result agtype);"
    with conn.cursor() as cur:
        cur.execute(age_query, params or {})
        return cur.fetchall()

def execute_cypher_single(conn: Connection, graph_name: str, query: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict]:
    """Execute a Cypher query and return single result."""
    results = execute_cypher(conn, graph_name, query, params)
    return results[0] if results else None

def create_graph(conn: Connection, graph_name: str) -> bool:
    """Create the AGE graph if it doesn't exist."""
    try:
        query = f"SELECT create_graph('{graph_name}');"
        with conn.cursor() as cur:
            cur.execute(query)
        return True
    except Exception:
        # Graph might already exist
        return False

def drop_graph(conn: Connection, graph_name: str) -> bool:
    """Drop the AGE graph."""
    try:
        query = f"SELECT drop_graph('{graph_name}', true);"
        with conn.cursor() as cur:
            cur.execute(query)
        return True
    except Exception:
        return False


# Utility methods

def create_node(conn: Connection, graph_name: str, label: str, properties: Dict[str, Any]) -> Optional[Dict]:
    """Create a node with given label and properties."""
    props_str = ", ".join([f"{k}: '{v}'" for k, v in properties.items()])
    query = f"CREATE (n:{label} {{{props_str}}}) RETURN n"
    return execute_cypher_single(conn, graph_name, query)

def create_edge(conn: Connection, graph_name: str, from_node_id: str, to_node_id: str, edge_type: str, 
                properties: Optional[Dict[str, Any]] = None) -> Optional[Dict]:
    """Create an edge between two nodes."""
    props_str = ""
    if properties:
        props_str = "{" + ", ".join([f"{k}: '{v}'" for k, v in properties.items()]) + "}"
    
    query = f"""
    MATCH (a), (b) 
    WHERE id(a) = {from_node_id} AND id(b) = {to_node_id}
    CREATE (a)-[r:{edge_type} {props_str}]->(b) 
    RETURN r
    """
    return execute_cypher_single(conn, graph_name, query)

def find_nodes(conn: Connection, graph_name: str, label: Optional[str] = None, 
                properties: Optional[Dict[str, Any]] = None) -> List[Dict]:
    """Find nodes by label and/or properties."""
    query = "MATCH (n"
    if label:
        query += f":{label}"
    query += ")"
    
    if properties:
        where_clauses = [f"n.{k} = '{v}'" for k, v in properties.items()]
        query += " WHERE " + " AND ".join(where_clauses)
    
    query += " RETURN n"
    return execute_cypher(conn, graph_name, query)
