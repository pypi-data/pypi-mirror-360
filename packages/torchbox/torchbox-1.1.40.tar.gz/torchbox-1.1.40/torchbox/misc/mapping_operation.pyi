def dynrng(X, idrange=None, odrange=(0., 255.), mode='abs', method='2Sigma', odtype='auto', **kwargs):
    r"""adjust dynamic range

    Parameters
    ----------
    X : Tensor
        data to be converted
    idrange : tuple, optional
        dynamic range of input (the default is :obj:`None`)
    odrange : tuple, optional
        dynamic range of output (the default is (0., 255.))
    mode : str, optional
        mode for preprocessing :attr:`X`, ``'abs'`` (default), ``'angle'``, ``'pow'`` or None.
    method : str, optional
        dynamic range adjust method, surpported values are ``'1Sigma'``, ``'2Sigma'``, ... ``'xSigma'``,
        or ``None``, ``'<TH'``, ``'>TH'`` (The elements of 10log10(X) that lower (< or '') / greater (>) than TH will be set to TH),
        or ``'log'``, ``'<THlog'``, ``'>THlog'`` (The elements of X  that lower (< or '') / greater (>) than TH will be set to TH),
        or ``'logmax'``, ``'<THlogmax'``, ``'>THlogmax'`` (The elements of 10log10(X/max(X)) that lower (< or '') / greater (>) than TH will be set to TH),
        or ``'lognorm'``, ``'<THlognorm'``, ``'>THlognorm'`` (The elements of 10log10(X/norm(X)) that lower (< or '') / greater (>) than TH will be set to TH),
        (the default is '2Sigma', which means two-sigma mapping)
    odtype : str or None, optional
        output data type, supportted are ``'auto'`` (auto infer, default), or dtype string.
        If the type of :attr:`odtype` is not string, the output data type is ``'th.float32'``.
    cdim : None or int, optional
        If :attr:`X` is complex-valued, :attr:`cdim` is ignored. If :attr:`X` is real-valued and :attr:`cdim` is integer
        then :attr:`X` will be treated as complex-valued, in this case, :attr:`cdim` specifies the complex axis;
        otherwise (None), :attr:`X` will be treated as real-valued
    dim : int or None, optional
        Specifies the dimensions for adjusting dynamic range, if not specified, it's set to :obj:`None`, 
        which means all the dimensions.
    keepdim : bool, optional
        keep dimensions?, default is :obj:`False`

    Returns
    -------
    Y : Tensor
        adjusted data

    """

