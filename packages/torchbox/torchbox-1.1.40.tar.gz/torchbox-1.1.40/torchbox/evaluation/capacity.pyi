def capacity(H, snr, cdim, dim=(-2, -1), keepdim=False, reduction='mean'):
    """computes capacity of channel

    MIMO-OFDM Wireless Communications with MATLAB

    Parameters
    ----------
    H : Tensor
        the input channel
    snr : float
        the signal-to-noise ratio
    cdim : int or None
        If :attr:`H` is complex-valued, :attr:`cdim` is ignored. 
        If :attr:`H` is real-valued and :attr:`cdim` is an integer
        then :attr:`H` will be treated as complex-valued, in this case, :attr:`cdim` specifies the complex axis.
    dim : int or None
        The dimension indexes of antenna of BS and MS. 
        The default is ``(-2, -1)``. 
    keepdim : bool
        keep dimensions? (include complex dim, defalut is :obj:`False`)
    reduction : str or None, optional
        The operation mode of reduction, :obj:`None`, ``'mean'`` or ``'sum'`` (the default is 'mean')
        
    """


