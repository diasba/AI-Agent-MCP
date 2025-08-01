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

# 🔹 Normale Funktion (nicht direkt dekorieren)
def fetch_products_impl(params: Params) -> List[Product]:
    url = "https://3fcbdd45-930d-4a02-b0af-a2ab64be67c0.mock.pstmn.io/products"
    query = {"page": params.page, "limit": 10}
    if params.filter:
        query["filter"] = params.filter
    try:
        response = requests.get(url, params=query)
        response.raise_for_status()
        products = response.json().get("products", [])
        return [Product(**p) for p in products]
    except Exception as e:
        return [Product(id=0, name=f"ERROR: {str(e)}", type="none", available=False)]

# 🔹 Tool-Registrierung über Wrapper
@mcp.tool
def fetch_products(params: Params) -> List[Product]:
    return fetch_products_impl(params)