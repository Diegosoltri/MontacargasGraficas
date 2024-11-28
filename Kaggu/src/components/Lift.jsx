const Lift = ({ position }) => {
  const [x, y, z] = position;
  console.log("Lift position:", position); 

  return (
    <>
      {/* Base of the forklift */}
      <mesh position={[x, y + 1, z]}>
        <boxGeometry args={[6, 2, 4]} />
        <meshStandardMaterial color="yellow" />
      </mesh>

      {/* Wheels */}
      <mesh position={[x - 2.5, y, z + 1.5]} rotation={[Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[1, 1, 0.5, 32]} />
        <meshStandardMaterial color="black" />
      </mesh>
      <mesh position={[x + 2.5, y, z + 1.5]} rotation={[Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[1, 1, 0.5, 32]} />
        <meshStandardMaterial color="black" />
      </mesh>
      <mesh position={[x - 2.5, y, z - 1.5]} rotation={[Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[1, 1, 0.5, 32]} />
        <meshStandardMaterial color="black" />
      </mesh>
      <mesh position={[x + 2.5, y, z - 1.5]} rotation={[Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[1, 1, 0.5, 32]} />
        <meshStandardMaterial color="black" />
      </mesh>

      {/* Vertical mast */}
      <mesh position={[x, y + 4, z + 1.5]}>
        <boxGeometry args={[0.5, 8, 0.5]} />
        <meshStandardMaterial color="black" />
      </mesh>
      <mesh position={[x, y + 4, z - 1.5]}>
        <boxGeometry args={[0.5, 8, 0.5]} />
        <meshStandardMaterial color="black" />
      </mesh>

      {/* Forks */}
      <mesh position={[x + 1, y + 6, z + 1]}>
        <boxGeometry args={[4, 0.5, 0.5]} />
        <meshStandardMaterial color="black" />
      </mesh>
      <mesh position={[x + 1, y + 6, z - 1]}>
        <boxGeometry args={[4, 0.5, 0.5]} />
        <meshStandardMaterial color="black" />
      </mesh>

      {/* Driver Seat */}
      <mesh position={[x - 1.5, y + 2.5, z]}>
        <boxGeometry args={[1, 1, 1]} />
        <meshStandardMaterial color="black" />
      </mesh>

      {/* Control Stick */}
      <mesh position={[x - 1, y + 3, z]} rotation={[0, 0, Math.PI / 4]}>
        <cylinderGeometry args={[0.1, 0.1, 1]} />
        <meshStandardMaterial color="black" />
      </mesh>
    </>
  );
};

export default Lift;
