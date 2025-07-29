import numpy as np

class Optimisers:
    def _trainGradientDescent(self, inputData, labels, epochs, weights, biases, momentumCoefficient, momentumDecay, useMomentum, velocityWeight, velocityBias, learningRate, _):
        """
        Trains a model using gradient descent.

        Args:
            inputData (ndarray): All the training data.
            labels (ndarray): All the true labels for the training data.
            epochs (int): Number of training iterations over the dataset.
            weights (list of ndarray): Current weights of the model.
            biases (list of ndarray): Current biases of the model.
            momentumCoefficient (float): Coefficient for momentum.
            momentumDecay (float): Decay factor for the momentum coefficient.
            useMomentum (bool): Whether to use momentum.
            velocityWeight (list of ndarray): Velocity terms for weights, if using momentum.
            velocityBias (list of ndarray): Velocity terms for biases, if using momentum.
            learningRate (float): The learning rate for optimisation.
            
        Returns: 
            l (list): Output of the network for each epoch.
            weights (list of ndarray): Updated weights after training.
            biases (list of ndarray): Updated biases after training.
            velocityWeight (list of ndarray): Updated velocity for weights.
            velocityBias (list of ndarray): Updated velocity for biases.
        """
        l = []
        if(useMomentum == True):
            self.initialiseVelocity()
        for _ in range(epochs):
            weightGradients, biasGradients = self._initialiseGradients(weights, biases)
            for data in range(len(inputData)):
                layerNodes = self.forwardPropagation(inputData[data])
                l.append(layerNodes[len(layerNodes) - 1])
                w, b = self._backPropgation(layerNodes, weights, biases, labels[data])
                velocityWeight, velocityBias = self._addGradients(weightGradients, biasGradients, w, b)
            weights, biases, velocityWeight, velocityBias = self._updateWeightsBiases(len(inputData), weights, biases, weightGradients, biasGradients, velocityWeight, velocityBias, useMomentum, momentumCoefficient, learningRate)
            momentumCoefficient *= momentumDecay
        return l, weights, biases, velocityWeight, velocityBias

    def _trainStochasticGradientDescent(self, inputData, labels, epochs, weights, biases, momentumCoefficient, momentumDecay, useMomentum, velocityWeight, velocityBias, learningRate, _):
        """
        Trains a model using stochastic gradient descent (SGD).

        Args:
            inputData (ndarray): All the training data.
            labels (ndarray): All the true labels for the training data.
            epochs (int): Number of training iterations over the dataset.
            weights (list of ndarray): Current weights of the model.
            biases (list of ndarray): Current biases of the model.
            momentumCoefficient (float): Coefficient for momentum.
            momentumDecay (float): Decay factor for the momentum coefficient.
            useMomentum (bool): Whether to use momentum.
            velocityWeight (list of ndarray): Velocity terms for weights, if using momentum.
            velocityBias (list of ndarray): Velocity terms for biases, if using momentum.
            learningRate (float): The learning rate for optimisation.
            
        Returns: 
            l (list): Output of the network for each epoch.
            weights (list of ndarray): Updated weights after training.
            biases (list of ndarray): Updated biases after training.
            velocityWeight (list of ndarray): Updated velocity for weights.
            velocityBias (list of ndarray): Updated velocity for biases.
        """
        l = []
        if(useMomentum == True):
            self.initialiseVelocity()        
        for _ in range(epochs):
            for data in range(len(inputData)):
                layerNodes = self.forwardPropagation(inputData[data])
                l.append(layerNodes)
                w, b = self._backPropgation(layerNodes, weights, biases, labels[data])
                if(useMomentum == True):
                    velocityWeight = momentumCoefficient * velocityWeight - learningRate * w
                    weights += velocityWeight
                    velocityBias = momentumCoefficient * velocityBias - learningRate * b
                    biases += velocityBias
                else:
                    for i in range(len(weights)):
                        weights[i] -= learningRate * w[i]
                    for i in range(len(biases)):
                        biases[i] -= learningRate * b[i]

            momentumCoefficient *= momentumDecay
        return l, weights, biases, self.velocityWeight, self.velocityBias

    def _trainGradientDescentUsingBatching(self, inputData, labels, epochs, weights, biases, momentumCoefficient, momentumDecay, useMomentum, velocityWeight, velocityBias, learningRate, batchSize):
        """
        Trains a model using gradient descent.

        Args:
            inputData (ndarray): All the training data.
            labels (ndarray): All the true labels for the training data.
            epochs (int): Number of training iterations over the dataset.
            weights (list of ndarray): Current weights of the model.
            biases (list of ndarray): Current biases of the model.
            momentumCoefficient (float): Coefficient for momentum.
            momentumDecay (float): Decay factor for the momentum coefficient.
            useMomentum (bool): Whether to use momentum.
            velocityWeight (list of ndarray): Velocity terms for weights, if using momentum.
            velocityBias (list of ndarray): Velocity terms for biases, if using momentum.
            learningRate (float): The learning rate for optimisation.
            batchSize (int): The size of each mini batch 
            
        Returns: 
            l (list): Output of the network for each epoch.
            weights (list of ndarray): Updated weights after training.
            biases (list of ndarray): Updated biases after training.
            velocityWeight (list of ndarray): Updated velocity for weights.
            velocityBias (list of ndarray): Updated velocity for biases.
        """
        l = []
        if(useMomentum == True):
            velocityWeight, velocityBias = self.initialiseVelocity(velocityWeight, velocityBias, weights, biases)
        for _ in range(epochs):
            for i in range(0, len(inputData), batchSize):
                batchData = inputData[i:i+batchSize]
                batchLabels = labels[i:i+batchSize]
                weightGradients, biasGradients = self._initialiseGradients(weights, biases)
                for j in range(len(batchData)):
                    layerNodes = self.forwardPropagation(batchData[j])
                    l.append(layerNodes)
                    w, b = self._backPropgation(layerNodes, weights, biases, batchLabels[j])
                    weightGradients, biasGradients = self._addGradients(weightGradients, biasGradients, w, b)
                weights, biases, velocityWeight, velocityBias = self._updateWeightsBiases(batchSize, weights, biases, weightGradients, biasGradients, velocityWeight, velocityBias, useMomentum, momentumCoefficient, learningRate)
            momentumCoefficient *= momentumDecay
        return l, weights, biases, velocityWeight, velocityBias

    def _initialiseVelocity(self, velocityWeight, velocityBias, weights, biases):
        """
        Initialise velocity terms for momentum optimisation.

        Args:
            velocityWeight (list of ndarray): Velocity terms for weights.
            velocityBias (list of ndarray): Velocity terms for biases.
            weights (list of ndarray): The weights of the model.
            biases (list of ndarray): The biases of the model.

        Returns:
            velocityWeight (list of ndarray): Initialised velocity for weights.
            velocityBias (list of ndarray): Initialised velocity for biases.
        """
        if(velocityWeight == None):
            velocityWeight = []
            for i in weights:
                velocityWeight.append(np.zeros_like(i))
        if(velocityBias == None):
            velocityBias = []
            for i in biases:
                velocityBias.append(np.zeros_like(i))
        return velocityWeight, velocityBias
    
    def _initialiseGradients(self, weights, biases):
        """
        Initialise gradients for weights and biases.

        Args:
            weights (list of ndarray): The weights of the model.
            biases (list of ndarray): The biases of the model.

        Returns:
            weightGradients (list of ndarray): Initialised gradients for weights.
            biasGradients (list of ndarray): Initialised gradients for biases.
        """
        weightGradients, biasGradients = [], []
        for i in weights:
            weightGradients.append(np.zeros_like(i))
        for i in biases:
            biasGradients.append(np.zeros_like(i))
        return weightGradients, biasGradients

    def _addGradients(self, weightGradients, biasGradients, w, b):
        """
        Accumulates gradients for weights and biases.

        Args:
            weightGradients (list of ndarray): Accumulated weight gradients.
            biasGradients (list of ndarray): Accumulated bias gradients. 
            w (list of ndarray): Gradients of the weights from the current batch.
            b (list of ndarray): Gradients of the biases from the current batch.
        
        Returns:
            weightGradients (list of ndarray): Updated accumulated weight gradients.
            biasGradients (list of ndarray): Updated accumulated bias gradients. 
        """
        for i in range(len(weightGradients)):
            weightGradients[i] += w[i]
            weightGradients[i] = np.clip(weightGradients[i], -1, 1)
        for i in range(len(biasGradients)):
            biasGradients[i] += b[i].T
            biasGradients[i] = np.clip(biasGradients[i], -1, 1)
        return weightGradients, biasGradients
    
    def _updateWeightsBiases(self, size, weights, biases, weightGradients, biasGradients, velocityWeight, velocityBias, useMomentum, momentumCoefficient, learningRate):
        """
        Updates the weights and biases of the model.

        Args:
            size (int): Number of samples in the batch.
            weights (list of ndarray): Current weights of the model.
            biases (list of ndarray): Current biases of the model.
            weightGradients (list of ndarray): Weight gradients.
            biasGradients (list of ndarray): Bias gradients. 
            velocityWeight (list of ndarray): Velocity terms for weights, if using momentum.
            velocityBias (list of ndarray): Velocity terms for biases, if using momentum.
            useMomentum (bool): Whether to use momentum.
            momentumCoefficient (float): Coefficient for momentum.
            learningRate (float): The learning rate for optimisation.
            
        Returns: 
            weights (list of ndarray): Updated weights after training.
            biases (list of ndarray): Updated biases after training.
            velocityWeight (list of ndarray): Updated velocity for weights.
            velocityBias (list of ndarray): Updated velocity for biases.
        """
        if(useMomentum == True):
            for i in range(len(weights)):
                velocityWeight[i] -= momentumCoefficient * velocityWeight[i] - learningRate * (weightGradients[i] / size)
                weights[i] += velocityWeight[i]
            for i in range(len(biases)):
                velocityBias[i] = momentumCoefficient * velocityBias[i] - learningRate * (biasGradients[i] / size)
                biases[i] += velocityBias[i]
        else:
            for i in range(len(weights)):
                weights[i] = weights[i] - learningRate * (weightGradients[i] / size)
            for i in range(len(biases)):
                biases[i] -= learningRate * (biasGradients[i] / size)
        return weights, biases, velocityWeight, velocityBias