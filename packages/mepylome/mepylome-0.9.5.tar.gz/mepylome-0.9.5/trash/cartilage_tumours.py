"""Script used for output of publication.

Title: Methylome profiling of cartilage tumours: a promising new tool for
biopsy material?

Tested on: Ubuntu 20.04.6, Python 3.12.6, mepylome 0.4.5

author: Jon Brugger
"""

import io
import zipfile
from pathlib import Path

import distinctipy
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import requests
import umap
from inmoose.pycombat import pycombat_norm
from PIL import Image
from scipy import stats
from scipy.spatial import ConvexHull
from scipy.special import logit
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, auc, f1_score, roc_curve
from sklearn.model_selection import (
    StratifiedKFold,
    cross_val_predict,
    cross_validate,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm

from mepylome import CNV, ArrayType, Manifest, MethylData, ReferenceMethylData
from mepylome.analysis import MethylAnalysis
from mepylome.analysis.methyl import reordered_cpgs_by_variance
from mepylome.analysis.methyl_aux import IdatHandler
from mepylome.analysis.methyl_plots import _mixed_sort_key, continuous_colors
from mepylome.dtypes.manifests import (
    DOWNLOAD_DIR,
    MANIFEST_URL,
    REMOTE_FILENAME,
)
from mepylome.utils import ensure_directory_exists


def pdp(df_in):
    """Prints all rows of pandas data frame."""
    print(df_in.to_string())


OUTPUT_DIR = Path("/data/csa_project_output_dir").expanduser()
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FONTSIZE = 23
CNV_THRESHOLD = 0.1
CLUSTER = "cluster_brjo"


def normalize_df(df_in):
    """Normalize the columns of a pandas data frame."""
    return pd.DataFrame(
        StandardScaler().fit_transform(df_in),
        columns=df_in.columns,
    )


def generate_blacklist_cpgs():
    """Returns and caches CpG sites that should be blacklisted."""
    print("Generate blacklist. Can take some time...")
    blacklist_path = OUTPUT_DIR / "cpg_blacklist.csv"
    if not blacklist_path.exists():
        manifest_url = MANIFEST_URL[ArrayType.ILLUMINA_EPIC]
        ensure_directory_exists(DOWNLOAD_DIR)
        response = requests.get(manifest_url)
        html_sucess_ok_code = 200
        if response.status_code == html_sucess_ok_code:
            with zipfile.ZipFile(io.BytesIO(response.content)) as thezip:
                thezip.extractall(DOWNLOAD_DIR)
        else:
            raise Exception(
                f"Failed to download the file: {response.status_code}"
            )
        csv_path = DOWNLOAD_DIR / REMOTE_FILENAME[ArrayType.ILLUMINA_EPIC]
        manifest_df = pd.read_csv(csv_path, skiprows=7)
        flagged_cpgs = manifest_df[
            manifest_df["MFG_Change_Flagged"].fillna(False)
        ]["IlmnID"]
        flagged_cpgs.to_csv(blacklist_path, index=False, header=False)
        csv_path.unlink()
    blacklist = pd.read_csv(blacklist_path, header=None)
    return set(blacklist.iloc[:, 0])


def sex_chromosome_cpgs():
    """Returns CpGs on sex chromosomes for EPIC and 450k arrays."""
    manifest = Manifest("epic")
    sex_cpgs_epic = manifest.data_frame[
        manifest.data_frame.Chromosome.isin([23, 24])
    ].IlmnID
    manifest = Manifest("450k")
    sex_cpgs_450k = manifest.data_frame[
        manifest.data_frame.Chromosome.isin([23, 24])
    ].IlmnID
    return set(sex_cpgs_epic) | set(sex_cpgs_450k)


# Chose CpG list that should be blacklisted
blacklist = generate_blacklist_cpgs()
# blacklist = generate_blacklist_cpgs() | sex_chromosome_cpgs()

# IDAT directory
analysis_dir = Path("/mnt/storage/chondrosarcoma/")
# analysis_dir = "/data/csa_project_all/csa_project/"
# analysis_dir = "/mnt/storage/MNG_IDAT"
# analysis_dir = "/mnt/storage/epidip_IDAT"

annotation = analysis_dir / "csa_project/Triplicate_CSA_NL.xlsx"


def use_own_samples():
    idat_handler = IdatHandler(
        analysis_dir=analysis_dir,
        annotation=annotation,
        overlap=True,
    )
    samples_annotated = idat_handler.samples_annotated
    return samples_annotated[
        samples_annotated.Origin.isin(
            [
                "BSL",
                "EXT",
                "HEI",
                "HEI_BSL",
                "NL",
                "SWE",
                "UCL",
            ]
        )
    ].index


def use_all_samples():
    idat_handler = IdatHandler(
        analysis_dir=analysis_dir,
        annotation=annotation,
        overlap=True,
    )
    all_ids = set(idat_handler.ids)
    samples_annotated = idat_handler.samples_annotated
    censor = samples_annotated[
        samples_annotated[CLUSTER].isin(["CSA_PER"])
    ].index
    return all_ids - set(censor)


# Toggle this one line to switch logic
analysis_ids = use_own_samples()
# analysis_ids = use_all_samples()


# Remove HN CSA
# ids = pd.Series(idat_handler.ids)
# methyl_class = pd.Series(idat_handler.features("CLUSTER"))
# analysis_ids = ids[methyl_class != "IDH_MUT_HN"].tolist()

analysis = MethylAnalysis(
    analysis_dir=analysis_dir,
    output_dir=OUTPUT_DIR,
    reference_dir="/data/ref_IDAT",
    annotation=annotation,
    analysis_ids=analysis_ids,
    n_cpgs=25000,
    load_full_betas=True,
    overlap=False,
    use_gpu=True,
    cpg_blacklist=blacklist,
    debug=True,
    do_seg=True,
    umap_parms={
        "n_neighbors": 12,
        "metric": "manhattan",
        "min_dist": 0.00005,
    },
)


def add_grade_columns():
    analysis.idat_handler.samples_annotated["Grade_No_GX"] = (
        analysis.idat_handler.samples_annotated["Grade"].apply(
            lambda x: "" if x == "GX" else x
        )
    )
    analysis.idat_handler.samples_annotated["Grade_Category"] = (
        analysis.idat_handler.samples_annotated["Grade"].apply(
            lambda x: (
                "low_grade"
                if x in ("G0", "G1")
                else "high_grade"
                if x in ("G2", "G3", "G4")
                else ""
            )
        )
    )
    analysis.idat_handler.samples_annotated["Grade_Category_No_G4"] = (
        analysis.idat_handler.samples_annotated["Grade"].apply(
            lambda x: (
                "low_grade"
                if x in ("G0", "G1")
                else "high_grade"
                if x in ("G2", "G3")
                else ""
            )
        )
    )


def start_gui():
    """Open mepylome in browser."""
    analysis.make_umap()
    analysis.idat_handler.selected_columns = [CLUSTER]
    analysis.run_app(open_tab=True)


def calculate_cn_summary(class_, filename, own_samples_only=True):
    """Calculates and saves CN summary plots."""
    df_class = pd.DataFrame(
        {"Class": class_},
        index=analysis.idat_handler.samples_annotated.index,
    )["Class"]
    if own_samples_only:
        our_study_ids = analysis.idat_handler.samples_annotated[:212].index
        df_class = df_class.loc[our_study_ids]
    plot_list = []
    all_classes = sorted(df_class.unique())
    for methyl_class in all_classes:
        df_index = df_class == methyl_class
        sample_ids = df_class.index[df_index]
        plot, df_cn_summary = analysis.cn_summary(sample_ids)
        _ = plot.update_layout(
            title=f"{methyl_class}",
            title_x=0.5,
            yaxis_title="Proportion of CNV gains/losses",
        )
        plot.update_layout(
            title_font_size=FONTSIZE + 3,
            yaxis_title_font_size=FONTSIZE - 2,
        )
        _ = plot_list.append(plot)
        plot.show()
    png_suffix = f"cn_summary_{filename}"
    for i, fig in enumerate(plot_list):
        fig.write_image(OUTPUT_DIR / f"{png_suffix}_{i + 1}.png")
    image_paths = [
        OUTPUT_DIR / f"{png_suffix}_{i + 1}.png"
        for i in range(len(all_classes))
    ]
    images = [Image.open(path) for path in image_paths]
    width, height = images[0].size
    n_columns = 3
    n_images = len(images)
    n_rows = (n_images + n_columns - 1) // n_columns
    total_width = width * n_columns
    total_height = height * n_rows
    new_image = Image.new("RGB", (total_width, total_height))
    for index, img in enumerate(images):
        row = index // n_columns
        col = index % n_columns
        x = col * width
        y = row * height
        new_image.paste(img, (x, y))
    new_image.save(OUTPUT_DIR / f"{png_suffix}_all.png")
    return plot_list


def get_df_cnv_segments():
    """Returns the CN data frame of all samples using the segments data."""
    bins0 = analysis.get_cnv(analysis.idat_handler.ids[0], extract="bins")
    bins0 = bins0[["Chromosome", "Start", "End"]]
    bins0 = bins0[~bins0["Chromosome"].isin(["chrX", "chrY"])]
    new_columns = pd.DataFrame(
        {sample_id: 0 for sample_id in analysis.idat_handler.ids},
        index=bins0.index,
    )
    bins0 = pd.concat([bins0, new_columns], axis=1)
    for sample_id in analysis.idat_handler.ids:
        segments = analysis.get_cnv(sample_id, extract="segments")
        for _, segment in segments.iterrows():
            bins0.loc[
                (bins0["Chromosome"] == segment.Chromosome)
                & (bins0["Start"] >= segment.Start)
                & (bins0["End"] <= segment.End),
                sample_id,
            ] = segment.Median
    df_result = bins0.drop(columns=["Chromosome", "Start", "End"]).T
    df_result = normalize_df(df_result)
    return df_result


def get_df_cnv_bins():
    """Returns the CN data frame of all samples using the bins data."""
    bins_median_list = []
    for sample_id in analysis.idat_handler.ids:
        bins = analysis.get_cnv(sample_id, extract="bins").rename(
            columns={"Median": sample_id}
        )
        bins = bins[~bins["Chromosome"].isin(["chrX", "chrY"])]
        bins_median_list.append(bins[sample_id])
    df_result = pd.concat(bins_median_list, axis=1).T
    df_result = normalize_df(df_result)
    return df_result


def set_methyl_cnv_feature_matrix(
    n_methyl, n_cnv=0, df_cnv=None, normalize_methyl=False, umap_parms=None
):
    """Creates a feature matrix by applying UMAP on methylation and CNV data.
    Args:
        n_methyl (int or None): Number of UMAP dimensions for methylation. Use
            full data if None.
        n_cnv (int, optional): Number of UMAP dimensions for CNV. Use full data
            if None. Defaults to 0.
        df_cnv (pd.DataFrame, optional): CNV data to reduce. Required if n_cnv
            > 0.
        normalize_methyl (bool, optional): Whether to normalize methylation
            data. Defaults to False.
    Returns:
        None: Updates `analysis.feature_matrix` with the combined feature
            matrix.
    """
    umap_parms = umap_parms or {}
    if n_methyl == 0 and n_cnv == 0:
        raise ValueError("Both n_methyl and n_cnv cannot be zero.")
    feature_matrices = []
    analysis.set_betas()
    betas_sel = (
        normalize_df(analysis.betas_sel)
        if normalize_df
        else analysis.betas_sel
    )
    if n_methyl is not None and n_methyl > 0:
        reduced_methyl = umap.UMAP(
            **umap_parms,
            n_components=n_methyl,
        ).fit_transform(betas_sel)
        feature_matrices.append(reduced_methyl)
    if n_methyl is None:
        feature_matrices.append(betas_sel)
    if n_cnv is not None and n_cnv > 0:
        reduced_cnv = umap.UMAP(
            **umap_parms,
            n_components=n_cnv,
        ).fit_transform(df_cnv)
        feature_matrices.append(reduced_cnv)
    if n_cnv is None:
        feature_matrices.append(df_cnv)
    analysis.feature_matrix = pd.DataFrame(
        np.column_stack(feature_matrices),
        index=analysis.betas_sel.index,
    )
    print("\n\nFeature matrix set to:")
    print(analysis.feature_matrix)


def classify_cdkn2a_cnv_median(median):
    if median > 0.4:
        return "8 gain>0.4"
    if median > 0.3:
        return "7 gain>0.3"
    if median > 0.2:
        return "6 gain>0.2"
    if median > 0.1:
        return "5 gain>0.1"
    if median < -0.4:
        return "0 loss>0.4"
    if median < -0.3:
        return "1 loss>0.3"
    if median < -0.2:
        return "2 loss>0.2"
    if median < -0.1:
        return "3 loss>0.1"
    return "4 balanced"


def round_to_nearest_5_percent(value):
    return round(value * 20) / 20


def write_annotation_file_columns():
    """Writes some columns that can be copied into the annotation file."""
    csv_file = OUTPUT_DIR / "annotation_file_columns.csv"
    if csv_file.exists():
        return
    sentrix_ids = analysis.idat_handler.annotation_df.index
    annotations = {
        "CDKN2A_median": [],
        "CDKN2A_status": [],
        "CNV_involved": [],
        "CNV_segments_involved": [],
        "Chr14q32_median": [],
        "Noise": [],
    }
    for sentrix_id in sentrix_ids:
        try:
            path = analysis.cnv_dir / f"{sentrix_id}_cnv.zip"
            if not path.exists():
                raise FileNotFoundError
            bins, detail, segments, metadata = analysis.get_cnv(
                sentrix_id, extract=["bins", "detail", "segments", "metadata"]
            )
            median_value = detail.loc[
                detail["Name"] == "CDKN2A", "Median"
            ].values[0]
            annotations["CDKN2A_status"].append(
                classify_cdkn2a_cnv_median(median_value)
            )
            annotations["CDKN2A_median"].append(median_value)
            cnv_percentage = round_to_nearest_5_percent(
                np.sum(np.abs(bins.Median) > CNV_THRESHOLD) / bins.shape[0]
            )
            annotations["CNV_involved"].append(cnv_percentage)
            segments_percentage = round_to_nearest_5_percent(
                sum(
                    (segments.End - segments.Start)
                    * (abs(segments.Median) > CNV_THRESHOLD)
                )
                / sum(segments.End - segments.Start)
            )
            annotations["CNV_segments_involved"].append(segments_percentage)
            medians_14q32 = bins[
                (bins["Chromosome"] == "chr14") & (bins["Start"] >= 89800000)
            ]["Median"].median()
            annotations["Chr14q32_median"].append(
                round(medians_14q32 / 0.05) * 0.05
            )
            annotations["Noise"].append(metadata.Noise[0])
        except Exception:
            print(f"[ERROR] Sentrix ID: {sentrix_id}")
            for values in annotations.values():
                values.append("")
    pd.DataFrame(annotations).to_csv(csv_file, index=False)


def cnv_stats(confidence_level=0.95, cnv_col="CNV_segments_involved"):
    """Calculate some stats of CN for all samples."""
    df_anno = analysis.idat_handler.samples_annotated
    for grade in [f"G{x}" for x in range(5)]:
        # grade_data = df_anno[df_anno.Grade == grade][cnv_col]
        grade_data = df_anno[df_anno.Grade == grade][cnv_col]
        if len(grade_data) == 0:
            print(f"No data available for grade {grade}.")
            continue
        cnv_mean = np.mean(grade_data)
        # Standard error of the mean
        sem = stats.sem(grade_data)
        confidence_interval = stats.t.interval(
            confidence_level, len(grade_data) - 1, loc=cnv_mean, scale=sem
        )
        lower_bound, upper_bound = confidence_interval
        lower_bound *= 100
        upper_bound *= 100
        print(
            f"Genome involved by CNV for grade {grade}: {100 * cnv_mean:.2f}% "
            f"with a {confidence_level * 100:.0f}% CI of [{lower_bound:.2f}%, "
            f"{upper_bound:.2f}%]"
        )
    for grade in [f"G{x}" for x in range(5)]:
        cdkn2a_data = df_anno[df_anno.Grade == grade].CDKN2A_median
        loss_count = np.sum(cdkn2a_data < -CNV_THRESHOLD)
        gain_count = np.sum(cdkn2a_data > CNV_THRESHOLD)
        total_cases = len(cdkn2a_data)
        loss_percentage = (loss_count / total_cases) * 100
        gain_percentage = (gain_count / total_cases) * 100
        loss_ci = stats.binom.interval(
            0.95, total_cases, loss_count / total_cases
        )
        gain_ci = stats.binom.interval(
            0.95, total_cases, gain_count / total_cases
        )
        loss_ci_percent = (np.array(loss_ci) / total_cases) * 100
        gain_ci_percent = (np.array(gain_ci) / total_cases) * 100
        print(
            f"Percentage of CDKN2A loss for grade {grade}: "
            f"{loss_percentage:.2f}% ({len(cdkn2a_data)} cases), "
            f"95% CI: [{loss_ci_percent[0]:.2f}%, {loss_ci_percent[1]:.2f}%]"
        )
        print(
            f"Percentage of CDKN2A gain for grade {grade}: "
            f"{gain_percentage:.2f}% ({len(cdkn2a_data)} cases), "
            f"95% CI: [{gain_ci_percent[0]:.2f}%, {gain_ci_percent[1]:.2f}%]"
        )
    for idh_status in ["IDH_WT", "IDH_MUT"]:
        idh_data = df_anno[df_anno.IDH_bool == idh_status][cnv_col]
        if len(idh_data) == 0:
            print(f"No data available for {idh_status}.")
            continue
        cnv_mean = np.mean(idh_data)
        # Standard error of the mean
        sem = stats.sem(idh_data)
        confidence_interval = stats.t.interval(
            confidence_level, len(idh_data) - 1, loc=cnv_mean, scale=sem
        )
        lower_bound, upper_bound = confidence_interval
        lower_bound *= 100
        upper_bound *= 100
        print(
            f"Genome involved by CNV for {idh_status}: {100 * cnv_mean:.2f}% "
            f"with a {confidence_level * 100:.0f}% CI of [{lower_bound:.2f}%, "
            f"{upper_bound:.2f}%]"
        )
        for grade in [f"G{x}" for x in range(5)]:
            # CDKN2A methylation analysis
            idh_grade_data = df_anno[
                (df_anno.IDH_bool == idh_status) & (df_anno.Grade == grade)
            ][cnv_col]
            cnv_mean = np.mean(idh_grade_data)
            # Standard error of the mean
            sem = stats.sem(idh_grade_data)
            confidence_interval = stats.t.interval(
                confidence_level,
                len(idh_grade_data) - 1,
                loc=cnv_mean,
                scale=sem,
            )
            lower_bound, upper_bound = confidence_interval
            lower_bound *= 100
            upper_bound *= 100
            print(
                f"    - grade {grade} ({len(idh_grade_data)}): "
                f"{100 * cnv_mean:.2f}% with a "
                f"{confidence_level * 100:.0f}% CI of "
                f"[{lower_bound:.2f}%, {upper_bound:.2f}%]"
            )
    for cluster in sorted(set(df_anno[CLUSTER])):
        print(f"\n{cluster}")
        df_cl = df_anno[df_anno[CLUSTER] == cluster]
        for grade in [f"G{x}" for x in range(5)]:
            grade_percentage = np.mean(df_cl.Grade == grade) * 100
            print(
                f"Percentage of grade {grade} in cluster {cluster}: "
                f"{grade_percentage:.2f}%"
            )
        # Calculate CDKN2A loss and gain in this cluster
        cdkn2a_data = df_cl.CDKN2A_median
        loss_percentage = np.mean(cdkn2a_data < -CNV_THRESHOLD) * 100
        gain_percentage = np.mean(cdkn2a_data > CNV_THRESHOLD) * 100
        print(
            f"Percentage of samples with CDKN2A loss in cluster {cluster}: "
            f"{loss_percentage:.2f}%"
        )
        print(
            f"Percentage of samples with CDKN2A gain in cluster "
            f"{cluster}: {gain_percentage:.2f}%"
        )
        # Mean CNV involvement and confidence interval in this cluster
        cnv_data = df_cl[cnv_col]
        if len(cnv_data) == 0:
            print(f"No CNV data available for cluster {cluster}.")
            continue
        cnv_mean = np.mean(cnv_data)
        sem = stats.sem(cnv_data)
        confidence_interval = stats.t.interval(
            confidence_level, len(cnv_data) - 1, loc=cnv_mean, scale=sem
        )
        lower_bound, upper_bound = confidence_interval
        lower_bound *= 100
        upper_bound *= 100
        print(
            f"Genome involved by CNV for cluster {cluster}: "
            f"{100 * cnv_mean:.2f}% with a "
            f"{confidence_level * 100:.0f}% CI of "
            f"[{lower_bound:.2f}%, {upper_bound:.2f}%]"
        )


def calculate_cnv_noise():
    """Calculates the noise of the CN for all suppliers."""
    df_anno = analysis.idat_handler.samples_annotated.copy()
    mean_noise_per_supplier = (
        df_anno[df_anno.Noise < 0.75].groupby("Origin")["Noise"].mean()
    )
    print(mean_noise_per_supplier)
    mean_noise_per_supplier = (
        df_anno[:116][df_anno.Noise < 0.75].groupby("Origin")["Noise"].mean()
    )
    print(mean_noise_per_supplier)


def get_rgb256(color):
    """Returns RGB from 3 floats."""
    return (
        int(round(color[0] * 255)),
        int(round(color[1] * 255)),
        int(round(color[2] * 255)),
    )


def discrete_colors(names, seed=123):
    """Returns good visable colors."""
    n_names = len(names)
    colors = distinctipy.get_colors(n_names, rng=seed)
    return {name: f"rgb{get_rgb256(col)}" for name, col in zip(names, colors)}


def hull_boundary(points, smooth_factor=1.5, expand_factor=1.0):
    """Can be used to enlarge the convex hull."""
    center = np.mean(points, axis=0)
    return (points - center) * expand_factor + center


def get_umap_plot(umap_df, fontsize=FONTSIZE, use_discrete_colors=True):
    """Returns UMAP plot for publication."""
    methyl_classes = np.sort(umap_df["Umap_color"].unique())
    if use_discrete_colors:
        color_map = discrete_colors(methyl_classes)
    else:
        methyl_classes = sorted(methyl_classes, key=_mixed_sort_key)
        color_map = continuous_colors(methyl_classes)
    category_orders = {"Umap_color": methyl_classes}
    # If there are too many columns, they are not displayed correctly
    n_hover = 35
    fig = px.scatter(
        umap_df,
        x="Umap_x",
        y="Umap_y",
        labels={
            "Umap_x": "UMAP 0",
            "Umap_y": "UMAP 1",
            "Umap_color": "Class",
        },
        title="",
        color="Umap_color",
        color_discrete_map=color_map if use_discrete_colors else None,
        color_continuous_scale=px.colors.sequential.Plasma
        if not use_discrete_colors
        else None,
        hover_name=umap_df.index,
        category_orders=category_orders,
        hover_data=umap_df.columns[:n_hover],
        render_mode="webgl",
        template="simple_white",
    )
    fig.update_yaxes(
        # title_font=dict(size=fontsize),
        # tickfont=dict(size=fontsize),
        mirror=True,
    )
    x_margin = 0.1
    x_min = umap_df["Umap_x"].min()
    x_max = umap_df["Umap_x"].max()
    x_delta = x_max - x_min
    fig.update_xaxes(
        # title_font=dict(size=fontsize),
        # tickfont=dict(size=fontsize),
        mirror=True,
        range=[x_min - x_margin * x_delta, x_max + x_margin * x_delta],
    )
    fig.update_layout(
        legend=dict(
            title="",
            x=0.80,
            y=0.70,
            bgcolor="rgba(255, 255, 255, 0.5)",
            # font=dict(size=fontsize),
        ),
        font=dict(size=fontsize),
    )
    fig.update_layout(
        coloraxis_colorbar=dict(
            title="",
            x=0.9,
            y=0.4,
            len=0.5,
            thickness=15,
            bgcolor="rgba(255, 255, 255, 0.5)",
        ),
        font=dict(size=fontsize),
    )
    for cluster_id in umap_df[CLUSTER].unique():
        points = umap_df[umap_df[CLUSTER] == cluster_id][
            ["Umap_x", "Umap_y"]
        ].values
        if len(points) > 2:
            hull = ConvexHull(points)
            hull_points = points[hull.vertices]
            hull_points = hull_boundary(points[hull.vertices])
            hull_trace = go.Scatter(
                x=np.append(hull_points[:, 0], hull_points[0, 0]),
                y=np.append(hull_points[:, 1], hull_points[0, 1]),
                mode="lines",
                line=dict(color="black", width=1.5),
                fill="toself",
                fillcolor="rgba(0,0,0,0)",
                name=f"{cluster_id}",
                showlegend=False,
            )
            fig.add_trace(hull_trace)
            min_x = np.min(hull_points[:, 0])
            min_y = np.min(hull_points[:, 1])
            max_x = np.max(hull_points[:, 0])
            max_y = np.max(hull_points[:, 1])
            mean_x = np.mean(hull_points[:, 0])
            mean_y = np.mean(hull_points[:, 1])
            if cluster_id in ["IDH_WT_2", "IDH_MUT_1"]:
                x = mean_x - 0.0
                y = max_y + 0.2
                textposition = "top center"
            else:
                x = mean_x - 0.0
                y = min_y - 0.2
                textposition = "bottom center"
            fig.add_trace(
                go.Scatter(
                    x=[x],
                    y=[y],
                    mode="text",
                    text=f"{cluster_id}",
                    textposition=textposition,
                    showlegend=False,
                    # textfont=dict(size=fontsize),
                )
            )
    fig.update_traces(
        marker=dict(size=17, line=dict(width=1, color="DarkSlateGrey"))
    )
    return fig


def cross_validation(include_g4=False):
    """Validate classification of the tumor grade using feature_matrix."""
    bin_replace_map = {"G0": 0, "G1": 0, "G2": 1, "G3": 1, "G4": -1, "GX": -1}
    if include_g4:
        bin_replace_map["G4"] = 1
    grade = analysis.idat_handler.samples_annotated.Grade
    grades = (
        grade.replace(bin_replace_map)
        .loc[lambda x: x.isin([0, 1])]
        .astype(int)
    )
    X = analysis.feature_matrix.loc[grades.index]
    classifier = RandomForestClassifier(n_estimators=150, random_state=42)
    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("classifier", classifier),
        ]
    )
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scoring = ["accuracy", "roc_auc", "f1"]
    cv_results = cross_validate(
        pipeline, X, grades, cv=cv, scoring=scoring, n_jobs=-1
    )
    accuracy_scores = cv_results["test_accuracy"]
    auc_scores = cv_results["test_roc_auc"]
    f1_scores = cv_results["test_f1"]
    print(f"X shape: {X.shape}")
    print(f"Accuracy: {np.mean(accuracy_scores)} -+ {np.std(accuracy_scores)}")
    print(f"AUC: {np.mean(auc_scores)} -+ {np.std(auc_scores)}")
    print(f"F1-Score: {np.mean(f1_scores)} -+ {np.std(f1_scores)}")


