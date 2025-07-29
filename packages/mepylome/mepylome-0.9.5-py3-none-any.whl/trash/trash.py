
# MEMORY LEAK
import gc
import os
import tracemalloc

import psutil

# import objgraph
# from pympler.tracker import SummaryTracker

tracemalloc.start()


def print_mem(msg=""):
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / 1024**2
    print(f"[{msg}] RSS Memory: {mem:.2f} MB")
    # gc.collect()
    # print("Top object types:")
    # for name, count in objgraph.most_common_types()[:10]:
    #     print(f"  {name:<30} {count}")


def print_snapshot_diff(snapshot1, snapshot2):
    top_stats = snapshot2.compare_to(snapshot1, "lineno")
    print("[ Top 10 differences ]")
    for stat in top_stats[:10]:
        print(stat)


print_mem("Start")

from mepylome import *
from mepylome.analysis import *
from mepylome.analysis.methyl_plots import write_cnv_to_disk

# snapshot_0 = tracemalloc.take_snapshot()

print_mem("Before init")

self = MethylAnalysis(
    analysis_dir="~/mepylome/data/salivary_gland_tumors/",
    reference_dir="~/mepylome/cnv_references/",
)

print_mem("After MethylAnalysis init")
# [After MethylAnalysis init] RSS Memory: 907.71 MB

# snapshot_1 = tracemalloc.take_snapshot()
# print_snapshot_diff(snapshot_0, snapshot_1)

self.set_betas()
print_mem("After set_betas")


self.make_umap()
print_mem("After make_umap")
# [After set_betas] RSS Memory: 3063.21 MB

# snapshot_2 = tracemalloc.take_snapshot()
# print_snapshot_diff(snapshot_1, snapshot_2)

ids = self.idat_handler.ids
ids = ids[:30]

write_cnv_to_disk(
    sample_path=[self.idat_handler.id_to_path[x] for x in ids],
    reference_dir=self.reference_dir,
    cnv_dir=self.cnv_dir,
    prep=self.prep,
    do_seg=self.do_seg,
    # n_cores=1,
)
# self.precompute_cnvs()

print_mem("After write_cnv_to_disk")
# [After write_cnv_to_disk] RSS Memory: 5323.46 MB

# snapshot_3 = tracemalloc.take_snapshot()
# print_snapshot_diff(snapshot_2, snapshot_3)

import mepylome

mepylome.clear_cache()

print_mem("After clean_cache")
# snapshot_4 = tracemalloc.take_snapshot()
# print_snapshot_diff(snapshot_3, snapshot_4)

self.idat_handler.selected_columns = ["Methylation class"]
clf_out_sg = self.classify(
    ids=ids,
    clf_list=[
        "none-kbest-et",
        "none-kbest-lr",
    ],
)

print_mem("After clf")
# snapshot_5 = tracemalloc.take_snapshot()
# print_snapshot_diff(snapshot_4, snapshot_5)

self.betas_all = None
self.betas_sel = None
gc.collect()

print_mem("After deleting betas")
# snapshot_6 = tracemalloc.take_snapshot()
# print_snapshot_diff(snapshot_5, snapshot_6)


# Final snapshot
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics("lineno")
print("\nTop memory lines:")
for stat in top_stats[:20]:
    print(stat)


if not annotation.exists():
def format_diagnosis(text):
    text = text.replace('`', "'")
    text = text.replace('´', "'")
    return ' '.join([word.capitalize() if word.islower() else word for word in text.split()])

raw_annotation = Path(CONFIG["raw_annotation"]).expanduser()
idat_handler = IdatHandler(idat_dir, annotation_file=raw_annotation)
new_annotation_df = idat_handler.annotation_df.copy()
new_annotation_df["Methylation_class"] = (
    new_annotation_df["Methylation Class Name"]
    .str.replace(r"^methylation class ", "", regex=True)  # Remove prefix
    .apply(format_diagnosis)
)
new_annotation_df = new_annotation_df.drop(
    columns=["Methylation Class Name"]
)
new_annotation_df.to_excel(
    "~/mepylome/ifp_mepylome_pipeline/sarcoma_annotations.xlsx",
    index=False,
)

