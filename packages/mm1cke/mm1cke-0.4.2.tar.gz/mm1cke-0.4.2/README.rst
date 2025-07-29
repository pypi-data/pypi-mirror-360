mm1cke
======

A Continuous Kolmogorov Equation (CKE) solver for M/M/1 queueing systems.

|pypi| |python| |license|

.. |pypi| image:: https://img.shields.io/pypi/v/mm1cke.svg
   :target: https://pypi.org/project/mm1cke/
.. |python| image:: https://img.shields.io/pypi/pyversions/mm1cke.svg
.. |license| image:: https://img.shields.io/github/license/smz70/MM1CKE

Overview
--------
mm1cke provides a fast and accurate solver for the transient behavior of M/M/1 queues using the continuous Kolmogorov equations (CKE). It is designed for researchers and practitioners in operations research, queueing theory, and performance analysis.

Features
--------
- Transient analysis of M/M/1 queues
- Vectorized and efficient implementation
- Outputs results as Polars DataFrames
- Easy integration with scientific Python stack

Installation
------------
Install with pip:

.. code-block:: bash

   pip install mm1cke

Requirements
------------
- Python >= 3.11
- simpy >= 4.1, < 5
- matplotlib >= 3.10, < 4
- polars >= 1.30, < 4
- rich >= 14
- scipy >= 1.15
- seaborn >= 0.13
- pydantic >= 2.11

Usage Example
-------------

.. code-block:: python

   from mm1cke import TransientCase, solve_transient

   case = TransientCase(L_0=9, λ=0.88, μ=1, ls_max=500, time_step=0.5)
   probs_df = solve_transient(case)
   print(probs_df)

   # Calculate performance measures (mean and coefficient of variation)
   from mm1cke.utils import calculate_performance_measures
   plot_df = calculate_performance_measures(probs_df)
   print(plot_df)

   # Plotting (optional)
   import seaborn as sns
   import matplotlib.pyplot as plt
   ax = sns.lineplot(plot_df, x="t", y="e_l_s")
   plt.show()

API Reference
-------------

- ``mm1cke.TransientCase``: Configuration for a transient M/M/1 queue case.
- ``mm1cke.solve_transient(case: TransientCase) -> polars.DataFrame``: Solves the transient CKE for the given case.
- ``mm1cke.utils.calculate_performance_measures(probs_df: polars.DataFrame)``: Computes mean and coefficient of variation of the queue length over time.

Project Links
-------------
- Homepage: https://github.com/smz70/MM1CKE
- Bug Tracker: https://github.com/smz70/MM1CKE/issues

License
-------
MIT License. See LICENSE file for details.
