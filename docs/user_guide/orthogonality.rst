.. _orthogonality:

Orthogonal Polynomials
======================

The core idea of polynomial chaos expansions is that the polynomials used as an
expansion are all mutually orthogonal. The relation is typically written
mathematically as:

.. math::
    \left\langle \Phi_n, \Phi_m \right\rangle = 0 \qquad n \neq m

In practice this relation is instead expressed by the equivalent notation using
expected values:

.. math::
    \mbox E\left(\Phi_n \Phi_m\right) = 0 \qquad n \neq m

In ``chaospy`` this property can be tested by taking the outer product of two
expansions, and checking if the expected value of the resulting matrix is
diagonal. For example, for a basic monomial::

    >>> expansion = chaospy.monomial(4)
    >>> expansion
    polynomial([1, q0, q0**2, q0**3])
    >>> outer_product = chaospy.outer(expansion, expansion)
    >>> outer_product
    polynomial([[1, q0, q0**2, q0**3],
                [q0, q0**2, q0**3, q0**4],
                [q0**2, q0**3, q0**4, q0**5],
                [q0**3, q0**4, q0**5, q0**6]])
    >>> distribution = chaospy.Normal()
    >>> chaospy.E(outer_product, distribution)
    array([[ 1.,  0.,  1.,  0.],
           [ 0.,  1.,  0.,  3.],
           [ 1.,  0.,  3.,  0.],
           [ 0.,  3.,  0., 15.]])

In other words, the basic monomial (beyond polynomial order 1) are not
orthogonal.

But if we replace the basic monomial with an explicit orthogonal polynomial
constructor, we get::

    >>> expansion = chaospy.generate_expansion(3, distribution)
    >>> expansion
    polynomial([1.0, q0, q0**2-1.0, q0**3-3.0*q0])
    >>> outer_product = chaospy.outer(expansion, expansion)
    >>> chaospy.E(outer_product, distribution).round(15)
    array([[1., 0., 0., 0.],
           [0., 1., 0., 0.],
           [0., 0., 2., 0.],
           [0., 0., 0., 6.]])

A fully diagonal matrix, which implies all the polynomials in the expansion are
mutually orthogonal.

Algorithms
----------

There are three algorithms available:

+------------------------+--------------------------------------------------+
| Algorithm              | Description                                      |
+------------------------+--------------------------------------------------+
| three_terms_recurrence | Three terms recurrence coefficients generated    |
|                        | using Stieltjes :cite:`stieltjes_quelques_1884`  |
|                        | and Golub-Welsch method                          |
|                        | :cite:`golub_calculation_1967`. The most stable  |
|                        | of the methods, but do not work on               |
|                        | dependent distributions.                         |
+------------------------+--------------------------------------------------+
| gram_schmidt           | Gram-Schmidt orthogonalization method applied on |
|                        | polynomial expansions. Know for being            |
|                        | numerically unstable.                            |
+------------------------+--------------------------------------------------+
| cholesky               | Orthogonalization through decorrelation of the   |
|                        | covariance matrix. Uses Gill-King's Cholesky     |
|                        | decomposition method for higher numerical        |
|                        | stability. Still not scalable to high number of  |
|                        | dimensions.                                      |
+------------------------+--------------------------------------------------+

.. _lagrange:

Lagrange Polynomials
--------------------

Lagrange polynomials are not a method for creating orthogonal polynomials.
Instead it is an interpolation method for creating an polynomial expansion that
has the property that each polynomial interpolates exactly one point in space
with the value 1 and has the value 0 for all other interpolation values.
For more details, see this `article on Lagrange polynomials`_.

.. _article on Lagrange polynomials: https://en.wikipedia.org/wiki/Lagrange_polynomial
