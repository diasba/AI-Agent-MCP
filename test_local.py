from tool import fetch_products_impl, Params

print("\n🔹 Test 1: Triangle (mit 'type:' Präfix)")
result = fetch_products_impl(Params(page=1, filter="type:Triangle"))
for p in result:
    print(p)

print("\n🔹 Test 2: Triangle (ohne Präfix)")
result = fetch_products_impl(Params(page=1, filter="Triangle"))
for p in result:
    print(p)

print("\n🔹 Test 3: Hexagon (mit Leerzeichen)")
result = fetch_products_impl(Params(page=1, filter="  Hexagon "))
for p in result:
    print(p)

print("\n🔹 Test 4: Available (als Wert)")
result = fetch_products_impl(Params(page=1, filter="Available"))
for p in result:
    print(p)

print("\n🔹 Test 5: Square (mit 'filter:' statt 'type:')")
result = fetch_products_impl(Params(page=1, filter="filter:Square"))
for p in result:
    print(p)

print("\n🔹 Test 6: Kein Filter (alle Produkte)")
result = fetch_products_impl(Params(page=1))
for p in result:
    print(p)

print("\n🔹 Test 7: Ungültiger Filter (erwarte leere Liste)")
result = fetch_products_impl(Params(page=1, filter="UnknownShape"))
for p in result:
    print(p)