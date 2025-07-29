import lpmalgos as algorithms
import plotly
import plotly.graph_objects as go
import numpy as np
import math


def plot_variogram_cloud(
    target_dir,
    variograms,
    variogram_model=None,
    ref_variograms=None,
    nsteps=100,
    prefix="",
    fig=None,
    sim_color="green",
):
    if fig is None:
        fig = go.Figure()

    for sim_id, exp_vars in enumerate(variograms):
        variogram = exp_vars.get_variogram(target_dir)
        fig.add_scatter(
            x=[np.linalg.norm(h) for h in variogram[0]],
            y=variogram[1],
            mode="markers",
            name=f"{prefix}  {sim_id + 1}",
            marker_color=sim_color,
        )

    if ref_variograms is not None:
        for sim_id, exp_vars in enumerate(ref_variograms):
            variogram = exp_vars.get_variogram(target_dir)
            fig.add_scatter(
                x=[np.linalg.norm(h) for h in variogram[0]],
                y=variogram[1],
                mode="markers",
                name=f"{prefix} ref variogram {sim_id + 1}",
                marker_color="red",
            )

    if variogram_model is not None:
        hs = [i * target_dir / float(nsteps) for i in range(2, nsteps)]
        fig.add_scatter(
            x=[np.linalg.norm(h) for h in hs],
            y=[variogram_model(h) for h in hs],
            mode="lines",
            marker_color="red",
            name=f"{prefix} reference_model",
        )
    return fig


def plot_scatter_3d(
    locs, values, fig=None, colorscale="Viridis", opacity=0.8, size=2, max_size=50000
):
    if len(locs) > max_size:
        idx = np.random.choice([i for i in range(len(locs))], max_size)
        return plot_scatter_3d(
            np.array(locs)[idx],
            np.array(values)[idx],
            fig=fig,
            colorscale=colorscale,
            opacity=opacity,
            size=size,
            max_size=max_size,
        )

    if fig is None:
        fig = go.Figure()

    fig.add_scatter3d(
        x=[l[0] for l in locs],
        y=[l[1] for l in locs],
        z=[l[2] for l in locs],
        mode="markers",
        marker=dict(
            size=size,
            color=values,  # set color to an array/list of desired values
            colorscale=colorscale,  # choose a colorscale
            opacity=opacity,
        ),
    )
    fig.update_layout(showlegend=False)
    return fig


def plot_variograms(
    cov_ani,
    simulation_variograms,
    variogram_model=None,
    ref_variograms=None,
    prefix="Simulation",
    fig=None,
    nsteps=100,
    show_minor=True,
    show_mid=True,
    show_major=True,
):
    major_dir = cov_ani.major_axis()
    mid_dir = cov_ani.mid_axis()
    minor_dir = cov_ani.minor_axis()
    if show_minor:
        fig = plot_variogram_cloud(
            1.1 * minor_dir,
            simulation_variograms,
            variogram_model=variogram_model,
            ref_variograms=ref_variograms,
            prefix=f"{prefix} minor direction",
            sim_color="blue",
            fig=fig,
            nsteps=nsteps,
        )
    if show_mid:
        fig = plot_variogram_cloud(
            1.1 * mid_dir,
            simulation_variograms,
            variogram_model=variogram_model,
            ref_variograms=ref_variograms,
            prefix=f"{prefix} mid direction",
            sim_color="yellow",
            fig=fig,
            nsteps=nsteps,
        )
    if show_major:
        fig = plot_variogram_cloud(
            1.1 * major_dir,
            simulation_variograms,
            variogram_model=variogram_model,
            ref_variograms=ref_variograms,
            prefix=f"{prefix} major direction",
            sim_color="green",
            fig=fig,
            nsteps=nsteps,
        )
    fig.update_layout(
        showlegend=False,
        xaxis=dict(title="h"),
        yaxis=dict(title="γ(h)"),
        title=f"{prefix} variograms",
    )
    return fig


def plot_line(
    x,
    y,
    fig=None,
    colorscale="Viridis",
    opacity=0.8,
    size=2,
    max_size=50000,
    name="data",
    mode="lines",
    marker_color="red",
    line_color="red",
):
    if fig is None:
        fig = go.Figure()
    fig.add_scatter(
        x=x, y=y, mode=mode, marker_color=marker_color, line_color=line_color, name=name
    )
    return fig


