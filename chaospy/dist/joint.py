"""
Operators for creating multivariate distributions.

It contains the following two operators:

    J       Joint operator
    Iid     Independent identical distributed generator

Extra for these distribution beyond bavckend.Dist is that they
behave like a itterable tuple.
It support __getitem__, __iter__.
"""
import numpy as np
from copy import copy
from backend import Dist

__all__ = ["J", "Iid"]

class Joint(Dist):
    """
Joint probability operator
    """

    def __init__(self, *args):
        """
Parameters
----------
*args : [Dist, ..., Dist]
    Set of univariate distributions to join into joint.
        """

        assert np.all([isinstance(_, Dist) for _ in args])
        prm = {"_%03d" % i:args[i] for i in range(len(args))}
        Dist.__init__(self, _advance=True, _length=len(args), **prm)
        self.sorting = []
        for dist in self.G:
            if dist in args:
                self.sorting.append(args.index(dist))

    def _cdf(self, x, G):

        dim,size = x.shape
        out = np.empty((dim,1,size))
        x = x.reshape(dim,1,size)

        for i in self.sorting[::-1]:
            key = "_%03d" % i
            if key in G.K:
                out[i] = G.K[key]
            else:
                out[i] = G(x[i], G.D[key])

        return out.reshape(dim,size)

    def _mom(self, K, G):

        if self.dependent():
            raise NotImplementedError

        dim,size = K.shape
        K = K.reshape(dim,1,size)

        out = np.ones(K.shape[-1])
        for i in self.sorting:
            out *= G(K[i], G.D["_%03d" % i])

        return out

    def _pdf(self, x, G):

        dim,size = x.shape
        out = np.empty((dim,1,size))
        x = x.reshape(dim,1,size)

        for i in self.sorting[::-1]:
            key = "_%03d" % i
            if key in G.K:
                out[i] = G.K[key]
            else:
                out[i] = G(x[i], G.D[key])

        return out.reshape(dim,size)

    def _ppf(self, q, G):

        dim,size = q.shape
        out = np.empty((dim,size))
        q = q.reshape(dim,1,size)

        for i in self.sorting[::-1]:
            key = "_%03d" % i
            if key in G.K:
                out[i] = G.K[key]
            else:
                out[i] = G(q[i], G.D[key])

        return out.reshape(dim,size)

    def _ttr(self, K, G):

        if self.dependent():
            raise NotImplementedError, "dependency"

        dim,size = K.shape
        K = K.reshape(dim,1,size)

        out = np.zeros((2,dim,size))
        for i in self.sorting:
            out[:, i] = G(K[i], G.D["_%03d" % i])[:,0]

        return out

    def _bnd(self, x, G):


        dim,size = x.shape
        bnd = np.empty((2,dim,1,size))
        x = x.reshape(dim,1,size)

        for i in self.sorting[::-1]:

            key = "_%03d" % i
            if key in G.K:
                bnd[:,i] = G.K[key]
            else:
                bnd[:,i] = G(x[i], G.D[key])

        return bnd.reshape(2, dim, size)

    def _val(self, G):

        if len(G.K)!=len(self):
            return self
        out = np.array([G.K["_%03d" % i] \
                for i in self.sorting])
        out = out.reshape(len(out), out.shape[-1])
        return out

    def _str(self, **prm):
        dists = [prm["_%03d" % i] \
                for i in xrange(self.length)]
        dists = ",".join(map(str, dists))
        return "J(" + dists + ")"

    def _dep(self, G):
        dists = [self.prm["_%03d" % i] \
                for i in xrange(len(self))]
        sets = [G(dist)[0] for dist in dists]
        return sets

    def __getitem__(self, i):

        if isinstance(i, int):
            i = "_%03d" % i
            if i in self.prm:
                return self.prm[i]
            raise IndexError

        if isinstance(i, slice):
            start, stop, step = i.start, i.stop, i.step
            if start is None: start = 0
            if stop is None: stop = len(self)
            if step is None: step = 1
            out = []
            prm = self.prm
            for i in xrange(start, stop, step):
                out.append(prm["_%03d" % i])
            return J(*out)

        raise NotImplementedError, "index not recogniced"

def J(*args):
    """
Joint random variable generator

Parameters
----------
*args : Dist
    Distribution to join together

Returns
-------
dist : Dist
    Multivariate distribution

Examples
--------
Independent
>>> dist = cp.J(cp.Uniform(), cp.Normal())
>>> print(dist.mom([[0,0,1], [0,2,2]]))
[ 1.   1.   0.5]

Dependent
>>> d0 = cp.Uniform()
>>> dist = cp.J(d0, d0+cp.Uniform())
>>> print(dist.mom([[0,0,1], [0,1,1]]))
[ 1.          1.          0.53469533]
    """
    out = []
    args = list(args)
    while args:
        dist = args.pop(0)
        if isinstance(dist, Joint):
            prm = dist.prm
            args = [prm["_%03d" % i] for i in range(len(dist))] + args
        else:
            out.append(dist)

    return Joint(*out)

class Iid(Dist):
    """
Opaque method for creating independent identical distributed random
variables from an univariate variable.

Examples
--------
>>> X = cp.Normal()
>>> Y = cp.Iid(X, 4)
>>> cp.seed(1000)
>>> print(Y.sample())
[ 0.39502989 -1.20032309  1.64760248 -0.04465437]
    """

    def __init__(self, dist, N):
        """
Parameters
----------
dist : Dist
    Input variable. Must have `len(dist)==1`.
N : int
    Number of variable in the output.
        """
        assert len(dist)==1 and N>1
        Dist.__init__(self, dist=dist, _length=N)

    def _pdf(self, x, dist):
        return dist.pdf(x)

    def _cdf(self, x, dist):
        return dist.fwd(x)

    def _ppf(self, q, dist):
        return dist.inv(q)

    def _bnd(self, dist):
        return dist.range()

    def _mom(self, k, dist):
        return np.prod(dist.mom(k), 0)

    def _ttr(self, k, dist):
        return dist.ttr(k)

    def _str(self, dist):
        return "[%s]%d" % (dist, len(self))

    def __getitem__(self, i):

        if isinstance(i, int):
            return self.prm["dist"]

        raise NotImplementedError, "index not recogniced"

    def _dep(self, G):
        dist = G.D["dist"]
        return [set([copy(dist)]) for _ in range(len(self))]


if __name__=='__main__':
    import __init__ as cp
    import numpy as np
    import doctest
    doctest.testmod()