def mapping(X, drange=(0., 255.), mode='amplitude', method='2Sigma', odtype='auto'):
    r"""map to image

    Convert data to image data :math:`\bm X` with dynamic range :math:`d=[min, max]`.

    Parameters
    ----------
    X : Tensor
        data to be converted
    drange : tuple, optional
        dynamic range (the default is (0., 255.))
    mode : str, optional
        data mode in :attr:`X`, ``'amplitude'`` (default) or ``'power'``.
    method : str, optional
        mapping method, surpported values are ``'1Sigma'``, ``'2Sigma'``, ... ``'xSigma'``,
        or ``'log'``, ``'<THlog'``, ``'<THlog'`` (The elements of 10log10(X) lower (< or '') / greater (>) than TH will be set to TH),
        or ``'logmax'``, ``'<THlogmax'``, ``'>THlogmax'`` (The elements of 10log10(X/max(X)) lower (< or '') / greater (>) than TH will be set to TH),
        or ``'lognorm'``, ``'<THlognorm'``, ``'>THlognorm'`` (The elements of 10log10(X/norm(X)) lower (< or '') / greater (>) than TH will be set to TH),
        (the default is '2Sigma', which means two-sigma mapping)
    odtype : str or None, optional
        output data type, supportted are ``'auto'`` (auto infer, default), or dtype string.
        If the type of :attr:`odtype` is not string, the output data type is ``'th.float32'``.

    Returns
    -------
    Y : Tensor
        converted image data

    Examples
    ---------

    ::

        X = th.randn(3, 4) + 1j*th.randn(3, 4)
        print(X)
        print("---complex, Sigma")
        Y = dynrng(X, idrange=None, odrange=(0., 255.), mode='abs', method='2Sigma', odtype='auto')
        print(Y, Y.shape)

        Y = dynrng(X, idrange=None, odrange=(0., 255.), mode='angle', method='2Sigma', odtype='auto')
        print(Y, Y.shape)

        Y = dynrng(X, idrange=None, odrange=(0., 255.), mode='pow', method='2Sigma', odtype='auto')
        print(Y, Y.shape)

        Y = dynrng(X, idrange=None, odrange=(0., 255.), mode='', method='2Sigma', odtype='auto')
        print(Y, Y.shape)

        Y = tb.r2c(dynrng(tb.c2r(X), cdim=-1, idrange=None, odrange=(0., 255.), mode='', method='2Sigma', odtype='auto'))
        print(Y, Y.shape)

        print("---complex, Log")
        Y = dynrng(X, idrange=None, odrange=(0., 255.), mode='abs', method='<-10log', odtype='auto')
        print(Y, Y.shape)

        Y = dynrng(X, idrange=None, odrange=(0., 255.), mode='angle', method='<-10log', odtype='auto')
        print(Y, Y.shape)

        Y = dynrng(X, idrange=None, odrange=(0., 255.), mode='pow', method='<-10log', odtype='auto')
        print(Y, Y.shape)

        Y = dynrng(X, idrange=None, odrange=(0., 255.), mode='', method='<-10log', odtype='auto')
        print(Y, Y.shape)

        Y = tb.r2c(dynrng(tb.c2r(X), cdim=-1, idrange=None, odrange=(0., 255.), mode='', method='<-10log', odtype='auto'))
        print(Y, Y.shape)

        # ---output:
        ---complex, Sigma
        tensor([[-0.5677+0.5894j,  1.0390+0.5422j, -0.6507+2.4994j, -1.0951+0.0883j],
                [-1.0354-0.2675j, -2.4364-0.7381j, -0.7252-1.3905j,  0.0519-0.0911j],
                [ 1.5187-0.8795j,  1.8736-0.5303j, -1.5583+0.4149j,  1.1492-0.1923j]])
        tensor([[ 73, 109, 255, 102],
                [ 99, 251, 150,   0],
                [169, 189, 155, 109]], dtype=torch.uint8) torch.Size([3, 4])
        tensor([[223, 144, 202, 255],
                [  0,   1,  35,  78],
                [101, 111, 247, 116]], dtype=torch.uint8) torch.Size([3, 4])
        tensor([[ 25,  52, 254,  45],
                [ 43, 247,  93,   0],
                [117, 144,  99,  51]], dtype=torch.uint8) torch.Size([3, 4])
        tensor([[101.+165.j, 190.+162.j,  97.+255.j,  72.+137.j],
                [ 75.+118.j,   0.+92.j,  92.+56.j, 135.+127.j],
                [216.+84.j, 236.+103.j,  46.+155.j, 196.+122.j]]) torch.Size([3, 4])
        tensor([[101.+165.j, 190.+162.j,  97.+255.j,  72.+137.j],
                [ 75.+118.j,   0.+92.j,  92.+56.j, 135.+127.j],
                [216.+84.j, 236.+103.j,  46.+155.j, 196.+122.j]]) torch.Size([3, 4])
        ---complex, Log
        tensor([[115, 159, 255, 151],
                [147, 253, 194,   0],
                [208, 220, 197, 158]], dtype=torch.uint8) torch.Size([3, 4])
        tensor([[243, 205, 234, 255],
                [  0,   0,  84, 152],
                [174, 183, 252, 187]], dtype=torch.uint8) torch.Size([3, 4])
        tensor([[115, 159, 255, 151],
                [147, 253, 194,   0],
                [208, 220, 197, 158]], dtype=torch.uint8) torch.Size([3, 4])
        tensor([[164.+209.j, 222.+208.j, 160.+255.j, 134.+192.j],
                [138.+178.j,   0.+155.j, 156.+111.j, 191.+185.j],
                [234.+147.j, 242.+166.j,  94.+204.j, 225.+181.j]]) torch.Size([3, 4])
        tensor([[164.+209.j, 222.+208.j, 160.+255.j, 134.+192.j],
                [138.+178.j,   0.+155.j, 156.+111.j, 191.+185.j],
                [234.+147.j, 242.+166.j,  94.+204.j, 225.+181.j]]) torch.Size([3, 4])

    """


