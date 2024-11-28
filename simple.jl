using Agents, Random, PyCall

# Importar py3dbp
py3dbp = pyimport("py3dbp")

# Definición de agentes
@agent struct Box(GridAgent{3, Float64})
    width::Int
    height::Int
    depth::Int
    carried::Bool = false
    packed::Bool = false  # Inicializar como `false` por defecto
end

@agent struct Lift(GridAgent{3, Float64})
    carried_box::Union{Box, Nothing}
    carrying_box::Bool = false
    direction::Symbol
    move_count::Int
end

@agent struct Trailer(GridAgent{3, Float64})
    dimensions::Tuple{Int, Int, Int}
    py3dbp_bin::PyObject
    packed_boxes::Vector{Box}
end

# Inicializar el espacio
space = GridSpace((100, 100, 100); periodic=false, metric=:manhattan)

function agent_step!(agent::Box, model)
    """
    if agent.carried == true
        for other in agents_in_position(agent, model)
            if other isa Lift && other.carrying_box == true && other.carried_box == agent
                agent.pos = other.pos
            end
        end
    end"""
end

function agent_step!(agent::Trailer, model)
end

function agent_step!(agent::Lift, model)
    directions = Dict(
        :north => (0, 0, 1),
        :south => (0, 0, -1),
        :east  => (1, 0, 0),
        :west  => (-1, 0, 0),
        :northeast => (1, 0, 1),
        :northwest => (-1, 0, 1),
        :southeast => (1, 0, -1),
        :southwest => (-1, 0, -1),
        :up => (0, 1, 0),
        :down => (0, -1, 0)
    )
    current_pos = agent.pos
    move = directions[agent.direction]
    new_pos = current_pos .+ move

    if agent.carrying_box == false
        boxes = [box for box in allagents(model) if box isa Box && !box.packed && !box.carried]
        if !isempty(boxes)
            target_box_pos = boxes[1].pos
            # Calcular la dirección hacia la caja
            dx = target_box_pos[1] - current_pos[1]
            dy = target_box_pos[2] - current_pos[2]
            dz = target_box_pos[3] - current_pos[3]
            # Determina la dirección hacia la caja considerando diagonales
            if abs(dx) >= abs(dy) && abs(dx) >= abs(dz)
                agent.direction = dx > 0 ? :east : :west
            elseif abs(dy) >= abs(dx) && abs(dy) >= abs(dz)
                agent.direction = dy > 0 ? :up : :down
            else
                agent.direction = dz > 0 ? :north : :south
            end
            move = directions[agent.direction]
            new_pos = current_pos .+ move
            if agent.pos != target_box_pos
                move_agent!(agent, new_pos, model)
            elseif  agent.pos == target_box_pos
                boxes[1].carried = true
                agent.carried_box = boxes[1]
                agent.carried_box.carried = true
                println("Lift $(agent.id) recogió una caja con las caracteristicas: $(boxes[1].width) x $(boxes[1].height) x $(boxes[1].depth).")
                agent.carrying_box = true
                println("Lift $(agent.id) recogió la caja en $(target_box_pos).")  
                boxes[1].pos = new_pos
                agent.carried_box.pos = new_pos
            end
        else
            println("No quedan cajas por recoger o empacar.")
        end
    end
    
    if agent.carrying_box == true
        nearby_trailer = [cont for cont in allagents(model) if cont isa Trailer]
        if !isempty(nearby_trailer)
            #trailer = nearby_trailer[1]
            target_trailer_pos = nearby_trailer[1].pos
            # Calcular la dirección hacia el tráiler
            dx = target_trailer_pos[1] - current_pos[1]
            dy = target_trailer_pos[2] - current_pos[2]
            dz = target_trailer_pos[3] - current_pos[3]
            # Determina la dirección hacia el trailer considerando diagonales
            if abs(dx) >= abs(dy) && abs(dx) >= abs(dz)
                # Predomina el movimiento en X
                if abs(dz) > 0
                    agent.direction = dx > 0 ? (dz > 0 ? :northeast : :southeast) : (dz > 0 ? :northwest : :southwest)
                else
                    agent.direction = dx > 0 ? :east : :west
                end
            elseif abs(dz) >= abs(dx) && abs(dz) >= abs(dy)
                # Predomina el movimiento en Z
                if abs(dx) > 0
                    agent.direction = dz > 0 ? (dx > 0 ? :northeast : :northwest) : (dx > 0 ? :southeast : :southwest)
                else
                    agent.direction = dz > 0 ? :north : :south
                end
            else
                # Predomina el movimiento en Y
                agent.direction = dy > 0 ? :up : :down
            end
            move = directions[agent.direction]
            new_pos = current_pos .+ move
            move_agent!(agent, new_pos, model)
            agent.carried_box.pos = new_pos
            println("Caja cargada por lift $(agent.id) en posición $(agent.carried_box.pos).")
            if agent.pos == target_trailer_pos
                pack_boxes!(nearby_trailer[1], [agent.carried_box])
                nearby_trailer[1].packed_boxes = [agent.carried_box; nearby_trailer[1].packed_boxes]
                agent.carried_box.packed = true
                agent.carried_box = nothing
                agent.carrying_box = false
                println("Lift entregó una caja al tráiler.")
                println("Cajas en el tráiler: $(length(nearby_trailer[1].packed_boxes))")
            end
        end
    end
