import re

"""
agent.py

The FitFindr planning loop. Orchestrates the three tools in response to a
natural language user query, passing state between them via a session dict.

Complete tools.py and test each tool in isolation before implementing this file.

Usage (once implemented):
    from agent import run_agent
    from utils.data_loader import get_example_wardrobe

    result = run_agent(
        query="vintage graphic tee under $30, size M",
        wardrobe=get_example_wardrobe(),
    )
    print(result["fit_card"])
    print(result["error"])   # None on success
"""

from tools import search_listings, suggest_outfit, create_fit_card


# ── session state ─────────────────────────────────────────────────────────────

def _new_session(query: str, wardrobe: dict) -> dict:
    """
    Initialize and return a fresh session dict for one user interaction.

    The session dict is the single source of truth for everything that happens
    during a run — it stores the original query, parsed parameters, tool results,
    and any error that caused early termination.

    You may add fields to this dict as needed for your implementation.
    """
    return {
        "query": query,              # original user query
        "parsed": {},                # extracted description / size / max_price
        "search_results": [],        # list of matching listing dicts
        "selected_item": None,       # top result, passed into suggest_outfit
        "wardrobe": wardrobe,        # user's wardrobe dict
        "outfit_suggestion": None,   # string returned by suggest_outfit
        "fit_card": None,            # string returned by create_fit_card
        "error": None,               # set if the interaction ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    
    #Start session
    session = _new_session(query, wardrobe)

    #Regex pattern to parse the size
# Match letter sizes OR shoe sizes (5-15) only when preceded by "size"
    size_match = re.search(
    r'\b(XXS|XS|S|M|L|XL|XXL)\b|(?:size\s+)(\d+(?:\.\d+)?)',query,  re.IGNORECASE)   
    price_match = re.search(r'\$(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s*(?:dollars?|bucks?)', query, re.IGNORECASE)

    size = size_match.group(1).upper() if size_match else None
    max_price = float(price_match.group(1)) if price_match else None

    description = query
    if size_match:

        size = (size_match.group(1) or size_match.group(2))
        size = size.upper() if size else None
    else:
    
      size = None
    if price_match:
        max_price = float(price_match.group(1) or price_match.group(2))
    else:
        max_price = None

    for filler in ["under", "below", "around", "about", "size", "in", "size", "good", "condition", "fair", "excellent", "worn", "want", "need"]:
        description = re.sub(rf'\b{filler}\b', "", description, flags=re.IGNORECASE)
    description = " ".join(description.split())

    #Parse Query 
    session["parsed"] = {
        "description": description,
        "size":        size,
        "max_price":   max_price,
    }

    # Step 3: search listings — branch here if nothing matches
    results = search_listings(description, size, max_price)
    session["search_results"] = results

    if len(results) == 0:
        size_str  = f"size {size}"  if size      else "any size"
        price_str = f"under ${int(max_price)}" if max_price else "any price"
        session["error"] = (
            f"Nothing matched '{description}' in {size_str} at {price_str}. "
            f"Try raising your budget, removing the size filter, or using "
            f"different keywords."
        )
        return session 

    session["selected_item"] = results[0]

    session["outfit_suggestion"] = suggest_outfit(
        new_item=session["selected_item"],
        wardrobe=wardrobe,
    )

    session["fit_card"] = create_fit_card(
        outfit=session["outfit_suggestion"],
        new_item=session["selected_item"],
    )


    return session


# ── CLI test ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

    print("=== Happy path: graphic tee ===\n")
    session = run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    )
    if session["error"]:
        print(f"Error: {session['error']}")
    else:
        print(f"Found: {session['selected_item']['title']}")
        print(f"\nOutfit: {session['outfit_suggestion']}")
        print(f"\nFit card: {session['fit_card']}")

    print("\n\n=== No-results path ===\n")
    session2 = run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    )
    print(f"Error message: {session2['error']}")
