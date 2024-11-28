import React, { useState, useEffect } from "react";
import {
  Badge,
  Button,
  Card,
  Flex,
  Heading,
  Loader,
  Text,
  View,
} from "@aws-amplify/ui-react";
import "@aws-amplify/ui-react/styles.css";
import { Canvas } from "@react-three/fiber";
import Scene from "./components/Scene";
import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000", // URL base de tu backend
  withCredentials: false,          // Opcional: si necesitas cookies
  headers: {
    "Content-Type": "application/json", // Tipo de contenido esperado por el backend
  },
});

const BoxVisualization = () => {
  const [simulationId, setSimulationId] = useState(null);
  const [boxes, setBoxes] = useState([]);
  const [lifts, setLifts] = useState([]);
  const [container, setContainer] = useState(null);
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isRunning, setIsRunning] = useState(false);

  const initializeSimulation = async () => {
    try {
      setLoading(true);
      setError(null);
  
      // Envía el cuerpo correcto en la solicitud POST
      const { data } = await api.post("/simulations", {
        dim: [48, 48, 48], // Asegúrate de ajustar estos valores según lo necesario
      });
  
      const id = data.Location.split("/").pop();
      setSimulationId(id);

      if (!data.boxes || data.boxes.length === 0) {
        console.warn("No boxes received from the backend");
      }
  
      setBoxes(data.boxes); // Asegúrate de que este paso esté configurando correctamente las cajas
      setContainer(data.trailers[0]); // Usar el primer tráiler
      setLifts(data.lifts);
  
      console.log("Container data: ", data.trailers[0]);
    } catch (error) {
      let errorMessage = "Failed to initialize simulation";
      if (error.response) {
        errorMessage = `Server error: ${error.response.status}`;
      } else if (error.request) {
        errorMessage = "No response from server";
      } else {
        errorMessage = error.message;
      }
      setError(errorMessage);
      console.error("Error details:", error);
    } finally {
      setLoading(false);
    }
  };

  const stepSimulation = async () => {
    if (!simulationId) return;

    try {
      setError(null);

      const { data } = await api.get(`/simulations/${simulationId}`);
      setBoxes(data.boxes);
      setLifts(data.lifts);
      setContainer(data.trailers[0]);
      setStep(data.step);
    } catch (error) {
      let errorMessage = "Failed to step simulation";
      if (error.response) {
        errorMessage = `Server error: ${error.response.status}`;
      } else if (error.request) {
        errorMessage = "No response from server";
      } else {
        errorMessage = error.message;
      }
      setError(errorMessage);
      console.error("Error details:", error);
    }
  };

  useEffect(() => {
    let interval;
    if (isRunning) {
      interval = setInterval(() => {
        stepSimulation();
      }, 100);
    }
    return () => clearInterval(interval);
  }, [isRunning, simulationId]);

  return (
    <Card padding="large" variation="elevated">
      <Flex direction="column" gap="medium">
        <Heading level={3}>3D Box Visualization</Heading>

        <Flex direction="row" gap="small" alignItems="center">
          <Button
            onClick={initializeSimulation}
            isDisabled={loading || simulationId !== null}
            variation="primary"
          >
            Initialize Simulation
          </Button>

          <Button
            onClick={() => setIsRunning(!isRunning)}
            isDisabled={simulationId === null}
            variation="primary"
          >
            {isRunning ? "Pause Simulation" : "Start Simulation"}
          </Button>

          {loading && <Loader size="small" />}
        </Flex>

        {error && (
          <View padding="small" backgroundColor="error.10">
            <Text color="error.80">{error}</Text>
          </View>
        )}

        <View
          height="600px"
          borderRadius="medium"
          backgroundColor="background.secondary"
        >
          <Canvas camera={{ position: [100, 100, 100] }}>
            {container && <Scene boxes={boxes} lifts={lifts} container={container} />}
          </Canvas>
        </View>

        <Flex direction="row" gap="small" alignItems="center">
          <Text>Current Step:</Text>
          <Badge variation="info">{step}</Badge>
          {simulationId && (
            <Text fontSize="small" color="font.tertiary">
              Simulation ID: {simulationId}
            </Text>
          )}
        </Flex>

        <Flex direction="column" gap="small">
          <Text fontSize="small" color="font.secondary">
            Statistics:
          </Text>
          <Text fontSize="small">Total Boxes: {boxes.length}</Text>
          <Text fontSize="small">
            Packed Boxes: {boxes.filter((box) => box.packed).length}
          </Text>
        </Flex>
      </Flex>
    </Card>
  );
};

export default BoxVisualization;