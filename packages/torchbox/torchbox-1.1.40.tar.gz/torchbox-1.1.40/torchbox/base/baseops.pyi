def sub2ind(siz, sub):
    """returns linear index from multiple subscripts

    Parameters
    ----------
    siz : list, tuple, ndarray or Tensor
        the size of matrix (S1, S2, ...)
    sub : list, tuple, ndarray or Tensor
        the subscripts [(s11, s12, ...), (s21, s22, ...), ...]

    .. seealso:: :func:`ind2sub`
        
    Examples
    ---------

    conversion between subscripts and linear index of one, two and three dimensional data.

    ::

        print('---sub2ind([12], [1, 10])')
        print(sub2ind([12], [1, 10]))
        print('---ind2sub([12], [1, 10])')
        print(ind2sub([12], [1, 10]))

        print('---sub2ind([3, 4], [[1, 2], [2, 3], [0, 2]])')
        print(sub2ind([3, 4], [[1, 2], [2, 3], [0, 2]]))
        print('---ind2sub([3, 4], [6, 11, 2])')
        print(ind2sub([3, 4], [6, 11, 2]))

        print('---sub2ind([3, 4, 5], [[0, 3, 0], [1, 1, 1]])')
        print(sub2ind([3, 4, 5], [[0, 3, 0], [1, 1, 1]]))
        print('---ind2sub([3, 4, 5], [15, 26])')
        print(ind2sub([3, 4, 5], [15, 26]))

    """

def ind2sub(siz, ind):
    """returns multiple subscripts from linear index

    Parameters
    ----------
    siz : list, tuple, ndarray or Tensor
        the size of matrix (S1, S2, ...)
    ind : list, tuple, ndarray or Tensor
        the linear index


    .. seealso:: :func:`sub2ind`
        
    Examples
    ---------

    conversion between subscripts and linear index of one, two and three dimensional data.

    ::

        print('---sub2ind([12], [1, 10])')
        print(sub2ind([12], [1, 10]))
        print('---ind2sub([12], [1, 10])')
        print(ind2sub([12], [1, 10]))

        print('---sub2ind([3, 4], [[1, 2], [2, 3], [0, 2]])')
        print(sub2ind([3, 4], [[1, 2], [2, 3], [0, 2]]))
        print('---ind2sub([3, 4], [6, 11, 2])')
        print(ind2sub([3, 4], [6, 11, 2]))

        print('---sub2ind([3, 4, 5], [[0, 3, 0], [1, 1, 1]])')
        print(sub2ind([3, 4, 5], [[0, 3, 0], [1, 1, 1]]))
        print('---ind2sub([3, 4, 5], [15, 26])')
        print(ind2sub([3, 4, 5], [15, 26]))

    """    

def dimpos(ndim, dim):
    """make positive dimensions

    Parameters
    ----------
    ndim : int
        the number of dimensions
    dim : int, list or tuple
        the dimension index to be converted
    """

def rmcdim(ndim, cdim, dim, keepdim):
    r"""get dimension indexes after removing cdim

    Parameters
    ----------
    ndim : int
        the number of dimensions
    cdim : int, optional
        If data is complex-valued but represented as real tensors, 
        you should specify the dimension. Otherwise, set it to :obj:`None`
    dim : int, None, tuple or list
        dimensions to be re-defined
    keepdim : bool
        keep dimensions? (include complex dim, defalut is :obj:`False`)

    Returns
    -------
    int, tuple or list
         re-defined dimensions
        
    """

def dimpermute(ndim, dim, mode=None, dir='f'):
    """permutes dimensions

    Parameters
    ----------
    ndim : int
        the number of dimensions
    dim : list or tuple
        the order of new dimensions (:attr:`mode` is :obj:`None`) or multiplication dimensions (``'matmul'``)
    mode : str or None, optional
        permution mode, ``'matmul'`` for matrix multiplication; ``'swap'`` for swapping two dimensions;
        ``'merge'`` for dimension merging (putting the dimensions specified by second and subsequent elements of :attr:`dim`
        after the dimension specified by the specified by the first element of :attr:`dim`); 
        ``'gather0'``: the specified dims are gathered at begin; ``'gather-1'``: the specified dims are gathered at end.
        :obj:`None` for regular permute, such as torch.permute, by default :obj:`None`.
    dir : str, optional
        the direction, ``'f'`` or ``'b'`` (reverse process of ``'f'``), default is ``'f'``.
    """

