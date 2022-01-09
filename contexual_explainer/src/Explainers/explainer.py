import shap
import dice_ml
from dice_ml.utils import helpers  # helper functions
from nice.explainers import NICE
from tabulate import tabulate


def shap_explain(ds, clf, X):
    """

    :param ds:
    :param clf:
    :param X:
    """
    explainer = shap.TreeExplainer(clf)
    shap_values = explainer.shap_values(X)
    class_names = ds['machine_status'].unique()
    bar_plot = shap.summary_plot(shap_values, X, plot_type="bar", class_names=class_names,
                                 feature_names=ds.iloc[:, 1:-1].columns)
    shap.summary_plot(shap_values[1], X, feature_names=ds.iloc[:, 1:-1].columns)


def dice_explain(clf, ds, query_instance):
    """

    :param clf:
    :param ds:
    :param query_instance:
    """
    # d = dice_ml.Data(dataframe=ds,
    #                  continuous_features=['sensor_44', 'sensor_45', 'sensor_46', 'sensor_47',
    #                                       'sensor_48', 'sensor_49', 'sensor_50', 'sensor_51'],
    #                  outcome_name='machine_status')
    d = dice_ml.Data(dataframe=helpers.load_adult_income_dataset(),
                     continuous_features=['age', 'hours_per_week'],
                     outcome_name='income')
    m = dice_ml.Model(model_path=dice_ml.utils.helpers.get_adult_income_modelpath())
    exp = dice_ml.Dice(d, m)
    query_instance = {'age': 22,
                      'workclass': 'Private',
                      'education': 'HS-grad',
                      'marital_status': 'Single',
                      'occupation': 'Service',
                      'race': 'White',
                      'gender': 'Female',
                      'hours_per_week': 45}
    dice_exp = exp.generate_counterfactuals(query_instance, total_CFs=4, desired_class="opposite")
    dice_exp.visualize_as_dataframe()
    dice_exp.cf_examples_list[0].final_cfs_df.to_csv(path_or_buf='counterfactuals.csv', index=False)


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
    NICE_explainer = NICE(optimization='sparsity',
                          justified_cf=True)
    NICE_explainer.fit(predict_fn, X_train, cat_feat, num_feat, y_train)
    cf = NICE_explainer.explain(query_instance)
    return cf


def visualize_explanation(clf, cf, query_instance):
    """

    :param clf:
    :param cf:
    :param query_instance:
    """
    features = ['age', 'workclass', 'education', 'marital-status', 'occupation', 'relationship', 'race', 'sex',
                'capital-gain', 'capital-loss', 'hours-per-week']

    print("Model Decision:", clf.predict(query_instance))

    print("Query Instance: \n {}".format(
        tabulate(query_instance, headers=features, tablefmt='fancy_grid', missingval='N/A')))

    print("Counterfactual tagret class:", clf.predict(cf))

    print("Counterfactuals: \n {}".format(tabulate(cf, headers=features, tablefmt='fancy_grid', missingval='N/A')))