# output_dir.mkdir(parents=True, exist_ok=True)
def info_to_html(input_str):
    sections = input_str.strip().split("\n\n")
    full_html = ""
    for section in sections:
        lines = section.strip().split("\n")
        title = lines[0].strip()
        full_html += f"<h2>{title}</h2><table>"
        for line in lines[1:]:
            line = line.strip()
            if ":" in line:
                key, value = [x.strip() for x in line.split(":", 1)]
                full_html += (
                    f"<tr><td class='label'>{key}</td>"
                    f"<td class='value'>{value}</td></tr>"
                )
            else:
                full_html += (
                    f"<tr><td class='label'>{line}</td>"
                    f"<td class='value'></td></tr>"
                )
        full_html += "</table>"
    return full_html.strip()


def prettify_html(html_str):
    soup = BeautifulSoup(html_str, "html.parser")
    return soup.prettify()


print(prettify_html(pretty_html))
import polars as pl


def to_polars(df, index_name="index"):
    df_with_index = df.reset_index()
    if df.index.name is None:
        df_with_index.rename(columns={"index": index_name}, inplace=True)
    pl_df = pl.DataFrame(df_with_index)
    return pl_df


def to_polars(df):
    for col in df.select_dtypes(include=["Int64", "Float64"]).columns:
        df[col] = df[col].astype(
            "float" if "float" in str(df[col].dtype) else "int"
        )
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str)
    return pl.DataFrame(df)


detail_df = self.annotation.detail.df.copy()
detail_df_pl = to_polars(detail_df)

self.annotation._cpg_detail_pl = pl.DataFrame(self.annotation._cpg_detail)

self.ratio_pl = to_polars(self.ratio)


def set_detail(self):
    timer.start()
    if self.verbose:
        log(f"[CNV] {self.probe} Setting detail...")
    timer.stop("0")
    cpg_detail = self.annotation._cpg_detail.copy()
    timer.stop("1")
    cpg_detail["ratio"] = _pd_loc(self.ratio, cpg_detail.IlmnID).ratio.values
    timer.stop("2")
    result = cpg_detail.groupby("Name", dropna=False)["ratio"].agg(
        ["median", "var", "count"]
    )
    timer.stop("3")
    detail_df = self.annotation.detail.df.set_index("Name")
    timer.stop("4")
    detail_df["Median"] = np.nan
    timer.stop("5")
    detail_df["Var"] = np.nan
    timer.stop("6")
    detail_df["N_probes"] = 0
    timer.stop("7")
    idx = cached_index(detail_df.index, result.index.values)
    timer.stop("8")
    detail_df.iloc[
        idx, detail_df.columns.get_indexer(["Median", "Var", "N_probes"])
    ] = result.values
    timer.stop("9")
    detail_df["N_probes"] = detail_df["N_probes"].astype(int)
    timer.stop("10")
    detail_df = detail_df.reset_index()
    timer.stop("11")
    self.detail = pr.PyRanges(detail_df)
    timer.stop("12")


OLD = self.detail.df.copy()


self.annotation_detail_df_pl = pl.from_pandas(self.annotation.detail.df)


def _set_detail(self):
    timer.start()
    if self.verbose:
        log(f"[CNV] {self.probe} Setting detail...")
    timer.stop("0")
    cpg_detail = self.annotation._cpg_detail_pl.clone()
    timer.stop("1")
    ratio_pl = pl.DataFrame(self.ratio.reset_index())
    timer.stop("2")
    cpg_detail = cpg_detail.join(
        ratio_pl, left_on="IlmnID", right_on="index", how="left"
    )
    timer.stop("3")
    result = cpg_detail.group_by("Name").agg(
        [
            pl.col("ratio").median().alias("Median"),
            pl.col("ratio").var().alias("Var"),
            pl.col("ratio").count().alias("N_probes"),
        ]
    )
    timer.stop("4")
    detail_df = pl.from_pandas(self.annotation.detail.df)
    timer.stop("5")
    detail_df = detail_df.join(result, on="Name", how="left")
    timer.stop("6")
    detail_df = self.annotation_detail_df_pl.join(
        result, on="Name", how="left"
    )
    timer.stop("7")
    detail_df = detail_df.with_columns(
        [
            pl.col("Median").fill_null(np.nan),
            pl.col("Var").fill_null(np.nan),
            pl.col("N_probes").fill_null(0),
        ]
    )
    timer.stop("8")
    # Convert to PyRanges
    self.detail = pr.PyRanges(detail_df.to_pandas())
    timer.stop("9")