def cross_validation_and_auc_plot(method_name="", fig=None, include_g4=False):
    """Sampe as cross_val_predict but adds plot."""
    bin_replace_map = {"G0": 0, "G1": 0, "G2": 1, "G3": 1, "G4": -1, "GX": -1}
    if include_g4:
        bin_replace_map["G4"] = 1
    grade = analysis.idat_handler.samples_annotated.Grade
    grades = (
        grade.replace(bin_replace_map)
        .loc[lambda x: x.isin([0, 1])]
        .astype(int)
    )
    X = analysis.feature_matrix.loc[grades.index]
    classifier = RandomForestClassifier(n_estimators=150, random_state=42)
    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("classifier", classifier),
        ]
    )
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    y_scores = cross_val_predict(
        pipeline, X, grades, cv=cv, method="predict_proba", n_jobs=-1
    )
    accuracy_scores = []
    auc_scores = []
    f1_scores = []
    for train_idx, test_idx in cv.split(X, grades):
        y_true = grades[test_idx]
        y_pred = y_scores[test_idx, 1]
        predicted_classes = np.argmax(y_scores[test_idx], axis=1)
        accuracy_scores.append(accuracy_score(y_true, predicted_classes))
        f1_scores.append(f1_score(y_true, predicted_classes, average="binary"))
        fpr, tpr, _ = roc_curve(y_true, y_pred, pos_label=1)
        roc_auc = auc(fpr, tpr)
        auc_scores.append(roc_auc)
    fpr, tpr, _ = roc_curve(grades, y_scores[:, 1], pos_label=1)
    # roc_auc = auc(fpr, tpr)
    accuracy_mean = np.mean(accuracy_scores)
    accuracy_std = np.std(accuracy_scores)
    auc_mean = np.mean(auc_scores)
    auc_std = np.std(auc_scores)
    f1_mean = np.mean(f1_scores)
    f1_std = np.std(f1_scores)
    print(f"X shape: {X.shape}")
    print(f"Accuracy: {accuracy_mean} -+ {accuracy_std}")
    print(f"AUC: {auc_mean} -+ {auc_std}")
    print(f"F1-Score: {f1_mean} -+ {f1_std}")
    if fig is None:
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=[0, 1],
                y=[0, 1],
                mode="lines",
                name="Chance",
                line=dict(dash="dash", color="gray"),
                showlegend=False,
            )
        )
        fig.update_layout(
            title="Mean ROC Curves from Cross-Validation",
            title_x=0.5,
            xaxis_title="False Positive Rate",
            yaxis_title="True Positive Rate",
            template="plotly_white",
            width=600,
            height=600,
            showlegend=True,
            yaxis=dict(scaleanchor="x", scaleratio=1),
            xaxis=dict(constrain="domain"),
            legend=dict(
                title="",
                x=0.45,
                y=0.03,
                bgcolor="rgba(255, 255, 255, 0.5)",
            ),
        )
        fig.add_shape(
            type="rect",
            x0=0,
            y0=0,
            x1=1,
            y1=1,
            line=dict(color="black", width=2),
            fillcolor="rgba(0,0,0,0)",
        )
        fig.update_xaxes(
            range=[0, 1],
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            # title_standoff=10,
            automargin=True,
            title_standoff=None,
        )
        fig.update_yaxes(
            range=[0, 1],
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            # title_standoff=10,
            automargin=True,
            title_standoff=None,
        )
    fig.add_trace(
        go.Scatter(
            x=fpr,
            y=tpr,
            mode="lines",
            name=f"{method_name} (AUC = {auc_mean:.2f} ± {auc_std:.2f})",
            line=dict(width=2),
        )
    )
    return fig