def plot_cdf(
    cdf,
    N=1000,
    fig=None,
    colorscale="Viridis",
    opacity=0.8,
    size=2,
    max_size=50000,
    name="CDF",
    mode="lines",
    marker_color="red",
    line_color="red",
):
    y = [(i + 1) / N for i in range(N - 2)]
    x = cdf.values(y)
    return plot_line(
        **{key: value for key, value in locals().items() if key != "cdf" and key != "N"}
    )


def plot_pdf(
    pdf,
    dv=0.05,
    fig=None,
    colorscale="Viridis",
    opacity=0.8,
    size=2,
    max_size=50000,
    name="PDF",
    mode="lines",
    marker_color="red",
    line_color="red",
):
    min_v, max_v = (pdf.min(), pdf.max())
    N = int((max_v - min_v) / dv)
    x = [min_v + (i + 2) * dv for i in range(N - 3)]
    y = pdf.probs(x, dv=dv)
    return plot_line(
        **{
            key: value
            for key, value in locals().items()
            if key != "pdf"
            and key != "N"
            and key != "dv"
            and key != "min_v"
            and key != "max_v"
            and key != "N"
        }
    )


def serialize_cov(cov):
    infos = [algorithms.extract_ellipsoid_info(c.ellipsoid().matrix()) for c in cov]

    j = {"nugget": 0.0, "model": []}
    for c, info in zip(cov, infos):
        if c.type() == "nugget":
            j["nugget"] += c.sill()
        else:
            j["model"].append(
                {
                    "model": c.type(),
                    "sill": c.sill(),
                    "r1": info.r1(),
                    "r2": info.r2(),
                    "r3": info.r3(),
                    "azimuth": info.azimuth(),
                    "dip": info.dip(),
                    "rake": info.rake(),
                }
            )
    return j


def unserialize_cov(j):
    models = dict(
        spherical=algorithms.Covariance.spherical,
        gaussian=algorithms.Covariance.gaussian,
        exponential=algorithms.Covariance.exponential,
    )

    cov = []
    if j["nugget"] > 0:
        cov.append(algorithms.Covariance.nugget(j["nugget"]))
    for c in j["model"]:
        ellipsoid = algorithms.Ellipsoid(
            c["r1"], c["r2"], c["r3"], c["azimuth"], c["dip"], c["rake"]
        )
        sill = c["sill"]
        cov.append(models[c["model"]](sill, ellipsoid))
    return cov


DEFAULT_KFOLD_ERROR_PARAMETERS = dict(
    min_partition_size=10, max_partition_size=40, n_partition_size=15, seed=123451
)


def kfold_error_idw(
    data_locs,
    data,
    cov,
    max_distance,
    max_size=300,
    return_full_error=False,
    power_a=3,
    n_threads=0,
    kfold_parameters=DEFAULT_KFOLD_ERROR_PARAMETERS,
):
    errors = algorithms.kfold_cross_validation_using_idw(
        data_locs=data_locs,
        data_values=data,
        covs=cov,
        max_distance=max_distance,
        max_size=max_size,
        power_a=power_a,
        n_threads=n_threads,
        **kfold_parameters,
    )
    e = [np.median(np.abs(e)) for e in errors]
    if return_full_error:
        return np.median(e), e, errors
    return np.median(e), e


def kfold_error_sk(
    data_locs,
    data,
    cov,
    max_distance,
    max_size=300,
    return_full_error=False,
    n_threads=0,
    kfold_parameters=DEFAULT_KFOLD_ERROR_PARAMETERS,
):
    errors = algorithms.kfold_cross_validation_using_sk(
        data_locs=data_locs,
        data_values=data,
        covs=cov,
        max_distance=max_distance,
        max_size=max_size,
        n_threads=n_threads,
        **kfold_parameters,
    )
    e = [np.median(np.abs(e)) for e in errors]
    if return_full_error:
        return np.median(e), e, errors
    return np.median(e), e


def kfold_error_ok(
    data_locs,
    data,
    cov,
    max_distance,
    max_size=300,
    return_full_error=False,
    n_threads=0,
    kfold_parameters=DEFAULT_KFOLD_ERROR_PARAMETERS,
):
    errors = algorithms.kfold_cross_validation_using_ok(
        data_locs=data_locs,
        data_values=data,
        covs=cov,
        max_distance=max_distance,
        max_size=max_size,
        n_threads=n_threads,
        **kfold_parameters,
    )
    e = [np.median(np.abs(e)) for e in errors]
    if return_full_error:
        return np.median(e), e, errors
    return np.median(e), e


