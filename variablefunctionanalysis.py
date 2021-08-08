import random, pprint
import matplotlib.pyplot as plt
import numpy as np
import math
#Storage
import mydataclasses as dc


def generationOfVariableFunction(length_of_test = 100, starting_value = 0, mean = 0,  sigma = 3):
    #Generowanie zmiennej funkcji (szum gaussa)
    graph = []
    i = 0
    while i < length_of_test:
        starting_value += random.gauss(mean, sigma)
        graph.append(starting_value)
        i += 1
    return graph

def generateStaticAverageBluringKernel(size_of_blur_kernel = 100):
    blur_kernel = []
    for i in range(size_of_blur_kernel):
        blur_kernel.append(1)
    return dc.BluringKernel(blur_kernel, size_of_blur_kernel)

def generateStaticGaussBluringKernel(size_of_blur_kernel = 100, standard_deviation = 3, mean = 0):
    #Generowanie jądra wygładzającego
    if len(size_of_blur_kernel)<1000:
        amount_of_sigmas = 6
    else:
        amount_of_sigmas = 8
    half_of_sigmas = amount_of_sigmas * standard_deviation / 2
    x = mean - half_of_sigmas
    step = amount_of_sigmas*standard_deviation/len(size_of_blur_kernel)
    blur_kernel = []
    const1 = 1/(standard_deviation*math.sqrt(2*math.pi))
    const2 = 2*standard_deviation**2
    integral_of_probability = 0
    i = 0
    while i < len(size_of_blur_kernel):
        temp = (const1*math.e**((-x**2)/const2))
        blur_kernel.append(temp)
        integral_of_probability += temp
        x += step
        i += 1
    return dc.BluringKernel(blur_kernel, integral_of_probability)

def generateDynamicGaussBluringKernel(size_of_blur_kernel = 30, standard_deviation = 3, mean = 0):
    #Generowanie jądra wygładzającego
    if size_of_blur_kernel<1000:
        amount_of_sigmas = 3
    else:
        amount_of_sigmas = 4
    sigmas = amount_of_sigmas * standard_deviation
    x = mean - sigmas
    step = sigmas/size_of_blur_kernel
    blur_kernel = []
    const1 = 1/(standard_deviation*math.sqrt(2*math.pi))
    const2 = 2*standard_deviation**2
    integral_of_probability = 0
    i = 0
    while i < size_of_blur_kernel:
        temp = (const1*math.e**((-x**2)/const2))
        blur_kernel.append(temp)
        integral_of_probability += temp
        x += step
        i += 1
    return dc.BluringKernel(blur_kernel, integral_of_probability)

def longAnalysisWithBluringKernel(blrKernel, exchange_rate):        
    #Analiza danych przy wykorzystaniu jądra wygładzającego
    if len(blrKernel <= len(exchange_rate)):        
        size_of_blur_kernel = range(blrKernel.kernel)
        length_of_test = len(exchange_rate)
        x = 0
        analysed_exchange_rate = []
        while x + len(size_of_blur_kernel) < length_of_test:
            temp = 0  
            i = 0
            while i < len(size_of_blur_kernel):
                temp += blrKernel.kernel[i] * exchange_rate[i + x]
                i += 1
            temp /= blrKernel.weight
            analysed_exchange_rate.append(temp)
            x += 1
        return analysed_exchange_rate
    else: 
        raise Exception("List to analyse should be longer or equaly long to bluring kernel.")

def shortAnalysisWithBluringKernel(blrKernel, exchange_rate):        
    #Analiza danych przy wykorzystaniu jądra wygładzającego
    smoothed_exchange_rate = 0
    for i in range(len(blrKernel.kernel)):
        smoothed_exchange_rate += blrKernel.kernel[i] * exchange_rate[i]
    smoothed_exchange_rate /= blrKernel.weight
    return smoothed_exchange_rate