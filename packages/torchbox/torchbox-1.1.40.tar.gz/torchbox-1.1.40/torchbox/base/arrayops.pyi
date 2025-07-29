def sl(ndim, axis=None, idx=None, **kwargs):
    r"""Slice any axis

    generates slice in specified axis.

    Parameters
    ----------
    ndim : int
        total dimensions
    axis : int, list or None
        select axis list.
    idx : list or None, optional
        slice lists of the specified :attr:`axis`, if None, does nothing (the default)
    dim : int or list
        (kwargs) if specified, will overwrite :attr:`axis`

    Returns
    -------
    tuple of slice
        slice for specified axis elements.

    Examples
    --------

    ::

        import numpy as np

        np.random.seed(2020)
        X = np.random.randint(0, 100, (9, 10))
        print(X, 'X)
        print(X[sl(2, -1, [0, 1])], 'Xsl')

        # output:

        [[96  8 67 67 91  3 71 56 29 48]
        [32 24 74  9 51 11 55 62 67 69]
        [48 28 20  8 38 84 65  1 79 69]
        [74 73 62 21 29 90  6 38 22 63]
        [21 68  6 98  3 20 55  1 52  9]
        [83 82 65 42 66 55 33 80 82 72]
        [94 91 14 14 75  5 38 83 99 10]
        [80 64 79 30 84 22 46 26 60 13]
        [24 63 25 89  9 69 47 89 55 75]] X
        [[96  8]
        [32 24]
        [48 28]
        [74 73]
        [21 68]
        [83 82]
        [94 91]
        [80 64]
        [24 63]] Xsl

    """

def ta(shape, axis=None, idx=None, **kwargs):
    r"""returns take/put along dimension indexes

    Parameters
    ----------
    shape : list or tuple
        the shape of data
    axis : int, list or None
        axis list, If :attr:`axis` is None, the input array is treated as if it has been flattened to 1d.
    idx : list or None, optional
        slice lists of the specified :attr:`axis`, if None, does nothing (the default)
    dim : int or list
        (kwargs) if specified, will overwrite :attr:`axis`

    Returns
    -------
    tuple of slice
        slice for specified axis elements.

    Examples
    --------

    ::

        import torch as th
        import torchbox as tb

        tb.setseed(2025)

        print("---three dimensional")
        x = th.rand(3, 4, 5)
        print(x, x.shape)
        y = x.argmax(dim=1, keepdim=True)
        print(y, y.shape)
        print(th.take_along_dim(x, y, 1))
        print(x[tb.ta(x.shape, dim=1, idx=y)])

        print("---two dimensional")
        x = th.rand(3, 4)
        print(x, x.shape)
        y = x.argmax(dim=1, keepdim=True)
        print(y, y.shape)
        print(th.take_along_dim(x, y, 1))
        print(x[tb.ta(x.shape, dim=1, idx=y)])

        # outputs:
        ---three dimensional
        tensor([[[0.6850, 0.9355, 0.2900, 0.3991, 0.7470],
                [0.0215, 0.0654, 0.7855, 0.3883, 0.6340],
                [0.9447, 0.4773, 0.2861, 0.3887, 0.1099],
                [0.3606, 0.8450, 0.8059, 0.0520, 0.3438]],

                [[0.5326, 0.5318, 0.0709, 0.8716, 0.6798],
                [0.2956, 0.9812, 0.9813, 0.8118, 0.0463],
                [0.9592, 0.5132, 0.3941, 0.6953, 0.7350],
                [0.0309, 0.8294, 0.3368, 0.6413, 0.6471]],

                [[0.5964, 0.9792, 0.8084, 0.9328, 0.8772],
                [0.1945, 0.5616, 0.6019, 0.5040, 0.0028],
                [0.2127, 0.0655, 0.0905, 0.2134, 0.0313],
                [0.6896, 0.6147, 0.6534, 0.7446, 0.0566]]]) torch.Size([3, 4, 5])
        tensor([[[2, 0, 3, 0, 0]],

                [[2, 1, 1, 0, 2]],

                [[3, 0, 0, 0, 0]]]) torch.Size([3, 1, 5])
        tensor([[[0.9447, 0.9355, 0.8059, 0.3991, 0.7470]],

                [[0.9592, 0.9812, 0.9813, 0.8716, 0.7350]],

                [[0.6896, 0.9792, 0.8084, 0.9328, 0.8772]]])
        tensor([[[0.9447, 0.9355, 0.8059, 0.3991, 0.7470]],

                [[0.9592, 0.9812, 0.9813, 0.8716, 0.7350]],

                [[0.6896, 0.9792, 0.8084, 0.9328, 0.8772]]])
        ---two dimensional
        tensor([[0.0063, 0.8315, 0.6700, 0.5649],
                [0.3642, 0.8325, 0.3829, 0.1168],
                [0.2533, 0.3268, 0.7434, 0.9798]]) torch.Size([3, 4])
        tensor([[1],
                [1],
                [3]]) torch.Size([3, 1])
        tensor([[0.8315],
                [0.8325],
                [0.9798]])
        tensor([[0.8315],
                [0.8325],
                [0.9798]])

    """

