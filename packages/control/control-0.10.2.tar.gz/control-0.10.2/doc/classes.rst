.. currentmodule:: control

.. _class-ref:

**********************
Control System Classes
**********************

Input/Output System Classes
===========================

The classes listed below are used to represent models of input/output
systems (both linear time-invariant and nonlinear).  They are usually
created from factory functions such as :func:`tf` and :func:`ss`, so the
user should normally not need to instantiate these directly.

The following figure illustrates the relationship between the classes:

.. figure:: figures/classes.svg
   :width: 640
   :align: center

.. autosummary::
   :toctree: generated/
   :template: custom-class-template.rst
   :nosignatures:

   InputOutputSystem
   NonlinearIOSystem
   LTI
   StateSpace
   TransferFunction
   FrequencyResponseData
   InterconnectedSystem
   LinearICSystem

The time response of an input/output system is represented using a
special :class:`NamedSignal` class that allows the individual signal
elements to be access using signal names in place of integer offsets:

.. autosummary::
   :toctree: generated/
   :template: extended-class-template.rst
   :nosignatures:

   NamedSignal


Response and Plotting Classes
=============================

These classes are used as the outputs of `_response`, `_map`, and
`_plot` functions:

.. autosummary::
   :toctree: generated/
   :template: custom-class-template.rst
   :nosignatures:

   ControlPlot
   FrequencyResponseData
   NyquistResponseData
   PoleZeroData
   TimeResponseData

In addition, the following classes are used to store lists of
responses, which can then be plotted using the ``.plot()`` method:

.. autosummary::
   :toctree: generated/
   :template: list-class-template.rst
   :nosignatures:

   FrequencyResponseList
   NyquistResponseList
   PoleZeroList
   TimeResponseList

More information on the functions used to create these classes can be
found in the :ref:`response-chapter` chapter.


Nonlinear System Classes
========================

These classes are used for various nonlinear input/output system
operations:

.. autosummary::
   :toctree: generated/
   :template: custom-class-template.rst
   :nosignatures:

   DescribingFunctionNonlinearity
   DescribingFunctionResponse
   flatsys.BasisFamily
   flatsys.BezierFamily
   flatsys.BSplineFamily
   flatsys.FlatSystem
   flatsys.LinearFlatSystem
   flatsys.PolyFamily
   flatsys.SystemTrajectory
   OperatingPoint
   optimal.OptimalControlProblem
   optimal.OptimalControlResult
   optimal.OptimalEstimationProblem
   optimal.OptimalEstimationResult

More information on the functions used to create these classes can be
found in the :ref:`nonlinear-systems` chapter.
