# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 10:38:37 2023

author: Ahmed H. Hanfy
"""
import sys
import numpy as np
from .constants import BCOLOR
from .support_func import log_message


def XCheck(x: float, Shp: tuple[int], slope: float, a: float) -> tuple[float]:
    """
    Check and calculate the image boundary y-coordinate based on the given x-coordinate and slope.

    This function takes an x-coordinate, image shape parameters (Shp), slope, and intercept (a) as inputs,
    and calculates the corresponding y-coordinate (p2) based on the specified conditions.

    Parameters:
        - **x (float)**: The x-coordinate to be checked.
        - **Shp (tuple)**: A tuple containing shape parameters (Shp[0] for y-axis limit, Shp[1] for x-axis limit).
        - **slope (float)**: The slope of the line.
        - **a (float)**: The y-intercept of the line.

    Returns:
        tuple: A tuple (p2) representing the calculated point (x, y).

    Example:
        >>> instance = YourClass()
        >>> result = instance.XCheck(2.5, (10, 5), 2, 3)
        >>> print(result)
        (2.5, 8)

    .. note::
        - If x is within the range [0, Shp[1]], the y-coordinate is calculated based on the line equation.
        - If x is greater than Shp[1], the y-coordinate is calculated at the point (Shp[1], y2), where y2 is determined by the line equation.
        - If x is less than 0, the y-coordinate is calculated at the point (0, y2), where y2 is determined by the line equation.

    """
    if   x >= 0 and x <= Shp[1]:                           p2 = (x, Shp[0])
    elif x >= 0 and x >  Shp[1]: y2 = int(Shp[1]*slope+a); p2 = (Shp[1],y2)
    elif x <  0 and x <= Shp[1]: y2 = int(a);              p2 = (0,y2)
    return p2

def InclinedLine(P1: tuple[int], P2: tuple[int]=(), slope: float=None, 
                 imgShape: tuple[int]=(), log_dirc='') -> tuple[tuple[int], tuple[int],float,float]:
    """
    Generates the inclined line equation from two points or one point and slope.

    The image boundary/shape should be given.

    Parameters:
        - **P1 (tuple)**: First point tuple (a1, b1).
        - **P2 (tuple, optional)**: Second point tuple (a2, b2). Defaults to ().
        - **slope (float, optional)**: Slope of the line. Defaults to None.
        - **imgShape (tuple)**: Image size (y-length, x-length).

    Returns:
        tuple: A tuple containing:
            - first boundary point tuple.
            - second boundary point tuple.
            - line slope.
            - y-intercept.

    Example:
        >>> instance = YourClass()
        >>> result = instance.InclinedLine((0, 0), (2, 4), imgShape=(5, 5))
        >>> print(result)
        ((0, 0), (5, 5), 1.0, 0)

    .. note::
        - If `imgShape` is not provided, the function prints an error message and aborts the program.
        - If only one point (`P1`) and slope (`slope`) are provided, the function calculates the second point.
        - If the line is not vertical or horizontal, it calculates the boundary points based on the image shape.
        - If the line is vertical, the slope is `np.inf`, and the function returns vertical boundary points.
        - If the line is horizontal, the slope is 0, and the function returns horizontal boundary points.

    """
    if len(imgShape) < 1:
        error='Image shape is not provided, program aborting ...'
        log_message(error, log_dirc)
        print(f'{BCOLOR.FAIL}Error:{BCOLOR.ENDC}', end= ' ')
        print(f'{BCOLOR.ITALIC}{error}{BCOLOR.ENDC}')
        sys.exit()

    if len(P2) > 0 and slope is None:
        dx = P1[0]-P2[0];   dy = P1[1]-P2[1]
        if dx != 0: slope = dy/dx
    elif len(P2) == 0 and slope is np.inf: dx = 0;
    else: dx = -1

    if (slope != 0) and (slope is not None) and (slope != np.inf):
        a = P1[1] - slope*P1[0]
        try:
            Xmax = int((imgShape[0]-a)/slope)
        except Exception as e:
            error = f'InclinedLine error: y-intercept = {a}, slope = {slope}, type = {type(slope)}'
            log_message(error, log_dirc)
            log_message(e, log_dirc)
            print(a,slope, type(slope))
            
        Xmin = int(-a/slope)
        if   Xmin >= 0 and Xmin <= imgShape[1]:
            p1 = (Xmin,0)
            p2 = XCheck(Xmax,imgShape,slope,a)
        elif Xmin >= 0 and Xmin >  imgShape[1]:
            y = int(imgShape[1]*slope+a)
            p1 = (imgShape[1],y)
            p2 = XCheck(Xmax,imgShape,slope,a)
        else:
            y1 = int(a);
            p1 = (0,y1)
            p2 = XCheck(Xmax,imgShape,slope,a)
        return p1, p2, slope, a
    elif dx == 0 or slope == np.inf:
        return (P1[0],0), (P1[0],imgShape[0]), np.inf, 0
    else:
        return (0,P1[1]), (imgShape[1],P1[1]), 0, P1[1]


def AngleFromSlope(slope: float) -> float:
    """
    Calculate the angle in degrees from the given slope.
    This function computes the angle in degrees corresponding to the provided slope value.

    Parameters:
        - **slope (float)**:   The slope of the line.

    Returns:
        float: The angle in degrees corresponding to the given slope.

    Example:
        >>> slope = 2
        >>> angle = AngleFromSlope(slope)
        >>> print(angle)
        26.56505117707799

    """
    if   slope > 0:ang_deg = 180 - np.arctan(slope)*180/np.pi
    elif slope < 0:ang_deg = abs(np.arctan(slope)*180/np.pi)
    else:  ang_deg = 90
    return ang_deg
