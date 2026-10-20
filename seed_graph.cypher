
MERGE (coimbatore:City {name: "Coimbatore"})
MERGE (chennai:City {name: "Chennai"})
MERGE (bangalore:City {name: "Bengaluru"})
MERGE (madurai:City {name: "Madurai"})

MERGE (srk:TransportPartner {name: "SRK Transport"})
MERGE (alpha:TransportPartner {name: "Alpha Logistics"})
MERGE (fast:TransportPartner {name: "FastTrack Transport"})

MERGE (t1:Truck {truck_id: "TRK001"})
SET t1.capacity_tons = 10,
    t1.truck_type = "Open Truck",
    t1.available = true

MERGE (t2:Truck {truck_id: "TRK002"})
SET t2.capacity_tons = 5,
    t2.truck_type = "Closed Truck",
    t2.available = true

MERGE (t3:Truck {truck_id: "TRK003"})
SET t3.capacity_tons = 15,
    t3.truck_type = "Container Truck",
    t3.available = true

MERGE (srk)-[:OPERATES]->(t1)
MERGE (alpha)-[:OPERATES]->(t2)
MERGE (fast)-[:OPERATES]->(t3)

MERGE (r1:Route {route_id: "R001"})
SET r1.distance_km = 500
MERGE (r1)-[:STARTS_AT]->(coimbatore)
MERGE (r1)-[:ENDS_AT]->(chennai)
MERGE (srk)-[:SERVES]->(r1)

MERGE (r2:Route {route_id: "R002"})
SET r2.distance_km = 350
MERGE (r2)-[:STARTS_AT]->(coimbatore)
MERGE (r2)-[:ENDS_AT]->(bangalore)
MERGE (alpha)-[:SERVES]->(r2)

MERGE (r3:Route {route_id: "R003"})
SET r3.distance_km = 220
MERGE (r3)-[:STARTS_AT]->(madurai)
MERGE (r3)-[:ENDS_AT]->(chennai)
MERGE (fast)-[:SERVES]->(r3)
