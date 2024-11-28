from py3dbp import Packer, Bin, Item

# Dimensiones del contenedor (en cm)
container_length = 320  # Largo
container_width = 220   # Ancho
container_height = 300  # Asumimos una altura suficiente (ejemplo: 300 cm)

# Crear el contenedor (tráiler)
bin1 = Bin("Trailer", container_length, container_width, container_height, 99999)

# Dimensiones de las cajas (en cm)
caja1 = Item("Caja 10x10x10", 10, 10, 10, 1)
caja2 = Item("Caja 50x50x50", 50, 50, 50, 1)
caja3 = Item("Caja 70x70x70", 70, 70, 70, 1)
caja4 = Item("Caja 50x50x50_2", 50, 50, 50, 1)
caja5 = Item("Caja 70x70x70_2", 70, 70, 70, 1)

# Inicializar el empaquetador
packer = Packer()

# Agregar el contenedor al empaquetador
packer.add_bin(bin1)

# Agregar las cajas al empaquetador
packer.add_item(caja1)
packer.add_item(caja2)
packer.add_item(caja3)
packer.add_item(caja4)
packer.add_item(caja5)

# Ejecutar el algoritmo de bin packing
packer.pack()

for b in packer.bins:
    print(f"Contenedor: {b.string()}")
    print("Cajas empaquetadas:")
    for item in b.items:
        print(f"- {item.string()} at position {item.position}")
    print("Cajas no empaquetadas:")
    for item in b.unfitted_items:
        print(f"- {item.string()}")
    print("-" * 50)