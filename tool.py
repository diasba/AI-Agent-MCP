from fastmcp import FastMCP
import requests
from typing import Optional, List
from pydantic import BaseModel

mcp = FastMCP("C24 Product Tool")

class Product(BaseModel):
    id: int
    name: str
    type: str
    available: bool

class Params(BaseModel):
    page: int = 1
    filter: Optional[str] = None

def fetch_products_impl(params: Params) -> List[Product]:
    url = "https://3fcbdd45-930d-4a02-b0af-a2ab64be67c0.mock.pstmn.io/products"
    query = {"page": params.page, "limit": 10}

    if params.filter:
        # Filter bereinigen und in Kleinbuchstaben umwandeln
        raw = params.filter.strip().lower()
        filter_clean = raw.split(":")[-1].strip()
        print(f"🧪 [DEBUG] Filter cleaned: '{raw}' → '{filter_clean}'")
        
        # Filter zur Query hinzufügen
        query["filter"] = filter_clean

    try:
        response = requests.get(url, params=query)
        response.raise_for_status()
        products_raw = response.json().get("products", [])
        return [Product(**p) for p in products_raw]

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return [Product(id=0, name=f"ERROR: {str(e)}", type="none", available=False)]
    
@mcp.tool
def fetch_products(params: Params) -> List[Product]:
    return fetch_products_impl(params)