def create_bounding_box(data_locs, n_rays=300, seed=1231, n_threads=0):
    corners = algorithms.extreme_points(
        data_locs, n_rays=n_rays, seed=seed, n_threads=n_threads
    )
    return algorithms.BoundingBox(corners)


def create_data(
    r1,
    r2,
    r3,
    azimuth,
    dip,
    rake,
    n_drillholes=150,
    nugget=0.02,
    use_tbsim=True,
    min_length=0.3,
    max_length=0.7,
    n_sim=10,
    seed=12315,
    factor=2.5,
):
    import time

    target_anisotropy = algorithms.Ellipsoid(r1, r2, r3, azimuth, dip, rake)
    target_cov = [
        algorithms.Covariance.nugget(nugget),
        algorithms.Covariance.spherical(1 - nugget, target_anisotropy),
    ]

    max_r = factor * max([r1, r2, r3])

    dh_deformation = algorithms.Ellipsoid(1, 1, 1, 0, 0, 0)

    data_locs, dhids = algorithms.create_random_drillholes(
        l1=max_r,
        l2=max_r,
        n_drillholes=n_drillholes,
        min_azimuth=0,
        max_azimuth=360,
        min_dip=-90 - 45,
        max_dip=-90 + 45,
        min_length=min_length * max_r,
        max_length=max_length * max_r,
        min_dist_to_bottom=10,
        max_dist_to_bottom=120,
        min_n_samples_by_dh=220,
        max_n_samples_by_dh=320,
        deformation=dh_deformation,
        seed=seed,
    )

    corners = algorithms.extreme_points(data_locs, n_rays=300, seed=1231, n_threads=0)
    bbox = algorithms.BoundingBox(corners)
    target_corners = bbox.corners()

    data_values = []
    np.random.seed(seed)
    st = time.time()
    for i in range(n_sim):
        if use_tbsim:
            tbsim = algorithms.TBSIM(
                corners=target_corners,
                covs=target_cov,
                seed=np.random.randint(11_111_111, 99_999_999),
                n=800,
            )
            data_values.append(tbsim.simulate(data_locs))
        else:
            fim = algorithms.FIM(
                corners=target_corners,
                covs=target_cov,
                seed=np.random.randint(11_111_111, 99_999_999),
                n=200,
            )
            data_values.append(fim.simulate(data_locs))
    dt = time.time() - st
    print(f"sim dt:{dt}")

    return data_locs, data_values, dhids, target_cov, target_anisotropy


DEFAULT_ELLIPSOID_OPTIMIZATION_IDW_PARAMETERS = dict(
    power_a=3.0,
    max_nei_size=400,
    min_partition_size=15,
    max_partition_size=25,
    n_partitions=4,
    n_centers=10,
    tol=0.002,
    seed=1231,
)


def optimize_ellipsoid_using_lbfgs(
    data_locs,
    data,
    cov_type="spherical",
    length_weigth=1.25,
    regularization_const=1.0,
    cauchy_loss=0.0,
    n_partitions=15,
    min_partition_size=15,
    max_partition_size=40,
    max_nei_size=1000,
    n_centers=51,
    n_iterations=1000,
    n_rays=300,
    seed=121351,
    n_threads=0,
    debug=False,
    folds=None,
):
    corners = algorithms.extreme_points(
        data_locs, n_rays=n_rays, seed=seed, n_threads=n_threads
    )

    bbox = algorithms.BoundingBox(corners)
    length = bbox.length()
    max_r = np.linalg.norm(length)
    if folds is None:
        folds = algorithms.create_folds(
            data_locs,
            data,
            max_distance=length_weigth * max_r,
            max_size=max_nei_size,
            n_centers=n_centers,
            seed=seed,
        )

    return algorithms.optimize_ellipsoid_using_kfold(
        folds=folds,
        cov_type=cov_type,
        r1_max=length_weigth * max_r,
        r2_max=length_weigth * max_r,
        r3_max=length_weigth * max_r,
        regularization_const=regularization_const * n_partitions * len(folds),
        cauchy_loss=cauchy_loss,
        min_partition_size=min_partition_size,
        max_partition_size=max_partition_size,
        n_partitions=n_partitions,
        n_iterations=n_iterations,
        seed=seed,
        n_threads=n_threads,
        debug=debug,
    )