_set_detail(self)

NEW = self.detail.df.copy()
NEW = NEW[OLD.columns]

NEW.equals(OLD)


def get_indexer_numpy(left_arr, right_arr):
    index_map = {val: idx for idx, val in enumerate(left_arr)}
    return np.array([index_map.get(val, -1) for val in right_arr])


def get_indexer_polars(left_arr, right_arr):
    left_df = pl.DataFrame({"values": left_arr})
    right_df = pl.DataFrame({"values": right_arr})
    # left_df = left_df.with_columns(pl.col("values").cast(pl.Int64).alias("index"))
    # right_df = right_df.with_columns(pl.col("values").cast(pl.Int64).alias("index_right"))
    # joined_df = left_df.join(right_df, left_on="values", right_on="values", how="left")
    # indices = joined_df["index"].to_numpy()
    # return indices if indices.size > 0 else -1


# Use best 20000 samples selected from SelectKBest for UMAP
X = analysis.betas_all
y = analysis.idat_handler.features()
clf = SelectKBest(k=20000)
clf.fit(X, y)
best_cpgs = X.columns[clf.get_support()]
analysis.cpgs = best_cpgs
analysis.make_umap()
analysis.run_app(open_tab=True)


import cupy as cp


def _preprocess_raw_old_gpu(self, ci):
    """Same as _preprocess_raw but with GPU acceleration using CuPy."""
    # Allocate the arrays on the GPU (using CuPy instead of NumPy)
    self.methyl = cp.full((len(self.probes), len(ci["idx"])), cp.nan)
    self.unmethyl = cp.full((len(self.probes), len(ci["idx"])), cp.nan)
    # Perform element-wise assignment using GPU arrays
    self.methyl[:, ci["idx_1_red__"]] = self._red[:, ci["ids_1_red_b"]]
    self.methyl[:, ci["idx_1_grn__"]] = self._grn[:, ci["ids_1_grn_b"]]
    self.methyl[:, ci["idx_2______"]] = self._grn[:, ci["ids_2_____a"]]
    self.unmethyl[:, ci["idx_1_red__"]] = self._red[:, ci["ids_1_red_a"]]
    self.unmethyl[:, ci["idx_1_grn__"]] = self._grn[:, ci["ids_1_grn_a"]]
    self.unmethyl[:, ci["idx_2______"]] = self._red[:, ci["ids_2_____a"]]
    # Transfer the data back to the CPU (if needed)
    self.methyl = cp.asnumpy(self.methyl)
    self.unmethyl = cp.asnumpy(self.unmethyl)
    self.methyl_index = ci["idx"]
    self.methyl_ilmnid = ci["ilmnid"]


timer.start()
self.ids = reduce(np.intersect1d, [idat.illumina_ids for idat in grn_idat])
timer.stop()

timer.start()
ids_sets = [set(idat.illumina_ids) for idat in grn_idat]
cpgs = set.intersection(*ids_sets)
timer.stop()

illumina_ids = np.concatenate([idat.illumina_ids for idat in grn_idat])
self.ids = np.lib.arraysetops.intersect1d(illumina_ids, return_indices=False)


self = Manifest("450k")
epic = Manifest("epic")
epicv2 = Manifest("epicv2")

import numba


