# extracthero/extracthero.py
# run with: python -m extracthero.extracthero

from __future__ import annotations

from time import time
from typing import List, Union, Optional
import json

from extracthero.myllmservice import MyLLMService
from extracthero.schemes import (
    ExtractConfig,
    ExtractOp,
    FilterOp,
    ParseOp,
    WhatToRetain,
)
from extracthero.filterhero import FilterHero
from extracthero.parsehero import ParseHero
from extracthero.utils import load_html


class ExtractHero:
    """High-level orchestrator that chains FilterHero → ParseHero with rich metrics."""

    def __init__(self, config: ExtractConfig | None = None, llm: MyLLMService | None = None):
        self.config = config or ExtractConfig()
        self.llm = llm or MyLLMService()
        self.filter_hero = FilterHero(self.config, self.llm)
        self.parse_hero = ParseHero(self.config, self.llm)

    def extract(
        self,
        text: str | dict,
        extraction_spec: WhatToRetain | List[WhatToRetain],
        text_type: Optional[str] = None,
        reduce_html: bool = True,
        enforce_llm_based_filter: bool = False,
        enforce_llm_based_parse: bool = False,
        filter_separately: bool = False,
    ) -> ExtractOp:
        """
        End-to-end extraction pipeline with rich metrics and error tracking.

        Parameters
        ----------
        text : raw HTML / JSON string / dict / plain text
            The source content to extract data from
        extraction_spec: one or many WhatToRetain specifications  
            Defines what data to extract and how
        text_type : "html" | "json" | "dict" | None
            Type hint for input processing optimization
        reduce_html : bool, default True
            Apply DomReducer to strip HTML down to essential content
        enforce_llm_based_filter : bool, default False
            Force JSON/dict inputs through LLM filter instead of fast-path
        enforce_llm_based_parse : bool, default False  
            Force structured data through LLM parse instead of fast-path
        filter_separately : bool, default False
            Run separate LLM calls per extraction spec (enables concurrency)
            
        Returns
        -------
        ExtractOp
            Rich result object with content, timing, usage, and error details
        """
        # ⏱️ Start timing the entire extraction operation
        extraction_start_time = time()
        
        # Phase-1: Filtering
        print("🔍 Starting filter phase...")
        filter_op: FilterOp = self.filter_hero.run(
            text,
            extraction_spec,
            text_type=text_type,
            filter_separately=filter_separately,
            reduce_html=reduce_html,
            enforce_llm_based_filter=enforce_llm_based_filter,
        )
        
        print(f"✅ Filter phase completed - Success: {filter_op.success}")

        # Check if filter phase failed
        if not filter_op.success:
            print("❌ Filter phase failed, short-circuiting parse phase")
            
            # Create failed parse operation
            parse_op = ParseOp.from_result(
                config=self.config,
                content=None,
                usage=None,
                start_time=time(),
                success=False,
                error="Filter phase failed - parse not attempted",
                generation_result=None
            )
            
            # Create rich ExtractOp with failure details
            return ExtractOp.from_operations(
                filter_op=filter_op,
                parse_op=parse_op,
                start_time=extraction_start_time,
                content=None
            )

        # Phase-2: Parsing
        print("🔧 Starting parse phase...")
        parse_op = self.parse_hero.run(
            filter_op.content, 
            extraction_spec,
            enforce_llm_based_parse=enforce_llm_based_parse
        )
        
        print(f"✅ Parse phase completed - Success: {parse_op.success}")
        
        # Create rich ExtractOp with all metrics
        result = ExtractOp.from_operations(
            filter_op=filter_op,
            parse_op=parse_op,
            start_time=extraction_start_time,
            content=parse_op.content if parse_op.success else None
        )
        
        print(f"🎯 Extraction completed in {result.elapsed_time:.3f}s - Overall success: {result.success}")
        
        return result
    
    # ─────────────────── extraction (async) ──────────────────
    async def extract_async(
        self,
        text: str | dict,
        extraction_spec: WhatToRetain | List[WhatToRetain],
        text_type: Optional[str] = None,
        reduce_html: bool = True,
        enforce_llm_based_filter: bool = False,
        enforce_llm_based_parse: bool = False,
        filter_separately: bool = False,
    ) -> ExtractOp:
        """
        Async end-to-end extraction pipeline with rich metrics.
        
        Same parameters as extract() but runs asynchronously for high-throughput scenarios.
        Particularly useful when filter_separately=True for concurrent processing.
        
        Returns
        -------
        ExtractOp
            Rich result object with content, timing, usage, and error details
        """
        # ⏱️ Start timing the entire extraction operation
        extraction_start_time = time()
        
        print("🔍 Starting async filter phase...")
        
        # Phase-1: Async Filtering
        filter_op: FilterOp = await self.filter_hero.run_async(
            text,
            extraction_spec,
            text_type=text_type,
            filter_separately=filter_separately,
            reduce_html=reduce_html,
            enforce_llm_based_filter=enforce_llm_based_filter,
        )
        
        print(f"✅ Async filter phase completed - Success: {filter_op.success}")

        # Check if filter phase failed
        if not filter_op.success:
            print("❌ Async filter phase failed, short-circuiting parse phase")
            
            parse_op = ParseOp.from_result(
                config=self.config,
                content=None,
                usage=None,
                start_time=time(),
                success=False,
                error="Filter phase failed - parse not attempted",
                generation_result=None
            )
            
            return ExtractOp.from_operations(
                filter_op=filter_op,
                parse_op=parse_op,
                start_time=extraction_start_time,
                content=None
            )

        # Phase-2: Async Parsing
        print("🔧 Starting async parse phase...")
        parse_op = await self.parse_hero.run_async(
            filter_op.content, 
            extraction_spec,
            enforce_llm_based_parse=enforce_llm_based_parse
        )
        
        print(f"✅ Async parse phase completed - Success: {parse_op.success}")
        
        # Create rich ExtractOp with all metrics
        result = ExtractOp.from_operations(
            filter_op=filter_op,
            parse_op=parse_op,
            start_time=extraction_start_time,
            content=parse_op.content if parse_op.success else None
        )
        
        print(f"🎯 Async extraction completed in {result.elapsed_time:.3f}s - Overall success: {result.success}")
        
        return result




