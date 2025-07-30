"""
This module contains the LogisticNet class, a scikit-learn compatible wrapper
for penalized logistic regression.
"""

from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.linear_model import LogisticRegression
from sklearn.utils.multiclass import unique_labels
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted


# noinspection PyAttributeOutsideInit
class LogisticNet(ClassifierMixin, BaseEstimator):
    """
    A scikit-learn compatible estimator for penalized logistic regression.

    This class provides a user-friendly interface that mirrors the API of
    scikit-learn's `LogisticRegression`, but is designed to be powered by the
    high-performance glmnet library in its final implementation.

    For initial development and testing, it wraps scikit-learn's
    `LogisticRegression` to provide a functional baseline.

    Parameters
    ----------
    C : float, default=1.0
        Inverse of regularization strength; must be a positive float.
    penalty : {'l1', 'l2'}, default='l2'
        Regularization type.

    Attributes
    ----------
    coef_ : ndarray of shape (1, n_features)
        The coefficients (weights) of the features in the decision function.
    intercept_ : ndarray of shape (1,)
        The intercept (or bias) term in the decision function.
    classes_ : ndarray of shape (n_classes,)
        The unique class labels seen during `fit`.
    n_features_in_ : int
        The number of features seen during `fit`.
    is_fitted_ : bool
        A boolean indicating that the estimator has been fitted.
    _estimator : LogisticRegression
        Internal LogisticRegression instance for the facade.

    Examples
    --------
    >>> from sklearn.datasets import make_classification
    >>> from sklearn.metrics import accuracy_score
    >>> X, y = make_classification(n_features=10, n_informative=5, random_state=42)
    >>> model = LogisticNet()
    >>> model.fit(X, y)
    LogisticNet()
    >>> accuracy = accuracy_score(y, model.predict(X))
    >>> print(f"Accuracy: {accuracy:.2f}")
    Accuracy: 0.87
    """

    def __init__(self, C: float = 1.0, penalty: str = "l2"):
        """
        Initializes the LogisticNet model.
        """
        self.C = C
        self.penalty = penalty
        self._estimator = LogisticRegression(
            C=self.C,
            penalty=self.penalty,
            solver="liblinear"
        )

    def fit(self, X, y):
        """
        Fit the logistic regression model according to the given training data.

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
        X, y = check_X_y(X, y, accept_sparse=True)
        self.classes_ = unique_labels(y)
        self.n_features_in_ = X.shape[1]
        self._estimator.fit(X, y)
        self.coef_ = self._estimator.coef_
        self.intercept_ = self._estimator.intercept_
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
        check_is_fitted(self, ["coef_", "intercept_", "is_fitted_"])
        X = check_array(X, accept_sparse=True)
        return self._estimator.predict(X)

    def predict_proba(self, X):
        """
        Probability estimates for samples in X.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Vector to be scored.

        Returns
        -------
        T : array-like of shape (n_samples, n_classes)
            Returns the probability of the sample for each class in the model.
        """
        check_is_fitted(self, ["coef_", "intercept_", "is_fitted_"])
        X = check_array(X, accept_sparse=True)
        return self._estimator.predict_proba(X)

    def get_params(self, deep=True):
        """
        Get parameters for this estimator.

        Parameters
        ----------
        deep : bool, default=True
            If True, will return the parameters for this estimator and
            contained subobjects that are estimators.

        Returns
        -------
        params : dict
            Parameter names mapped to their values.
        """
        # Get base parameters from LogisticRegression, subset to C and penalty
        params = {"C": self.C, "penalty": self.penalty}
        return params

    def set_params(self, **params):
        """
        Set the parameters of this estimator.

        Parameters
        ----------
        **params : dict
            Estimator parameters.

        Returns
        -------
        self
            Estimator instance.
        """
        # Update LogisticNet parameters
        super().set_params(**params)
        # Filter parameters for LogisticRegression
        estimator_params = {k: v for k, v in params.items() if k in ["C", "penalty"]}
        self._estimator.set_params(**estimator_params)
        return self

    def __sklearn_tags__(self):
        """
        Define estimator tags for capabilities and type.
        """
        # Use LogisticRegression's tags directly
        return LogisticRegression().__sklearn_tags__()
