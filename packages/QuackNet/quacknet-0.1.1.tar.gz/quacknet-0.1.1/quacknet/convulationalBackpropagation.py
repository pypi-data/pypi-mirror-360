import numpy as np

class CNNbackpropagation:
    def _ConvolutionDerivative(self, errorPatch, kernals, inputTensor, stride):
        """
        Compute gradients for conolutional layer weights, biases and input errors during backpropagation.

        Args:
            errorPatch (ndarray): Error gradient from the next layer.
            kernals (ndarray): Kernals used during forward propagatation, shape (input channels, num kernels, kernel height, kernel width).
            inputTensor (ndarray): Input to the convolutional layer during forward propagation.
            stride (int): Stride length used during convolution.
        
        Returns:
            weightGradients (ndarray): Gradients of the loss with respect to kernels.
            biasGradients (ndarray): Gradients of the loss with respect to biases for each kernel.
            inputErrorTerms (ndarray): Error terms propagated to the previous layer.
        """
        ###################################        
        # gets the error gradient from the layer infront and it is a error patch
        # this error patch is the same size as what the convolutional layer outputed during forward propgation
        # get the kernal (as in a patch of the image) again, but this time you are multipling each value in the kernal by 1 value that is inside the error patch
        # this makes the gradient of the loss of one kernal's weight
        
        # the gradient of the loss of one kernal's bias is the summ of all the error terms
        # because bias is applied to every input in forward propgation
        
        # the gradient of the loss of the input, which is the error terms for the layer behind it
        # firstly the kernal has to be flipped, meaning flip the kernal left to right and then top to bottom, but not flipping the layers,
        # the gradient of one pixel, is the summ of each error term multiplied by the flipped kernal 
        ###################################     
        
        kernalSize = self.kernalSize # all kernals are the same shape and squares
        weightGradients = np.zeros((len(inputTensor), len(kernals), kernalSize, kernalSize)) #kernals are the same size
        outputHeight, outputWidth = errorPatch.shape[1], errorPatch.shape[2]
        for output in range(len(kernals)):
            for layer in range(len(inputTensor)):
                for i in range(outputHeight):
                    for j in range(outputWidth):
                        startI = i * stride
                        startJ = j * stride
                        if(startI + kernalSize > inputTensor.shape[1] or startJ + kernalSize > inputTensor.shape[2]):
                            continue
                        kernal = inputTensor[layer, startI: startI + kernalSize, startJ : startJ + kernalSize]
                        weightGradients[layer, output] += kernal * errorPatch[output, i, j]
    
        biasGradients = np.sum(errorPatch, axis=(1, 2))

        inputErrorTerms = np.zeros_like(inputTensor)
        flipped = kernals[:, :, ::-1, ::-1]
        for output in range(len(errorPatch)):
            for layer in range(len(inputTensor)):
                for i in range(outputHeight):
                    inputI = i * stride
                    for j in range(outputWidth):
                        inputJ = j * stride
                        if(inputI + kernalSize > inputTensor.shape[1] or inputJ + kernalSize > inputTensor.shape[2]):
                            continue
                        errorKernal = errorPatch[output, i, j]
                        inputErrorTerms[layer, inputI: inputI + kernalSize, inputJ: inputJ + kernalSize] += errorKernal * flipped[output, layer]
        
        weightGradients = np.transpose(weightGradients, (1, 0, 2, 3))
        return weightGradients, biasGradients, inputErrorTerms
            
            
    def _MaxPoolingDerivative(self, errorPatch, inputTensor, sizeOfGrid, strideLength):
        """
        Compute the gradient of the loss with respect to the input of the max pooling layer during backpropagation.

        Args:
            errorPatch (ndarray): Error gradient from the next layer.
            inputTensor (ndarray): Input to the max pooling layer during forward propagation.
            sizeOfGrid (int): Size of the pooling window.
            strideLength (int): Stride length used during pooling.
        
        Returns:
            inputGradient (ndarray): Gradient of the loss with respect to the inputTensor
        """
        inputGradient = np.zeros_like(inputTensor, dtype=np.float64)
        outputHeight = (inputTensor.shape[1] - sizeOfGrid) // strideLength + 1
        outputWidth = (inputTensor.shape[2] - sizeOfGrid) // strideLength + 1
        for image in range(len(inputTensor)): # tensor is a 3d structures, so it is turning it into a 2d array (eg. an layer or image)
            for x in range(outputHeight):
                for y in range(outputWidth):
                    indexX = x * strideLength
                    indexY = y * strideLength

                    gridOfValues = inputTensor[image, indexX: indexX + sizeOfGrid, indexY: indexY + sizeOfGrid]
                    indexMax = np.argmax(gridOfValues)
                    maxX, maxY = divmod(indexMax, sizeOfGrid)

                    #newValues = np.zeros((sizeOfGrid, sizeOfGrid))
                    #newValues[maxX, maxY] = 1
                    #inputGradient[image, indexX: indexX + sizeOfGrid, indexY: indexY + sizeOfGrid] += newValues * errorPatch[image, x, y]

                    inputGradient[image, indexX + maxX, indexY + maxY] += errorPatch[image, x, y]
        return inputGradient

    def _AveragePoolingDerivative(self, errorPatch, inputTensor, sizeOfGrid, strideLength):
        """
        Compute the gradient of the loss with respect to the input of the average pooling layer during backpropagation.

        Args:
            errorPatch (ndarray): Error gradient from the next layer.
            inputTensor (ndarray): Input to the average pooling layer during forward propagation.
            sizeOfGrid (int): Size of the pooling window.
            strideLength (int): Stride length used during pooling.
        
        Returns:
            inputGradient (ndarray): Gradient of the loss with respect to the inputTensor
        """       
        inputGradient = np.zeros_like(inputTensor, dtype=np.float32)
        outputHeight = (inputTensor.shape[1] - sizeOfGrid) // strideLength + 1
        outputWidth = (inputTensor.shape[2] - sizeOfGrid) // strideLength + 1
        avgMultiplier = 1 / (sizeOfGrid ** 2)
        for image in range(len(inputTensor)): # tensor is a 3d structures, so it is turning it into a 2d array (eg. an layer or image)
            for x in range(outputHeight):
                for y in range(outputWidth):
                    indexX = x * strideLength
                    indexY = y * strideLength
                    #newValues = np.ones((sizeOfGrid, sizeOfGrid)) * errorPatch[image, x, y] / (sizeOfGrid ** 2)
                    newValues = errorPatch[image, x, y] * avgMultiplier
                    inputGradient[image, indexX: indexX + sizeOfGrid, indexY: indexY + sizeOfGrid] += newValues 
        return inputGradient
    
    def _GlobalAveragePoolingDerivative(self, inputTensor):
        """
        Compute the gradient of the loss with respect to the input of the global average pooling layer during backpropagation.

        Args:
            inputTensor (ndarray): Input to the global average pooling layer during forward propagation.
        
        Returns:
            inputGradient (ndarray): Gradient of the loss with respect to the inputTensor
        """     
        return np.ones_like(inputTensor) * (1 / (inputTensor.shape[1] * inputTensor.shape[2]))
    
    def _ActivationLayerDerivative(self, errorPatch, activationDerivative, inputTensor):
        """
        Compute the gradient of the loss with respect to the input of the activation layer during backpropagation.

        Args:
            errorPatch (ndarray): Error gradient from the next layer.
            activationDerivative (function): Derivative function of the activation function.
            inputTensor (ndarray): Input to the activation layer during forward propagation.
        
        Returns:
            inputGradient (ndarray): Gradient of the loss with respect to the inputTensor
        """  
        return errorPatch * activationDerivative(inputTensor)