def optimize_ellipsoid(
    data_locs,
    data,
    min_range=0.1,
    max_range=1,
    cov_kernel=None,
    n_ellipsoids=400,
    n_scales=8,
    n_iterations=150,
    n_iterations_without_upgrade=50,
    debug=False,
    regularization_const=0.025,
    n_threads=-1,
    opt_parameters=DEFAULT_ELLIPSOID_OPTIMIZATION_IDW_PARAMETERS,
):
    data = (data - np.nanmean(data)) / np.nanstd(data)
    if cov_kernel is None:
        cov_kernel = algorithms.Kernel.spherical

    corners = algorithms.extreme_points(data_locs, n_rays=300, seed=1231, n_threads=0)
    bbox = algorithms.BoundingBox(corners)
    length = bbox.length()

    vol = (
        math.log(1 + length[0])
        + math.log(1 + length[1])
        + math.log(1 + length[2])
        + 1e-6
    )

    max_range = max_range * np.linalg.norm(length)
    min_range = min_range * np.linalg.norm(length)
    return algorithms.optimize_ellipsoid_using_idw(
        data_locs=data_locs,
        data=data,
        cov_kernel=cov_kernel,
        min_range=min_range,
        max_range=max_range,
        max_distance=max_range,
        n_rays=n_ellipsoids,
        n_scales=n_scales,
        n_iterations=n_iterations,
        n_iterations_without_upgrade=n_iterations_without_upgrade,
        debug=debug,
        regularization_const=regularization_const / vol,
        n_threads=n_threads,
        **opt_parameters,
    )


def optimize_covariance(
    data_locs,
    data,
    ellipsoid=None,
    n_kernels=1,
    min_range=0.1,
    max_range=1,
    cov_kernel=None,
    n_ellipsoids=400,
    n_covs=8000,
    n_scales=8,
    n_iterations=150,
    n_iterations_without_upgrade=50,
    debug=False,
    delta_angle=10,
    min_str_range=0.1,
    max_str_range=1.3,
    min_sill=0.001,
    max_sill=1,
    regularization_const=0.015,
    n_threads=-1,
    opt_parameters=DEFAULT_ELLIPSOID_OPTIMIZATION_IDW_PARAMETERS,
):
    data = (data - np.nanmean(data)) / np.nanstd(data)

    if ellipsoid is None:
        ellipsoid = optimize_ellipsoid(
            data_locs,
            data,
            min_range=min_range,
            max_range=max_range,
            cov_kernel=cov_kernel,
            n_ellipsoids=n_ellipsoids,
            n_scales=n_scales,
            debug=debug,
            n_iterations=n_iterations,
            n_iterations_without_upgrade=n_iterations_without_upgrade,
            regularization_const=regularization_const,
            n_threads=n_threads,
            opt_parameters=opt_parameters,
        )[0]
    if cov_kernel is None:
        cov_kernel = algorithms.Kernel.spherical
    corners = algorithms.extreme_points(data_locs, n_rays=300, seed=1231, n_threads=0)
    bbox = algorithms.BoundingBox(corners)
    length = bbox.length()

    vol = (
        math.log(1 + length[0])
        + math.log(1 + length[1])
        + math.log(1 + length[2])
        + 1e-6
    )

    max_range = max_range * np.linalg.norm(length)
    min_range = min_range * np.linalg.norm(length)
    return algorithms.optimize_covariance_using_idw(
        data_locs=data_locs,
        data=data,
        ellipsoid=ellipsoid,
        n_kernels=n_kernels,
        n_covs=n_covs,
        delta_angle=delta_angle,
        min_str_range=min_str_range,
        max_str_range=max_str_range,
        min_sill=min_sill,
        max_sill=max_sill,
        cov_kernel=cov_kernel,
        min_range=min_range,
        max_range=max_range,
        max_distance=max_range,
        n_rays=n_ellipsoids,
        n_scales=n_scales,
        n_iterations=n_iterations,
        n_iterations_without_upgrade=n_iterations_without_upgrade,
        debug=debug,
        regularization_const=regularization_const / vol,
        n_threads=n_threads,
        **opt_parameters,
    )


def serialize_local_covs(local_covs):
    return {
        "centers": np.array(local_covs.centers).tolist(),
        "errors": np.array(local_covs.errors).tolist(),
        "covariances": [serialize_cov(c) for c in local_covs.covariances],
    }


def save_local_covs(local_covs, filename):
    import json

    with open(filename, "w") as out:
        out.write(json.dumps(serialize_local_covs(local_covs)))


