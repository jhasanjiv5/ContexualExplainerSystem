import pytest

from src.DiscoverEnvironment import collectLogs, discover
from src.Explainers import explainer
from src.SurrogateModels import classifier
from src.TimeSyncAndCorrelation import correlate


def test_get_context_logs():
    with pytest.raises(Exception) as e_info:
        collectLogs.get_context_logs(['co2'])
    assert collectLogs.get_context_logs().size > 0


def test_discover_context():
    with pytest.raises(Exception) as e_info:
        discover.discover_context()
    assert discover.discover_context()


def test_shap_explain():
    with pytest.raises(Exception) as e_info:
        explainer.shap_explain(ds, clf, X)
    assert explainer.shap_explain(ds, clf, X)


def test_nice_explain():
    with pytest.raises(Exception) as e_info:
        explainer.nice_explain(predicr_fn, X_train, cat_feat, num_feat, y_train, query_instance)
    assert explainer.nice_explain(predicr_fn, X_train, cat_feat, num_feat, y_train, query_instance)


def test_train_model():
    with pytest.raises(Exception) as e_info:
        classifier.train_model()
    assert classifier.train_model()


def test_predict_ir():
    with pytest.raises(Exception) as e_info:
        classifier.predict_ir()
    assert classifier.predict_ir()


def test_check_for_correlation():
    with pytest.raises(Exception) as e_info:
        correlate.check_for_correlation(dfs)
    assert correlate.check_for_correlation(dfs)

