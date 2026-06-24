# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
This fitfindr assistant needs to search through the internet to find clothing items that matches the item's parameters given by the user. The fitfindr returns 3 matching listings, sorted by relevance. The user will give the agent a general traits about the item and the agent should return items that accurately matches the item's description

Example: 
search_listings("khaki-colored carpenter pants", size = "32", max_price = 120)
Find me a pair of khaki-colored carpenter pants that have a vintage washed effect and is in good
 condition. The item should be in good condition overall and should only have a max price of 120 ---> suggest_outfit() 
Pair this with a long-sleeve tee that displays an avant-garde graphic. The shirt should be a neutral toned color and in good condition 


**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `description` (str): This parameter represents the item's characteristics 
- `size` (str): describes the general measurements of the clothing item
- `max_price` (float): The maximum price for the item being searched

**What it returns:**
<!-- Describe the return value — what fields does a result contain? -->
'description' (str): Returns a list that includes an item's distinctive traits such as color, condition, wash effect, garment craftmanship(long-sleeve, short-sleeve, hoodie, cropped tee), graphics(if any) on the shirt, and all of the distinctive features that makes the item stand out

'size' (str): Returns a string of the general measurement of the clothing top item (XS,S,M,L,XL), If the item is a bottom garment, the agent should prompt the user to enter an integer based on their waist measurement and filter out all items that dont match the description given

'max_price'(int): Returns an non negative integer of the MAX dollar amount of the item being searched

**What happens if it fails or returns nothing:**
<!-- What should the agent do if no listings match? -->
'description'(str): If the description doesn't match with any items, the agent should prompt the user to be more specific about the make of the item, and ask the user to provide a reference item from a brand to find any matches that fit that same criteria

'size'(str): If the listing doesn't match, the agent should prompt the user to enter the next best size and see if there are any items that matches that size

'max_price'(int): If no listing matches, the agent should tell the user that there are no items that fit the description that also matches the maximum price point.
---

### Tool 2: suggest_outfit

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
This function is meant to suggest complementary clothing items that matches the user's initial item. The agent should acurately assess all streetwear clothing trends and see what specific clothing garments are usually paired with. 

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `new_item` (dict): ...
- `wardrobe` (dict): ...

**What it returns:**
<!-- Describe the return value -->

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the wardrobe is empty or no outfit can be suggested? -->

---

### Tool 3: create_fit_card

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
Takes a complete outfit suggestion and the thrifted item that anchors it, then calls the LLM to generate a short, shareable caption — the kind of thing someone would post on Instagram or TikTok. Output should sound like a real person wrote it, not a product description, and must vary each call even for identical inputs.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `outfit` (str): The full outfit suggestion returned by suggest_outfit — e.g. "Pair this faded band tee with wide-leg jeans and platform Docs. Roll one sleeve, front-tuck slightly." This is the primary content the caption is built from.
- `new_item` (dict): The listing dict selected by search_listings, containing fields like title, price, platform, and condition. Used to ground the caption in specific details (e.g. the price paid, where it was found).

**What it returns:**
<!-- Describe the return value -->
A single string — a 1–3 sentence caption in a casual, first-person voice. Example: "thrifted this faded band tee off depop for $22 and honestly it was made for my wide-legs 🖤 full look in my stories". The string should never be identical across two calls on the same input; set LLM temperature ≥ 0.8 to ensure variation.

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the outfit data is incomplete? -->
Failure modeCauseAgent responseoutfit == ""suggest_outfit returned emptyReturn the string 

"Couldn't generate a fit card — the outfit description was empty." immediately. Do not call the LLM. 
new_item is missing key fieldsMalformed listing dictBuild the prompt with whatever fields exist; omit missing ones gracefully rather than crashing.

LLM call raises an exceptionNetwork error, API timeoutCatch the exception, return "Fit card unavailable right now — try again in a moment." Do not propagate the exception to the agent loop.

LLM returns an empty stringModel returned nothingTreat as a failure, return the same fallback string as the timeout case above.

---

### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->

---

## Planning Loop

**How does your agent decide which tool to call next?**
<!-- Describe the logic your planning loop uses. What does it look at? What conditions change its behavior? How does it know when it's done? -->

---

## State Management

**How does information from one tool get passed to the next?**
<!-- Describe how your agent stores and accesses state within a session. What data is tracked? How is it passed between tool calls? -->