def unserialize_local_covs(local_covs):
    return algorithms.LocalCovariances(
        centers=local_covs["centers"],
        errors=local_covs["errors"],
        covariances=[unserialize_cov(c) for c in local_covs["covariances"]],
    )


def load_local_covs(filename):
    import json

    with open(filename, "r") as infile:
        j = json.loads(infile.read())
        return unserialize_local_covs(j)


def local_covs_to_dict(local_covs):
    r1 = []
    r2 = []
    r3 = []

    azimuth = []
    dip = []
    rake = []

    center_x = []
    center_y = []
    center_z = []

    errors = []

    for cov, center, error in zip(
        local_covs.covariances, local_covs.centers, local_covs.errors
    ):
        cov_j = serialize_cov(cov)
        ellipsoid = cov_j["model"][0]
        r1.append(ellipsoid["r1"])
        r2.append(ellipsoid["r2"])
        r3.append(ellipsoid["r3"])
        azimuth.append(ellipsoid["azimuth"])
        dip.append(ellipsoid["dip"])
        rake.append(ellipsoid["rake"])
        center_x.append(center[0])
        center_y.append(center[1])
        center_z.append(center[2])
        errors.append(error)
    return {
        "r1": r1,
        "r2": r2,
        "r3": r3,
        "azimuth": azimuth,
        "dip": dip,
        "rake": rake,
        "errors": errors,
        "center_x": center_x,
        "center_y": center_y,
        "center_z": center_z,
    }


def save_local_covs_as_csv(local_covs, filename):
    import pandas as pd

    df = pd.DataFrame(local_covs_to_dict(local_covs))
    df.to_csv(filename)


def ensemble_model(r1, r2, r3, azimuth, dip, rake, operator=np.mean):
    return dict(
        r1=operator(r1),
        r2=operator(r2),
        r3=operator(r3),
        azimuth=operator(azimuth),
        dip=operator(dip),
        rake=operator(rake),
    )


def optimize_local_covs_using_lbfgs(
    data_locs,
    data,
    cov_type="spherical",
    n_centers=30,
    n_local_centers=30,
    center_max_distance=2.0,
    cluster_size=2.0,
    local_center_size=457,
    regularization_const=1.0,
    max_local_range=1.25,
    cauchy_loss=0,
    min_partition_size=15,
    max_partition_size=35,
    n_partitions=7,
    n_iterations=1000,
    seed=123151,
    n_threads=0,
    debug=True,
):
    corners = algorithms.extreme_points(
        data_locs, n_rays=300, seed=1231, n_threads=n_threads
    )
    bbox = algorithms.BoundingBox(corners)
    length = bbox.length()
    vol = (
        math.log(1 + length[0])
        + math.log(1 + length[1])
        + math.log(1 + length[2])
        + 1e-6
    )

    opt_parameters = algorithms.EllipsoidLBFGSParameters(
        regularization_const=regularization_const,
        cauchy_loss=cauchy_loss,
        min_partition_size=min_partition_size,
        max_partition_size=max_partition_size,
        n_partitions=n_partitions,
        n_iterations=n_iterations,
        seed=seed,
        n_threads=n_threads,
        debug=debug,
    )

    return algorithms.optimize_local_ellipsoids_using_lbfgs(
        data_locs,
        data,
        cov_type=cov_type,
        n_centers=n_centers,
        n_local_centers=n_local_centers,
        center_max_size=center_max_distance * n_centers / 15.0,
        center_size=int(cluster_size * len(data) / float(n_centers) * n_centers / 15.0),
        local_center_size=local_center_size,
        max_local_range=max_local_range * np.linalg.norm(length),
        ellipsoid_opt_params=opt_parameters,
    )


def optimize_local_covs(
    data_locs,
    data,
    cov_kernel=algorithms.Kernel.spherical,
    min_range=0.1,
    max_range=2.0,
    n_centers=20,
    center_max_distance=2.0,
    cluster_size=2.0,
    debug=True,
    regularization_const=0.2,
    n_threads=-1,
    opt_parameters=None,
):
    corners = algorithms.extreme_points(
        data_locs, n_rays=300, seed=1231, n_threads=n_threads
    )
    bbox = algorithms.BoundingBox(corners)
    length = bbox.length()
    vol = (
        math.log(1 + length[0])
        + math.log(1 + length[1])
        + math.log(1 + length[2])
        + 1e-6
    )

    if opt_parameters is None:
        opt_parameters = algorithms.EllipsoidOptimizationParameters(
            debug=debug,
            n_threads=n_threads,
            regularization_const=regularization_const / (vol) * n_centers / 15.0,
        )

    return algorithms.optimize_local_ellipsoids(
        data_locs,
        data,
        cov_kernel=cov_kernel,
        min_range=min_range,
        max_range=max_range,
        n_centers=n_centers,
        center_max_size=center_max_distance * n_centers / 15.0,
        center_size=int(cluster_size * len(data) / float(n_centers) * n_centers / 15.0),
        ellipsoid_opt_params=opt_parameters,
    )