# This is 40% faster
def new_preprocess_raw(self, ci):
    self.methyl = np.full((len(self.probes), len(ci["idx"])), np.nan)
    self.unmethyl = np.full((len(self.probes), len(ci["idx"])), np.nan)
    _preprocess_raw_numba(
        self.methyl,
        self.unmethyl,
        self._grn,
        self._red,
        ci["ids_1_grn_a"],
        ci["ids_1_grn_b"],
        ci["ids_1_red_a"],
        ci["ids_1_red_b"],
        ci["ids_2_____a"],
        ci["idx_1_grn__"],
        ci["idx_1_red__"],
        ci["idx_2______"],
    )
    self.methyl_index = ci["idx"]
    self.methyl_ilmnid = ci["ilmnid"]


@numba.njit
def _preprocess_raw_numba(
    methyl,
    unmethyl,
    grn,
    red,
    ids_1_grn_a,
    ids_1_grn_b,
    ids_1_red_a,
    ids_1_red_b,
    ids_2_____a,
    idx_1_grn__,
    idx_1_red__,
    idx_2______,
):
    methyl[:, idx_1_red__] = red[:, ids_1_red_b]
    methyl[:, idx_1_grn__] = grn[:, ids_1_grn_b]
    methyl[:, idx_2______] = grn[:, ids_2_____a]
    unmethyl[:, idx_1_red__] = red[:, ids_1_red_a]
    unmethyl[:, idx_1_grn__] = grn[:, ids_1_grn_a]
    unmethyl[:, idx_2______] = red[:, ids_2_____a]


from numba import njit


@njit
def numba_merge_bins(matrix, min_probes_per_bin, verbose=False):
    I_START = 0
    I_END = 1
    I_N_PROBES = 2
    INVALID = np.iinfo(np.int64).max
    while np.any(matrix[:, I_N_PROBES] < min_probes_per_bin):
        i_min = np.argmin(matrix[:, I_N_PROBES])
        n_probes_left = INVALID
        n_probes_right = INVALID
        # Left
        if i_min > 0:
            delta_left = np.argmax(
                matrix[i_min - 1 :: -1, I_N_PROBES] != INVALID
            )
            i_left = i_min - delta_left - 1
            if (
                matrix[i_left, I_N_PROBES] != INVALID
                and matrix[i_min, I_START] == matrix[i_left, I_END]
            ):
                n_probes_left = matrix[i_left, I_N_PROBES]
        # Right
        if i_min < len(matrix) - 1:
            delta_right = np.argmax(matrix[i_min + 1 :, I_N_PROBES] != INVALID)
            i_right = i_min + delta_right + 1
            if (
                matrix[i_right, I_N_PROBES] != INVALID
                and matrix[i_min, I_END] == matrix[i_right, I_START]
            ):
                n_probes_right = matrix[i_right, I_N_PROBES]
        # Invalid
        if n_probes_left == INVALID and n_probes_right == INVALID:
            matrix[i_min, I_N_PROBES] = INVALID
            continue
        elif n_probes_right == INVALID or n_probes_left <= n_probes_right:
            i_merge = i_left
        else:
            i_merge = i_right
        matrix[i_merge, I_N_PROBES] += matrix[i_min, I_N_PROBES]
        matrix[i_merge, I_START] = min(
            matrix[i_merge, I_START], matrix[i_min, I_START]
        )
        matrix[i_merge, I_END] = max(
            matrix[i_merge, I_END], matrix[i_min, I_END]
        )
        matrix[i_min, I_N_PROBES] = INVALID
    return matrix


# z = numba_merge_bins(
#     df[["Start", "End", "n_probes"]].values.astype(np.int64),
#     min_probes_per_bin,
#     verbose=True,
# )


