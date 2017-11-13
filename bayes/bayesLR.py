import os
import numpy as np


class BayesMISO:
    def __init__(self, nIn, noise):
        '''
        1. nIn:     number of input
        2. noise:   sigma_d, read theory.md for more information
        '''
        self.__n = nIn + 1
        self.__sigma = np.mat(np.identity(self.__n, dtype=np.float64))
        self.__mu = np.mat(np.zeros(self.__n, dtype=np.float64))
        self.__NOISE_I = np.mat(np.eye(self.__n, dtype=np.float64) * noise).I
        self.index = 0

    def new_data(self, x, y):
        self.index += 1
        X = np.mat(x)
        Y = np.mat(y)
        if self.index is 1:
            self.__sigma = (X * self.__NOISE_I * X.T).I
            self.__mu = Y * self.__NOISE_I * X.T * self.__sigma
        else:
            sigma_p = self.__sigma
            mu_p = self.__mu
            self.__sigma = (X * self.__NOISE_I * X.T + sigma_p).I
            self.__mu = (Y * self.__NOISE_I * X.T + mu_p * sigma_p) * self.__sigma
        return self.__mu


class BayesMIMO:
    def __init__(self, nIn, nOut, noise):
        self.W = np.mat(np.eye(nIn + 1, dtype=np.float64))
        self.__Warray = []
        for i in range(0, nOut):
            self.__Warray[i] = BayesMISO(nIn, noise)

    def new_data(self, x, y):
        for i in range(0, len(self.__Warray)):
            self.W[i, :] = self.__Warray[i].new_data(x, y[i])
        return self.W
