include("simple.jl")
using Genie, Genie.Renderer.Json, Genie.Requests, HTTP
using UUIDs
using StatsBase

# Diccionario para almacenar las instancias de simulación
instances = Dict()

# Ruta para inicializar simulaciones
route("/simulations", method = POST) do
    payload = jsonpayload()

    # Validar el payload
    if payload === nothing || !haskey(payload, "dim")
        return json(Dict("error" => "Invalid payload: 'dim' field is required"), status = 400)
    end

    x, y, z = payload["dim"]

    # Inicializar el modelo
    model = initialize_model((x, y, z))
    id = string(uuid1())
    instances[id] = model

    # Procesar agentes
    lifts = []
    for agent in allagents(model)
        if agent isa Lift
            push!(lifts, Dict(
                "id" => agent.id,
                "pos" => agent.pos,
                "direction" => agent.direction,
                "move_count" => agent.move_count,
                "carrying_box" => agent.carrying_box
            ))
        end
    end

    boxes = []
    for box in allagents(model)
        if box isa Box
            push!(boxes, Dict(
                "id" => box.id,
                "pos" => box.pos,
                "WHD" => [box.width, box.height, box.depth],
                "color" => "blue",
                "carried" => box.carried
            ))
        end
    end

    trailers = []
    for trailer in allagents(model)
        if trailer isa Trailer
            push!(trailers, Dict(
                "id" => trailer.id,
                "pos" => trailer.pos,
                "width" => trailer.dimensions[1],
                "height" => trailer.dimensions[2],
                "depth" => trailer.dimensions[3]
            ))
        end
    end

    # Respuesta con los datos iniciales de la simulación
    json(Dict(
        "Location" => "/simulations/$id",
        "lifts" => lifts,
        "boxes" => boxes,
        "trailers" => trailers
    ))
end

# Ruta para ejecutar un paso de simulación
route("/simulations/:id") do
    model = instances[params(:id)]
    # Ejecutar un paso de la simulación
    run!(model, 1)

    # Actualizar datos de los agentes
    lifts = []
    for agent in allagents(model)
        if agent isa Lift
            push!(lifts, Dict(
                "id" => agent.id,
                "pos" => agent.pos,
                "direction" => agent.direction,
                "move_count" => agent.move_count
            ))
        end
    end

    boxes = []
    for box in allagents(model)
        if box isa Box
            push!(boxes, Dict(
                "id" => box.id,
                "pos" => box.pos,
                "WHD" => [box.width, box.height, box.depth],
                "color" => "blue"
            ))
        end
    end

    trailers = []
    for trailer in allagents(model)
        if trailer isa Trailer
            push!(trailers, Dict(
                "id" => trailer.id,
                "pos" => trailer.pos,
                "width" => trailer.dimensions[1],
                "height" => trailer.dimensions[2],
                "depth" => trailer.dimensions[3]
            ))
        end
    end

    # Respuesta con los datos actualizados de la simulación
    json(Dict(
        "message" => "Simulation updated",
        "lifts" => lifts,
        "boxes" => boxes,
        "trailers" => trailers
    ))
end

# Configuración de CORS
Genie.config.run_as_server = true
Genie.config.cors_headers["Access-Control-Allow-Origin"] = "*"
Genie.config.cors_headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
Genie.config.cors_headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
Genie.config.cors_allowed_origins = ["*"]

# Levantar el servidor
up()