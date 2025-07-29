def rect(t):
    r"""create rectangle signal

    .. math::
        {\rm rect}(x) = {1, {\rm if} |x|<= 0.5; 0, {\rm otherwise}}

    Parameters
    ----------
    t : tensor
        time tensor

    Returns
    -------
    tensor
        rectangle signal

    Examples
    --------

    ::

        import torchbox as tb

        Ts = 3
        Fs = 100
        Ns = int(Ts * Fs)
        t = th.linspace(-Ts / 2., Ts / 2., Ns)

        x = tb.rect(t)

        plt = tb.plot([[x]], Xs=[[t]], grids=True, xlabels=['Times(s)'])
        plt.show()

    """

def chirp(t, fc, Kr, fm=0, pm=0, fmdir=-1, pmdir=-1, phi0=0, g=1):
    r"""create a chirp signal

    .. math::
        s_{\rm Tx}(t)={\rm exp}\left\{j2\pi((f_c+f_m)t+{\beta /2}t^2)+p_m + \varphi_0\right\}
        
    Parameters
    ----------
    t : tensor
        the time tensor (s)
    fc : float
        carrier frequency (Hz)
    Kr : float
        chirp rate (Hz/s)
    fm : float or tensor, optional
        modulated frequency, by default 0
    pm : float or tensor, optional
        modulated phase, by default 0
    fmdir : int, optional
        frequency modulation direction, 1 or -1, by default -1
    pmdir : int, optional
        phase modulation direction, 1 or -1, , by default -1
    phi0 : float, optional
        the initial phase, by default 0
    g : float or tensor, optional
        effective gain/rcs/amplitude, by default 1

    Returns
    -------
    tensor
        chirp signal

    Examples
    ---------

    ::

        Tc = 10e-6
        Fs = 100e6
        B = 1e9
        Kr = B / Tc
        fc = 77e9
        R = 100.

        t = th.arange(0, Tc, 1./Fs)
        st = chirp(t, fc, Kr)
        sr = chirp(t-R/tb.C, fc, Kr)

        sif = dechirp(sr, st)
        y = tb.fft(sif).abs()

        plt = tb.plot([[st.real, st.imag, st.abs()], [sr.real, sr.imag, sr.abs()], [sif.real, sif.imag, sif.abs()], [y]], Xs=[[t, t, t], [t, t, t], [t, t, t], [None]], grids=True, xlabels=['Times(s)', 'Times(s)', 'Times(s)', 'Frequency(Hz)'], legends=[['I', 'Q', 'A'], ['I', 'Q', 'A'], ['I', 'Q', 'A'], ['A']], titles=['Transmitted', 'Received', 'Dechirped', 'FFT of dechirped'])
        plt.show()
        
    """

def dechirp(srcv, sref, mod='+'):
    r"""dechirp signal

    Parameters
    ----------
    srcv : tensor
        received signal
    sref : tensor
        referenced signal
    mod : str, optional
        dechirp mode, ``'+'`` means the term :math:`j2\pi f_c \tau_{k}` in dechirped signal is positive
        otherwise, negative, by default '+'

    Returns
    -------
    tensor
        dechirped signal

    .. seealso:: :func:`chirp`
    
    """