def print_clusters():
    """Prints the calculated clusters along with UMAP clusters."""
    for cluster in range(8):
        pdp(anno[[CLUSTER, "Cluster"]][anno.Cluster == cluster])
        print()


def validate_gui_prediction():
    """Validates the internal classifier of mepylome."""
    grade_map = {"G0": 0, "G1": 1, "G2": 2, "G3": 3, "G4": 4, "GX": -1}
    add_grade_columns()
    analysis.idat_handler.selected_columns = ["Grade_No_GX"]
    ids = analysis.idat_handler.ids
    clf = analysis.classify(ids=ids, clf_list="vtl-kbest-rf")[0]
    pred_grades = clf.prediction.idxmax(axis=1)
    grade_list = []
    for sample_id, pred_grade in pred_grades.items():
        print(sample_id)
        true_grade = analysis.idat_handler.samples_annotated.loc[sample_id][
            "Grade"
        ]
        if true_grade in ["G0", "G1", "G2", "G3", "G4"]:
            grade_list.append(
                [
                    sample_id,
                    true_grade,
                    grade_map[true_grade],
                    grade_map[pred_grade],
                ]
            )
    correct_predictions = sum(
        1 for _, _, true, pred in grade_list if true == pred
    )
    accuracy = correct_predictions / len(grade_list)
    for sample_id, grade, true, pred in grade_list:
        if true != pred:
            print(
                f"Wrong Prediction - ID: {sample_id}, True: {grade}, "
                f"Pred: G{pred}"
            )
    print(f"Accuracy: {accuracy:.4f} ({len(grade_list)} samples)")