def weighted_ensemble_model(r1, r2, r3, azimuth, dip, rake, errors, power_a=1):
    sum_inv_errors = sum(np.power(1.0 / np.array(errors), power_a))
    w = np.power(1.0 / np.array(errors), power_a) / sum_inv_errors
    return algorithms.ensemble_model(w, r1, r2, r3, azimuth, dip, rake)


def create_ellipsoid_pts(
    r1, r2, r3, azimuth, dip, rake, error=0, n_rays=300, center=np.zeros(3)
):
    ellipsoid = algorithms.Ellipsoid(r1, r2, r3, azimuth, dip, rake)
    rays = algorithms.generate_random_sphere(n_rays)
    locs = [ellipsoid.backward(p) + center for p in rays]
    return dict(locs=locs, error=[error for p in range(len(locs))])


def plot_ellipsoid(r1, r2, r3, azimuth, dip, rake, error=0, n_rays=300, fig=None):
    pts = create_ellipsoid_pts(r1, r2, r3, azimuth, dip, rake, error, n_rays)
    return plot_scatter_3d(pts["locs"], pts["error"], fig=fig)


def plot_local_covs(
    local_covs,
    target_ellipsoid=None,
    n_rays=200,
    fig=None,
    use_centers=False,
    colorscale="Viridis",
):
    local_covs_dict = local_covs_to_dict(local_covs)
    r1, r2, r3, azimuth, dip, rake = (
        local_covs_dict["r1"],
        local_covs_dict["r2"],
        local_covs_dict["r3"],
        local_covs_dict["azimuth"],
        local_covs_dict["dip"],
        local_covs_dict["rake"],
    )
    errors = local_covs_dict["errors"]

    if use_centers:
        centroid = np.mean(local_covs.centers, axis=0)
    else:
        centroid = np.zeros(3)

    if target_ellipsoid is not None:
        pts = create_ellipsoid_pts(
            **target_ellipsoid, n_rays=n_rays, error=0, center=centroid
        )
        locs, error = (pts["locs"], pts["error"])
    else:
        locs, error = ([], [])

    for i in range(len(r1)):
        pts = create_ellipsoid_pts(
            r1[i],
            r2[i],
            r3[i],
            azimuth[i],
            dip[i],
            rake[i],
            errors[i],
            n_rays=300,
            center=local_covs.centers[i] if use_centers else centroid,
        )
        locs.extend(pts["locs"])
        error.extend(pts["error"])
    return plot_scatter_3d(locs, error, fig=fig, colorscale=colorscale)


def save_variogram(exp_variogram, filename):
    lags = exp_variogram.lags()
    variogram = exp_variogram.variogram()
    npairs = exp_variogram.npairs()
    direction_ids = exp_variogram.direction_ids()
    directions = exp_variogram.directions()

    import json

    with open(filename, "w+") as f:
        f.write(
            json.dumps(
                dict(
                    lags=np.array(lags).tolist(),
                    variogram=np.array(variogram).tolist(),
                    npairs=np.array(npairs).tolist(),
                    direction_id=np.array(direction_ids).tolist(),
                    directions=np.array(directions).tolist(),
                )
            )
        )


def load_variogram(filename):
    import json

    with open(filename, "r") as f:
        j = f.read()
        d = json.loads(j)
        return algorithms.ExperimentalVariogram(**d)


