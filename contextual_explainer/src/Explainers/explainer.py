import shap
import dice_ml
from dice_ml.utils import helpers  # helper functions
from nice import NICE
from tabulate import tabulate


def shap_explain(ds, clf, X, class_name):
    """

    :param ds:
    :param clf:
    :param X:
    """
    explainer = shap.TreeExplainer(clf)
    shap_values = explainer.shap_values(X)
    class_names = ds[class_name].unique()
    bar_plot = shap.summary_plot(shap_values, X, plot_type="bar", class_names=class_names,
                                 feature_names=ds.iloc[:, 1:-1].columns)
    shap.summary_plot(shap_values[1], X, feature_names=ds.iloc[:, 1:-1].columns)


def dice_explain(clf, ds, query_instance, features, class_name):
    """

    :param clf:
    :param ds:
    :param query_instance:
    """
    d = dice_ml.Data(dataframe=ds,
                     continuous_features=features,
                     outcome_name=class_name)
    m = dice_ml.Model(model=clf, backend='sklearn')
    exp = dice_ml.Dice(d, m, method="random")
    dice_exp = exp.generate_counterfactuals(query_instance, total_CFs=4, desired_class="opposite",
                                            features_to_vary=features)
    #dice_exp.visualize_as_dataframe()
    #dice_exp.cf_examples_list[0].final_cfs_df.to_csv(path_or_buf='counterfactuals.csv', index=False)
    return dice_exp.cf_examples_list[0].final_cfs_df

def nice_explain(predict_fn, X_train, cat_feat, num_feat, y_train, query_instance):
    """

    :param predict_fn:
    :param X_train:
    :param cat_feat:
    :param num_feat:
    :param y_train:
    :param query_instance:
    :return:
    """
    NICE_explainer = NICE(predict_fn,
                          X_train,
                          cat_feat,
                          num_feat,
                          y_train,
                          optimization='sparsity',
                          justified_cf=True,
                          distance_metric='HEOM',
                          num_normalization='minmax',
                          auto_encoder=None)
    # NICE_explainer.fit(predict_fn, X_train, cat_feat, num_feat, y_train)
    cf = NICE_explainer.explain(query_instance)
    return cf


'''def visualize_explanation(clf, cf, query_instance, feature_names):
    """

    :param clf:
    :param cf:
    :param query_instance:
    """
    features = feature_names

    print("Model Decision:", clf.predict(query_instance))

    print("Query Instance: \n {}".format(
        tabulate(query_instance, headers=features, tablefmt='pretty', missingval='N/A')))

    print("Counterfactual tagret class:", clf.predict(cf))

    print("Counterfactuals: \n {}".format(tabulate(cf, headers=features, tablefmt='pretty', missingval='N/A')))
'''