def validate_gui_prediction_high_vs_low(include_g4=False):
    """Validates the internal classifier of mepylome for high vs low grade."""
    map_g4_to_g2 = {"G0": 0, "G1": 0, "G2": 1, "G3": 1, "G4": -1, "GX": -1}
    add_grade_columns()
    if include_g4:
        map_g4_to_g2["G4"] = 1
        grade_col = "Grade_Category"
    else:
        grade_col = "Grade_Category_No_G4"
    analysis.idat_handler.selected_columns = [grade_col]
    ids = analysis.idat_handler.ids
    clf = analysis.classify(ids=ids, clf_list="vtl-kbest-rf")[0]
    pred_grades = clf.prediction.idxmax(axis=1)
    pred_prob = clf.prediction
    grade_list = []
    for sample_id in ids:
        anno = analysis.idat_handler.samples_annotated.loc[sample_id]
        true_grade_4 = anno["Grade"]
        if map_g4_to_g2[true_grade_4] in [0, 1]:
            pred_prob_2 = max(pred_prob.loc[sample_id])
            pred_grade_2 = pred_grades.loc[sample_id]
            true_grade_2 = anno[grade_col]
            # true_grade_2 = map_g4_to_g2[true_grade_4]
            grade_list.append(
                {
                    "sample_id": sample_id,
                    "true_grade_4": true_grade_4,
                    "true_grade_2": true_grade_2,
                    "pred_grade_2": pred_grade_2,
                    "pred_prob_2": pred_prob_2,
                    "pred_correct": int(true_grade_2 == pred_grade_2),
                    "clf": clf,
                }
            )
    correct_predictions = sum(result["pred_correct"] for result in grade_list)
    accuracy = correct_predictions / len(grade_list)
    for result in grade_list:
        if result["true_grade_2"] != result["pred_grade_2"]:
            print(
                f"Sample: {result['sample_id']}, "
                f"True: {result['true_grade_4']}, "
                f"Pred: {result['pred_grade_2']}, "
                f"Prob: {result['pred_prob_2']}, "
            )
    print(f"Accuracy: {accuracy} ({len(grade_list)} samples)")
    return grade_list


