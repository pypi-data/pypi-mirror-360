# extracthero

Extract **accurate, structured facts** from messy real-world content — raw HTML, screenshots, PDFs, JSON blobs or plain text — with *almost zero compromise.*

---

## Why extracthero?

| Pain-point                                                       | extracthero's answer                                                                                                                                                                                        |
| ---------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| *DOM spaghetti* (ads, nav bars, JS widgets) pollutes extraction. Markdown converters drop dynamic/JS-rendered elements. | We use a rule-based **DomReducer** to remove non-content related HTML tags. This process is custom tailored to not destroy any structural data including tables etc. In general this gives us 20% reduction in size. Markdown converting operations are too vague to trust for prod and they usually dismiss useful data. |
| Needle in haystack is common problem. If you overwork a LLM, it can hallucinate or start outputting unstructured garbage which breaks production. | We define extraction in 2 phases. **First phase is context aware filtering**, and **second phase is parsing this filtered data**. Since LLM processes less data, the attention mechanism works better as well and more accurate results. |
| LLM prompts that just say "extract price" are brittle because in real life scenarios extraction logic is more complex and dependent on other variables. | Extracthero asks you to fill **`WhatToRetain`** specifications that include the field's `name`, `desc`, and optional `text_rules`, so the LLM knows the full context and returns *sniper-accurate* results. |
| In real life, source data comes in different formats (JSON, strings, dicts, HTML) and each requires different optimization strategies. | ExtractHero handles each data format intelligently. You can input JSON and if it can extract keys directly, it will use a fast-path. If it doesn't find what you need, you can use fallback mechanisms to route it to LLM processing for extraction. |
| Post-hoc validation is messy. | Regex/type guards live inside each `WhatToRetain`; a failed field flips `success=False`, so you can retry or send to manual review. |

---

## Key ideas

### 1  Schema-first extraction

```python
from extracthero import WhatToRetain

price_spec = WhatToRetain(
    name="price",
    desc="currency-prefixed current product price",
    regex_validator=r"€\d+\.\d{2}",
    text_rules=[
        "Ignore crossed-out promotional prices",
        "Return the live price only"
    ],
    example="€49.99"
)
```

### 2  DomReducer > HTML→Markdown

* **Rule-based processing** – fast, deterministic HTML reduction without LLM costs.
* Works directly on the DOM tree with spatial awareness.
* Preserves semantic structure and element relationships.
* Removes scripts, ads, banners while keeping content hierarchy intact.
* Shrinks a 40 kB e-commerce page to <3 kB of clean, LLM-ready text without losing context.

### 3  Two-phase pipeline

```
Raw input  ──▶  DomReducer (rule-based)  ──▶  FilterHero (LLM)  ──▶  ParseHero (LLM)  ──▶  dict + metrics
```

---

## Features

* **Rule-based HTML preprocessing** – DomReducer uses deterministic rules (no LLM tokens) for fast, predictable content reduction.
* **Multi-modal input** – raw HTML, JSON, Python dicts, screenshots (vision LLM in roadmap).
* **Spatial context** – DomReducer preserves layout coordinates and element proximity so LLMs understand structural relationships between content pieces.
* **LLM-agnostic** – default wrapper targets OpenAI; swap in any `.filter_via_llm` / `.parse_via_llm` service.
* **Per-field validation** – regex, required/optional, custom lambdas.
* **Usage metering** – token counts & cost returned with every operation.
* **Opt-in strictness** – force LLM even for dicts (`enforce_llm_based_*`) or skip HTML reduction (`reduce_html=False`).
* **Generation tracking** – access full LLM request/response details via `generation_result` for debugging and optimization.

---

## Installation

```bash
pip install extracthero
```

---

## Quick-start

```python
from extracthero import ExtractHero, WhatToRetain

html = open("product-page.html").read()

extraction_spec = [
    WhatToRetain(
        name="title", 
        desc="product title", 
        example="Wireless Keyboard"
    ),
    WhatToRetain(
        name="price",
        desc="currency-prefixed price",
        regex_validator=r"€\d+\.\d{2}",
        example="€49.99"
    ),
]

hero = ExtractHero()
result = hero.extract(html, extraction_spec, text_type="html")

print("✅ success:", result.success)
print("📊 extracted data:", result.content)

# Access detailed LLM usage
if result.filter_op.generation_result:
    print("🔍 filter tokens:", result.filter_op.generation_result.usage)
if result.parse_op.generation_result:
    print("🔍 parse tokens:", result.parse_op.generation_result.usage)
```

---

## Typical HTML workflow

1. **Scrape or load** the raw HTML.
2. **DomReducer** intelligently trims it to essential content using rule-based processing (no LLM tokens consumed) while preserving spatial relationships and semantic structure.
3. **FilterHero** sees only that structured, reduced text, calling the LLM once (or per-field) to keep the lines that mention title, price, SKU, etc.
4. **ParseHero** builds a schema-driven prompt and emits strict JSON.
5. **Validation** – invalid prices (`"129.50"`) are rejected for lacking "€".
6. **ExtractOp** bundles both steps plus token/cost metrics for budgeting.

> 💡 **Cost efficiency**: DomReducer's rule-based preprocessing dramatically reduces LLM input size without consuming tokens, making your extraction pipeline faster and cheaper.

---

## Advanced Usage

### Force LLM Usage
```python
# Force LLM even for JSON inputs (useful for debugging)
result = hero.extract(
    json_data, 
    extraction_spec,
    text_type="dict",
    enforce_llm_based_filter=True,
    enforce_llm_based_parse=True
)
```

### Async Processing
```python
# For high-throughput pipelines
result = await hero.extract_async(html, extraction_spec, text_type="html")
```

### Contextual Filtering
```python
price_spec = WhatToRetain(
    name="price",
    desc="Product price with currency symbol",
    wrt_to_source_filter_desc="""
    Return only prices for the main hero product.
    Ignore sidebar recommendations and related products.
    """,
    example="€49.99"
)
```

### Access Generation Details
```python
result = hero.extract(html, extraction_spec, text_type="html")

# Debug filter phase
if result.filter_op.generation_result:
    filter_gen = result.filter_op.generation_result
    print("Filter prompt:", filter_gen.generation_request.formatted_prompt)
    print("Filter model:", filter_gen.generation_request.model)

# Debug parse phase  
if result.parse_op.generation_result:
    parse_gen = result.parse_op.generation_result
    print("Parse prompt:", parse_gen.generation_request.formatted_prompt)
    print("Parse success:", parse_gen.success)
```

---

## API Reference

### Core Classes

- **`ExtractHero`** - Main orchestrator class
- **`WhatToRetain`** - Specification for what data to extract
- **`FilterHero`** - Handles content filtering and reduction  
- **`ParseHero`** - Handles structured data parsing

### Key Methods

- **`extract()`** - Synchronous extraction
- **`extract_async()`** - Asynchronous extraction for high throughput

### Result Objects

- **`ExtractOp`** - Contains filter and parse results plus final content
- **`FilterOp`** - Filter phase results with generation details
- **`ParseOp`** - Parse phase results with generation details

---

## Roadmap

| Status | Feature                                          |
| ------ | ------------------------------------------------ |
| ✅      | Sync FilterHero & ParseHero                      |
| ✅      | Generation result tracking for debugging         |
| ✅      | Async heroes for high-throughput pipelines       |
| 🟡     | Built-in key:value fallback parser              |
| 🟡     | Vision-LLM screenshot mode                       |
| 🟡     | Pydantic schema-driven auto-prompts & auto-regex |

---