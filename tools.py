import os
import re
from dotenv import load_dotenv
from groq import Groq
from utils.data_loader import load_listings

load_dotenv()

def _get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set.")
    return Groq(api_key=api_key)

def search_listings(description: str, size: str | None, max_price: float | None) -> list:
    listings = load_listings()
    keywords = [word.lower() for word in description.split() if len(word) > 2]
    matched = []
    for item in listings:
        if max_price is not None and item["price"] > max_price:
            continue
        if size is not None and item.get("size", "").upper() != size.upper():
            continue
        searchable = " ".join([
            item.get("title", ""),
            item.get("description", ""),
            " ".join(item.get("style_tags", [])),
            item.get("category", ""),
        ]).lower()
        hits = sum(1 for kw in keywords if kw in searchable)
        if hits > 0:
            matched.append((hits, item))
    matched.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in matched]

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    item_summary = (
        f"{new_item.get('title', 'Unknown item')} — "
        f"{new_item.get('description', '')}. "
        f"Style tags: {', '.join(new_item.get('style_tags', []))}. "
        f"Colors: {', '.join(new_item.get('colors', []))}. "
        f"Condition: {new_item.get('condition', 'unknown')}. "
        f"Price: ${new_item.get('price', '?')} from {new_item.get('platform', 'unknown')}."
    )
    wardrobe_items = wardrobe.get("items", [])
    if len(wardrobe_items) == 0:
        prompt = f"""A thrifter just found this item:
{item_summary}
They haven't described their existing wardrobe. Suggest 1-2 complete outfits
that would work well with this piece. Be specific and practical. Keep it under 100 words."""
    else:
        wardrobe_summary = "\n".join([
            f"- {w.get('title', 'item')}: {w.get('category', '')}, "
            f"{', '.join(w.get('colors', []))}, {w.get('style', '')}"
            for w in wardrobe_items
        ])
        prompt = f"""A thrifter just found this item:
{item_summary}
Their existing wardrobe includes:
{wardrobe_summary}
Suggest 1-2 complete outfits using the new item and specific pieces from
their wardrobe. Name the exact wardrobe pieces. Include one styling tip.
Keep it under 120 words."""
    try:
        client = _get_groq_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7,
        )
        result = response.choices[0].message.content.strip()
        if not result:
            return "This piece has a lot of potential — try pairing it with neutral basics."
        return result
    except Exception as e:
        return f"Couldn't generate an outfit suggestion right now. ({type(e).__name__})"

def create_fit_card(outfit: str, new_item: dict) -> str:
    if not outfit or not outfit.strip():
        return "Couldn't generate a fit card — the outfit description was empty."
    title    = new_item.get("title", "thrifted piece")
    price    = new_item.get("price", "?")
    platform = new_item.get("platform", "a thrift app")
    style_tags = ", ".join(new_item.get("style_tags", []))
    prompt = f"""You are writing an Instagram caption for a thrift outfit post.
Item found: {title}, ${price}, from {platform}.
Style tags: {style_tags}
Outfit: {outfit}
Write a caption that sounds like a real person posting their outfit.
Mention the item name, price, and platform once each.
2-3 sentences max, casual tone.
Only return the caption itself."""
    try:
        client = _get_groq_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.9,
        )
        result = response.choices[0].message.content.strip()
        if not result:
            return f"found this {title} on {platform} for ${price} and couldn't stop thinking about it"
        return result
    except Exception as e:
        return f"Fit card unavailable right now. ({type(e).__name__})"
