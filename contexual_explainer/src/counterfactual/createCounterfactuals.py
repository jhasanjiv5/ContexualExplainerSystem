from src.SurrogateModels import classifier


def find_counterfactuals(instance):
    clf = classifier.train_model()
    clf.predict(instance)

    # The first term is the quadratic distance between the model prediction for the counterfactual x’
    # and the desired outcome y’, which the user must define in advance.

