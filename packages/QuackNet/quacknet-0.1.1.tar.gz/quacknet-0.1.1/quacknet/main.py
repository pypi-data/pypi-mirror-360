from . import backPropgation
from quacknet.activationFunctions import relu, sigmoid, tanH, linear, softMax
from quacknet.lossFunctions import MSELossFunction, MAELossFunction, CrossEntropyLossFunction
from quacknet.optimisers import Optimisers
from quacknet.initialisers import Initialisers
from quacknet.writeAndReadWeightBias import writeAndRead
from quacknet.convulationalManager import CNNModel
from quacknet.dataAugmentation import Augementation
import numpy as np
import matplotlib.pyplot as plt

class Network(Optimisers, Initialisers, writeAndRead, CNNModel, Augementation):
    def __init__(self, lossFunc = "MSE", learningRate = 0.01, optimisationFunc = "gd", useMomentum = False, momentumCoefficient = 0.9, momentumDecay = 0.99, useBatches = False, batchSize = 32):
        """
        Args:
            lossFunc (str): Loss function name ('mse', 'mae', 'cross'). Default is "MSE".
            learningRate (float, optional): Learning rate for training. Default is 0.01.
            optimisationFunc (str, optional): Optimisaztion method ('gd', 'sgd', 'batching'). Default is "gd".
            useMomentum (bool, optional): Wether to use momentum in optimisation. Default is False.
            momentumCoefficient (float, optional): Momentum coefficient if used. Default is 0.9.
            momentumDecay (float, optional): Decay rate for momentum. Default is 0.99.
            useBatches (bool, optional): Wether to use mini batches. Default is False.
            batchSize (int, optional): size of mini batches. Default is 32.
        """
        self.layers = []
        self.weights = []
        self.biases = []
        self.learningRate = learningRate

        lossFunctionDict = {
            "mse": MSELossFunction,
            "mae": MAELossFunction,
            "cross entropy": CrossEntropyLossFunction,"cross": CrossEntropyLossFunction,
        }
        self.lossFunction = lossFunctionDict[lossFunc.lower()]

        optimisationFunctionDict = {
            "gd": self._trainGradientDescent,
            "sgd": self._trainStochasticGradientDescent,
            "batching": self._trainGradientDescentUsingBatching, "batches": self._trainGradientDescentUsingBatching, 
        }
        self.optimisationFunction = optimisationFunctionDict[optimisationFunc.lower()]
        if(useBatches == True):
            self.optimisationFunction = self._trainGradientDescentUsingBatching

        self.useMomentum = useMomentum
        self.momentumCoefficient = momentumCoefficient
        self.momentumDecay = momentumDecay
        self.velocityWeight = None
        self.velocityBias = None

        self.useBatches = useBatches
        self.batchSize = batchSize

    def addLayer(self, size, activationFunction="relu"):
        """
        Add a layer to the network with the specified number of nodes and activation function.

        Args:
            size (int): Number of nodes in the new layer.
            activationFunction (str, optional): Activation function name ('relu', 'sigmoid', 'linear', 'tanh', 'softmax'). Default is "relu".
        """
        funcs = {
            "relu": relu,
            "sigmoid": sigmoid,
            "linear": linear,
            "tanh": tanH,
            "softmax": softMax,
        }
        if(activationFunction.lower() not in funcs):
            raise ValueError(f"Activation function not made: {activationFunction.lower()}")
        self.layers.append([size, funcs[activationFunction.lower()]])

    def _calculateLayerNodes(self, lastLayerNodes, lastLayerWeights, biases, currentLayer) -> np.ndarray:
        """
        Calculate the output of a layer given inputs, weights and biases.

        Args:
            lastLayerNodes (ndarray): Output from the previous layer.
            lastLayerWeights (ndarray): Weights connecting the previous layer.
            biases (ndarray): Biases of the current layer.
            currentLayer (list): List containing layer size and activation function.
        
        Returns:
            ndarray: Output of the current layer.
        """
        
        summ = np.dot(lastLayerNodes, lastLayerWeights) + biases
        if(currentLayer[1] != softMax):
            return currentLayer[1](summ)
        else:
            return softMax(summ)
        
    def forwardPropagation(self, inputData):
        """
        Perform forward propagation through the network for the given input data.

        Args:
            inputData (list): Input data for the network.

        Returns:
            list of ndarray: List containing outputs of each layer including input layer.
        """
        layerNodes = [np.array(inputData)]
        for i in range(1, len(self.layers)):
            layerNodes.append(np.array(self._calculateLayerNodes(layerNodes[i - 1], self.weights[i - 1], self.biases[i - 1], self.layers[i])))
        return layerNodes
    
    def _backPropgation(self, layerNodes, weights, biases, trueValues, returnErrorTermForCNN = False):
        """
        Perform backpropagation over the network layers to compute gradients for weights and biases.

        Args:
            layerNodes (list of ndarray): List of output values for each layer.
            weights (list of ndarray): List of weights for each layer.
            biases (list of ndarray): List of biases for each layer.
            trueValues (ndarray): True target values for the output layer.
            returnErrorTermForCNN (bool, optional): Whether to return error terms for CNN backpropagation. Defaults to False.

        Returns:
            weightGradients (list of ndarray): Gradients of weights for each layer.
            biasGradients (list of ndarray): Gradients of biases for each layer.
            If returnErrorTermForCNN is True:
                hiddenWeightErrorTermsForCNNBackpropgation (ndarray): Error terms from the output layer weights.   
        """  
        return backPropgation._backPropgation(layerNodes, weights, biases, trueValues, self.layers, self.lossFunction, returnErrorTermForCNN)
    
    def train(self, inputData, labels, epochs):
        """
        Train the neural network using the specified optimisation function.

        Args:
            inputData (list of lists): All of the training input data
            labels (list of ndarray): All of the labels for all the input data.
            epochs (int): Number of training epochs.
        
        Returns:
            float: Average accauracy over all epochs.
            float: Average loss over all epochs.
        """
        self._checkIfNetworkCorrect()
        correct = 0
        totalLoss = 0
        nodes, self.weights, self.biases, self.velocityWeight, self.velocityBias = self.optimisationFunction(inputData, labels, epochs, self.weights, self.biases, self.momentumCoefficient, self.momentumDecay, self.useMomentum, self.velocityWeight, self.velocityBias, self.learningRate, self.batchSize)        
        lastLayer = len(nodes[0]) - 1
        labels = np.tile(labels, (epochs, 1)) # duplicates the labels ([1, 2], (3, 1)) would become [[1, 2], [1, 2], [1, 2]]
        for i in range(len(nodes)): 
            totalLoss += self.lossFunction(nodes[i][lastLayer], labels[i])
            nodeIndex = np.argmax(nodes[i][lastLayer])
            labelIndex = np.argmax(labels[i])
            if(nodeIndex == labelIndex):
                correct += 1
        return correct / (len(labels) * epochs), totalLoss / (len(labels) * epochs)
    
    def _checkIfNetworkCorrect(self): #this is to check if activation functions/loss functions adhere to certain rule
        for i in range(len(self.layers) - 1): #checks if softmax is used for any activation func that isnt output layer
            if(self.layers[i][1] == softMax): #if so it stops the user
                raise ValueError(f"Softmax shouldnt be used in non ouput layers. Error at Layer {i + 1}")
        usingSoftMax = self.layers[len(self.layers) - 1][1] == softMax
        if(usingSoftMax == True):
            if(self.lossFunction != CrossEntropyLossFunction): #checks if softmax is used without cross entropy loss function
                raise ValueError(f"Softmax output layer requires Cross Entropy loss function") #if so stops the user
        elif(self.lossFunction == CrossEntropyLossFunction):
            raise ValueError(f"Cross Entropy loss function requires Softmax output layer") #if so stops the user
    
    def drawGraphs(self, allAccuracy, allLoss):
        """
        Plot training accuracy and loss graphs over epochs for multiple runs.

        Args:
            allAccuracy (list of lists): Accuracy at each epoch for each run.
            allLoss (list of lists): Loss at each epoch for each run.

        Displays:
            Matplotlib plots of accuracy and loss trends.
        """
        epochs = list(range(1, len(allAccuracy[0]) + 1))
        figure, axis = plt.subplots(1, 2)
        meanAccuracy = np.mean(allAccuracy, axis=0)
        meanLoss = np.mean(allLoss, axis=0)

        for i in range(len(allAccuracy)):
            axis[0].plot(epochs, allAccuracy[i], marker="o", label=f'Run {i+1}', alpha=0.3)
        axis[0].plot(epochs, meanAccuracy, marker="o", label=f'Average', alpha=1)
        axis[0].set_xticks(epochs)
        axis[0].set_xlabel("epochs")
        axis[0].set_ylabel("accauracy")
        axis[0].set_title("model accuracy")
        axis[0].grid(True)
        axis[0].legend()

        for i in range(len(allLoss)):
            axis[1].plot(epochs, allLoss[i], marker="o", label=f'Run {i+1}', alpha=0.3)
        axis[1].plot(epochs, meanLoss, marker="o", label=f'Average', alpha=1)
        axis[1].set_xticks(epochs)
        axis[1].set_xlabel("epochs")
        axis[1].set_ylabel("loss")
        axis[1].set_title("model loss")
        axis[1].grid(True)
        axis[1].legend()


        plt.tight_layout()
        plt.show()


# use this to get how many functions are tests or not: coverage run -m pytest unitTests/
# then to see results do: coverage report -m

#to generate documentation using pdoc do: pdoc quacknet --output-dir docs