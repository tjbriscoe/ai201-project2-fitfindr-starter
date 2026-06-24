"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""

import os

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()


# ── Groq client ───────────────────────────────────────────────────────────────

def _get_groq_client():
    """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the mock listings dataset for items matching the description,
    optional size, and optional price ceiling.

    Args:
        description: Keywords describing what the user is looking for
                     (e.g., "vintage graphic tee").
        size:        Size string to filter by, or None to skip size filtering.
                     Matching is case-insensitive (e.g., "M" matches "S/M").
        max_price:   Maximum price (inclusive), or None to skip price filtering.

    Returns:
        A list of matching listing dicts, sorted by relevance (best match first).
        Returns an empty list if nothing matches — does NOT raise an exception.

    Each listing dict has the following fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand, platform

    TODO:
        1. Load all listings with load_listings().
        2. Filter by max_price and size (if provided).
        3. Score each remaining listing by keyword overlap with `description`.
        4. Drop any listings with a score of 0 (no relevant matches).
        5. Sort by score, highest first, and return the listing dicts.

    Before writing code, fill in the Tool 1 section of planning.md.
    """

    listings = load_listings()

    # Pull keywords from the description for text matching
    keywords = [word.lower() for word in description.split() if len(word) > 2]

    matched = []

    for item in listings:

        # Price filter — skip if item exceeds max_price
        if max_price is not None and item["price"] > max_price:
            continue

        # Size filter — skip if size doesn't match
        if size is not None and item.get("size", "").upper() != size.upper():
            continue

        # Text match — count how many keywords appear in the searchable fields
        searchable = " ".join([
            item.get("title", ""),
            item.get("description", ""),
            " ".join(item.get("style_tags", [])),
            item.get("category", ""),
        ]).lower()

        hits = sum(1 for kw in keywords if kw in searchable)

        if hits > 0:
            matched.append((hits, item))

    # Sort by relevance — most keyword hits first
    matched.sort(key=lambda x: x[0], reverse=True)

    # Replace this with your implementation
    return []

# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Generate a short, shareable outfit caption for the thrifted find.

    Args:
        outfit:   The outfit suggestion string from suggest_outfit().
        new_item: The listing dict for the thrifted item.

    Returns:
        A 2–4 sentence string usable as an Instagram/TikTok caption.
        If outfit is empty or missing, return a descriptive error message
        string — do NOT raise an exception.

    The caption should:
    - Feel casual and authentic (like a real OOTD post, not a product description)
    - Mention the item name, price, and platform naturally (once each)
    - Capture the outfit vibe in specific terms
    - Sound different each time for different inputs (use higher LLM temperature)

    TODO:
        1. Guard against an empty or whitespace-only outfit string.
        2. Build a prompt that gives the LLM the item details and the outfit,
           and asks for a caption matching the style guidelines above.
        3. Call the LLM and return the response.

    Before writing code, fill in the Tool 3 section of planning.md.
    """


    if not outfit or not outfit.strip():
        return (
            "Couldn't generate a fit card — the outfit description was empty. "
            "Make sure suggest_outfit ran successfully before calling this."
        )

    # Build readable item details for the prompt
    title    = new_item.get("title", "thrifted piece")
    price    = new_item.get("price", "?")
    platform = new_item.get("platform", "a thrift app")
    style_tags = ", ".join(new_item.get("style_tags", []))

    # Step 2: build the prompt
    prompt = f"""You are writing an Instagram caption for a thrift outfit post.

Item found: {title}, ${price}, from {platform}.
Style tags: {style_tags}
Outfit: {outfit}

Write a caption that:
- Sounds like a real person posting their outfit, not a product description
- Mentions the item name, price, and platform naturally — once each
- Captures the specific vibe of this outfit (grunge, cottagecore, Y2K, etc.)
- Is 2-3 sentences max, casual and lowercase is fine
- Feels different and specific to THIS outfit, not generic

Only return the caption itself — no intro, no explanation."""

    # Step 3: call the LLM at high temperature for varied output
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.9,
        )
        result = response.choices[0].message.content.strip()

        # Guard against empty LLM response
        if not result:
            return (
                f"found this {title} on {platform} for ${price} and "
                f"couldn't stop thinking about it 🖤"
            )

        return result

    except Exception as e:
        return (
            f"Fit card unavailable right now — try again in a moment. "
            f"({type(e).__name__})"
        )
        
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest 1–2 complete outfits.

    Args:
        new_item: A listing dict (the item the user is considering buying).
        wardrobe: A wardrobe dict with an 'items' key containing a list of
                  wardrobe item dicts. May be empty — handle this gracefully.

    Returns:
        A non-empty string with outfit suggestions.
        If the wardrobe is empty, offer general styling advice for the item
        rather than raising an exception or returning an empty string.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If empty: call the LLM with a prompt for general styling ideas
           (what kinds of items pair well, what vibe it suits, etc.).
        3. If not empty: format the wardrobe items into a prompt and ask
           the LLM to suggest specific outfit combinations using the new item
           and named pieces from the wardrobe.
        4. Return the LLM's response as a string.

    Before writing code, fill in the Tool 2 section of planning.md.
    """
    # Build a readable summary of the new item
    item_summary = (
        f"{new_item.get('title', 'Unknown item')} — "
        f"{new_item.get('description', '')}. "
        f"Style tags: {', '.join(new_item.get('style_tags', []))}. "
        f"Colors: {', '.join(new_item.get('colors', []))}. "
        f"Condition: {new_item.get('condition', 'unknown')}. "
        f"Price: ${new_item.get('price', '?')} from {new_item.get('platform', 'unknown')}."
    )

    # Step 1: check if wardrobe is empty
    wardrobe_items = wardrobe.get("items", [])
    is_empty = len(wardrobe_items) == 0

    # Step 2: empty wardrobe — ask for general styling advice
    if is_empty:
        prompt = f"""A thrifter just found this item:

{item_summary}

They haven't described their existing wardrobe. Suggest 1-2 complete outfits 
that would work well with this piece. Describe the types of items that pair 
well with it, what vibe or aesthetic it suits, and one specific way to wear it.
Be specific and practical. Keep it under 100 words."""

    # Step 3: wardrobe exists — suggest outfits using named pieces
    else:
        wardrobe_summary = "\n".join([
            f"- {w.get('title', 'item')}: {w.get('category', '')}, "
            f"{', '.join(w.get('colors', []))}, "
            f"{w.get('style', '')}"
            for w in wardrobe_items
        ])

        prompt = f"""A thrifter just found this item:

{item_summary}

Their existing wardrobe includes:
{wardrobe_summary}

Suggest 1-2 complete outfits using the new item and specific pieces from 
their wardrobe. Name the exact wardrobe pieces you're pairing it with. 
Include one styling tip (how to wear it, tuck it, roll it, etc.).
Keep it under 120 words."""

    # Step 4: call the LLM and return the response
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7,
        )
        result = response.choices[0].message.content.strip()

        # Guard against empty response
        if not result:
            return "This piece has a lot of potential — try pairing it with neutral basics to let it stand out."

        return result

    except Exception as e:
        return (
            f"Couldn't generate an outfit suggestion right now — "
            f"try again in a moment. ({type(e).__name__})"
        )
    