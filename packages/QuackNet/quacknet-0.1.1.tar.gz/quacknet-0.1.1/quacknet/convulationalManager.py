from quacknet.convulationalFeutures import ConvulationalNetwork
from quacknet.convulationalBackpropagation import CNNbackpropagation
from quacknet.activationDerivativeFunctions import ReLUDerivative
from quacknet.convulationalOptimiser import CNNoptimiser
import numpy as np

class CNNModel(CNNoptimiser):
    def __init__(self, NeuralNetworkClass):
        self.layers = []
        self.weights = []
        self.biases = []
        self.NeuralNetworkClass = NeuralNetworkClass
    
    def addLayer(self, layer):
        """
        Adds a layer to the CNN model.

        Args:
            layer (class): ConvLayer, PoolingLayer, ActivationLayer, and DenseLayer
        """
        self.layers.append(layer)
    
    def forward(self, inputTensor):
        """
        Performs a forward pass through all layers.

        Args:
            inputTensor (ndarray): Input data tensor to the CNN.
        
        Returns:
            list: List of tensors output by each layer including the input.
        """
        allTensors = [inputTensor]
        for layer in self.layers:
            inputTensor = layer.forward(inputTensor)
            allTensors.append(inputTensor)
        return allTensors

    def _backpropagation(self, allTensors, trueValues):
        """
        Performs backpropagation through all layers to compute gradients.

        Args:
            allTensors (list): List of all layer outputs from forward propagation.
        
        Returns:
            allWeightGradients (list): List of all the weight gradients calculated during backpropgation.
            allBiasGradients (list): List of all the bias gradients calculated during backpropgation.
        """
        weightGradients, biasGradients, errorTerms = self.layers[-1]._backpropagation(trueValues) # <-- this is a neural network 
        allWeightGradients = [weightGradients]
        allBiasGradients = [biasGradients]
        for i in range(len(self.layers) - 2, -1, -1):
            if(type(self.layers[i]) == PoolingLayer or type(self.layers[i]) == ActivationLayer):
                errorTerms = self.layers[i]._backpropagation(errorTerms, allTensors[i])
            elif(type(self.layers[i]) == ConvLayer):
                weightGradients, biasGradients, errorTerms = self.layers[i]._backpropagation(errorTerms, allTensors[i])
                allWeightGradients.insert(0, weightGradients)
                allBiasGradients.insert(0, biasGradients)
        
        return allWeightGradients, allBiasGradients
    
    def _optimser(self, inputData, labels, useBatches, weights, biases, batchSize, alpha, beta1, beta2, epsilon):
        """
        Runs the Adam optimiser either with or without batches.

        Args:
            inputData (ndarray): All the training data.
            labels (ndarray): All the true labels for the training data.
            useBatches (bool): Whether to use batching.
            weights (list): Current weights.
            biases (list): Current biases.
            batchSize (int): Size of batches.
            alpha (float): Learning rate.
            beta1 (float): Adam's beta1 parameter.
            beta2 (float): Adam's beta2 parameter.
            epsilon (float): Adam's epsilon parameter.
        
        Returns:
            list: The nodes (returned to calculate accuracy and loss).
            list: Updated weights after optimisation
            list: Updated biases after optimisation
        """
        if(useBatches == True):
            return CNNoptimiser._AdamsOptimiserWithBatches(self, inputData, labels, weights, biases, batchSize, alpha, beta1, beta2, epsilon)
        else:
            return CNNoptimiser._AdamsOptimiserWithoutBatches(self, inputData, labels, weights, biases, alpha, beta1, beta2, epsilon)
    
    def train(self, inputData, labels, useBatches, batchSize, alpha = 0.001, beta1 = 0.9, beta2 = 0.999, epsilon = 1e-8):
        """
        Trains the CNN for one epoch and calculates accuracy and average loss.

        Args:
            inputData (ndarray): All the training data.
            labels (ndarray): All the true labels for the training data.
            useBatches (bool): Whether to use batching.
            batchSize (int): Size of batches.
            alpha (float, optional): Learning rate. Default is 0.001.
            beta1 (float, optional): Adam's beta1 parameter. Default is 0.9.
            beta2 (float, optional): Adam's beta2 parameter. Default is 0.999.
            epsilon (float, optional): Adam's epsilon parameter. Default is 1e-8.

        Returns:
            float: accuracy percentage.
            float: average loss.
        """
        correct, totalLoss = 0, 0
        
        nodes, self.weights, self.biases = self._optimser(inputData, labels, useBatches, self.weights, self.biases, batchSize, alpha, beta1, beta2, epsilon)        
        
        lastLayer = len(nodes[0]) - 1
        for i in range(len(nodes)): 
            totalLoss += self.NeuralNetworkClass.lossFunction(nodes[i][lastLayer], labels[i])
            nodeIndex = np.argmax(nodes[i][lastLayer])
            labelIndex = np.argmax(labels[i])
            if(nodeIndex == labelIndex):
                correct += 1
        return 100 * (correct / len(labels)), totalLoss / len(labels)
    
    def createWeightsBiases(self):
        """
        Initialises weights and biases for convolutional and dense layers.
        """
        for i in range(len(self.layers)):
            if(type(self.layers[i]) == ConvLayer):
                kernalSize = self.layers[i].kernalSize
                numKernals = self.layers[i].numKernals
                depth = self.layers[i].depth

                bounds =  np.sqrt(2 / kernalSize) # He initialisation

                self.weights.append(np.random.normal(0, bounds, size=(numKernals, depth, kernalSize, kernalSize)))
                self.biases.append(np.zeros((numKernals)))

                self.layers[i].kernalWeights = self.weights[-1]
                self.layers[i].kernalBiases = self.biases[-1]
            elif(type(self.layers[i]) == DenseLayer):
                self.weights.append(self.layers[i].NeuralNetworkClass.weights)
                self.biases.append(self.layers[i].NeuralNetworkClass.biases)

    def saveModel(self, NNweights, NNbiases, CNNweights, CNNbiases, filename = "modelWeights.npz"):
        """
        Saves model weights and biases to a compressed npz file.

        Args:
            NNweights (list): Weights of the dense neural network layers.
            NNbiases (list): Biases of the dense neural network layers.
            CNNweights (list): Weights of the convolutional layers.
            CNNbiases (list): Biases of the convolutional layers.
            filename (str, optional): Filename to save the weights. Default is "modelWeights.npz".
        """
        CNNweights = np.array(CNNweights, dtype=object)
        CNNbiases = np.array(CNNbiases, dtype=object)
        NNweights = np.array(NNweights, dtype=object)
        NNbiases = np.array(NNbiases, dtype=object)
        np.savez_compressed(filename, CNNweights = CNNweights, CNNbiases = CNNbiases, NNweights = NNweights, NNbiases = NNbiases, allow_pickle = True)

    def loadModel(self, neuralNetwork, filename = "modelWeights.npz"):
        """
        Loads model weights and biases from a compressed npz file and assigns them to layers.
        
        Args:
            neuralNetwork (class): The dense neural network to load weights into.
            filename (str, optional): Filename to save the weights. Default is "modelWeights.npz".
        """
        data = np.load(filename, allow_pickle = True)
        CNNweights = data["CNNweights"]
        CNNbiases = data["CNNbiases"]
        NNweights = data["NNweights"]
        NNbiases = data["NNbiases"]

        self.layers[-1].NeuralNetworkClass.weights = NNweights
        self.layers[-1].NeuralNetworkClass.biases = NNbiases
        neuralNetwork.weights = NNweights
        neuralNetwork.biases = NNbiases
        self.weights = CNNweights
        self.biases = CNNbiases

        currWeightIndex = 0
        for i in range(len(self.layers)):
            if(type(self.layers[i]) == ConvLayer):
                self.layers[i].kernalWeights = CNNweights[currWeightIndex]
                self.layers[i].kernalBiases = CNNbiases[currWeightIndex]
                currWeightIndex += 1