def dimreduce(ndim, cdim, dim, keepcdim=False, reduction=None):
    """get dimensions for reduction operation

    Parameters
    ----------
    ndim : int
        the number of dimensions
    cdim : int, optional
        if the data is complex-valued but represented as real tensors, 
        you should specify the dimension. Otherwise, set it to :obj:`None`
    dim : int, list, tuple or None
        dimensions for processing, :obj:`None` means all
    keepcdim : bool
        keep the complex dimension? The default is :obj:`False`
    reduction : str or None, optional
        The operation in other dimensions except the dimensions specified by :attr:`dim`,
        :obj:`None`, ``'mean'`` or ``'sum'`` (the default is :obj:`None`)

    """    

def dimmerge(ndim, mdim, dim, keepdim=False):
    """obtain new dimension indexes after merging

    Parameters
    ----------
    ndim : int
        the number of dimensions
    mdim : int, list or tuple
        the dimension indexes for merging
    dim : int, list or tuple
        the dimension indexes that are not merged
    keepdim : bool
        keep the dimensions when merging?
    """

def upkeys(D, mode='-', k='module.'):
    r"""update keys of a dictionary

    Parameters
    ----------
    D : dict
        the input dictionary
    mode : str, optional
        ``'-'`` for remove key string which is specified by :attr:`k`, by default '-'
        ``'+'`` for add key string which is specified by :attr:`k`, by default '-'
    k : str, optional
        key string pattern, by default 'module.'

    Returns
    -------
    dict
        new dictionary with keys updated
    """

def dreplace(d, fv=None, rv='None', new=False):
    """replace dict value

    Parameters
    ----------
    d : dict
        the dict
    fv : any, optional
        to be replaced, by default :obj:`None`
    rv : any, optional
        replaced with, by default 'None'
    new : bool, optional
        if true, deep copy dict, will not change input, by default False

    Returns
    -------
    dict
        dict with replaced value
    """

def dmka(D, Ds):
    r"""Multiple key-value assign to a dict

    Parameters
    ----------
    D : dict
        main dict
    Ds : dict
        sub dict

    Returns
    -------
    dict
        after assign
    """

def cat(shapes, axis=0):
    r"""Concatenates

    Concatenates the given sequence of seq shapes in the given dimension.
    All tensors must either have the same shape (except in the concatenating dimension) or be empty.

    Parameters
    ----------
    shapes : tuples or lists
        (shape1, shape2, ...)
    axis : int, optional
        specify the concatenated axis (the default is 0)

    Returns
    -------
    tuple or list
        concatenated shape

    Raises
    ------
    ValueError
        Shapes are not consistent in axises except the specified one.
    """

def argsort(x, reverse=False):
    r"""returns index of sorted array

    Parameters
    ----------
    x : list, ndarray or tensor
        the input
    reverse : bool, optional
        sort in reversed order?, by default False

    Returns
    -------
    list, ndarray or tensor
        the index
    """

def argmin(X, cdim=None, dim=None, keepdim=False):
    """return index of minimum values

    Parameters
    ----------
    X :  tensor
        the input data
    cdim : int or None
        If :attr:`X` is complex-valued, :attr:`cdim` is ignored. If :attr:`X` is real-valued and :attr:`cdim` is integer
        then :attr:`X` will be treated as complex-valued, in this case, :attr:`cdim` specifies the complex axis;
        otherwise (None), :attr:`X` will be treated as real-valued
    dim : tuple, None, optional
        The dimension axis for computing dot product. The default is :obj:`None`, which means all.
    keepdim : bool
        keep dimensions? (include complex dim, defalut is :obj:`False`)

    """   

def argmax(X, cdim=None, dim=None, keepdim=False):
    """return index of maximum values

    Parameters
    ----------
    X :  tensor
        the input data
    cdim : int or None
        If :attr:`X` is complex-valued, :attr:`cdim` is ignored. If :attr:`X` is real-valued and :attr:`cdim` is integer
        then :attr:`X` will be treated as complex-valued, in this case, :attr:`cdim` specifies the complex axis;
        otherwise (None), :attr:`X` will be treated as real-valued
    dim : tuple, None, optional
        The dimension axis for computing dot product. The default is :obj:`None`, which means all.
    keepdim : bool
        keep dimensions? (include complex dim, defalut is :obj:`False`)

    """   