end

function initialize_model(dimensions=(49, 49, 49))
    # Crear el espacio y el modelo con las dimensiones especificadas
    space = GridSpace(dimensions; periodic=false, metric=:manhattan)
    model = ABM(Union{Box, Lift, Trailer}, space; agent_step!)

    # Crear tráiler
    trailer_dimensions = (5, 5, 8)  # Dimensiones del tráiler
    pos = (2, 1, 2)  # Posición central del tráiler
    create_trailer(model, pos, trailer_dimensions)

    # Rango para la esquina, ajusta los valores a tu necesidad
    x_range = (dimensions[1] - 8, dimensions[1]-3)  # Rango de x en la esquina
    y_pos = 1  # Fijar y a 1 (pegado al suelo)
    z_range = (dimensions[3] - 30, dimensions[3]-3)  # Rango de z en la esquina

    # Crear cajas aleatorias dentro del rango de la esquina
    for _ in 1:15
        x_pos = rand(x_range[1]:x_range[2])  # Posición aleatoria en el rango de x
        z_pos = rand(z_range[1]:z_range[2])  # Posición aleatoria en el rango de z
        # Crear la caja en la posición aleatoria, con y fijo en 1
        create_random_box(model, (x_pos, y_pos, z_pos))
    end

    # Crear montacargas en el medio sobre el eje x, z
    lift_pos = (dimensions[1] ÷ 2, 1, dimensions[3] ÷ 2)  # y = 1, x y z centrados
    add_agent!(Lift, model; pos=lift_pos,  carried_box=nothing, carrying_box=false, direction=:north, move_count=0)

    return model
end

function create_trailer(model, pos, dimensions)
    py3dbp_bin = py3dbp.Bin("Trailer", dimensions[1], dimensions[2], dimensions[3], 99999)
    add_agent!(Trailer, model; pos=pos, dimensions=dimensions, py3dbp_bin=py3dbp_bin, packed_boxes=[])
end

function create_random_box(model, pos)
    sizes = [(1, 1, 1), (2, 2, 2), (3, 3, 3)]
    dimensions = rand(sizes)
    println("Intentando crear caja en posición: $pos")
    add_agent!(Box, model; pos=pos, width=dimensions[1], height=dimensions[2], depth=dimensions[3], carried = false, packed=false)
end

function pack_boxes!(trailer::Trailer, boxes::Vector{Box})
    packer = py3dbp.Packer()
    packer.add_bin(trailer.py3dbp_bin)

    for box in boxes
        if box.packed === false
            item = py3dbp.Item("Box", box.width, box.height, box.depth, 1)
            packer.add_item(item)
        end
    end

    packer.pack()

    # Get the Python built-in 'float' function
    float_py = pybuiltin("float")

    for item in trailer.py3dbp_bin.items
        # Convert each element of item.position using float_py
        pos = [float_py(x) for x in item.position]
        println("Posición del item empaquetado: ", pos)

        # Find the corresponding box
        packed_box = findfirst(b -> b.width == item.width && b.height == item.height && b.depth == item.depth, boxes)
        if packed_box !== nothing
            boxes[packed_box].packed = true
            # Update the position of the box in the model
            boxes[packed_box].pos = (
                trailer.pos[1] + Int(pos[1]),  # Adjust for Julia's 1-based indexing
                trailer.pos[2] + Int(pos[2]),
                trailer.pos[3] + Int(pos[3])
            )
            push!(trailer.packed_boxes, boxes[packed_box])
        end
    end
end

# Ejecutar simulación
model = initialize_model()