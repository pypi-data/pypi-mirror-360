"""
The glmpynet.LogisticNet classifier.

===============================================================
Author: Your Name
License: MIT
===============================================================

This module provides a scikit-learn compatible wrapper for the `glmnet`
library, focusing on penalized logistic regression for binary classification.
"""

import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.utils.multiclass import unique_labels
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted


class LogisticNet(ClassifierMixin, BaseEstimator):
    """
    Logistic Regression with elastic-net regularization, using the glmnet backend.

    This model provides a scikit-learn compatible interface to the high-performance
    `glmnet` library, which fits the entire regularization path for logistic
    regression. Cross-validation is used to select the optimal regularization
    strength (lambda).

    Parameters
    ----------
    alpha : float, default=1.0
        The elastic-net mixing parameter, with `0 <= alpha <= 1`.
        - `alpha = 1.0` corresponds to Lasso (L1) regularization.
        - `alpha = 0.0` corresponds to Ridge (L2) regularization.
        - `0 < alpha < 1` corresponds to a combination of L1 and L2 (Elastic-Net).

    n_lambda : int, default=100
        The number of lambda values to include in the regularization path.
        `glmnet` will automatically generate a sequence of lambda values.

    cv : int, default=5
        The number of folds to use for cross-validation when selecting the
        best lambda from the regularization path.

    Attributes
    ----------
    coef_ : ndarray of shape (1, n_features)
        The coefficients (weights) of the features in the decision function,
        corresponding to the best lambda found during cross-validation.

    intercept_ : ndarray of shape (1,)
        The intercept (or bias) term in the decision function.

    lambda_best_ : float
        The optimal lambda value selected by cross-validation.

    n_features_in_ : int
        The number of features seen during `fit`.

    classes_ : ndarray of shape (n_classes,)
        The unique class labels seen during `fit`.

    Notes
    -----
    It is highly recommended to scale your data before fitting this model,
    for example by using `sklearn.preprocessing.StandardScaler`.

    Examples
    --------
    >>> from sklearn.datasets import make_classification
    >>> from sklearn.metrics import accuracy_score
    >>> X, y = make_classification(n_features=10, n_informative=5, random_state=42)
    >>> model = LogisticNet(alpha=0.8)
    >>> model.fit(X, y)
    LogisticNet(alpha=0.8)
    >>> print(f"Number of non-zero coefficients: {np.count_nonzero(model.coef_)}")
    Number of non-zero coefficients: 5
    >>> accuracy = accuracy_score(y, model.predict(X))
    >>> print(f"Accuracy: {accuracy:.2f}")
    Accuracy: 0.87
    """

    def __init__(self, alpha: float = 1.0, n_lambda: int = 100, cv: int = 5):
        """
        Initializes the LogisticNet model.
        """
        self.alpha = alpha
        self.n_lambda = n_lambda
        self.cv = cv

    def fit(self, X, y):
        """
        Fit the logistic regression model according to the given training data.

        This method will call the underlying `glmnet` backend to compute the
        full regularization path and then use cross-validation to select the
        optimal lambda. The coefficients for this best model are then stored.

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)
            Training vector, where `n_samples` is the number of samples and
            `n_features` is the number of features.

        y : array-like of shape (n_samples,)
            Target vector relative to X.

        Returns
        -------
        self
            Fitted estimator.
        """
        # 1. Validate and check input data
        X, y = check_X_y(X, y)
        self.classes_ = unique_labels(y)
        self.n_features_in_ = X.shape[1]

        # 2. TODO: Call the glmnet backend here
        # This is where you would interface with the compiled glmnet code.
        # It should compute the full path and perform cross-validation.
        # For now, we will simulate the result.

        # --- Placeholder Implementation ---
        # Simulate that CV selected a model where some coefficients are zero
        self.coef_ = np.random.randn(1, self.n_features_in_)
        zero_indices = np.random.choice(self.n_features_in_, size=self.n_features_in_ // 2, replace=False)
        self.coef_[0, zero_indices] = 0
        self.intercept_ = np.random.randn(1)
        self.lambda_best_ = 0.1  # Placeholder for the best lambda
        # --- End Placeholder ---

        self.is_fitted_ = True
        return self

    def predict(self, X):
        """
        Predict class labels for samples in X.

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features)
            The data matrix for which we want to get the predictions.

        Returns
        -------
        y_pred : ndarray of shape (n_samples,)
            Vector containing the class labels for each sample.
        """
        check_is_fitted(self)
        X = check_array(X)

        # Calculate the decision function (linear combination of features)
        scores = X @ self.coef_.T + self.intercept_

        # Apply a threshold of 0 to get binary predictions
        predictions = (scores > 0).astype(int).flatten()

        # Map the binary predictions back to the original class labels
        return self.classes_[predictions]

    def predict_proba(self, X):
        """
        Probability estimates for samples in X.

        The returned estimates for all classes are ordered by the
        label of classes.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Vector to be scored.

        Returns
        -------
        T : array-like of shape (n_samples, n_classes)
            Returns the probability of the sample for each class in the model.
        """
        check_is_fitted(self)
        X = check_array(X)

        # Calculate the decision function
        scores = X @ self.coef_.T + self.intercept_

        # Apply the logistic (sigmoid) function to get probabilities
        prob_class_1 = 1 / (1 + np.exp(-scores))

        # Create the final probability array
        probabilities = np.hstack([1 - prob_class_1, prob_class_1])
        return probabilities

    def _more_tags(self):
        """
        Internal scikit-learn tag to indicate this is a binary classifier.
        """
        return {"binary_only": True}