def smooth_variogram_direction(
    vario, b=0.001, power_a=3, dr=0.02, n_points=2000, window_size=10, freq_filter=0.2
):
    lags = vario[0]
    variogram = vario[1]

    lag_values = [np.linalg.norm(p) for p in lags]
    var_values = [v for v in variogram]

    variogram_line = algorithms.fft.project_to_line(
        lag_values,
        [v for v in variogram],
        b=b,
        power_a=power_a,
        n_points=n_points,
        window_size=window_size,
    )
    variogram_spectral_info = algorithms.fft.SpectralData1D.forward(variogram_line[1])
    s = int(len(variogram_spectral_info) * freq_filter) + 1
    selected_freqs = [i for i in range(0, s)] + [
        i for i in range(len(variogram_line[0]) - s + 1, len(variogram_line[0]))
    ]
    filtered_info = variogram_spectral_info.filter_frequencies(selected_freqs)
    back_data = filtered_info.backward()
    return algorithms.fft.project_back_to_source(
        lag_values,
        [p for p in variogram_line[0]],
        back_data,
        dr=dr * max([np.linalg.norm(p) for p in lags]),
        b=b,
        power_a=power_a,
    )


def smooth_variogram(
    exp_variogram,
    b=0.0001,
    power_a=1,
    dr=0.005,
    n_points=2000,
    window_size=2,
    freq_filter=0.2,
):
    directions = exp_variogram.directions()

    final_lags = []
    final_variogram = []
    final_npairs = []
    final_direction_id = []

    for dir_id, d in enumerate(directions):
        var = exp_variogram.get_variogram_by_direction_id(dir_id)
        lags = var[0]
        npairs = var[2]
        dir_ids = [dir_id for i in range(len(lags))]

        smoothed_line = smooth_variogram_direction(
            var,
            b=b,
            power_a=power_a,
            dr=dr,
            n_points=n_points,
            window_size=window_size,
            freq_filter=freq_filter,
        )
        final_lags.extend(lags)
        final_variogram.extend(smoothed_line)
        final_npairs.extend(npairs)
        final_direction_id.extend(dir_ids)
    return algorithms.ExperimentalVariogram(
        final_lags,
        final_variogram,
        final_npairs,
        final_direction_id,
        directions=directions,
    )


def extract_cov_from_varmap(
    varmap,
    total_sill,
    n_structures=1,
    cov_kernel="spherical",
    n_iterations=100,
    min_r1=0.01,
    min_r2=0.01,
    min_r3=0.01,
    max_r1=1,
    max_r2=1,
    max_r3=1,
    b=0.5,
    cauchy_loss=0.0,
    regularization_const=1e-5,
    threshold=1.3,
    seed=123151,
    n_threads=0,
    debug=False,
):
    lags = varmap.lags()
    variogram = varmap.variogram()
    npairs = varmap.npairs()

    length = max([np.linalg.norm(p) for p in lags])

    return algorithms.extract_covariance_from_varmap(
        lags=lags,
        variogram=variogram,
        weight=npairs,
        n_structures=n_structures,
        cov_kernel=cov_kernel,
        min_r1=min_r1 * length,
        min_r2=min_r2 * length,
        min_r3=min_r3 * length,
        max_r1=max_r1 * length,
        max_r2=max_r2 * length,
        max_r3=max_r3 * length,
        total_sill=total_sill,
        n_iterations=n_iterations,
        b=b,
        cauchy_loss=cauchy_loss,
        regularization_const=regularization_const * len(lags),
        threshold=threshold,
        seed=seed,
        n_threads=n_threads,
        debug=debug,
    )


def compute_score_error(
    proj_data,
    target_data,
    quantiles=[
        1e-8,
        1 - 1e-8,
        1,
        1,
        1,
        0.1,
        0.25,
        0.4,
        0.5,
        0.5,
        0.5,
        0.6,
        0.75,
        0.9,
        0.9,
        0.9,
    ],
):
    e = abs(np.array(proj_data) - target_data)
    forward_score_v = [np.quantile(e, q=q) / np.std(target_data) for q in quantiles]
    forward_score = sum(q * s for (q, s) in zip(quantiles, forward_score_v)) / (
        sum(quantiles)
    )
    return (forward_score, forward_score_v)


