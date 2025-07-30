import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.utils import Tags, check_X_y
from sklearn.utils.validation import check_is_fitted

class CustomMeanClassifier(BaseEstimator, ClassifierMixin):
    """
    A custom classifier that predicts the most frequent class in the training data.
    """
    def __init__(self):
        # Parameters should be stored as attributes with the same name.
        pass

    def fit(self, X, y):
        """
        Fits the classifier to the training data.
        """
        # Perform validation on X and y
        X, y = check_X_y(X, y)

        # Manually compute the most frequent class
        unique_classes, counts = np.unique(y, return_counts=True)
        self.most_frequent_ = unique_classes[np.argmax(counts)]

        self.is_fitted_ = True  # Set the fitted status
        self.n_features_in_ = X.shape[1] # Store number of features

        return self

    def predict(self, X):
        """
        Makes predictions based on the fitted classifier.
        """
        # Ensure the estimator is fitted before predicting
        check_is_fitted(self, 'is_fitted_')

        # Predict the most frequent class for all instances
        return np.full(shape=(X.shape[0],), fill_value=self.most_frequent_)

    def __sklearn_tags__(self):
        """
        Define estimator tags for capabilities and type.
        """
        return Tags(
            estimator_type="classifier",  # Indicate it's a classifier
            target_tags=y
            # Specify it requires a target variable (y) for fitting
            # Add other relevant tags as needed
            # sparse_input=False,
            # non_deterministic=False,
        )

# Example Usage:
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

# Load the Iris dataset
iris = load_iris()
X, y = iris.data, iris.target

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

# Create an instance of the custom estimator
custom_classifier = CustomMeanClassifier()

# Fit the classifier
custom_classifier.fit(X_train, y_train)

# Make predictions
predictions = custom_classifier.predict(X_test)

# You can also get the tags programmatically
from sklearn.utils import get_tags
tags = get_tags(custom_classifier)
print(tags)

