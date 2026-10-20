
import os
from dotenv import load_dotenv
from groq import Groq

from graph_retriever import find_transport_partners

load_dotenv()


def ask_logistics_question(origin, destination, min_capacity):
    # Step 1: Retrieve matching records from Neo4j
    records = find_transport_partners(
        origin=origin,
        destination=destination,
        min_capacity=min_capacity,
    )

    # Step 2: Do not ask the LLM to invent missing records
    if not records:
        return (
            "No matching truck was found in the Neo4j graph "
            f"for {origin} to {destination} with capacity "
            f"of at least {min_capacity} tons."
        )

    # Step 3: Send retrieved evidence to Groq
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

    if not api_key:
        raise ValueError("GROQ_API_KEY is missing from .env")

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model=model,
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a logistics assistant. "
                    "Answer using only the supplied Neo4j records. "
                    "Explain the matching partner, truck, capacity, "
                    "route, and distance. Do not invent prices, "
                    "delivery times, or availability. "
                    "These are sample demonstration records."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Find a truck from {origin} to {destination} "
                    f"with at least {min_capacity} tons capacity.\n\n"
                    f"Neo4j records: {records}"
                ),
            },
        ],
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    print("LOGISTICS GRAPH RAG CHATBOT")
    print("-" * 35)

    origin = input("Enter origin city: ").strip()
    destination = input("Enter destination city: ").strip()

    try:
        min_capacity = float(input("Minimum truck capacity (tons): "))

        answer = ask_logistics_question(
            origin,
            destination,
            min_capacity,
        )

        print("\nChatbot Answer:")
        print(answer)

    except ValueError as error:
        print("Input or configuration error:", error)
    except Exception as error:
        print("Error:", error)