swan = np.full((len(self.probes), len(self.methyl_index)), np.nan)
for i in range(len(self.probes)):
    for probe_type in [ProbeType.ONE, ProbeType.TWO]:
        curr_intensity = intensity[i, all_indices[probe_type]]
        x = rankdata(curr_intensity) / len(curr_intensity)
        xp = np.sort(x[random_indices[probe_type]])
        fp = sorted_subset_intensity[i, :]
        # xp = intensity[i,random_indices[probe_type]]
        # x = normed_rank[i,:]
        intensity_min = np.min(curr_intensity[random_indices[probe_type]])
        intensity_max = np.max(curr_intensity[random_indices[probe_type]])
        i_max = np.where(x > np.max(xp))
        i_min = np.where(x < np.min(xp))
        delta_max = curr_intensity[i_max] - intensity_max
        delta_min = curr_intensity[i_min] - intensity_min
        interp = np.interp(x=x, xp=xp, fp=fp)
        interp[i_max] = np.max(fp) + delta_max
        interp[i_min] = np.min(fp) + delta_min
        interp = np.where(interp <= 0, bg_intensity[i], interp)
        swan[i, all_indices[probe_type]] = interp


################### NOOB

from scipy.stats import norm


def huber(y, k=1.5, tol=1.0e-6):
    y = y[~np.isnan(y)]
    n = len(y)
    mu = np.median(y)
    s = np.median(np.abs(y - mu)) * 1.4826
    if s == 0:
        raise ValueError("Cannot estimate scale: MAD is zero for this sample")
    while True:
        yy = np.clip(y, mu - k * s, mu + k * s)
        mu1 = np.sum(yy) / n
        if np.abs(mu - mu1) < tol * s:
            break
        mu = mu1
    return mu, s


def normexp_signal(par, x):
    mu = par[0]
    sigma = np.exp(par[1])
    sigma2 = sigma * sigma
    alpha = np.exp(par[2])
    if alpha <= 0:
        raise ValueError("alpha must be positive")
    if sigma <= 0:
        raise ValueError("sigma must be positive")
    mu_sf = x - mu - sigma2 / alpha
    log_dnorm = norm.logpdf(0, loc=mu_sf, scale=sigma)
    log_pnorm = norm.logsf(0, loc=mu_sf, scale=sigma)
    signal = mu_sf + sigma2 * np.exp(log_dnorm - log_pnorm)
    o = ~np.isnan(signal)
    if np.any(signal[o] < 0):
        print(
            "Limit of numerical accuracy reached with very low intensity or "
            "very high background:\nsetting adjusted intensities to small "
            "value"
        )
        signal[o] = np.maximum(signal[o], 1e-6)
    return signal


def normexp_get_xs(xf, controls=None, offset=50, param=None):
    xf_idx = xf.index
    xf_cols = xf.columns
    result = np.empty(xf.shape)
    n_probes = xf.shape[1]
    if param is None:
        if controls is None:
            ValueError("'controls' or 'param' must be given")
        alpha = np.empty(n_probes)
        mu = np.empty(n_probes)
        sigma = np.empty(n_probes)
        for i in range(n_probes):
            mu[i], sigma[i] = huber(controls[:, i])
            alpha[i] = max(huber(xf.values[:, i])[0] - mu[i], 10)
        param = np.column_stack((mu, np.log(sigma), np.log(alpha)))
    for i in range(n_probes):
        result[:, i] = normexp_signal(param[i], xf.values[:, i])
    return {
        "xs": (result + offset).T,
        "param": param,
    }


offset = 15
dye_corr = True
verbose = False
dye_method = "single"

raw = RawData([ref0, ref1])
self = MethylData(raw, prep="raw")

timer.start()

grn = raw.grn
red = raw.red

timer.stop("0")

i_grn = self.manifest.probe_info(ProbeType.ONE, Channel.GRN)
i_red = self.manifest.probe_info(ProbeType.ONE, Channel.RED)

timer.stop("1")

grn_oob = pd.concat(
    [grn.loc[i_red.AddressA_ID], grn.loc[i_red.AddressB_ID]], axis=0
)
red_oob = pd.concat(
    [red.loc[i_grn.AddressA_ID], red.loc[i_grn.AddressB_ID]], axis=0
)

timer.stop("2.0")

control_probes = self.manifest.control_data_frame

timer.stop("2.1")

control_probes = control_probes[
    control_probes.Address_ID.isin(red.index)
].reset_index(drop=True)

timer.stop("3")

