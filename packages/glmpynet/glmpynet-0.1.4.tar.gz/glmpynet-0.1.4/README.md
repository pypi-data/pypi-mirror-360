#  glmpynet

[![CircleCI](https://circleci.com/gh/hrolfrc/glmpynet.svg?style=shield)](https://circleci.com/gh/hrolfrc/glmpynet)
[![ReadTheDocs](https://readthedocs.org/projects/glmpynet/badge/?version=latest)](https://glmpynet.readthedocs.io/en/latest/)
[![Codecov](https://codecov.io/gh/hrolfrc/glmpynet/branch/master/graph/badge.svg)](https://codecov.io/gh/hrolfrc/glmpynet)

## glmnet-based Logistic Regression for Scikit-Learn

**glmpynet** is a high-performance Python wrapper for the `glmnet` library, providing a scikit-learn compatible estimator for penalized logistic regression.

This project aims to bridge the gap between the raw computational speed of the original Fortran/C++ `glmnet` code and the ease-of-use of the Python data science ecosystem. It provides a single, focused class that acts as a drop-in replacement for `sklearn.linear_model.LogisticRegression` for users who need the power of elastic-net regularization for binary classification.

## Key Features

* **High Performance:** Leverages the highly optimized, battle-tested `glmnet` Fortran backend for fitting models, making it suitable for large datasets.

* **Scikit-learn Compatible:** Implements the standard `fit`, `predict`, and `predict_proba` API, allowing it to be seamlessly integrated into `sklearn` pipelines, `GridSearchCV`, and other tools.

* **Full Regularization Suite:** Supports L1 (Lasso), L2 (Ridge), and Elastic-Net regularization for robust feature selection and prevention of overfitting.

## Installation

Once released, you will be able to install `glmpynet` via pip:

pip install glmpynet

## Quick Start

Using `glmpynet` is designed to be as simple as using any other scikit-learn estimator.

    import numpy as np
    from glmpynet import LogisticNet
    from sklearn.model\_selection import train\_test\_split
    from sklearn.metrics import accuracy\_score

# 1. Generate synthetic data

    X, y = np.random.rand(100, 10), np.random.randint(0, 2, 100)
    X\_train, X\_test, y\_train, y\_test = train\_test\_split(X, y)

# 2. Instantiate and fit the model

    # alpha=1 -\> Lasso, alpha=0 -\> Ridge, 0 \< alpha \< 1 -\> Elastic-Net

    model = LogisticNet(alpha=0.5)
    model.fit(X\_train, y\_train)

# 3. Make predictions

    y\_pred = model.predict(X\_test)

# 4. Evaluate the model

    accuracy = accuracy\_score(y\_test, y\_pred)
    print(f"Model Accuracy: {accuracy:.2f}")


## Project Status

This project is currently in the planning and development phase. The goal is to provide a simple, robust, and well-tested wrapper for the core binary classification functionality of `glmnet`.

## Contributing

Contributions are welcome! Please see the `CONTRIBUTING.md` file for guidelines on how to report bugs, suggest features, or submit pull requests.

## License

This project is distributed under the MIT License.
```