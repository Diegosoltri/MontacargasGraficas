# Crear un bin de ejemplo
bin = py3dbp.Bin("Trailer", 10, 10, 15, 99999)

# Crear un packer
packer = py3dbp.Packer()
packer.add_bin(bin)

# Añadir algunas cajas
item1 = py3dbp.Item("Box1", 2, 2, 2, 1)
item2 = py3dbp.Item("Box2", 3, 3, 3, 1)
item3 = py3dbp.Item("Box3", 1, 1, 1, 1)
packer.add_item(item1)
packer.add_item(item2)
packer.add_item(item3)

# Empacar las cajas
packer.pack()

# Imprimir los resultados
for bin in packer.bins
    println("Bin empacado:")
    for item in bin.items
        println("Item: $(item.name), Posición: $(item.position), Dimensiones: $(item.width)x$(item.height)x$(item.depth)")
    end
end