class ConvLayer(ConvulationalNetwork, CNNbackpropagation):
    def __init__(self, kernalSize, depth, numKernals, stride, padding = "no"):
        """
        Initialises a convolutional layer.

        Args:
            kernalSize (int): The size of the covolution kernel (assumed it is a square).
            depth (int): Depth of the input tensor.
            numKernals (int): Number of kernels in this layer.
            stride (int): The stride length for convolution.
            padding (str or int, optional): Padding size or "no" for no padding. Default is "no".
        """
        self.kernalSize = kernalSize
        self.numKernals = numKernals
        self.kernalWeights = []
        self.kernalBiases = []
        self.depth = depth
        self.stride = stride
        self.padding = padding
        if(padding.lower() == "no" or padding.lower() == "n"):
            self.usePadding = False
        else:
            self.padding = int(self.padding)
            self.usePadding = True
    
    def forward(self, inputTensor):
        """
        Performs a forward convolution pass.

        Args:
            inputTensor (ndarray): Input tensor to convolve.
        
        Returns:
            ndarray: Output tensor after convolution.
        """
        return ConvulationalNetwork._kernalisation(self, inputTensor, self.kernalWeights, self.kernalBiases, self.kernalSize, self.usePadding, self.padding, self.stride)

    def _backpropagation(self, errorPatch, inputTensor):
        """
        Performs backpropagation to compute gradients for convolutional layer.

        Args:
            errorPatch (ndarray): Error gradient from the next layer.
            inputTensor (ndarray): Input tensor to convolve.
        
        Returns:
            ndarray: Gradients of the loss with respect to kernels.
            ndarray: Gradients of the loss with respect to biases for each kernel.
            ndarray: Error terms propagated to the previous layer.
        """
        return CNNbackpropagation._ConvolutionDerivative(self, errorPatch, self.kernalWeights, inputTensor, self.stride)