self.methylated[self.methylated <= 0] = 1
self.unmethylated[self.unmethylated <= 0] = 1

timer.stop("4.0")

manifest_df = self.manifest.data_frame.iloc[self.methyl_index]

timer.stop("4.1")

probe_type = manifest_df.Probe_Type
color = manifest_df.Color_Channel

timer.stop("5")

ext_probe_type = np_ext_probe_type(probe_type, color)

timer.stop("6")

i_grn_idx = manifest_df.index[ext_probe_type == ExtProbeType.ONE_GRN]
i_red_idx = manifest_df.index[ext_probe_type == ExtProbeType.ONE_RED]
ii_idx = manifest_df.index[ext_probe_type == ExtProbeType.TWO]

timer.stop("7.0")

grn_m = self.methylated.iloc[i_grn_idx]
grn_u = self.unmethylated.iloc[i_grn_idx]
grn_2 = self.methylated.iloc[ii_idx]

timer.stop("7.1")

xf_grn = pd.concat([grn_m, grn_u, grn_2], axis=0)

timer.stop("7.2")

xs_grn = normexp_get_xs(xf_grn, controls=grn_oob.values, offset=offset)

timer.stop("8")

cumsum = np.cumsum([0, len(grn_m), len(grn_u), len(grn_2)])
range_grn_m = range(cumsum[0], cumsum[1])
range_grn_u = range(cumsum[1], cumsum[2])
range_grn_2 = range(cumsum[2], cumsum[3])

timer.stop("9.0")

red_m = self.methylated.iloc[i_red_idx]
red_u = self.unmethylated.iloc[i_red_idx]
red_2 = self.unmethylated.iloc[ii_idx]

timer.stop("9.1")

xf_red = pd.concat([red_m, red_u, red_2], axis=0)

timer.stop("9.2")

xs_red = normexp_get_xs(xf_red, controls=red_oob.values, offset=offset)

timer.stop("10")

cumsum = np.cumsum([0, len(red_m), len(red_u), len(red_2)])
range_red_m = range(cumsum[0], cumsum[1])
range_red_u = range(cumsum[1], cumsum[2])
range_red_2 = range(cumsum[2], cumsum[3])

timer.stop("11")

methyl = np.empty(self.methyl.shape)
unmethyl = np.empty(self.unmethyl.shape)

timer.stop("12")

methyl[:, i_grn_idx] = xs_grn["xs"][:, range_grn_m]
unmethyl[:, i_grn_idx] = xs_grn["xs"][:, range_grn_u]

timer.stop("13")

methyl[:, i_red_idx] = xs_red["xs"][:, range_red_m]
unmethyl[:, i_red_idx] = xs_red["xs"][:, range_red_u]

timer.stop("14")

methyl[:, ii_idx] = xs_grn["xs"][:, range_grn_2]
unmethyl[:, ii_idx] = xs_red["xs"][:, range_red_2]

timer.stop("15")

grn_control = grn.loc[control_probes.Address_ID]
red_control = red.loc[control_probes.Address_ID]

timer.stop("16")

xcs_grn = normexp_get_xs(grn_control, param=xs_grn["param"], offset=offset)
xcs_red = normexp_get_xs(red_control, param=xs_red["param"], offset=offset)

timer.stop("17.0")

cg_controls_idx = control_probes[
    control_probes.Control_Type.isin(["NORM_C", "NORM_G"])
].index
at_controls_idx = control_probes[
    control_probes.Control_Type.isin(["NORM_A", "NORM_T"])
].index

timer.stop("18")

grn_avg = np.mean(xcs_grn["xs"][:, cg_controls_idx], axis=1)
red_avg = np.mean(xcs_red["xs"][:, at_controls_idx], axis=1)

timer.stop("19")

red_grn_ratio = red_avg / grn_avg

timer.stop("20")

if dye_method == "single":
    red_factor = 1 / red_grn_ratio
    grn_factor = np.array([1, 1])
