# Instaseis - Instant high-frequency seismograms

[![Tests](https://github.com/krischer/instaseis/workflows/Tests/badge.svg)](https://github.com/krischer/instaseis/actions/workflows/test.yml)
[![Documentation](https://github.com/krischer/instaseis/workflows/Documentation/badge.svg)](https://github.com/krischer/instaseis/actions/workflows/docs.yml)

[Documentation](http://instaseis.net)

[![Instaseis](http://i.imgur.com/6LNoJD6.png)](instaseis.net)

Instaseis: Instant Global Broadband Seismograms Based on a Waveform Database

Instaseis calculates broadband seismograms from Green’s function databases
generated with AxiSEM and allows for near instantaneous (on the order of
milliseconds) extraction of seismograms. Using the 2.5D axisymmetric spectral
element method, the generation of these databases, based on reciprocity of the
Green’s functions, is very efficient and is approximately half as expensive as a
single AxiSEM forward run. Thus this enables the computation of full databases
at half the cost of the computation of seismograms for a single source in the
previous scheme and hence allows to compute databases at the highest frequencies
globally observed. By storing the basis coefficients of the numerical scheme
(Lagrange polynomials), the Green’s functions are 4th order accurate in space
and the spatial discretization respects discontinuities in the velocity model
exactly. On top, AxiSEM allows to include 2D structure in the source receiver
plane and readily includes other planets such as Mars.
