# FitFindr — Starter Kit

This starter kit contains everything you need to begin Project 2.

## What's Included

```
ai201-project2-fitfindr-starter/
├── data/
│   ├── listings.json          # 40 mock secondhand listings
│   └── wardrobe_schema.json   # Wardrobe format + example wardrobe
├── utils/
│   └── data_loader.py         # Helper functions for loading the data
├── planning.md                # Your planning template — fill this out first
└── requirements.txt           # Python dependencies
```

## Setup

**macOS / Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

Set your Groq API key in a `.env` file (get a free key at [console.groq.com](https://console.groq.com)):
```
GROQ_API_KEY=your_key_here
```

## The Mock Listings Dataset

`data/listings.json` contains 40 mock secondhand listings across categories (tops, bottoms, outerwear, shoes, accessories) and styles (vintage, y2k, grunge, cottagecore, streetwear, and more).

Each listing has: `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.

Load it with:
```python
from utils.data_loader import load_listings
listings = load_listings()
```

## The Wardrobe Schema

`data/wardrobe_schema.json` defines the format your agent uses to represent a user's existing wardrobe. It includes:

- `schema`: field definitions for a wardrobe item
- `example_wardrobe`: a sample wardrobe with 10 items you can use for testing
- `empty_wardrobe`: a starting template for a new user

Load an example wardrobe with:
```python
from utils.data_loader import get_example_wardrobe
wardrobe = get_example_wardrobe()
```

## Tool Inventory

Your README submission must document each tool's name, inputs, and return value. **These must exactly match your actual function signatures in `tools.py`.** Your documented interfaces will be checked against your actual function signatures in `tools.py` — if the parameter count or types contradict what's in the code, you may not receive full credit for that tool.

---

## Interaction Walkthrough

<!-- Walk through a complete interaction step by step: natural language query → each tool call (and why) → final fit card.
     Walk through this carefully — it's how graders follow your agent's reasoning without a live demo.
     Use a specific example — do not leave this as a template. -->

**User query:**

**Step 1 — Tool called:**
- Tool: search_listings()
- Input: description = "vintage graphic tee", size = None, max_price = 30.0
- Why this tool: This is the first tool called when the user runs the code. The agent is tasked with finding a listing befroe it can suggest anything. No other tool can run without knowing what the intial item is 
- Output: The agent lists 3 matching items, sorted by relevance. The top result is "Vintge band tee- faded grey", $28, Grailed, Excellent condition, size L

**Step 2 — Tool called:**
- Tool: suggest_outfit()
- Input:new_item={"title": "Vintage Band Tee — Faded Grey", "price": 28, "platform": "Depop", ...}, wardrobe={"items": [baggy jeans, chunky sneakers, oversized flannel, ...]}
- Why this tool: search returned results so the agent proceeds. The selected item and user wardrobe are passed in together — this tool only runs if step 1 found something.
- Output: "Pair the faded band tee with your baggy jeans and chunky sneakers for a classic 90s grunge look. Roll one sleeve once and front-tuck just the corner for shape. Throw your oversized flannel over the top on cooler days."

**Step 3 — Tool called:**
- Tool: create_fit_card()
- Why this tool: suggest_outfit returned a non-empty string so the agent proceeds to generate the caption. This tool always runs last — it needs both the item details and the outfit suggestion to write a grounded caption.
- Output: "thrifted this faded band tee off depop for $28 and it was literally made for my wide-legs 🖤 rolled one sleeve, tucked the front, done."
 
**Final output to user:**
Top listing---->Vintage Band Tee — Faded Grey · $28 · Depop · Good condition · Size M
Outfit idea----->"Pair the faded band tee with your baggy jeans and chunky sneakers for a classic 90s grunge look. Roll one sleeve once and front-tuck just the corner for shape."
Your fit card---> "thrifted this faded band tee off depop for $28 and it was literally made for my wide-legs 🖤 rolled one sleeve, tucked the front, done."
---

## Error Handling and Fail Points

<!-- For each tool, describe the specific failure mode and what your agent does in response.
     This maps to the error handling section of the rubric (F5-C1). -->

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| `search_listings` |No listings match the description, size, and price combination |Returns []. Agent checks immediately — if empty, sets session["error"] to "Nothing matched '[description]' in size [size] at under $[price]. Try raising your budget, removing the size filter, or using different keywords." and returns early. suggest_outfit and create_fit_card are never called. The error appears in the top listing panel and the other two panels stay empty. |
| `suggest_outfit` |wardrobe["items"] is an empty list |Does not crash. Detects the empty list before building the LLM prompt and switches to a general styling prompt instead of a wardrobe-specific one. Always returns a non-empty string — the agent continues to create_fit_card normally. |
| `create_fit_card` |LLM call fails or returns an empty string |Catches the exception in a try/except block and returns "Couldn't generate an outfit suggestion right now. (ExceptionType)". Agent stores this in session["outfit_suggestion"] and continues to step 3 rather than crashing. |

---

## Spec Reflection

<!-- Answer both questions with at least 2–3 sentences each. -->

**One way planning.md helped during implementation:**
The agent diagram in planning.md was the single most useful reference during Milestone 4. Having the exact conditional logic written out — specifically that search_listings returning [] is the only hard stop and that all other failures degrade gracefully — meant the run_agent() planning loop had a clear target to implement against rather than being figured out on the fly. When the indentation bugs made it hard to tell if the code was doing what I intended, I could check each step against the diagram to verify the branching logic was correct.

**One divergence from your spec, and why:**
The spec described query parsing as a choice between regex, string splitting, or an LLM call, with a note to document whichever approach was chosen. During implementation, the LLM parsing option was dropped immediately — calling Groq just to extract a size and a price from a short string adds a network round trip and a potential failure point for something regex handles reliably in one line. The regex approach also made the no-results error message more useful, because the parsed size and max_price values are available as named variables to drop directly into the message string. This wasn't a flaw in the spec — the spec correctly flagged it as a decision to make — but the implementation landed more firmly on regex than the spec anticipated.

---

## Where to Start

1. **Read `planning.md` and fill it out before writing any code.**
2. Verify the data loads correctly by running `python utils/data_loader.py`.
3. Build and test each tool individually before connecting them through your planning loop.

Your implementation files go in this same directory. There's no required file structure for your agent code — organize it however makes sense for your design.