print("\nUse this script in interactive mode -i\n")
quit()

#################################### SETUP ####################################

# Calculat all CNV
analysis.precompute_cnvs()

# Generate some columns for the annotation file (include manually).
write_annotation_file_columns()

# Calculate data frames containing CN data (either all bins or the significant
# segments)
df_cnv_segments = get_df_cnv_segments()
df_cnv_bins = get_df_cnv_bins()


################################## DRAW UMAP ##################################

# Use methylation data only
analysis.feature_matrix = None
start_gui()

# Change certain UMAP Parameters
analysis.feature_matrix = None
analysis.n_cpgs = 25000
analysis.umap_parms = {
    "n_neighbors": 10,
    "metric": "manhattan",
    "min_dist": 0.00001,
    "verbose": True,
    # "local_connectivity": 2,
    # "n_epochs": 5000,
    # "random_state": 1000,
    # "spread": 2,
    # "n_neighbors": 10,
    # "min_dist": 0.05,
    # "spread": 2.5,
    # "metric": 'cosine',
    # "learning_rate": 0.5,
    # "n_epochs": 500,
    # "set_op_mix_ratio": 0.8,
    # "repulsion_strength": 10,
    # "target_weight": 0.7,
    # "init": "pca",
}
start_gui()

analysis.feature_matrix = None
analysis.umap_parms = {
    "n_neighbors": 14,
    "metric": "euclidean",
    "min_dist": 0.01,
    "random_state": 621,
}
start_gui()