def cut(x, pos, axis=None, **kwargs):
    r"""Cut array at given position.

    Cut array at given position.

    Parameters
    ----------
    x : array or tensor
        a tensor to be cut
    pos : tuple or list
        cut positions: ((cpstart, cpend), (cpstart, cpend), ...)
    axis : int, tuple or list, optional
        cut axis (the default is None, which means nothing)
    """

def arraycomb(arrays, out=None):
    r"""compute the elemnts combination of several lists.

    Args:
        arrays (list or tensor): The lists or tensors.
        out (tensor, optional): The combination results (defaults is :obj:`None`).

    Returns:
        tensor: The combination results.

    Examples:

    Compute the combination of three lists: :math:`[1,2,3]`, :math:`[4, 5]`, :math:`[6,7]`,
    this will produce a :math:`12\times 3` array.

    ::

        x = arraycomb(([1, 2, 3], [4, 5], [6, 7]))
        print(x, x.shape)

        # output:
        [[1 4 6]
        [1 4 7]
        [1 5 6]
        [1 5 7]
        [2 4 6]
        [2 4 7]
        [2 5 6]
        [2 5 7]
        [3 4 6]
        [3 4 7]
        [3 5 6]
        [3 5 7]] (12, 3)

    """

def permute(X, dim, mode=None, dir='f'):
    """permutes axes of tensor

    Parameters
    ----------
    X : Tensor
        the input tensor
    dim : list or tuple
        the order of new dimensions (:attr:`mode` is :obj:`None`) or multiplication dimensions (``'matmul'``)
    mode : str or None, optional
        permution mode, ``'matmul'`` for matrix multiplication; ``'swap'`` for swapping two dimensions;
        ``'merge'`` for dimension merging (putting the dimensions specified by second and subsequent elements of :attr:`dim`
        after the dimension specified by the specified by the first element of :attr:`dim`),
        ``'gather0'``: the specified dims are gathered at begin; ``'gather-1'``: the specified dims are gathered at end.
        :obj:`None` for regular permute, such as torch.permute, by default :obj:`None`.
    dir : str, optional
        the direction, ``'f'`` or ``'b'`` (reverse process of ``'f'``), default is ``'f'``.
    """    

def reduce(X, dim, keepdim, reduction):
    """reduce tensor in speciffied dimensions

    Parameters
    ----------
    X : Tensor
        the input tensor
    dim : int, list or tuple
        the dimensions for reduction
    keepdim : bool
        whether keep dimensions
    reduction : str or None
        The mode of reduction, :obj:`None`, ``'mean'`` or ``'sum'``

    Returns
    -------
    tensor
        the reduced tensor

    Raises
    ------
    ValueError
        reduction mode
    """

def swap(x, dim1, dim2):
    """swap dimensions of input

    Parameters
    ----------
    x : Tensor
        the input
    dim1 : int, list or tuple
        the first dimension
    dim2 : int, list or tuple
        the first dimension

    Returns
    -------
    tensor
        the result

    Raises
    ------
    TypeError
        :attr:`dim1` and :attr:`dim2` must be integer, list or tuple.
    """

def merge(x, dim, keepdim=False):
    """merge tensor's dimensions

    Parameters
    ----------
    x : Tensor
        the input
    dim : int, list or tuple
        dimensions indexes for merging, putting the dimensions specified by second and subsequent elements of :attr:`dim`
        after the dimension specified by the specified by the first element of :attr:`dim`)
    keepdim : bool, optional
        keep the dimensions?, by default False

    Returns
    -------
    tensor
        merged tensor.
    """

def roll(x, dim, shifts):
    r"""cyclic shift along specified dimension

    Roll the tensor :attr:`x` along the given dimension. Elements that are shifted beyond the last position are re-introduced at the first position.
    
    see `How to shift columns (or rows) in a tensor with different offsets in PyTorch? <https://stackoverflow.com/questions/66596699/how-to-shift-columns-or-rows-in-a-tensor-with-different-offsets-in-pytorch>`_
    
    Parameters
    ----------
    x : Tensor
        the input
    dim : int or None
        if :attr:`dim` is :obj:`None`, the tensor will be flattened before rolling and then restored to the original shape.
    shifts : int or Tensor
        the number of shifts, if :attr:`shifts` is an integer, all the data will be shifted with the same shifts, otherwise,
        will be shifted with different shifts which are specified by shifts.

    Returns
    -------
    Tensor
        the shifted tensor.

    Examples
    --------

    ::

        print('-------roll-------')
        x = th.rand(5, 7)
        print(x.shape)
        print(x)
        print('-------roll with the same shifts-------')
        print(roll(x, 1, 2))
        print('-------roll with different shifts-------')
        print(roll(x, 1, th.arange(1, 6)))

        print('-------roll a three-dimensional tensor-------')
        x = th.rand(5, 7, 3)
        y = roll(x, 1, th.arange(1, 6).view(5, 1).repeat(1, 3))
        print(x.shape)
        print(y.shape)
        print(x[..., 1])
        print(y[..., 1])
        
    """


