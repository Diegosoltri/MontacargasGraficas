import { Line } from "@react-three/drei";

// Axes component to render x, y, and z axes
const Axes = () => {
  return (
    <>
      {/* X-axis (red) */}
      <Line
        points={[
          [0, 0, 0], // Origin
          [48, 0, 0], // X-axis end
        ]}
        color="red"
        lineWidth={2}
      />
      {/* Y-axis (green) */}
      <Line
        points={[
          [0, 0, 0], // Origin
          [0, 48, 0], // Y-axis end
        ]}
        color="green"
        lineWidth={2}
      />
      {/* Z-axis (blue) */}
      <Line
        points={[
          [0, 0, 0], // Origin
          [0, 0, 48], // Z-axis end
        ]}
        color="blue"
        lineWidth={2}
      />
    </>
  );
};

export default Axes;
