const Box = ({ position, dimensions, color = '#1e40af' }) => {
	// Calculate the center position
	const centerX = position[0] + dimensions[0] / 2; // Corner X + half width
	const centerY = position[1] + dimensions[1] / 2; // Corner Y + half height
	const centerZ = position[2] + dimensions[2] / 2; // Corner Z + half depth

	return (
		<mesh position={[centerX, centerY, centerZ]}>
			<boxGeometry args={dimensions} />
			<meshStandardMaterial color={color} />
		</mesh>
	);
};

export default Box;
