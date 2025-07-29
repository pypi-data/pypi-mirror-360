*****************************************************************************************************
cuQuantum Python: A High-Performance Library for Accelerating Quantum Computing Simulations in Python
*****************************************************************************************************

NVIDIA cuQuantum Python provides Python bindings and high-level object-oriented models for accessing the full 
functionalities of `NVIDIA cuQuantum SDK <https://developer.nvidia.com/cuquantum-sdk>`_ from Python.

Documentation
=============

For detailed guide, please refer to `cuQuantum Python documentation <https://docs.nvidia.com/cuda/cuquantum/latest/python/index.html>`_.

Installation
============

.. code-block:: bash

   pip install -v --no-cache-dir cuquantum-python

.. note::

   Starting cuQuantum 22.11, this package is a meta package pointing to ``cuquantum-python-cuXX``,
   where XX is the CUDA major version (currently CUDA 11 & 12 are supported).
   The meta package will attempt to infer and install the correct ``-cuXX`` wheel. However,
   in situations where the auto-detection fails, this package currently points to ``cuquantum-python-cu11``
   with a warning raised (if the verbosity flag ``-v`` is set, as shown above). This behavior
   will change in the next release, moving from cu11 to cu12, and users are encouraged to install the new wheels that
   come *with* the ``-cuXX`` suffix.

   The argument ``--no-cache-dir`` is required for pip 23.1+. It forces pip to execute the
   auto-detection logic.

   Future support for CUDA 11 will be deprecated when support for CUDA 13 is added.

Citing cuQuantum
================

`H. Bayraktar et al., "cuQuantum SDK: A High-Performance Library for Accelerating Quantum Science," 2023 IEEE International Conference on Quantum Computing and Engineering (QCE), Bellevue, WA, USA, 2023, pp. 1050-1061, doi: 10.1109/QCE57702.2023.00119 <https://doi.org/10.1109/QCE57702.2023.00119>`_
