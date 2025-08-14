from pydantic import BaseModel, Field
from fastmcp import FastMCP
import requests
from typing import Optional, List, Tuple, Callable, Any
from datetime import datetime, timezone
import math, time

mcp = FastMCP("C24 Product Tool")

class Price(BaseModel):
    value: float
    currency: str

class Product(BaseModel):
    id: int
    name: str
    type: str
    available: bool
    color: Optional[str] = None
    imageURL: Optional[str] = None
    colorCode: Optional[str] = None
    releaseDate: Optional[int] = None
    releaseDate_iso: Optional[str] = None
    description: Optional[str] = None
    longDescription: Optional[str] = None
    rating: Optional[float] = None
    price: Optional[Price] = None
    class Config:
        extra = "ignore"

class Params(BaseModel):
    page: int = Field(1, description="Page index (1-based). Use 0 to load ALL pages.")
    filter: Optional[str] = Field(
        None,
        description=("Optional filter. One of: 'circle', 'triangle', 'square', 'hexagon', 'available'. "
                     "Also accepts synonyms like 'type:Triangle', 'Dreiecke', 'verfügbar'."
                     "Please avoid octagons for searching and retrieving from the API")
    )
    sort: Optional[str] = Field(
        None,
        description=("Optional sorting: 'price:asc|desc', 'name:asc|desc', 'rating:asc|desc', "
                     "'release:asc|desc' (release = releaseDate).")
    )

FILTER_MAPPING = {
    "circle":"circle","triangle":"triangle","square":"square","hexagon":"hexagon","available":"available",
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

def _augment_product_dict(p: dict) -> dict:
    ts = p.get("releaseDate")
    if isinstance(ts, (int, float)):
        try:
            p["releaseDate_iso"] = datetime.fromtimestamp(int(ts), tz=timezone.utc).isoformat()
        except Exception:
            pass
    return p

# Sortier-Parser
def _parse_sort(sort: Optional[str]) -> Tuple[Callable[[Product], Any], bool]:
    """
    Gibt (key_func, reverse) zurück. reverse=True = absteigend.
    Unterstützt: price, name, rating, release
    """
    if not sort:
        return (lambda p: p.id, False)
    s = sort.strip().lower()
    if ":" in s:
        key, order = s.split(":", 1)
        order = order.strip()
    else:
        key, order = s, "asc"
    reverse = (order == "desc")

    if key in ("price", "preis"):
        # fehlende Preise ans Ende
        def k(p: Product):
            v = p.price.value if (p.price and isinstance(p.price.value, (int, float))) else math.inf
            return v
        return k, reverse
    if key in ("name", "produkt", "product"):
        return (lambda p: (p.name or "").lower()), reverse
    if key in ("rating", "bewertung"):
        def k(p: Product):
            return p.rating if isinstance(p.rating, (int, float)) else -math.inf
        return k, reverse
    if key in ("release", "releasedate", "datum"):
        def k(p: Product):
            return int(p.releaseDate) if isinstance(p.releaseDate, (int, float)) else -math.inf
        return k, reverse

    # Fallback: nach id
    return (lambda p: p.id), False

@mcp.tool
def fetch_products(params: Params) -> List[Product]:
    """
    Retrieve products from the C24 mock API.
    Supports pagination over all pages if params.page == 0 (special case).
    Supports optional local sorting via params.sort.
    """
    url = "https://3fcbdd45-930d-4a02-b0af-a2ab64be67c0.mock.pstmn.io/products"
    limit = 10
    results: List[Product] = []
    seen_ids = set()
    normalized_filter = normalize_filter(params.filter) if params.filter else None

    def load_page(page: int):
        query = {"page": page, "limit": limit}
        if normalized_filter:
            query["filter"] = normalized_filter
        print(f"[DEBUG] API Request: {query}")

        last_err = None
        for attempt in range(3):
            try:
                r = requests.get(url, params=query, timeout=10)
                r.raise_for_status()
                data = r.json()
                break
            except Exception as e:
                last_err = e
                print(f"[WARN] attempt {attempt+1}/3 failed: {e}")
                time.sleep(0.4 * (attempt + 1))
        else:
            raise RuntimeError(f"API nicht erreichbar: {last_err}")

        for p in data.get("products", []):
            pid = p.get("id")
            if isinstance(pid, int) and pid not in seen_ids:
                results.append(Product(**_augment_product_dict(p)))
                seen_ids.add(pid)

        nxt = data.get("pagination", {}).get("next_page")
        try:
            return int(nxt) if nxt is not None else None
        except Exception:
            return None

    if params.page == 0:
        page = 1
        guard = 0
        MAX_PAGES = 200
        while page is not None and guard < MAX_PAGES:
            page = load_page(page)
            guard += 1
    else:
        load_page(params.page)

    # lokale Absicherung für 'available'
    if normalized_filter and "available" in normalized_filter.split(","):
        results = [p for p in results if p.available]

    # Sortierung anwenden
    key_func, reverse = _parse_sort(params.sort)
    results.sort(key=key_func, reverse=reverse)

    return results