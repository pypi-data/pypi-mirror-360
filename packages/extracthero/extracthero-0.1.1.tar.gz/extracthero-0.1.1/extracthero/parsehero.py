# extracthero/parsehero.py
# run with: python -m extracthero.parsehero


"""
ParseHero — the "parse" phase of ExtractHero.
  • Converts a filtered corpus into structured data keyed by WhatToRetain specs.
  • Skips the LLM when the corpus is already a dict, unless you force it.
  • Performs per-field regex validation after parsing.
  • Returns a ParseOp.
"""

from __future__ import annotations

import json as _json
from time import time
from typing import Any, Dict, List, Optional, Tuple, Union

from llmservice.generation_engine import GenerationResult
from extracthero.myllmservice import MyLLMService
from extracthero.schemes import ExtractConfig, ParseOp, WhatToRetain

import warnings
warnings.filterwarnings(
    "ignore",
    category=RuntimeWarning,
    message=r".*extracthero\.parsehero.*"
)


class ParseHero:
    # ───────────────────────── init ─────────────────────────
    def __init__(
        self,
        config: Optional[ExtractConfig] = None,
        llm: Optional[MyLLMService] = None,
    ):
        self.config = config or ExtractConfig()
        self.llm = llm or MyLLMService()

    # ───────────────────────── public ───────────────────────
    def run(
        self,
        corpus: str | Dict[str, Any],
        items: WhatToRetain | List[WhatToRetain],
        enforce_llm_based_parse: bool = False,
    ) -> ParseOp:
        """
        Parse the corpus into structured data using the WhatToRetain specifications.
        """
        start_ts = time()

        # Fast-path for dict inputs (unless LLM is enforced)
        if isinstance(corpus, dict):
            if not enforce_llm_based_parse:
                parsed_values_dict = self.make_new_dict_by_parsing_keys_with_their_values(corpus, items)
                return ParseOp.from_result(
                    config=self.config,
                    content=parsed_values_dict,
                    usage=None,
                    start_time=start_ts,
                    success=True,
                    generation_result=None  # No LLM was used
                )
            # If enforce_llm_based_parse=True, fall through to LLM processing

        # Try to parse string as JSON first
        elif isinstance(corpus, str):
            try:
                corpus_dict = _json.loads(corpus)
                parsed_values_dict = self.make_new_dict_by_parsing_keys_with_their_values(corpus_dict, items)
                return ParseOp.from_result(
                    config=self.config,
                    content=parsed_values_dict,
                    usage=None,
                    start_time=start_ts,
                    success=True,
                    generation_result=None  # No LLM was used
                )
            except Exception:
                # Not valid JSON, continue to LLM processing
                pass

        # If we reach here, we need to use LLM to parse the corpus
        
        # Build prompt from WhatToRetain specifications
        if isinstance(items, WhatToRetain):
            prompt = items.compile_parser()
        else:
            prompt = "\n\n".join(it.compile_parser() for it in items)

        # Call LLM for parsing
        model = "gpt-4o"
        # model = "gpt-4o-mini"
        generation_result = self.llm.parse_via_llm(corpus, prompt, model=model)

        if not generation_result.success:
            return ParseOp.from_result(
                config=self.config,
                content=None,
                usage=generation_result.usage,
                start_time=start_ts,
                success=False,
                error="LLM parse failed",
                generation_result=generation_result
            )

        # Return successful parse result
        return ParseOp.from_result(
            config=self.config,
            content=generation_result.content,
            usage=generation_result.usage,
            start_time=start_ts,
            success=True,
            error=None,
            generation_result=generation_result
        )

    # ───────────────────── helper utilities ─────────────────────
    @staticmethod
    def make_new_dict_by_parsing_keys_with_their_values(
        data: Dict[str, Any],
        items: WhatToRetain | List[WhatToRetain],
    ) -> Dict[str, Any]:
        """Extract only the specified keys from the data dictionary."""
        keys = [items.name] if isinstance(items, WhatToRetain) else [it.name for it in items]
        return {k: data.get(k) for k in keys}

    # ───────────────────────── public (async) ───────────────────────
    async def run_async(
        self,
        corpus: str | Dict[str, Any],
        items: WhatToRetain | List[WhatToRetain],
        enforce_llm_based_parse: bool = False,
    ) -> ParseOp:
        """
        Async version of run method.
        """
        start_ts = time()

        # Fast-path for dict inputs (unless LLM is enforced)
        if isinstance(corpus, dict):
            if not enforce_llm_based_parse:
                parsed_values_dict = self.make_new_dict_by_parsing_keys_with_their_values(corpus, items)
                return ParseOp.from_result(
                    config=self.config,
                    content=parsed_values_dict,
                    usage=None,
                    start_time=start_ts,
                    success=True,
                    generation_result=None  # No LLM was used
                )

        # Try to parse string as JSON first
        elif isinstance(corpus, str):
            try:
                corpus_dict = _json.loads(corpus)
                parsed_values_dict = self.make_new_dict_by_parsing_keys_with_their_values(corpus_dict, items)
                return ParseOp.from_result(
                    config=self.config,
                    content=parsed_values_dict,
                    usage=None,
                    start_time=start_ts,
                    success=True,
                    generation_result=None  # No LLM was used
                )
            except Exception:
                # Not valid JSON, continue to LLM processing
                pass

        # Build prompt from WhatToRetain specifications
        if isinstance(items, WhatToRetain):
            prompt = items.compile()
        else:
            prompt = "\n\n".join(it.compile() for it in items)

        # Call async LLM for parsing
        generation_result: GenerationResult = await self.llm.parse_via_llm_async(corpus, prompt)
        
        if not generation_result.success:
            return ParseOp.from_result(
                config=self.config,
                content=None,
                usage=generation_result.usage,
                start_time=start_ts,
                success=False,
                error="LLM parse failed",
                generation_result=generation_result
            )

        # Return successful parse result
        return ParseOp.from_result(
            config=self.config,
            content=generation_result.content,
            usage=generation_result.usage,
            start_time=start_ts,
            success=True,
            error=None,
            generation_result=generation_result
        )



