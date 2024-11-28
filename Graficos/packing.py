from py3dbp import Bin, Item, Packer

class PackingManager:
    def __init__(self, container_dimensions):
        """
        Inicializa el contenedor.
        :param container_dimensions: (width, height, length) del contenedor.
        """
        self.container = Bin('Camion', *container_dimensions)
        self.packer = Packer()
        self.packer.add_bin(self.container)

    def add_box(self, box_dimensions, box_id):
        """
        Agrega una caja al sistema de packing.
        :param box_dimensions: (width, height, length) de la caja.
        :param box_id: Identificador único de la caja.
        """
        self.packer.add_item(Item(f'Box-{box_id}', *box_dimensions))

    def pack(self):
        """
        Realiza el acomodo de las cajas en el contenedor.
        """
        self.packer.pack()

    def get_placements(self):
        """
        Obtiene la lista de posiciones donde se colocaron las cajas.
        """
        placements = []
        for placed_item in self.container.placed_items:
            placements.append({
                'id': placed_item.name,
                'position': placed_item.position,
                'dimensions': (placed_item.width, placed_item.height, placed_item.depth)
            })
        return placements