class PoolingLayer(CNNbackpropagation):
    def __init__(self, gridSize, stride, mode = "max"):
        """
        Initialises a pooling layer.

        Args:
            gridSize (int): The size of the pooling window.
            stride (int): The stride length for pooling.
            mode (str, optional): Pooling mode of "max", "ave" (average), or "gap" (global average pooling). Default is "max".        
        """
        self.gridSize = gridSize
        self.stride = stride
        self.mode = mode.lower()
    
    def forward(self, inputTensor):
        """
        Performs forward pooling operation.

        Args:
           inputTensor (ndarray): Input tensor to pool.

        Returns:
            ndarray: Output tensor after pooling. 
        """
        if(self.mode == "gap" or self.mode == "global"):
            return ConvulationalNetwork._poolingGlobalAverage(self, inputTensor)
        return ConvulationalNetwork._pooling(self, inputTensor, self.gridSize, self.stride, self.mode)

    def _backpropagation(self, errorPatch, inputTensor):
        """
        Performs backpropagation through the pooling layer.

        Args:
            errorPatch (ndarray): Error gradient from the next layer.
            inputTensor (ndarray): Input tensor during forward propagation.
        
        Returns:
            inputGradient (ndarray): Gradient of the loss.
        """
        if(self.mode == "max"):
            return CNNbackpropagation._MaxPoolingDerivative(self, errorPatch, inputTensor, self.gridSize, self.stride)
        elif(self.mode == "ave"):
            return CNNbackpropagation._AveragePoolingDerivative(self, errorPatch, inputTensor, self.gridSize, self.stride)
        else:
            return CNNbackpropagation._GlobalAveragePoolingDerivative(self, inputTensor)

class DenseLayer: # basically a fancy neural network
    def __init__(self, NeuralNetworkClass):
        """
        Initialises a dense layer using a NeuralNetworkClass.

        Args:
            NeuralNetworkClass (class): the fully connected neural network class.
        """
        self.NeuralNetworkClass = NeuralNetworkClass
        self.orignalShape = 0   # orignalShape is the original shape of the input tensor
        
    def forward(self, inputTensor):
        """
        Flattens the input tensor and performs a forward pass.

        Args:
            inputTensor (ndarray): Input tensor to flatten and process.
        
        Returns:
            ndarray: Output of the dense layer.
        """
        self.orignalShape = np.array(inputTensor).shape
        inputArray = ConvulationalNetwork._flatternTensor(self, inputTensor)
        self.layerNodes = self.NeuralNetworkClass.forwardPropagation(inputArray)
        return self.layerNodes[-1]
    
    def _backpropagation(self, trueValues): #return weigtGradients, biasGradients, errorTerms
        """
        Performs backpropagation through the dense layer.

        Args:
            trueValues (ndarray): True labels for the input data.
        
        Returns:
            weightGradients (list of ndarray): Gradients of weights for each layer.
            biasGradients (list of ndarray): Gradients of biases for each layer.
            errorTerms (ndarray): Error terms from the output layer weights, reshaped to the input tensor.   
        """  
        weightGradients, biasGradients, errorTerms = self.NeuralNetworkClass._backPropgation(
            self.layerNodes, 
            self.NeuralNetworkClass.weights,
            self.NeuralNetworkClass.biases,
            trueValues,
            True
        )
        #errorTerms = np.array(self.NeuralNetworkClass.weights).T @ errorTerms 
        #errorTerms = errorTerms.reshape(self.orignalShape)

        for i in reversed(range(len(self.NeuralNetworkClass.weights))):
            errorTerms = self.NeuralNetworkClass.weights[i] @ errorTerms
        errorTerms = errorTerms.reshape(self.orignalShape)

        return weightGradients, biasGradients, errorTerms

class ActivationLayer: # basically aplies an activation function over the whole Tensor (eg. leaky relu)
    def forward(self, inputTensor):
        """
        Applies the Leaky ReLU activation function to the input tensor.

        Args:
            inputTensor (ndarray): A 3D array representing the input.
        
        Returns:
            ndarray: A tensor with the same shape as the input with Leaky ReLU applied to it.
        """
        return ConvulationalNetwork._activation(self, inputTensor)

    def _backpropagation(self, errorPatch, inputTensor):
        """
        Compute the gradient of the loss with respect to the input of the activation layer during backpropagation.

        Args:
            errorPatch (ndarray): Error gradient from the next layer.
            inputTensor (ndarray): Input to the activation layer during forward propagation.
        
        Returns:
            inputGradient (ndarray): Gradient of the loss with respect to the inputTensor
        """  
        return CNNbackpropagation._ActivationLayerDerivative(self, errorPatch, ReLUDerivative, inputTensor)
    