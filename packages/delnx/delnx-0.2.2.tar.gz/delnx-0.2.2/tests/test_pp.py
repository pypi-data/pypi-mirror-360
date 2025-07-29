import pytest


def test_pseudobulk(adata):
    """Test pseudobulk aggregation."""
    import numpy as np

    import delnx

    # Test basic pseudobulk aggregation
    adata_pb = delnx.pp.pseudobulk(adata, sample_key="condition_sample", group_key="cell_type", layer="counts")
    assert adata_pb.n_obs < adata.n_obs  # Should have fewer observations
    assert adata_pb.n_vars == adata.n_vars  # Should have same number of variables
    assert "condition_sample" in adata_pb.obs.columns
    assert "cell_type" in adata_pb.obs.columns
    assert "condition" in adata_pb.obs.columns
    assert "sample" in adata_pb.obs.columns

    # Test with different aggregation mode
    adata_pb_mean = delnx.pp.pseudobulk(adata, sample_key="condition_sample", group_key="cell_type", mode="mean")
    assert not (adata_pb.X == adata_pb_mean.X).all()  # Should be different from sum

    # Test with count layer
    adata_pb_counts = delnx.pp.pseudobulk(adata, sample_key="condition_sample", group_key="cell_type", layer="counts")
    X_flat = adata_pb_counts.X.flatten()
    assert adata_pb_counts.n_obs == adata_pb.n_obs
    assert X_flat.max() > 1000
    assert np.all(np.equal(np.mod(X_flat, 1), 0))
    assert np.all(X_flat >= 0)

    # Test with binary layer
    adata_pb_counts = delnx.pp.pseudobulk(
        adata, sample_key="condition_sample", group_key="cell_type", layer="binary", mode="mean"
    )
    X_flat = adata_pb_counts.X.flatten()
    assert adata_pb_counts.n_obs == adata_pb.n_obs
    assert X_flat.max() <= 1
    assert X_flat.min() >= 0


@pytest.mark.parametrize("method", ["ratio", "quantile_regression", "library_size"])
def test_size_factors(adata_pb_counts, method):
    """Test size factor calculation."""
    import numpy as np

    import delnx

    # Test size factors calculation
    delnx.pp.size_factors(adata_pb_counts, method=method)

    # Check if size_factor column exists
    assert any(adata_pb_counts.obs.columns.str.startswith("size_factor"))

    # Check that size factors are positive and normalized over mean
    size_factor_col = adata_pb_counts.obs.columns[adata_pb_counts.obs.columns.str.startswith("size_factor")][0]
    size_factors = adata_pb_counts.obs[size_factor_col].values
    assert np.all(size_factors > 0)
    assert np.isclose(np.mean(size_factors), 1.0, atol=1e-5)


@pytest.mark.parametrize("size_factor_key", ["size_factors", None])
@pytest.mark.parametrize("method", ["full", "approx", "fast"])
def test_dispersion_estimation(adata_pb_counts, size_factor_key, method):
    """Test dispersion estimation."""
    import numpy as np

    import delnx

    # Test dispersion estimation
    delnx.pp.dispersion(adata_pb_counts, size_factor_key=size_factor_key, method=method)

    # Check if dispersion, dispersion_init, dispersion_mle, dispersion_trend, dispersion_map columns exist
    if method == "fast":
        dispersion_columns = ["dispersion_init", "dispersion"]
    elif method == "approx":
        dispersion_columns = ["dispersion_init", "dispersion_trend", "dispersion_map", "dispersion"]
    else:  # method == "full"
        dispersion_columns = [
            "dispersion_init",
            "dispersion_mle",
            "dispersion_trend",
            "dispersion_map",
            "dispersion",
        ]

    for col in dispersion_columns:
        assert any(adata_pb_counts.var.columns == col)

    # Check that dispersion values not NaN
    assert not np.any(np.isnan(adata_pb_counts.var["dispersion"]))

    # Check that dispersion values are non-negative
    assert np.all(adata_pb_counts.var["dispersion"] >= 0)

    # Check that dispersion is not constant across genes
    assert not np.all(adata_pb_counts.var["dispersion"] == adata_pb_counts.var["dispersion"].iloc[0])