def optimize_projection(
    source_data,
    target_data,
    kernel="exponential",
    n_centers=27,
    weight_tol=10,
    center_tol=10,
    min_beta=1 / 1e6,
    max_beta=4,
    min_partition_size=0.5,
    max_partition_size=2,
    n_partitions=20,
    cauchy_loss=0.0,
    n_iterations=50,
    n_threads=0,
    seed=123154,
    debug=False,
):
    min_w = min(target_data)
    max_w = max(target_data)
    l_w = max_w - min_w

    min_c = min(source_data)
    max_c = max(source_data)
    l_c = max_c - min_c

    min_beta_forward = min_beta / l_c
    max_beta_forward = max_beta / l_c

    min_partition_size = int(min_partition_size * len(source_data) / n_partitions) + 1
    max_partition_size = int(max_partition_size * len(source_data) / n_partitions) + 1

    min_weight = min_w - weight_tol * l_w
    max_weight = max_w + weight_tol * l_w

    min_center = min_c - center_tol * l_c
    max_center = max_c + center_tol * l_c

    return algorithms.optimize_projection(
        source=source_data,
        target=target_data,
        kernel=kernel,
        n_centers=n_centers,
        min_beta=min_beta_forward,
        max_beta=max_beta_forward,
        min_weight=min_weight,
        max_weight=max_weight,
        min_center=min_center,
        max_center=max_center,
        n_partitions=n_partitions,
        min_partition_size=min_partition_size,
        max_partition_size=max_partition_size,
        cauchy_loss=cauchy_loss,
        n_iterations=n_iterations,
        n_threads=n_threads,
        seed=seed,
        debug=debug,
    )


def optimize_isomorphism(
    source_data,
    target_data,
    kernel_forward="exponential",
    n_centers_forward=27,
    kernel_backward="exponential",
    n_centers_backward=33,
    weight_tol=10,
    center_tol=10,
    min_beta=1 / 1e6,
    max_beta=4,
    min_partition_size=0.5,
    max_partition_size=2,
    n_partitions=20,
    cauchy_loss=0.0,
    n_iterations=50,
    n_threads=0,
    seed=123154,
    debug=False,
):
    min_w = min(target_data)
    max_w = max(target_data)
    l_w = max_w - min_w

    min_c = min(source_data)
    max_c = max(source_data)
    l_c = max_c - min_c

    min_beta_forward = min_beta / l_c
    max_beta_forward = max_beta / l_c

    min_beta_backward = min_beta / l_w
    max_beta_backward = max_beta / l_w

    min_partition_size = int(min_partition_size * len(source_data) / n_partitions) + 1
    max_partition_size = int(max_partition_size * len(source_data) / n_partitions) + 1

    min_weight = min_w - weight_tol * l_w
    max_weight = max_w + weight_tol * l_w

    min_center = min_c - center_tol * l_c
    max_center = max_c + center_tol * l_c

    return algorithms.optimize_isomorphism(
        source=source_data,
        target=target_data,
        kernel_type_forward=kernel_forward,
        n_centers_forward=n_centers_forward,
        min_beta_forward=min_beta_forward,
        max_beta_forward=max_beta_forward,
        kernel_type_backward=kernel_backward,
        n_centers_backward=n_centers_backward,
        min_beta_backward=min_beta_backward,
        max_beta_backward=max_beta_backward,
        min_weight=min_weight,
        max_weight=max_weight,
        min_center=min_center,
        max_center=max_center,
        n_partitions=n_partitions,
        min_partition_size=min_partition_size,
        max_partition_size=max_partition_size,
        cauchy_loss=cauchy_loss,
        n_iterations=n_iterations,
        n_threads=n_threads,
        seed=seed,
        debug=debug,
    )


def optimize_dist_transform(
    source_dist,
    target_dist,
    N=200,
    kernel_forward="exponential",
    n_centers_forward=27,
    kernel_backward="spherical",
    n_centers_backward=33,
    weight_tol=10,
    center_tol=10,
    min_beta=1 / 1e6,
    max_beta=4,
    min_partition_size=0.5,
    max_partition_size=2,
    n_partitions=20,
    cauchy_loss=0.0,
    n_iterations=50,
    n_threads=0,
    seed=123154,
    debug=False,
):
    source_cdf = algorithms.CDF(source_dist)
    target_cdf = algorithms.CDF(target_dist)

    dp = 1.0 / N
    probs = [i * dp for i in range(1, N - 1)]
    source_data = source_cdf.values(probs, n_threads=n_threads)
    target_data = target_cdf.values(probs, n_threads=n_threads)
    return optimize_isomorphism(
        source_data=source_data,
        target_data=target_data,
        kernel_forward=kernel_forward,
        n_centers_forward=n_centers_forward,
        kernel_backward=kernel_backward,
        n_centers_backward=n_centers_backward,
        weight_tol=weight_tol,
        center_tol=center_tol,
        min_beta=min_beta,
        max_beta=max_beta,
        min_partition_size=min_partition_size,
        max_partition_size=max_partition_size,
        n_partitions=n_partitions,
        cauchy_loss=cauchy_loss,
        n_iterations=n_iterations,
        n_threads=n_threads,
        seed=seed,
        debug=debug,
    )
