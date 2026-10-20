
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()


def find_transport_partners(origin, destination, min_capacity=0):
    uri = os.getenv("NEO4J_URI")
    username = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")

    query = """
    MATCH (p:TransportPartner)-[:OPERATES]->(t:Truck)
    MATCH (p)-[:SERVES]->(r:Route)
    MATCH (r)-[:STARTS_AT]->(o:City)
    MATCH (r)-[:ENDS_AT]->(d:City)
    WHERE toLower(o.name) = toLower($origin)
      AND toLower(d.name) = toLower($destination)
      AND t.capacity_tons >= $min_capacity
      AND t.available = true
    RETURN p.name AS partner,
           t.truck_id AS truck_id,
           t.capacity_tons AS capacity_tons,
           t.truck_type AS truck_type,
           r.distance_km AS distance_km,
           o.name AS origin,
           d.name AS destination
    """

    with GraphDatabase.driver(
        uri, auth=(username, password)
    ) as driver:
        records, _, _ = driver.execute_query(
            query,
            origin=origin,
            destination=destination,
            min_capacity=min_capacity,
            database_="34531ae9",
        )
        return [record.data() for record in records]


if __name__ == "__main__":
    results = find_transport_partners(
        origin="Coimbatore",
        destination="Chennai",
        min_capacity=10,
    )

    if results:
        for item in results:
            print(item)
    else:
        print("No matching transport partners found.")