# Use PCA first
analysis.set_betas()
analysis.n_cpgs = 250000
analysis.feature_matrix = PCA(n_components=200).fit_transform(
    analysis.betas_sel
)
analysis.umap_parms = {
    "n_neighbors": 10,
    "metric": "euclidean",
    "min_dist": 0.00001,
    "verbose": True,
}
start_gui()


# Use PCA first
analysis.set_betas()
analysis.feature_matrix = PCA(
    n_components=20, svd_solver="full"
).fit_transform(analysis.betas_sel)
analysis.umap_parms = {
    "n_neighbors": 10,
    "metric": "euclidean",
    "min_dist": 0.00001,
    "verbose": True,
}
start_gui()

# CNV and Methyl unreduced
set_methyl_cnv_feature_matrix(None, None, df_cnv_segments, False)
analysis.umap_parms = {
    "n_neighbors": 10,
    "metric": "manhattan",
    "min_dist": 0.01,
    "verbose": True,
}
start_gui()


# CNV only (bins)
set_methyl_cnv_feature_matrix(0, None, df_cnv_bins, True)
analysis.umap_parms = {
    "n_neighbors": 10,
    "metric": "manhattan",
    "min_dist": 0.01,
    "verbose": True,
}
start_gui()


# CNV only (segments)
set_methyl_cnv_feature_matrix(
    0,
    None,
    # df_cnv_segments[reorder_columns_by_variance(df_cnv_segments)].iloc[:,:1000],
    df_cnv_segments,
    True,
)
analysis.umap_parms = {
    "n_neighbors": 10,
    "metric": "manhattan",
    "min_dist": 0.01,
    "verbose": True,
}
start_gui()


