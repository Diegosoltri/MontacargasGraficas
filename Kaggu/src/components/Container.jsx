const Container = ({ position, width, height, depth }) => {
	// Calculate center position assuming the container starts at (0, 0, 0)
	const centerX = position[0] + width / 2;
	const centerY = position[1] + height / 2;
	const centerZ = position[2] + depth / 2;

	return (
		<mesh position={[centerX, centerY, centerZ]}>
			<boxGeometry args={[width, height, depth]} />
			<meshStandardMaterial color="brown" transparent opacity={0.3} />
		</mesh>
	);
};

export default Container;