# ────────────────────────── demo ───────────────────────────
def main() -> None:
    cfg = ExtractConfig()
    hero = ParseHero(cfg)

    # items = [
    #     WhatToRetain(name="title", desc="Product title"),
    #     WhatToRetain(name="price", desc="Product price"),
    # ]


    # result dict should have a field called product 
    items = [
       #WhatToRetain(name="product", desc="Product info in plain text format, not json, DO NOT JSONIFY THIS PART!"),
       
        #  WhatToRetain(name="product", desc="Product title"),

         WhatToRetain(name="product_title", desc="Product title"),
         WhatToRetain(name="product_rating", desc="Product rating"),
        #  WhatToRetain(name="product_title"),
        # WhatToRetain(name="product", desc="Product info in SEO friendly format"),

        #   WhatToRetain(name="product", desc="Product info" , text_rules=["SEO friendly format plain text"]),
        #  WhatToRetain(name="SEO_mistakes", desc="Product price"),
    ]
    
    # 'product': title is Wireless Keyboard Pro and  price: €49.99,  list-price: €59.99,  rating: 4.5 ★  the availability: In Stock

    

    
    # filtered_text = """
    #     title: Wireless Keyboard Pro and  price: €49.99
    #     list-price: €59.99
    #     rating: 4.5 ★  the availability: In Stock
    #     delivery: Free next-day
    #     ---
    #     title: USB-C Hub (6-in-1)
    #     price: €29.50
    #     availability: Only 3 left!
    #     rating: 4.1 ★
    #     ---
    #     title: Gaming Mouse XT-8 and list_price: $42.00
    #     price: $35.00
    #     availability: Out of Stock
    #     warranty: 2-year limited
    #     ---
    #     title: Luggage Big 65 L
    #     availability: Pre-order (ships in 3 weeks)
    #     rating: 4.8 ★
    #     """
    
    filtered_text = """
        title: Wireless Keyboard Pro and  price: €49.99
        list-price: €59.99
        rating: 4.5 ★  the availability: In Stock
        delivery: Free next-day


        title: Fridge New
        
        """
    


    extraction_spec = [
            WhatToRetain(
                name="title",
                desc="Product title",
                example="Wireless Keyboard"
            ),
            WhatToRetain(
                name="price",
                desc="Product price with currency symbol",
                example="€49.99"
            )
        ]
    
    filtered_text2  ="""
            ```html
        <div class="product">
        <h2 class="title">Wireless Keyboard</h2>
        <span class="price">&euro;49.99</span>
        <p class="description">Compact wireless keyboard with RGB lighting</p>
        </div>
        <div class="product">
        <h2 class="title">USB-C Hub</h2>
        <span class="price">&euro;29.50</span>
        <p class="description">7-in-1 USB-C hub with HDMI output</p>
        </div>
        ```
        """
    
    
    p_op = hero.run(filtered_text2, extraction_spec, enforce_llm_based_parse=True)
    print("Success:", p_op.success)
    
    #print(p_op.content)
    print(" " )
    parsed_dict=p_op.content
    if isinstance(parsed_dict, list):
        print("List elements:" )
        for e in parsed_dict:
            print(e)
    else:
        print("Parsed dict:", parsed_dict)
    
    print(" ")
    print(" ")
    # print("pipeline_steps_results=",  p_op.generation_result.pipeline_steps_results)
   


if __name__ == "__main__":
    main()