elif dye_method == "reference":
    ref_idx = np.argmin(np.abs(red_grn_ratio - 1))
    ref = (grn_avg + red_avg)[ref_idx] / 2
    if np.isnan(ref):
        raise ValueError("'ref_idx' refers to an array that is not present")
    grn_factor = ref / grn_avg
    red_factor = ref / red_avg

timer.stop("21")


methyl[:, i_red_idx] *= np.reshape(red_factor, (2, 1))
unmethyl[:, i_red_idx] *= np.reshape(red_factor, (2, 1))
unmethyl[:, ii_idx] *= np.reshape(red_factor, (2, 1))

timer.stop("22")

if dye_method == "reference":
    methyl[:, i_grn_idx] *= np.reshape(grn_factor, (2, 1))
    unmethyl[:, i_grn_idx] *= np.reshape(grn_factor, (2, 1))
    methyl[:, ii_idx] *= np.reshape(grn_factor, (2, 1))

timer.stop("23")

methyl_df = pd.DataFrame(
    methyl.T, index=self.methyl_ilmnid, columns=self.probes
)
unmethyl_df = pd.DataFrame(
    unmethyl.T, index=self.methyl_ilmnid, columns=self.probes
)

timer.stop("24")


# Noob
# >>> methyl_df
# 3999997083_R02C02  5775446049_R06C01
# cg13869341       18532.097447       31249.660200
# cg14008030        7381.869629       17687.621094
# cg12045430         123.438129         273.567078
# cg20826792         530.955529        1632.319576
# cg00381604         130.188501         247.995769
# ...                       ...                ...
# cg17939569          87.637659        5362.623047
# cg13365400          91.106116        5940.623047
# cg21106100          78.593774        7248.623047
# cg08265308         121.063723        5180.034367
# cg14273923          90.267410       10678.623047

# [485512 rows x 2 columns]
# >>> unmethyl_df
# 3999997083_R02C02  5775446049_R06C01
# cg13869341        1131.388267        4347.401849
# cg14008030        2242.245217       11188.378244
# cg12045430        7880.098972       15914.997346
# cg20826792        9914.292138       16576.082461
# cg00381604        8556.804514       13605.383527
# ...                       ...                ...
# cg17939569         110.009358        1331.076523
# cg13365400         114.410604        5418.527098
# cg21106100         117.836945         497.635410
# cg08265308         125.480597         263.723241
# cg14273923         149.288049        4527.317418


# Noob
# > head(M)
self.methylated.loc["cg00050873"]  #          159.8342        17290.1654
self.methylated.loc["cg00212031"]  #          137.8445          279.9552
self.methylated.loc["cg00213748"]  #          137.6014         1669.8786
self.methylated.loc["cg00214611"]  #          115.2945          257.6655
self.methylated.loc["cg00455876"]  #          135.4455         4991.7508
self.methylated.loc["cg01707559"]  #          136.6361          351.7144
self.methylated.loc["ch.22.44116734F"]  #         213.94563          228.5676
self.methylated.loc["ch.22.909671F"]  #           407.93938          286.5847
self.methylated.loc["ch.22.46830341F"]  #         110.40962          361.7824
self.methylated.loc["ch.22.1008279F"]  #           90.47575          208.9519
self.methylated.loc["ch.22.47579720R"]  #         605.87659         1397.7026
self.methylated.loc["ch.22.48274842R"]  #         249.49046         2775.6227

# > head(U)
self.unmethylated.loc["cg00050873"]  #          131.0774          940.8142
self.unmethylated.loc["cg00212031"]  #          130.8542         7701.6419
self.unmethylated.loc["cg00213748"]  #          113.8862          291.8196
self.unmethylated.loc["cg00214611"]  #          124.6565         7961.0551
self.unmethylated.loc["cg00455876"]  #          183.1258          509.7173
self.unmethylated.loc["cg01707559"]  #          128.8744         9980.5724
self.unmethylated.loc["ch.22.44116734F"]  #          2724.296          5174.456
self.unmethylated.loc["ch.22.909671F"]  #            1527.832          2677.953
self.unmethylated.loc["ch.22.46830341F"]  #          6557.262         13366.890
self.unmethylated.loc["ch.22.1008279F"]  #           2083.260          7672.353
self.unmethylated.loc["ch.22.47579720R"]  #          7800.607         12882.931
self.unmethylated.loc["ch.22.48274842R"]  #         13027.749         14065.632


