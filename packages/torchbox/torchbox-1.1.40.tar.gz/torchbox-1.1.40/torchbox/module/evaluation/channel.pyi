class ChnlCapCor(th.nn.Module):
    r"""computes the capacity and correlation metric value of channel

    see "MIMO-OFDM Wireless Communications with MATLAB (Yong Soo Cho, Jaekwon Kim, Won Young Yang etc.)",
    

    Parameters
    ----------
    EsN0 : float
        the ratio of symbol energy to noise power spectral density, :math:`E_s/N_0({\rm dB}) = E_b/N_0 + 10{\rm log}_{10}K`
        :math:`E_s/N_0({\rm dB})=10{\rm log}_{10}(T_{\rm symbol}/T_{\rm sample}) + {\rm SNR}(dB)`, default is 30
    rank : int
        the rank of channel ( `what is <https://www.salimwireless.com/2022/11/channel-matrix-in-communication.html>`_ ), by default 4
    way : int
        computation mode: ``'det'``, ``'hadineq'`` (Hadamard inequality), ``'inv'`` (default)
    cdim : int or None
        If :attr:`H` is complex-valued, :attr:`cdim` is ignored. 
        If :attr:`H` is real-valued and :attr:`cdim` is an integer
        then :attr:`H` will be treated as complex-valued, in this case, :attr:`cdim` specifies the complex axis.
    dim : int or None
        The dimension indexes of (sub-carrirer, BS antenna, UE antenna), The default is ``(-3, -2, -1)``. 
    keepdim : bool
        keep dimensions? (include complex dim, defalut is :obj:`False`)
    reduction : str or None, optional
        The operation mode of reduction, :obj:`None`, ``'mean'`` or ``'sum'`` (the default is 'mean')
    
    Examples
    --------

    Here are demo codes.
    
    ::

        import torch as th
        import torchbox as tb

        th.manual_seed(2020)
        Nt, Nsc, Nbs, Nms = 10, 360, 64, 4
        # generates the ground-truth
        Hg = th.randn(Nt, 2, Nsc, Nbs, Nms)
        # noised version as the predicted
        Hp = tb.awgns(Hg, snrv=10, cdim=1, dim=(-3, -2, -1))

        # complex in real format
        metric = tb.ChnlCapCor(rank=4, cdim=1, dim=(-3, -2, -1), reduction='mean')
        metric.updategt(Hg)
        print(metric.forward(Hp))

        Hg = Hg[:, 0, ...] + 1j * Hg[:, 1, ...]
        Hp = Hp[:, 0, ...] + 1j * Hp[:, 1, ...]
        # complex in complex format
        metric = tb.ChnlCapCor(rank=4, cdim=None, dim=(-3, -2, -1), reduction='mean')
        metric.updategt(Hg)
        print(metric.forward(Hp))
        print(metric.forward(Hg))

        # complex in complex format
        metric = tb.ChnlCapCor(30, rank=4, cdim=None, dim=(-3, -2, -1), reduction=None)
        metric.updategt(Hg)
        capv, corv = metric.forward(Hp)
        print(capv.shape, corv.shape)

        # ---output
        (tensor(21.0226), tensor(0.8575))
        (tensor(21.0226), tensor(0.8575))
        (tensor(21.5848), tensor(1.))
        torch.Size([10]) torch.Size([10, 4])

    """

    def __init__(self, EsN0=30, rank=4, way='inv', cdim=None, dim=None, keepdim=False, reduction='mean'):
        ...

    def updategt(self, Hg):
        """update the ground-truth
        
        Parameters
        ----------
        Hg : Tensor
            the ground-truth channel

        """

    def forward(self, Hp):
        """forward process

        Parameters
        ----------
        Hp : Tensor
            the predicted/estimated channel.

        Returns
        -------
        capv : scalar or Tensor
            The capacity of the channel.
        corv : scalar or Tensor
            The correlation of the channel.
        """