# CNV ratio
reference = ReferenceMethylData(analysis.reference_dir)
ratio_list = []
for path in tqdm(analysis.idat_handler.paths):
    sample = MethylData(file=path)
    cnv = CNV(sample, reference)
    ratio_list.append(cnv._ratio)

cnv_ratio_df = pd.DataFrame(
    np.vstack(ratio_list), index=analysis.idat_handler.ids
)
cnv_ratio_df = cnv_ratio_df[reordered_cpgs_by_variance(cnv_ratio_df)]
analysis.feature_matrix = cnv_ratio_df.iloc[:, :10000]
analysis.umap_parms = {
    "n_neighbors": 10,
    "metric": "manhattan",
    "min_dist": 0.01,
    "verbose": True,
}
start_gui()


# Mixed methylation and cnv
set_methyl_cnv_feature_matrix(95, 5, df_cnv_bins, True)
analysis.umap_parms = {
    "n_neighbors": 25,
    "metric": "manhattan",
    "min_dist": 0.2,
    "verbose": True,
}
start_gui()


# OWN: Two step UMAP 25000 -> 100 -> 2
analysis.n_cpgs = 25000
seed = 23
set_methyl_cnv_feature_matrix(
    100,
    0,
    None,
    True,
    umap_parms={"random_state": seed, "n_neighbors": 15, "metric": "euclidean"},
)
analysis.umap_parms = {
    "n_neighbors": 15,
    "metric": "euclidean",
    "min_dist": 0.2,
    "verbose": True,
    "random_state": seed,
}
start_gui()

# ALL: Two step UMAP 25000 -> 100 -> 2
analysis.n_cpgs = 25000
seed = None
set_methyl_cnv_feature_matrix(
    100,
    0,
    None,
    True,
    umap_parms={"random_state": seed, "n_neighbors": 25, "metric": "euclidean"},
)
analysis.umap_parms = {
    "n_neighbors": 25,
    "metric": "euclidean",
    "min_dist": 0.2,
    "verbose": True,
    "random_state": seed,
}
start_gui()



# Two step UMAP 25000 -> 50 -> 2
analysis.n_cpgs = 25000
set_methyl_cnv_feature_matrix(
    50, 0, None, True, umap_parms={"random_state": 43}
)
analysis.umap_parms = {
    "n_neighbors": 15,
    "metric": "euclidean",
    "min_dist": 0.2,
    "verbose": True,
}
start_gui()


# Publication plot
analysis.feature_matrix = None
analysis.umap_parms = {
    "n_neighbors": 12,
    "metric": "manhattan",
    "min_dist": 0.00003,
    "random_state": 27,
    # "random_state": 12974,
}
start_gui()


# Round betas to 0,1
analysis.feature_matrix = None
analysis.set_betas()
analysis.feature_matrix = np.round(analysis.betas_sel)
analysis.umap_parms = {
    "n_neighbors": 12,
    "metric": "manhattan",
    "min_dist": 0.00003,
    # "random_state": 24,
    # "random_state": 12974,
}
start_gui()

# Best plot home
analysis.feature_matrix = None
analysis.umap_parms = {
    "n_neighbors": 12,
    "metric": "manhattan",
    "min_dist": 0.00003,
    "random_state": 20,
}
start_gui()


# Batch correction for all suppliers
analysis.betas_all = None
analysis.betas_sel = None
analysis.set_betas()
df_anno = analysis.idat_handler.samples_annotated.copy()
df_anno["Batch"] = 0
batch_number = 1
# for supplier in df_anno["Supplier"].unique():
# supplier_mask = df_anno["Supplier"] == supplier
for supplier in df_anno["Origin"].unique():
    supplier_mask = df_anno["Origin"] == supplier
    supplier_count = supplier_mask.sum()
    if supplier_count > 5:
        df_anno.loc[supplier_mask, "Batch"] = batch_number
        batch_number += 1

epsilon = 1e-6
transformed_betas = logit(analysis.betas_all.clip(epsilon, 1 - epsilon))
analysis.betas_all = pycombat_norm(
    analysis.betas_all.T,
    # transformed_betas.T,
    df_anno.Batch,
).T
# analysis.betas_all = expit(analysis.betas_all)
start_gui()


# Batch correction for specific suppliers
analysis.set_betas()
df_anno = analysis.idat_handler.samples_annotated
supplier_to_batch = {
    "Nicolle_2019": 1,
    # 'Lyskjaer_2021': 2,
    # 'Cross_2022': 3,
    # 'Dermawan_2023': 4,
}
batches = df_anno["Supplier"].map(supplier_to_batch).fillna(0).astype(int)
analysis.set_betas()
analysis.betas_all = pycombat_norm(
    analysis.betas_all.T,
    batches,
).T
start_gui()

# Reset betas
analysis.betas_all = None


#################################### STATS ####################################

# CN summary plots
rename = {
    "Dedifferentiated chondrosarcoma|G4": "DDCS",
    "ACT|G0": "ACT",
    "Chondrosarcoma|G3": "CS3",
    "Chondrosarcoma|G4": "DDCS",
    "Chondrosarcoma|G2": "CS2",
    "Enchondroma|G0": "EC",
    "Chondrosarcoma|G1": "CS1",
    "Chondrosarcoma|GX": "CSX",
    "Chondrosarcoma|": "CSX",
}
plots = calculate_cn_summary(
    class_=[
        rename[x]
        for x in analysis.idat_handler.features(["WHO_Diagnosis", "Grade"])
    ],
    filename="diagnoses_our_samples",
    own_samples_only=True,
)
plots = calculate_cn_summary(
    class_=analysis.idat_handler.features(["CLUSTER"]),
    filename="clusters_our_samples",
    own_samples_only=True,
)
plots = calculate_cn_summary(
    class_=analysis.idat_handler.features(["WHO_Diagnosis", "Grade"]),
    filename="diagnoses_all_samples",
    own_samples_only=False,
)

# Example CNV plot for publication
analysis.make_cnv_plot("206644420120_R05C01")
cnv_plot = analysis.cnv_plot
cnv_plot.update_layout(
    yaxis_range=[-1.1, 1.1],
    font=dict(size=FONTSIZE),
    margin=dict(t=50),
)

