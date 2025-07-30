evtpooling
==========

**evtpooling** provides a comprehensive framework for improving tail risk forecasts by combining robust statistical modeling, data transformation, and diagnostic backtesting.

It features a production-ready ETL pipeline for financial time series data, modular forecasting evaluation tools, and implementations of advanced tail-based clustering and testing methods. This includes RMTC-based clustering, HMIX mixture modeling, and a fully integrated traffic-light backtesting system with Diebold-Mariano forecast comparison.

The codebase follows modern Python packaging and style standards via `pyproject.toml`, and uses `pre-commit` for enforcing formatting (Black, Ruff), linting, and type safety.

**Note that** this package includes some constants accesible under `evtpooling.constants` that are used for convenience. These constants are mostly used for the etl_pipeline but can be modified to suit your needs.

Features
--------

* Full ETL pipeline for financial time series data
* Robust loss return calculations (daily, weekly, anchor-based)
* RMTC (Robust Model-based Tail Clustering) algorithm
* HMIX (Heteroscedastic Mixture) tail modeling with robust optimization
* Integrated backtesting framework with:
  - Traffic light logic
  - Diebold-Mariano forecast accuracy tests
* Visualizations of loss distributions, VaR exceedances, and tail index behavior
* Data validation (missing values, dtypes, fuzzy categorical matching)
* Clean, testable architecture (ETL, transform, modeling, testing modules)
* Interactive result summaries via DataFrames and matplotlib plots
* Fully automated testing with `pytest`
* Centralized configuration using `pyproject.toml`
* Pre-commit hooks for Ruff, Black, and Mypy integration
* CI-friendly and GitHub Actions-compatible

Installation
------------

You can install the released version from PyPI using:

.. code-block:: bash

    pip install evtpooling

Or install directly from the source (development version):

.. code-block:: bash

    git clone https://github.com/JTKimQF/evtpooling.git
    cd evtpooling
    pip install -e .

Usage Example
-------------

The package supports a full ETL-to-evaluation pipeline for tail risk modeling and backtesting. Below is a simplified example of its usage:

.. code-block:: python

    import numpy as np
    from evtpooling import (
        etl_pipeline,
        get_alpha_dict,
        get_var_dict,
        kmeans_pooling,
        rmtc_pooling,
        basel_backtesting,
        sener_backtesting,
        dm_test,
    )

    # Load and transform input data
    weekly_losses, daily_losses = etl_pipeline("path/to/input.csv", return_day_data=True)

    # Estimate tail indices (alphas) from the training portion
    k_thresh = 60
    weekly_losses_train = weekly_losses[weekly_losses.index <= "2018-12-31"]
    alpha_dict = get_alpha_dict(weekly_losses_train, k_threshold=k_thresh)

    # Generate non-pooled VaR estimates
    var_dict = get_var_dict(weekly_losses_train, k_threshold=k_thresh)

    # KMeans-based clustering and pooled VaR
    df_kmeans = kmeans_pooling(weekly_losses_train, k_threshold=k_thresh, num_clusters=4)
    var_dict_kmeans = dict(zip(df_kmeans.index, df_kmeans["kmeans_var"]))

    # RMTC-based clustering and pooled VaR
    df_rmtc, beta_list = rmtc_pooling(
        losses=weekly_losses_train,
        k_threshold=k_thresh,
        beta=([0.4, 0.4, 0.2], [(1.9, 0.2), (2.3, 0.3), (3.0, 0.5)]),
        threshold=1e-4,
        max_iter=50,
    )
    var_dict_rmtc = dict(zip(df_rmtc.index, df_rmtc["rmtc_var"]))

    # Backtesting on evaluation data
    weekly_losses_eval = weekly_losses[weekly_losses.index > "2018-12-31"]

    df_backtest_kmeans = basel_backtesting(weekly_losses_eval, var_dict=var_dict_kmeans)
    df_backtest_rmtc = basel_backtesting(weekly_losses_eval, var_dict=var_dict_rmtc)

    # Forecast accuracy comparison using Diebold-Mariano test
    dm_kmeans = dm_test(weekly_losses_eval, var_dict1=var_dict, var_dict2=var_dict_kmeans)
    dm_rmtc = dm_test(weekly_losses_eval, var_dict1=var_dict, var_dict2=var_dict_rmtc)

    print("DM test (non-pooling vs KMeans):")
    print(dm_kmeans)

    print("DM test (non-pooling vs RMTC):")
    print(dm_rmtc)

For further details check out the testing_script.py file

Documentation
-------------

Full documentation and function reference is available inside the code base (`src/evtpooling/...`).

License
-------

MIT License

Copyright (c) 2025 J.T. Kim

This package was created with `Cookiecutter`_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