wrt_to_source_filter_desc="""
### Task
Return **every content chunk** that is relevant to the main product
described in the page’s hero section.

### How to decide relevance
1. **Keep** a chunk if its title, brand, or descriptive text
   • matches the hero product **or**
   • is ambiguous / generic enough that it _could_ be the hero product.
2. **Discard** a chunk **only when** there is a **strong, explicit** signal
   that it belongs to a _different_ item (e.g. totally different brand,
   unrelated product type, “customers also bought” label).
3. When in doubt, **keep** the chunk (favor recall).

### Output
Return the retained chunks exactly as HTML snippets.
""".strip()
    


# ─────────────────────────── simple demo ───────────────────────────
def main() -> None:
    extractor = ExtractHero()
    
    # define what to extract
    items = [
        WhatToRetain(
            name="title",
            desc="Product title",
            example="Wireless Keyboard",
           # wrt_to_source_filter_desc=wrt_to_source_filter_desc
        ),
        WhatToRetain(
            name="price",
            desc="Product price with currency symbol",
            # regex_validator=r"€\d+\.\d{2}",
            example="€49.99",
            wrt_to_source_filter_desc=wrt_to_source_filter_desc
        ),
    ]
    
    sample_html = """
    <html><body>
      <div class="product">
        <h2 class="title">Wireless Keyboard</h2>
        <span class="price">€49.99</span>
      </div>
      <div class="product">
        <h2 class="title">USB-C Hub</h2>
        <span class="price">€29.50</span>
      </div>
    </body></html>
    """
    

   
    html_doc = load_html("extracthero/simple_html_sample_2.html")
    
    # op = extractor.extract(sample_html, items, text_type="html")
    op = extractor.extract(html_doc, items, text_type="html")
    print("Filtered corpus:\n", op.filter_op.content)
    print("Parsed result:\n", op.parse_op.content)


if __name__ == "__main__":
    main()
