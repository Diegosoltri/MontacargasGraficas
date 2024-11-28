import Container from "./Container";
import Axes from "./Axes";
import { OrbitControls } from "@react-three/drei";
import Box from "./Box";
import Lift from "./Lift";

const Scene = ({ boxes, lifts, container }) => {
  return (
    <>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} />
      <gridHelper args={[97, 97]} />

      {/* Render the axes */}
      <Axes />

      {/* Render the container */}
      {container && container.pos && container.width && container.height && container.depth ? (
        <Container
          position={[
            container.pos[0] ?? 0, 
            container.pos[1] ?? 0, 
            container.pos[2] ?? 0
          ]}
          width={container.width}
          height={container.height}
          depth={container.depth}
        />
      ) : (
        console.warn("Container data is incomplete:", container)
      )}

      {/* Render the boxes */}
      {boxes && boxes.length > 0 ? (
        boxes.map((box, index) =>
          box.pos && box.WHD ? (
            <Box
              key={index}
              position={[
                box.pos[0] ?? 0,
                box.pos[1] ?? 0,
                box.pos[2] ?? 0,
              ]}
              dimensions={[
                box.WHD[0] ?? 1,
                box.WHD[1] ?? 1,
                box.WHD[2] ?? 1,
              ]}
              color={box.color || "red"}
            />
          ) : (
            console.warn("Box data is incomplete:", box) || null
          )
        )
      ) : (
        console.warn("No boxes to render")
      )}

      {/* Render the lifts */}
      {lifts && lifts.length > 0 ? (
        lifts.map((lift, index) =>
          lift.pos ? (
            <Lift
              key={index}
              position={[
                lift.pos[0] || 0,
                lift.pos[1] || 0,
                lift.pos[2] || 0,
              ]}
            />
          ) : (
            console.warn("Lift data is incomplete:", lift) || null
          )
        )
      ) : (
        console.warn("No lifts to render")
      )}

      <OrbitControls />
    </>
  );
};

export default Scene;