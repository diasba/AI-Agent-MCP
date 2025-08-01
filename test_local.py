from tool import fetch_products_impl, Params

result = fetch_products_impl(Params(page=1, filter="Triangle"))
for product in result:
    print(product)