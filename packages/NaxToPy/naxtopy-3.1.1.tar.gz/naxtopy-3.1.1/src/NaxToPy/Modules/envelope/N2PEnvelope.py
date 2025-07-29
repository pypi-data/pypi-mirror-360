"""
Module that generates the envelope of points cloud.
"""
import sys, os
import numpy as np
from NaxToModel import N2Envelope
import System
from NaxToPy.Core._AuxFunc._NetToPython import _nettonumpy, _numpytonet
from NaxToPy.Core.Errors.N2PLog import N2PLog
from typing import Union

# Una envolvente es el conjunto de objetos de una dimensión menor que la de los puntos facilitados, y que es tangente
# a estos y que los encierra. Es decir, representa la frontera de estos puntos.

def envelope_list(*args: list) -> list[list]:
    """ Function that generates the envelope of a cloud of points. Args could be DF or lists.

        -args*: Lists as columns of the cloud of points: e = n2p.envelope([3,4,2,...], [6,2,7,...], ...)

        -arg: A single DataFrame: e = n2p.envelope(df)

        Return:
            list[list]

        Note:
            The column 0 is the solver element id when using DataFrame, but it is the position in the elements
            list when using lists!!! to know the solver id: get_elements()[index_0]

    """
    N2PLog.Info.I203()

    if isinstance(args[0], list):

        if isinstance(args[0][0], list):
            args = args[0]

        array_arrays = System.Array[System.Array[System.Double]](len(args[0]))

        length = len(args[0])

        if length > len(args):
            N2PLog.Warning.W300()

        for i in range(length):
            double_array = System.Array[System.Double]([aux[i] for aux in args])
            array_arrays[i] = double_array

        array_2D = N2Envelope.JoinDoubles(array_arrays)

        envel = N2Envelope.Calculate(array_2D, "all")

        if envel.Length == 1:
            if envel[0] == -801:
                N2PLog.Error.E308()
                return -801
            elif envel[0] == -802:
                N2PLog.Error.E309()
                return -802

        envelope_list = list()
        for i in range(envel.GetLength(0)):  # Rows
            aux_list = list()
            for j in range(envel.GetLength(1)):  # Columns
                if j == 0:
                    aux_val = envel[i, j] - 1  # qhull saca los indices empezando por 1
                else:
                    aux_val = envel[i, j]

                aux_list.append(aux_val)
            envelope_list.append(aux_list)

        return envelope_list

    else:
        N2PLog.Error.E306()
        return -1


def envelope_ndarray(array2D: np.ndarray) -> np.ndarray:
    """ Function that generates the envelope of a cloud of points. Args must be a numpy.array. This function is faster
    than envelope_list.

    Args:
        array2D (ndarray)
            2D Array [n*m]. Each row is point of the cloud, so there are n points. Each column is a
            coordinate of the point, so it is an m dimensional space.

    Return:
        ndarray

    Note:
        The column 0 is the position in the elements list!!! to know the solver id: get_elements()[index_0]
    """
    N2PLog.Info.I203()

    # Compruebo que efectivamente el usuario ha introducido un array de Numpy
    if isinstance(array2D, np.ndarray):

        # _numpytonet(array2D) es una funcion que transforma un array de numpy en un array de .NET, en este caso en un
        # System.Double[,]
        # Se llama a la funcion de envelope de NaxToModel
        aux = N2Envelope.Calculate(_numpytonet(array2D), "all")

        # Se crea un array de numpy vacio de objetos. Tiene que ser de objetos porque se mezclan variables, ya que en la
        # columna 0 habra enteros mientras que en las demas habra columnas
        envel = np.zeros((aux.GetLength(0), aux.GetLength(1)), dtype=object)

        # Relleno el array de numpy con los valores obtenidos del array de NaxToModel
        for i in range(aux.GetLength(0)):
            for j in range(aux.GetLength(1)):
                # qhull devulve los indices empezando por 1. Necesitamos que lo devuelva por 0.
                if j == 0:
                    envel[i, j] = aux[i, j] - 1
                else:
                    envel[i, j] = aux[i, j]

        return envel

    else:
        N2PLog.Error.E306()
        return -1