def min(X, cdim=None, dim=None, keepdim=False):
    """return minimum values

    Parameters
    ----------
    X :  tensor
        the input data
    cdim : int or None
        If :attr:`X` is complex-valued, :attr:`cdim` is ignored. If :attr:`X` is real-valued and :attr:`cdim` is integer
        then :attr:`X` will be treated as complex-valued, in this case, :attr:`cdim` specifies the complex axis;
        otherwise (None), :attr:`X` will be treated as real-valued
    dim : tuple, None, optional
        The dimension axis for computing dot product. The default is :obj:`None`, which means all.
    keepdim : bool
        keep dimensions? (include complex dim, defalut is :obj:`False`)

    Examples
    ---------

    ::

        th.manual_seed(2020)
        X = th.rand((2, 3, 4))
        print(X)
        print(min(X, cdim=None, dim=[-2, -1], keepdim=False))
        print((X[[0]]+1j*X[[1]]).abs())
        print('---argmin')
        print(argmin(X, cdim=None, dim=[-1, -2], keepdim=False))
        print(argmin(X, cdim=0, dim=[-2, -1], keepdim=False))
        print(argmin(X[[0]]+1j*X[[1]], cdim=None, dim=[-1, -2], keepdim=False))

        print('---min')
        print(min(X, cdim=None, dim=[-2, -1], keepdim=False))
        print(min(X, cdim=0, dim=[-2, -1], keepdim=False))
        print(min(X[[0]]+1j*X[[1]], cdim=None, dim=[-1, -2], keepdim=False))

        tensor([[[0.4869, 0.1052, 0.5883, 0.1161],
            [0.4949, 0.2824, 0.5899, 0.8105],
            [0.2512, 0.6307, 0.5403, 0.8033]],

            [[0.7781, 0.4966, 0.8888, 0.5570],
            [0.7127, 0.0339, 0.1151, 0.8780],
            [0.0671, 0.5173, 0.8126, 0.3861]]])
        tensor([0.1052, 0.0339])
        tensor([[[0.9179, 0.5077, 1.0659, 0.5690],
                [0.8676, 0.2844, 0.6011, 1.1949],
                [0.2600, 0.8158, 0.9758, 0.8912]]])
        ---argmin
        [tensor([1, 1]), tensor([0, 1])]
        [tensor(2), tensor(0)]
        [tensor([0]), tensor([2])]
        ---min
        tensor([0.1052, 0.0339])
        tensor([0.2512, 0.0671])
        tensor([0.2512+0.0671j])

    """   

def max(X, cdim=None, dim=None, keepdim=False):
    """return maximum values

    Parameters
    ----------
    X :  tensor
        the input data
    cdim : int or None
        If :attr:`X` is complex-valued, :attr:`cdim` is ignored. If :attr:`X` is real-valued and :attr:`cdim` is integer
        then :attr:`X` will be treated as complex-valued, in this case, :attr:`cdim` specifies the complex axis;
        otherwise (None), :attr:`X` will be treated as real-valued
    dim : tuple, None, optional
        The dimension axis for computing dot product. The default is :obj:`None`, which means all.
    keepdim : bool
        keep dimensions? (include complex dim, defalut is :obj:`False`)

    Examples
    ---------

    ::

        th.manual_seed(2020)
        X = th.rand((2, 3, 4))
        print(X)
        print((X[[0]]+1j*X[[1]]).abs())
        print('---argmax')
        print(argmax(X, cdim=None, dim=[-2, -1], keepdim=True))
        print(argmax(X, cdim=0, dim=[-2, -1], keepdim=True))
        print(argmax(X[[0]]+1j*X[[1]], cdim=None, dim=[-1, -2], keepdim=True))

        print('---max')
        print(max(X, cdim=None, dim=[-2, -1], keepdim=True))
        print(max(X, cdim=0, dim=[-2, -1], keepdim=True))
        print(max(X[[0]]+1j*X[[1]], cdim=None, dim=[-1, -2], keepdim=True))

        # outputs:
        tensor([[[0.4869, 0.1052, 0.5883, 0.1161],
                [0.4949, 0.2824, 0.5899, 0.8105],
                [0.2512, 0.6307, 0.5403, 0.8033]],

                [[0.7781, 0.4966, 0.8888, 0.5570],
                [0.7127, 0.0339, 0.1151, 0.8780],
                [0.0671, 0.5173, 0.8126, 0.3861]]])
        tensor([[[0.9179, 0.5077, 1.0659, 0.5690],
                [0.8676, 0.2844, 0.6011, 1.1949],
                [0.2600, 0.8158, 0.9758, 0.8912]]])
        ---argmax
        [tensor([[[1]],

                [[0]]]), tensor([[[3]],

                [[2]]])]
        [tensor([[[1]]]), tensor([[[3]]])]
        [tensor([[[3]]]), tensor([[[1]]])]
        ---max
        tensor([[[0.8105]],

                [[0.8888]]])
        tensor([[[0.8105]],

                [[0.8780]]])
        tensor([[[0.8105+0.8780j]]])

    """   