cnv_plot.write_image(
    OUTPUT_DIR / "cnv_plot.jpg",
    format="jpg",
    width=2000,
    height=1000,
    scale=2,
)
cnv_plot.show()

# Calculate statistics
cnv_stats()
calculate_cnv_noise()


############################## VERIFY CLUSTERING ##############################

anno = analysis.idat_handler.samples_annotated
analysis.set_betas()
df_betas = analysis.betas_sel.loc[anno.index]
# analysis.make_umap()
# df_betas = analysis.umap_df[["Umap_x", "Umap_y"]].loc[anno.index]


# Don't standardize the data
kmeans = KMeans(n_clusters=8, random_state=13, n_init=10)
kmeans.fit(df_betas)
anno["Cluster"] = kmeans.labels_
print_clusters()

# Standardize the data
scaler = StandardScaler()
df_scaled = scaler.fit_transform(df_betas)
kmeans = KMeans(n_clusters=8, random_state=43)
kmeans.fit(df_scaled)
anno["Cluster"] = kmeans.labels_
print_clusters()


############################## PUBLICATION PLOT ###############################

# Publication plot
analysis.feature_matrix = None
analysis.umap_parms = {
    "n_neighbors": 12,
    "metric": "manhattan",
    "min_dist": 0.00003,
    "random_state": 27,
    # "random_state": 12974,
}
start_gui()

analysis.idat_handler.selected_columns = [
    "WHO_Diagnosis",
    "Grade",
    "IDH_bool",
]
analysis.umap_df["Umap_color"] = analysis.idat_handler.features(
    analysis.idat_handler.selected_columns
)
rename = {
    "ACT|G1|": "ACT-IDH-UNK",
    "ACT|G1|IDH_MUT": "ACT-IDH-MUT",
    "Chondrosarcoma|G1|": "CS1-IDH-UNK",
    "Chondrosarcoma|G1|IDH_MUT": "CS1-IDH-MUT",
    "Chondrosarcoma|G1|IDH_WT": "CS1-IDH-WT",
    "Chondrosarcoma|G2|IDH_MUT": "CS2-IDH-MUT",
    "Chondrosarcoma|G2|IDH_WT": "CS2-IDH-WT",
    "Chondrosarcoma|G3|IDH_MUT": "CS3-IDH-MUT",
    "Chondrosarcoma|G3|IDH_WT": "CS3-IDH-WT",
    "Chondrosarcoma|GX|": "CSX-IDH-UNK",
    "Dedifferentiated chondrosarcoma|G4|": "DDCS-IDH-UNK",
    "Dedifferentiated chondrosarcoma|G4|IDH_MUT": "DDCS-IDH-MUT",
    "Dedifferentiated chondrosarcoma|G4|IDH_WT": "DDCS-IDH-WT",
    "Enchondroma|G0|": "EC",
    "Enchondroma|G0|IDH_WT": "EC",
}
analysis.umap_df["Umap_color"] = analysis.umap_df["Umap_color"].replace(rename)

fig = get_umap_plot(analysis.umap_df)
fig.write_image(
    OUTPUT_DIR / "umap.jpg",
    format="jpg",
    width=2000,
    height=1000,
    scale=2,
)
fig.show()


analysis.idat_handler.selected_columns = ["CNV_segments_involved"]
analysis.umap_df["Umap_color"] = analysis.idat_handler.features(
    analysis.idat_handler.selected_columns
)
analysis.umap_df["Umap_color"] = pd.to_numeric(analysis.umap_df["Umap_color"])
fig = get_umap_plot(analysis.umap_df, use_discrete_colors=False)
fig.write_image(
    OUTPUT_DIR / "umap_cnv_involved.jpg",
    format="jpg",
    width=2000,
    height=1000,
    scale=2,
)
fig.show()


################################ SUPERVISED ML ################################


fig = None
INCLUDE_G4 = True

analysis.set_betas()

analysis.feature_matrix = analysis.betas_sel
cross_validation(include_g4=INCLUDE_G4)
fig = cross_validation_and_auc_plot("25000 CpG's", fig, include_g4=INCLUDE_G4)

analysis.feature_matrix = analysis.betas_all
cross_validation(include_g4=INCLUDE_G4)
fig = cross_validation_and_auc_plot(
    f"All {analysis.feature_matrix.shape[1]} CpG's", fig, include_g4=INCLUDE_G4
)

set_methyl_cnv_feature_matrix(0, None, df_cnv_bins, False)
cross_validation(include_g4=INCLUDE_G4)
fig = cross_validation_and_auc_plot("CNV bins", fig, include_g4=INCLUDE_G4)

set_methyl_cnv_feature_matrix(0, None, df_cnv_segments, False)
cross_validation(include_g4=INCLUDE_G4)
fig = cross_validation_and_auc_plot("CNV segments", fig, include_g4=INCLUDE_G4)

set_methyl_cnv_feature_matrix(None, None, df_cnv_bins, False)
cross_validation(include_g4=INCLUDE_G4)
fig = cross_validation_and_auc_plot(
    "All CpG's and CNV bins", fig, include_g4=INCLUDE_G4
)

fig.show()

fig_to_save = go.Figure(fig)
fig_to_save.update_layout(
    title_font_size=FONTSIZE,
    yaxis_title_font_size=FONTSIZE - 2,
    xaxis_title_font_size=FONTSIZE - 2,
    legend_font_size=FONTSIZE - 2,
)
fig_to_save.write_image(
    OUTPUT_DIR / "auc.jpg",
    format="jpg",
    width=1000,
    height=1000,
    scale=2,
)


# Run validation functions
analysis.feature_matrix = analysis.betas_all
validate_gui_prediction()

np.random.seed(42)
analysis.feature_matrix = analysis.betas_all
results = validate_gui_prediction_high_vs_low(include_g4=False)
# results = validate_gui_prediction_high_vs_low(include_g4=True)


results = sorted(results, key=lambda x: x["pred_prob_2"], reverse=True)
for result in results:
    print(
        f"Sample: {result['sample_id']}, "
        f"Corr: {result['pred_correct']}, "
        f"True: {result['true_grade_4']}, "
        f"Pred: {result['pred_grade_2']}, "
        f"Prob: {result['pred_prob_2']}, "
    )
