from typing import TypedDict

class graph_state(TypedDict):
    amount_usd : float
    inr_amount : float
    eur_amount : float

def calculate_inr(graph_state_obj : graph_state) -> graph_state:
    graph_state_obj = {
        "inr_amount" : graph_state_obj["amount_usd"] * 90
    }
    return graph_state_obj

def set_usd_amount(graph_state_obj : graph_state) -> graph_state:
    graph_state_obj["amount_usd"] = 100
    print(f"USD_amount assigned : {graph_state_obj["amount_usd"]}")
    return graph_state_obj

def calculate_eur(graph_state_obj : graph_state) -> graph_state:
    graph_state_obj = {
        "eur_amount" : graph_state_obj["amount_usd"] * 35
    }
    return graph_state_obj

from langgraph.graph import StateGraph, START, END

builder = StateGraph(graph_state)

builder.add_node("start_node", set_usd_amount)
builder.add_node("convert_inr_node", calculate_inr)
builder.add_node("convert_eur_node", calculate_eur)