for x in grn_idat_files:
    # x = grn_idat_files[0]
    y = Path(BETA_VALUES, x.name)
    data_x = np.fromfile(x, dtype=np.float64)
    data_y = np.fromfile(y, dtype=np.float64)
    c = np.corrcoef(data_x, data_y)
    print(c[0, 1])


pdp = lambda x: print(x.to_string())

timer = Timer()


np.random.seed(0)
methyl_450k = pd.DataFrame(
    np.random.rand(1000, len(cpgs_450k)), columns=cpgs_450k
)
methyl_epic = pd.DataFrame(
    np.random.rand(500, len(cpgs_epic)), columns=cpgs_epic
)
methyl_epicv2 = pd.DataFrame(
    np.random.rand(500, len(cpgs_epicv2)), columns=cpgs_epicv2
)

file_path = "/tmp/mepylome/random_data.h5"
file_path_ = "/tmp/mepylome/random_data_.h5"

timer.start()
methyl_epicv2.to_hdf(file_path_, "data")
# methyl_epicv2.to_parquet(file_path_, engine="pyarrow")
timer.stop()
timer.start()
df3 = pd.read_hdf(file_path_)
# df3=pd.read_parquet(file_path_)
timer.stop()

with pd.HDFStore(file_path, mode="w") as store:
    store.put("methyl_450k", methyl_450k, format="table")
    store.put("methyl_epic", methyl_epic, format="table")
    store.put("methyl_epicv2", methyl_epicv2, format="table")

overlap = set(cpgs_450k) & set(cpgs_epic) & set(cpgs_epicv2)

overlap_array = np.array(list(overlap))
cols_to_retrieve = overlap_array[:50000]

timer.start()
with pd.HDFStore(file_path, mode="r") as store:
    df1 = store["methyl_450k"][cols_to_retrieve]
    df2 = store["methyl_epic"][cols_to_retrieve]
    df3 = store["methyl_epicv2"][cols_to_retrieve]

timer.stop()

timer.start()
df3 = pd.read_hdf(file_path_, columns=overlap_array)
timer.stop()


def retrieve_columns(store, key, columns):
    return store.select(key, columns=columns)


timer.start()
with pd.HDFStore(file_path, mode="r") as store:
    df1 = retrieve_columns(store, "methyl_450k", cols_to_retrieve)
    df2 = retrieve_columns(store, "methyl_epic", cols_to_retrieve)
    df3 = retrieve_columns(store, "methyl_epicv2", cols_to_retrieve)

timer.stop()


matrix_size = (1000, len(cpgs_epicv2))
matrix = np.random.rand(*matrix_size).astype(np.float32)

np.save(file_path_ + ".npy", matrix)

timer.start()
loaded_matrix = np.load(file_path_ + ".npy")
timer.stop()


with h5py.File(file_path_, "w") as f:
    f.create_dataset("data", data=matrix)


def get_submatrix(file_path, row_indices, col_indices):
    with h5py.File(file_path, "r") as f:
        data = f["data"]
        submatrix = data[row_indices, :][:, col_indices]
        return submatrix


row_indices = np.arange(0, 1000)
col_indices = np.arange(2000, 52000)

timer.start()
submatrix = get_submatrix(file_path_, row_indices, rand_cols)
timer.stop()


with h5py.File(file_path_, "r") as f:
    data = f["data"]
    submatrix = data[row_indices, :][:, col_indices]
    pass


fp = np.memmap(file_path_, dtype="float32", mode="w+", shape=matrix.shape)
fp[:] = matrix[:]
del fp  # Flushes changes to disk

timer.start()
fp = np.memmap(file_path_, dtype="float32", mode="r", shape=matrix.shape)
selected_columns = fp[:, col_indices]
del fp  # Flushes changes to disk
timer.stop()
