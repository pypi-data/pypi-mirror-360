import numpy as np

class CNNoptimiser:
    def _AdamsOptimiserWithBatches(self, inputData, labels, weights, biases, batchSize, alpha, beta1, beta2, epsilon):
        """
        Performs Adam optimisation on the CNN weights and biases using mini batches.

        Args:
            inputData (ndarray): All the training data.
            labels (ndarray): All the true labels for the training data.
            weights (list of ndarray): Current weights of the CNN layers.
            biases (list of ndarray): Current biases of the CNN layers.
            batchSize (int): Size of batches.
            alpha (float): Learning rate.
            beta1 (float): Decay rate for the first moment.
            beta2 (float): Decay rate for the second moment. 
            epsilon (float): Small constant to avoid division by zero.
        
        Returns: 
            allNodes (list): List of layers for each input processed.
            weights (list of ndarray): Updated weights after optimisation.
            biases (list of ndarray): Updated biases after optimisation.
        """
        firstMomentWeight, firstMomentBias = self._initialiseMoment(weights, biases)
        secondMomentWeight, secondMomentBias = self._initialiseMoment(weights, biases)
        weightGradients, biasGradients = self._initialiseGradients(weights, biases)
        allNodes = []
        for i in range(0, len(inputData), batchSize):
            batchData = inputData[i:i+batchSize]
            batchLabels = labels[i:i+batchSize]
            for j in range(len(batchData)):
                layerNodes = self.forward(batchData[j])
                allNodes.append(layerNodes)
                w, b = self._backpropagation(layerNodes, batchLabels[j])
                weightGradients, biasGradients = self._addGradients(batchSize, weightGradients, biasGradients, w, b)
            weights, biases, firstMomentWeight, firstMomentBias, secondMomentWeight, secondMomentBias = self._Adams(weightGradients, biasGradients, weights, biases, i + 1, firstMomentWeight, firstMomentBias, secondMomentWeight, secondMomentBias, alpha, beta1, beta2, epsilon)
            weightGradients, biasGradients = self._initialiseGradients(weights, biases)
            print(f"finished batch: {(i // batchSize) + 1}/{len(inputData) // batchSize}")
        return allNodes, weights, biases

    def _AdamsOptimiserWithoutBatches(self, inputData, labels, weights, biases, alpha, beta1, beta2, epsilon):
        """
        Performs Adam optimisation on the CNN weights and biases without using batches.

        Args:
            inputData (ndarray): All the training data.
            labels (ndarray): All the true labels for the training data.
            weights (list of ndarray): Current weights of the CNN layers.
            biases (list of ndarray): Current biases of the CNN layers.
            alpha (float): Learning rate.
            beta1 (float): Decay rate for the first moment.
            beta2 (float): Decay rate for the second moment. 
            epsilon (float): Small constant to avoid division by zero.
        
        Returns: 
            allNodes (list): List of layers for each input processed.
            weights (list of ndarray): Updated weights after optimisation.
            biases (list of ndarray): Updated biases after optimisation.
        """
        firstMomentWeight, firstMomentBias = self._initialiseMoment(weights, biases)
        secondMomentWeight, secondMomentBias = self._initialiseMoment(weights, biases)
        weightGradients, biasGradients = self._initialiseGradients(weights, biases)
        allNodes = []
        for i in range(len(inputData)):
            layerNodes = self.forward(inputData[i])
            allNodes.append(layerNodes)
            w, b = self._backpropagation(layerNodes, labels[i])
            weightGradients, biasGradients = self._addGradients(1, weightGradients, biasGradients, w, b)
            weights, biases, firstMomentWeight, firstMomentBias, secondMomentWeight, secondMomentBias = self._Adams(weightGradients, biasGradients, weights, biases, i + 1, firstMomentWeight, firstMomentBias, secondMomentWeight, secondMomentBias, alpha, beta1, beta2, epsilon)
            weightGradients, biasGradients = self._initialiseGradients(weights, biases)
        return allNodes, weights, biases

    def _Adams(self, weightGradients, biasGradients, weights, biases, timeStamp, firstMomentWeight, firstMomentBias, secondMomentWeight, secondMomentBias, alpha, beta1, beta2, epsilon):
        """
        Performs a single Adam optimisation update on weights and biases.

        Args:
            weightGradients (list of ndarray): Gradients of the weights.
            biasGradients (list of ndarray): Gradients of the biases.
            weights (list of ndarray): Current weights.
            biases (list of ndarray): Current biases.
            timeStamp (int): The current time step, used for bias correction.
            firstMomentWeight (list of ndarray): First moment estimates for weights.
            firstMomentBias (list of ndarray): First moment estimates for biases.
            secondMomentWeight (list of ndarray): Second moment estimates for weights.
            secondMomentBias (list of ndarray): Second moment estimates for biases.
            alpha (float): Learning rate.
            beta1 (float): Decay rate for the first moment.
            beta2 (float): Decay rate for the second moment. 
            epsilon (float): Small constant to avoid division by zero.
        
        Returns: 
            weights (list of ndarray): Updated weights after optimisation.
            biases (list of ndarray): Updated biases after optimisation.
            firstMomentWeight (list of ndarray): Updated firstMomentWeight after optimisation.
            firstMomentBias (list of ndarray): Updated firstMomentBias after optimisation.
            secondMomentWeight (list of ndarray): Updated secondMomentWeight after optimisation.
            secondMomentBias (list of ndarray): Updated secondMomentBias after optimisation.
        """
        for i in range(len(weights)):
            for j in range(len(weights[i])):
                firstMomentWeight[i][j] = beta1 * np.array(firstMomentWeight[i][j]) + (1 - beta1) * weightGradients[i][j]
                secondMomentWeight[i][j] = beta2 * np.array(secondMomentWeight[i][j]) + (1 - beta2) * (weightGradients[i][j] ** 2)

                firstMomentWeightHat = firstMomentWeight[i][j] / (1 - beta1 ** timeStamp)
                secondMomentWeightHat = secondMomentWeight[i][j] / (1 - beta2 ** timeStamp)

                weights[i][j] -= alpha * firstMomentWeightHat / (np.sqrt(secondMomentWeightHat) + epsilon)
            
        for i in range(len(biases)):
            for j in range(len(biases[i])):
                firstMomentBias[i][j] = beta1 * np.array(firstMomentBias[i][j]) + (1 - beta1) * np.array(biasGradients[i][j])
                secondMomentBias[i][j] = beta2 * np.array(secondMomentBias[i][j]) + (1 - beta2) * (np.array(biasGradients[i][j]) ** 2)

                firstMomentBiasHat = firstMomentBias[i][j] / (1 - beta1 ** timeStamp)
                secondMomentBiasHat = secondMomentBias[i][j] / (1 - beta2 ** timeStamp)

                biases[i][j] -= alpha * firstMomentBiasHat / (np.sqrt(secondMomentBiasHat) + epsilon)
        return weights, biases, firstMomentWeight, firstMomentBias, secondMomentWeight, secondMomentBias

    def _initialiseGradients(self, weights, biases):
        """
        Initialise the weight and bias gradients as zero arrays with the same shape as weights and biases.

        Args:
            weights (list of ndarray): The weights of the CNN layers.
            biases (list of ndarray): The biases of the CNN layers.

        Returns:
            weightGradients (list of ndarray): Initialised gradients for weights.
            biasGradients (list of ndarray): Initialised gradients for biases.
        """
        weightGradients, biasGradients = [], []
        for i in weights:
            w = []
            for j in i:
                w.append(np.zeros_like(j, dtype=np.float64))
            weightGradients.append(w)
        for i in biases:
            b = []
            for j in i:
                b.append(np.zeros_like(j, dtype=np.float64))
            biasGradients.append(b)
        return weightGradients, biasGradients

    def _addGradients(self, batchSize, weightGradients, biasGradients, w, b):
        """
        Adds gardients from a batch to the accumulated gradients.

        Args:
            batchSize (int): Number of samples in the current batch.
            weightGradients (list of ndarray): Accumulated weight gradients.
            biasGradients (list of ndarray): Accumulated bias gradients. 
            w (list of ndarray): Gradients of the weights from the current batch.
            b (list of ndarray): Gradients of the biases from the current batch.
        
        Returns:
            weightGradients (list of ndarray): Updated accumulated weight gradients.
            biasGradients (list of ndarray): Updated accumulated bias gradients. 
        """
        for i in range(len(weightGradients)):
            for j in range(len(weightGradients[i])):
                weightGradients[i][j] += np.array(w[i][j]) / batchSize
            #weightGradients[i] = np.clip(weightGradients[i], -1, 1)

        for i in range(len(biasGradients)):
            for j in range(len(biasGradients[i])):
                biasGradients[i][j] += np.array(b[i][j]) / batchSize
            #biasGradients[i] = np.clip(biasGradients[i], -1, 1)
        return weightGradients, biasGradients

    def _initialiseMoment(self, weights, biases):
        """
        Initialise the first and second moment estimates for Adam optimiser as zero arrays matching weights and biases.

        Args:
            weights (list of ndarray): The weights of the CNN layers.
            biases (list of ndarray): The biases of the CNN layers.

        Returns:
            momentWeight (list of ndarray): Initialised moments for weights.
            momentBias (list of ndarray): Initialised moments for biases.
        """
        momentWeight = []
        momentBias = []
        for i in weights:
            w = []
            for j in i:
                w.append(np.zeros_like(j))
            momentWeight.append(w)
        for i in biases:
            b = []
            for j in i:
                b.append(np.zeros_like(j))
            momentBias.append(b)
        return momentWeight, momentBias

    