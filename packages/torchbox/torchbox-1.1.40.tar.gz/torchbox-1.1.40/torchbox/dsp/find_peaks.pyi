def localmax1d(data, win=3, thresh=None, omode='sub'):
    r"""find local maximum points

    `Pytorch Argrelmax (or C++) function <https://discuss.pytorch.org/t/pytorch-argrelmax-or-c-function/36404/2>`_

    Parameters
    ----------
    data : list, ndarray or Tensor
        the input data (L or Sbatch x L)
    win : int, optional
        the local window size, by default 3
    thresh : list, ndarray, Tensor or None, optional
        the threshhold, by default :obj:`None`
    omode : str, optional
        not used argument since index and subscript are the same.

    Examples
    --------

    ::

        x = th.zeros(100, )
        x[10] = 1.
        x[30] = 1.2
        x[31] = 0.9
        x[80] = 1.
        x[90] = 0.3

        print(localmax1d(x, win=3, thresh=None))
        print(localmax1d(x, win=2, thresh=None))
        print(localmax1d(x, win=5))
        print(localmax1d(x, win=5, thresh=0.8))

        x = th.stack((x, x), dim=0)
        print(localmax1d(x, win=3, thresh=None))
        print(localmax1d(x, win=2, thresh=None))
        print(localmax1d(x, win=5))
        print(localmax1d(x, win=5, thresh=0.8))

        # outputs
        tensor([10, 30, 80, 90])
        tensor([10, 30, 80, 90])
        tensor([10, 30, 80, 90])
        tensor([10, 30, 80])
        [tensor([10, 30, 80, 90]), tensor([10, 30, 80, 90])]
        [tensor([10, 30, 80, 90]), tensor([10, 30, 80, 90])]
        [tensor([10, 30, 80, 90]), tensor([10, 30, 80, 90])]
        [tensor([10, 30, 80]), tensor([10, 30, 80])]

    """

def localmax2d(data, win=3, thresh=None, omode='sub'):
    r"""find local maximum points

    `Pytorch Argrelmax (or C++) function <https://discuss.pytorch.org/t/pytorch-argrelmax-or-c-function/36404/2>`_

    Parameters
    ----------
    data : list, ndarray or Tensor
        the input data (H x W or Sbatch x H x W)
    win : int, optional
        the local window size, by default 3
    thresh : list, ndarray, Tensor or None, optional
        the threshhold, by default :obj:`None`
    omode : str, optional
        output mode, ``'ind'`` for indexes, ``'sub'`` for subscription (default)

    Examples
    --------

    ::

        x = th.zeros((100, 100))
        x[50, 30] = 1.
        x[20, 80] = 0.1
        print(localmax2d(x, win=3, thresh=0.8))

        # outputs
        tensor([[50, 30]])

    """

def localmax3d(data, win=3, thresh=None, omode='sub'):
    r"""find local maximum points

    `Pytorch Argrelmax (or C++) function <https://discuss.pytorch.org/t/pytorch-argrelmax-or-c-function/36404/2>`_

    Parameters
    ----------
    data : list, ndarray or Tensor
        the input data
    win : int, optional
        the local window size, by default 3
    thresh : list, ndarray, Tensor or None, optional
        the threshhold, by default :obj:`None`
    omode : str, optional
        output mode, ``'ind'`` for indexes, ``'sub'`` for subscription (default)

    Examples
    --------

    ::

        x = th.zeros(60, 70, 80)
        x[1, 20, 3] = 1.
        x[2, 2, 20] = 0.3
        print(localmax3d(x, win=3, thresh=None))

        # outputs
        tensor([[ 1, 20,  3],
                [ 2,  2, 20]])

    """