---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | |
| suggest_outfit | Wardrobe is empty | |
| create_fit_card | Outfit input is missing or incomplete | |

---

## Architecture

<!-- Draw a diagram of your agent showing how the components connect:
     User input → Planning Loop → Tools (search_listings, suggest_outfit, create_fit_card)
                                                                          ↕
                                                                   State / Session
     Show what triggers each tool, how state flows between them, and where error paths branch off.
     Use ASCII art or a Mermaid diagram (https://mermaid.js.org/syntax/flowchart.html).
     Do NOT embed an image — graders need to read your diagram directly in the file;
     an embedded image or screenshot cannot be evaluated.
     You'll share this diagram with an AI tool when asking it to implement
     the planning loop and each individual tool. -->

User query
    │
    ▼
run_agent(query, wardrobe)
    │
    ├─► STEP 1: search_listings(description, size, max_price)
    │       │
    │       ├── results == [] ──► session["error"] = "Nothing found for
    │       │                      <size> under $<price>. Try raising
    │       │                      the price or removing the size filter."
    │       │                      session["fit_card"] = None
    │       │                      return session  ◄── AGENT STOPS HERE
    │       │
    │       └── results != [] ──► session["selected_item"] = results[0]
    │
    ├─► STEP 2: suggest_outfit(selected_item, wardrobe)
    │       │
    │       ├── wardrobe["items"] == [] ──► prompt LLM for general
    │       │                               styling advice only
    │       │
    │       └── wardrobe["items"] != [] ──► prompt LLM using both
    │                                        item fields + wardrobe items
    │       │
    │       └── result ──► session["outfit_suggestion"] = result
    │
    ├─► STEP 3: create_fit_card(outfit_suggestion, selected_item)
    │       │
    │       ├── outfit_suggestion == "" ──► session["fit_card"] =
    │       │                               "Couldn't generate a fit
    │       │                                card — outfit was empty."
    │       │
    │       └── outfit_suggestion != "" ──► call LLM, set
    │                                        session["fit_card"] = result
    │
    └─► return session

---

## AI Tool Plan

<!-- For each part of the implementation below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, your agent diagram)
     - What you expect it to produce
     - How you'll verify the output matches your spec before moving on

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Tool 1 spec (inputs, return value, failure mode) and ask it to implement
     search_listings() using load_listings() from the data loader — then test it against 3 queries
     before trusting it" is a plan. -->

     Tool: ClaudeInput I'll provide:

The Tool 1 spec block from this file (function signature, all three input parameters with types, return value description, empty-results failure mode) plus this instruction: "Implement search_listings(description, size, max_price) in tools.py using load_listings() from utils/data_loader.py. Do not re-implement file loading. Filter by all three parameters; size and max_price should be skippable if passed as None."Expected output: A working function in tools.py that filters the listings list, handles None parameters gracefully, and returns [] rather than raising when nothing matches.How I'll verify it:

Run three pytest cases before trusting it — one that expects results ("vintage graphic tee", no size filter, max_price=50), one that expects [] (impossible query: "designer ballgown", size "XXS", max_price=5), and one that checks every returned item has price <= max_price. If any test fails I'll fix the generated code myself rather than re-prompting blindly.

**Milestone 3 — Individual tool implementations:**

**Milestone 4 — Planning loop and state management:**

---

## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
<!-- What does the agent do first? Which tool is called? With what input? -->
search_listings("vintage graphic tee", size=None, max_price=30.0)What the agent extracts from the query:

description = "vintage graphic tee"
size = None (no size mentioned, filter is skipped)
max_price = 30.0

**Step 2:**
<!-- What happens next? What was returned from step 1? What tool is called now? -->

Calls load_listings(), then filters the full listings list down to items where:

price <= 30.0
"vintage" or "graphic" or "tee" appears in title, description, or style_tags

**Step 3:**
<!-- Continue until the full interaction is complete -->
create_fit_card(outfit=session["outfit_suggestion"], 

new_item=session["selected_item"])
The agent passes the full suggestion string from step 2 and the original listing dict from step 1. The function checks outfit != "" — it isn't, so it proceeds to the LLM call.

**Final output to user:**
<!-- What does the user actually see at the end? -->
 listingFaded Band Tee — $22 · Depop · Good condition · Size M  
 
 Outfit suggestion : "Pair the faded band tee with your baggy jeans and chunky sneakers..."Fit card "thrifted this faded band tee off depop for $22 and it was literally made for my wide-legs 🖤"


