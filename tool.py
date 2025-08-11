from pydantic import BaseModel, Field
from fastmcp import FastMCP
import requests
from typing import Optional, List

mcp = FastMCP("C24 Product Tool")

class Product(BaseModel):
    id: int
    name: str
    type: str
    available: bool

class Params(BaseModel):
    page: int = Field(1, description="Page index (1-based).")
    filter: Optional[str] = Field(
        None,
        description=(
            "Optional filter. One of: 'circle', 'triangle', 'square', 'hexagon', 'available'. "
            "Also accepts synonyms like 'type:Triangle', 'Dreiecke', 'verfügbar'. "
            "Examples: filter='triangle', filter='available'"
        ),
    )

FILTER_MAPPING = {
    # en
    "circle":"circle","triangle":"triangle","square":"square","hexagon":"hexagon","available":"available",
    # de
    "kreis":"circle","kreise":"circle","dreieck":"triangle","dreiecke":"triangle",
    "quadrat":"square","quadrate":"square","sechseck":"hexagon","sechsecke":"hexagon","verfügbar":"available"
}

def normalize_filter(raw_filter: str) -> Optional[str]:
    if not raw_filter:
        return None
    raw_filter = raw_filter.strip().lower()
    if ":" in raw_filter:
        raw_filter = raw_filter.split(":", 1)[1].strip()
    parts = [p.strip() for p in raw_filter.split(",") if p.strip()]
    mapped = [FILTER_MAPPING.get(p) for p in parts]
    mapped = [m for m in mapped if m]
    return ",".join(mapped) if mapped else None

@mcp.tool
def fetch_products(params: Params) -> List[Product]:
    """
    Retrieve products from the C24 mock API.
    - Use 'filter' to narrow results: 'circle' | 'triangle' | 'square' | 'hexagon' | 'available'
    - Examples:
        * "Show only available products" -> filter="available"
        * "Please show me products of type Triangle" -> filter="triangle"
        * "Bitte nur Dreiecke" -> filter="triangle"
    """
    url = "https://3fcbdd45-930d-4a02-b0af-a2ab64be67c0.mock.pstmn.io/products"
    query = {"page": params.page, "limit": 10}
    if params.filter:
        api_filter = normalize_filter(params.filter)
        if api_filter:
            query["filter"] = api_filter
        else:
            print(f"[WARN] Ungültiger Filter '{params.filter}', es wird ohne Filter geladen.")
    print(f"[DEBUG] API Request: {query}")
    try:
        r = requests.get(url, params=query, timeout=10)
        r.raise_for_status()
        products_raw = r.json().get("products", [])
        return [Product(**p) for p in products_raw]
    except Exception as e:
        print(f"[ERROR] {e}")
        return [Product(id=0, name=f"ERROR: {str(e)}", type="none", available=False)]