def filtpeaks(ppos, data, dim=-1, hmin=None, dmin=None, issort=True, returns=['pos', 'value']):
    r"""filter peaks by height and distance

    Parameters
    ----------
    ppos : Tensor
        peaks positions (N x D)
    data : Tensor
        the data tensor (N x S1 x S2 x ... x SD)
    dim : int or list, optional
        the number of dimensions should be equal to D, by default -1
    hmin : float or None, optional
        the minimum height of peak, by default :obj:`None`
    dmin : int, float or None, optional
        the minimum distance between two nearby peaks, by default :obj:`None`
    issort : bool, optional
        sort peaks according to peak's values before remove the peaks 
        that does not satisfy the minimum distance constraint, by default :obj:`True`
    returns : list, optional
        the variables to be returned, by default ['pos', 'value']

    Examples
    --------

    ::

        x = th.zeros(100, )
        x[10] = 1.
        x[30] = 1.2
        x[32] = 0.9
        x[34] = 1.1
        x[90] = 0.3

        ppos = localmax1d(x, win=3, thresh=None)
        print(ppos)
        print(filtpeaks(ppos, x, dim=0, hmin=0.5, dmin=1))
        print(filtpeaks(ppos, x, dim=0, hmin=0.3, dmin=3))

        x = th.zeros(60, 70, 80)
        x[1, 20, 3] = 1.
        x[2, 3, 20] = 0.5
        x[2, 5, 20] = 1.3
        x[2, 8, 20] = 0.3
        ppos = localmax3d(x, win=3, thresh=None)
        print(ppos)
        print(filtpeaks(ppos, x, dim=[0, 1, 2], hmin=0.5, dmin=1))
        print(filtpeaks(ppos, x, dim=[0, 1, 2], hmin=0.3, dmin=3))

        # outputs:
        tensor([10, 30, 32, 34, 90])
        [tensor([30, 34, 10, 32]), tensor([1.2000, 1.1000, 1.0000, 0.9000])]
        [tensor([30, 34, 10, 90]), tensor([1.2000, 1.1000, 1.0000, 0.3000])]
        tensor([[ 1, 20,  3],
                [ 2,  3, 20],
                [ 2,  5, 20],
                [ 2,  8, 20]])
        [tensor([[ 2,  5, 20],
                [ 1, 20,  3],
                [ 2,  3, 20]]), tensor([1.3000, 1.0000, 0.5000])]
        [tensor([[ 2,  5, 20],
                [ 1, 20,  3],
                [ 2,  8, 20]]), tensor([1.3000, 1.0000, 0.3000])]
        
    """    

def findpeaks(data, dim=-1, hmin=None, dmin=None, issort=True, returns=['pos', 'value']):
    r"""find peaks in data

    Parameters
    ----------
    data : Tensor
        the data tensor (N x S1 x S2 x ... x SD)
    dim : int or list, optional
        the number of dimensions should be equal to D, by default -1
    hmin : float or None, optional
        the minimum height of peak, by default :obj:`None`
    dmin : int, float or None, optional
        the minimum distance between two nearby peaks, by default :obj:`None`
    issort : bool, optional
        sort peaks according to peak's values before remove the peaks 
        that does not satisfy the minimum distance constraint, by default :obj:`True`
    returns : list, optional
        the variables to be returned, by default ['pos', 'value']

    Examples
    --------

    ::

        x = th.zeros(100, )
        x[10] = 1.
        x[30] = 1.2
        x[32] = 0.9
        x[34] = 1.1
        x[90] = 0.3

        print(findpeaks(x, dim=0, hmin=0.5, dmin=1))
        print(findpeaks(x, dim=0, hmin=0.3, dmin=3))

        x = th.zeros(60, 70, 80)
        x[1, 20, 3] = 1.
        x[2, 3, 20] = 0.5
        x[2, 5, 20] = 1.3
        x[2, 8, 20] = 0.3
        print(findpeaks(x, dim=[0, 1, 2], hmin=0.5, dmin=1))
        print(findpeaks(x, dim=[0, 1, 2], hmin=0.3, dmin=3))

        # outputs:
        [tensor([30, 34, 10, 32]), tensor([1.2000, 1.1000, 1.0000, 0.9000])]
        [tensor([30, 34, 10, 90]), tensor([1.2000, 1.1000, 1.0000, 0.3000])]
        [tensor([[ 2,  5, 20],
                [ 1, 20,  3],
                [ 2,  3, 20]]), tensor([1.3000, 1.0000, 0.5000])]
        [tensor([[ 2,  5, 20],
                [ 1, 20,  3],
                [ 2,  8, 20]]), tensor([1.3000, 1.0000, 0.3000])]

    """


