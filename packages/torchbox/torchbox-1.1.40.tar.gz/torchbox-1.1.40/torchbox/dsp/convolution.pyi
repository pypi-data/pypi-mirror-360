def cutfftconv1(y, nfft, Nx, Nh, shape='same', dim=0, ftshift=False):
    r"""Throwaway boundary elements to get convolution results.

    Throwaway boundary elements to get convolution results.

    Parameters
    ----------
    y : Tensor
        array after ``iff``.
    nfft : int
        number of fft points.
    Nx : int
        signal length
    Nh : int
        filter length
    shape : str
        output shape:
        1. ``'same' --> same size as input x``, :math:`N_x`
        2. ``'valid' --> valid convolution output``
        3. ``'full' --> full convolution output``, :math:`N_x+N_h-1`
        (the default is 'same')
    dim : int
        convolution dimension (the default is 0)
    ftshift : bool
        whether to shift zero the frequency to center (the default is False)

    Returns
    -------
    y : Tensor
        array with shape specified by :attr:`same`.
    """

def fftconv1(x, h, shape='same', nfft=None, ftshift=False, eps=None, **kwargs):
    r"""Convolution using Fast Fourier Transformation

    Convolution using Fast Fourier Transformation.

    Parameters
    ----------
    x : Tensor
        data to be convolved.
    h : Tensor
        filter array
    shape : str, optional
        output shape:
        1. ``'same' --> same size as input x``, :math:`N_x`
        2. ``'valid' --> valid convolution output``
        3. ``'full' --> full convolution output``, :math:`N_x+N_h-1`
        (the default is 'same')
    cdim : int or None
        If :attr:`x` is complex-valued, :attr:`cdim` is ignored. If :attr:`x` is real-valued and :attr:`cdim` is integer
        then :attr:`x` will be treated as complex-valued, in this case, :attr:`cdim` specifies the complex dim;
        otherwise (None), :attr:`x` will be treated as real-valued.
    dim : int, optional
        axis of fft operation (the default is 0, which means the first dimension)
    nfft : int, optional
        number of fft points (the default is :math:`2^{nextpow2(N_x+N_h-1)}`),
        note that :attr:`nfft` can not be smaller than :math:`N_x+N_h-1`.
    ftshift : bool, optional
        whether shift frequencies (the default is False)
    eps : None or float, optional
        x[abs(x)<eps] = 0 (the default is None, does nothing)

    Returns
    -------
    y : Tensor
        Convolution result array.

    """

def convn(A, B, dim=-1, shape='full', **kwargs):
    """convolution

    Parameters
    ----------
    A : tensor
        input
    B : tensor
        kernel
    dim : int, list or tuple, optional
        convolution dimensions, this dimensions will be permuted to the end, by default -1
    shape : str, optional
        convolution shape mode, ``'same'``, ``'valid'`` or ``'full'``, by default ``'full'``
    dimb : int, list or tuple
        (kwargs) convolution dim of :attr:`B`, if specified, :attr:`dim` only
        represents the convolution dim of :attr:`A`
    bias : bool or None
        (kwargs) with bias? by default None
    stride : int, list or tuple
        (kwargs) convolution stride
    padmode : str
        (kwargs) pad mode ``'constant'`` (default), ``'reflect'``, ``'replicate'``
    padvalue : float
        (kwargs) pad value
    dilation : int
        (kwargs) by default 1 
    groups : int
        (kwargs) by default 1

    Returns
    ---------
    C : tensor
        the convolution results
    
    Examples
    ----------

    ::

        import torch as th
        import torchbox as tb
        
        x = th.tensor([1, 2, 3, 4, 5.]).unsqueeze(0).unsqueeze(0)
        k = th.tensor([1, 2, 3.]).unsqueeze(0).unsqueeze(0)
        print(x.shape, k.shape)
        print(convn(x, k, dim=-1, shape='full').squeeze(0).squeeze(0))
        print(convn(x, k, dim=-1, shape='same').squeeze(0).squeeze(0))
        print(convn(x, k, dim=-1, shape='valid').squeeze(0).squeeze(0))

        x = th.tensor([1, 2, 3, 4, 5.])
        k = th.tensor([1, 2, 3.])
        print(x.shape, k.shape)
        print(convn(x, k, dim=-1, shape='full'))
        print(convn(x, k, dim=-1, shape='same'))
        print(convn(x, k, dim=-1, shape='valid'))


    """


