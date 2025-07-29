import gzip
import hashlib
import inspect
import logging
import os
import pickle
import re
import sys
import time
import timeit
import warnings
from functools import lru_cache, partial, reduce, wraps
from pathlib import Path
from urllib.parse import urljoin

import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import pkg_resources
import plotly.express as px
import plotly.graph_objs as go
import pyranges as pr
import scipy.stats as stats
import xxhash
from scipy.stats import norm, rankdata
from sklearn.linear_model import LinearRegression
from tqdm import tqdm

from mepylome import *
from mepylome.analysis.methyl import *
from mepylome.analysis.methyl_aux import *
from mepylome.analysis.methyl_clf import *
from mepylome.dtypes import *
from mepylome.dtypes.cache import *
from mepylome.dtypes.cnv import *
from mepylome.dtypes.manifests import *
from mepylome.dtypes.plots import *
from mepylome.tests.helpers import *
from mepylome.tests.write_idat import *
from mepylome.utils import *
from mepylome.utils.files import *

pdp = lambda x: print(x.to_string())

# warnings.simplefilter(action="ignore", category=FutureWarning)

# TODO: Delete button for uploaded files and corresponding betas/cnv
# TODO: Add warning if uploaded IDAT is in analysis_dir

ENDING_GZ = ".gz"
ENDING_GRN = "_Grn.idat"
ENDING_RED = "_Red.idat"


LOGGER = logging.getLogger(__name__)
print("imports done")

timer = Timer()

smp_dir = Path("~/mepylome/tutorial/tutorial_analysis").expanduser()
ref_dir = Path("~/mepylome/tutorial/tutorial_reference/").expanduser()

smp_files = sorted(smp_dir.glob("*"))[:8]
ref_files = sorted(ref_dir.glob("*"))[:5]

smp0, smp1, smp2, smp3, smp4, smp5, smp6, smp7 = map(str, smp_files)
ref0, ref1, ref2, ref3, ref4 = map(str, ref_files)

timer = Timer()
idat_data = IdatParser(smp0)
timer.stop("Parsing IDAT")

# timer = Timer()
# idat_data = _IdatParser(smp0)
# timer.stop("Parsing IDAT C++")

timer = Timer()
idat_data = IdatParser(smp0, intensity_only=True)
timer.stop("Parsing IDAT")


GENES = pkg_resources.resource_filename(
    "mepylome", "data/gene_loci_epicv2.tsv.gz"
)
GAPS = pkg_resources.resource_filename("mepylome", "data/gaps.csv.gz")


# quit()

timer.start()
# refs_raw = RawData(ref_dir)
refs_raw = RawData([ref0, ref1])
timer.stop("RawData ref")

timer.start()
ref_methyl = MethylData(refs_raw)
timer.stop("MethylData ref")


timer.start()
manifest = Manifest("epic")
timer.stop("Manifest")


timer.start()
sample_raw = RawData(smp0)
timer.stop("RawData sample")

timer.start()
sample_methyl = MethylData(sample_raw, prep="illumina")
timer.stop("MethylData sample")

timer.start()
betas = sample_methyl.betas_at(cpgs=None, fill=0.49)
timer.stop("beta 1")

timer.start()
betas = sample_methyl.betas_at(cpgs=None, fill=0.49)
timer.stop("beta 2")

gap = pr.PyRanges(pd.read_csv(GAPS))
gap.Start -= 1

timer.start()
genes_df = pd.read_csv(GENES, sep="\t")
genes_df.Start -= 1
genes = pr.PyRanges(genes_df)
genes = genes[["Name"]]
timer.stop("genes")

timer.start()
annotation = Annotation(manifest, gap=gap, detail=genes)
timer.stop("Annotation")

timer.start()
cnv = CNV(sample_methyl, ref_methyl, annotation)
timer.stop("CNV init")


timer.start()
cnv.set_bins()
timer.stop("CNV set_bins")

timer.start()
cnv.set_detail()
timer.stop("CNV set_detail")

timer.start()
cnv.set_segments()
timer.stop("CNV set_segments")

self = cnv
sample = sample_methyl
reference = ref_methyl

timer.start()
cnv = CNV.set_all(sample_methyl, ref_methyl)
timer.stop("CNV set_all")


quit()

timer.start()
# r = RawData(smp7)
r = RawData([ref0, ref1])
timer.stop("1")
m = MethylData(r)
timer.stop("2")
m.illumina_control_normalization()
timer.stop("2.1")
m.illumina_bg_correction()
timer.stop("2.2")
m.preprocess_raw_cached()
timer.stop("2.5")
b = m.beta
timer.stop("3")


cn = CNV(m, ref_methyl, annotation)
imer.stop("2")
timer.stop("3")

self = sample_methyl
self = ref_methyl

timer.start()
cn._set_bins()
# cn.set_bins()
timer.stop("4")
cn.bins

cn.set_detail()
timer.stop("5")
cn.set_segments()
timer.stop("file to csv")


filepath_gz = Path("~/Downloads/manifest.pkl.gz").expanduser()
filepath = Path("~/Downloads/manifest.pkl").expanduser()

timer.start()
with gzip.open(filepath_gz, "wb") as f:
    pickle.dump(manifest, f)

timer.stop("pickel")

timer.start()
with gzip.open(filepath_gz, "rb") as f:
    loaded_data = pickle.load(f)

timer.stop("pickel")


timer.start()
with open(filepath, "wb") as f:
    pickle.dump(manifest, f)

timer.stop("pickel")

timer.start()
with open(filepath, "rb") as f:
    loaded_data = pickle.load(f)

timer.stop("pickel")


# ANNOTATION
filepath = Path("~/Downloads/annotation.pkl").expanduser()
with open(filepath, "wb") as f:
    pickle.dump(annotation, f)

with open(filepath, "rb") as f:
    loaded_data = pickle.load(f)

filepath = Path("~/Downloads/ref_meth_data.pkl").expanduser()
with open(filepath, "wb") as f:
    pickle.dump(ref_meth_data, f)

with open(filepath, "rb") as f:
    loaded_data = pickle.load(f)

timer.start()
self = MethylData(file=smp6, prep="illumina")
timer.stop("*")


timer.start()
self = MethylData(raw, prep="noob")
timer.stop("*")

timer.start()
self = MethylData(sample_raw, prep="noob")
timer.stop("*")

timer.start()
self = MethylData(sample_raw, prep="swan")
timer.stop("*")


timer.start()
idat_data = mepylome._IdatParser(smp0)
timer.stop("Parsing C++")

timer.start()
py_idat_data = IdatParser(smp0, intensity_only=False)
timer.stop("Parsing Python")


# 0 Home
self = MethylAnalysis(
    analysis_dir="/data/epidip_IDAT",
    reference_dir="/data/ref_IDAT",
    overlap=False,
    cpgs=["450k", "epic", "epicv2"],
    load_full_betas=True,
)

# 1 Brain
self = MethylAnalysis(
    analysis_dir="/mnt/ws528695/data/epidip_IDAT",
    reference_dir="/data/ref_IDAT",
    overlap=True,
    load_full_betas=True,
    debug=True,
    # cpgs=["450k", "epic"],
)

timer.start()
reference_dir = "/data/ref_IDAT"
self = ReferenceMethylData(reference_dir, save_to_disk=True)
ref_meth_data = ReferenceMethylData(reference_dir)
timer.stop()

# 2 Chondrosarcoma
cpgs = Manifest("epic").methylation_probes
blacklist = pd.read_csv("~/Downloads/cpg_blacklist.csv", header=None)
cpgs = np.array(list(set(cpgs) - set(blacklist.iloc[:, 0])))
self = MethylAnalysis(
    # analysis_dir="/data/idat_CSA/",
    analysis_dir="/mnt/storage/sarcoma_idat/csa_project/",
    reference_dir="/data/ref_IDAT",
    n_cpgs=25000,
    load_full_betas=True,
    overlap=False,
    cpgs=cpgs,
    debug=True,
)

# 3 10 Samples
self = MethylAnalysis(
    analysis_dir="/mnt/ws528695/data/epidip_IDAT_10",
    reference_dir="/data/ref_IDAT",
    overlap=False,
    debug=True,
)

# 4 166 Samples
self = MethylAnalysis(
    analysis_dir="/mnt/ws528695/data/epidip_IDAT_116",
    reference_dir="/data/ref_IDAT",
    overlap=False,
    debug=True,
)

# 5 GSE140686_RAW
self = MethylAnalysis(
    analysis_dir="/mnt/storage/cns_tumours/",
    reference_dir="/data/ref_IDAT",
    overlap=False,
    debug=True,
    load_full_betas=False,
)

# 6 Tutorial
self = MethylAnalysis(
    analysis_dir="~/mepylome/tutorial/tutorial_analysis",
    reference_dir="~/mepylome/tutorial/tutorial_reference",
    test_dir="~/mepylome/tutorial/test_dir",
    debug=True,
    verbose=True,
    load_full_betas=False,
    do_seg=True,
)

self.run_app(open_tab=True)

# 7 Sarcoma
self = MethylAnalysis(
    analysis_dir="~/Downloads/CSA/E-MTAB-9875",
    reference_dir="/data/ref_IDAT",
    n_cpgs=25000,
    load_full_betas=True,
    debug=True,
)

# 8 Error file
cpgs = Manifest("epic").methylation_probes
self = MethylAnalysis()
self = MethylAnalysis(
    analysis_dir="~/Downloads/mepylome_test_06022025",
    reference_dir="/data/ref_IDAT/",
    debug=True,
    verbose=True,
    do_seg=True,
)

self = MethylAnalysis()
self.run_app(open_tab=True)
self.make_umap()
self.set_betas()

mfile = Path(
    "~/Downloads/Screening_Array_GSE270195_RAW/GSA-24v3-0_A1.csv"
    # "/applications/mepylome_cache/infinium-methylationepic-v-1-0-b5-manifest-file.csv"
).expanduser()
manifest = Manifest(raw_path=mfile)
idat_file = (
    Path("~/Downloads/Screening_Array_GSE270195_RAW")
    / "GSM8336639_204009170074_R01C01_Grn.idat.gz"
)
rdata = RawData(idat_file, manifest=manifest)

from cuml.manifold import UMAP

umap_2d = UMAP(**self.umap_parms).fit_transform(matrix_to_use)


import cupy as cp
import numpy as np
import plotly.express as px
from cuml.manifold import UMAP

np.random.seed(42)
matrix_to_use = cp.asarray(np.random.rand(1000, 50))
matrix_to_use = cp.asarray(analysis.betas_all)
umap_parms = {"n_neighbors": 15, "min_dist": 0.1}
umap_2d = UMAP(**umap_parms).fit_transform(matrix_to_use).get()
fig = px.scatter(x=umap_2d[:, 0], y=umap_2d[:, 1])
fig.show()

print(umap_2d)


np.random.seed(42)
matrix_to_use = cp.asarray(np.random.rand(1000, 50))  # Convert to GPU array
umap_parms = {"n_components": 2, "n_neighbors": 15, "min_dist": 0.1}
umap_2d = UMAP(**umap_parms).fit_transform(matrix_to_use)
umap_2d = cp.asnumpy(umap_2d)  # Convert back to NumPy for plotting
fig = px.scatter(x=umap_2d[:, 0], y=umap_2d[:, 1])
fig.show()

config_path = Path(
    "~/MEGA/programming/mepylome/scripts/diagnostics/config.yaml"
).expanduser()


DIR = Path.home() / "mepylome" / "tutorial"
ANALYSIS_DIR = DIR / "tutorial_analysis"
REFERENCE_DIR = DIR / "tutorial_reference"
from mepylome.utils import setup_tutorial_files

setup_tutorial_files(ANALYSIS_DIR, REFERENCE_DIR)
idat_file = ANALYSIS_DIR / "200925700125_R07C01_Grn.idat"
idat_data = IdatParser(idat_file)
methyl_data = MethylData(file=idat_file)
reference = MethylData(file=REFERENCE_DIR)
cnv = CNV.set_all(methyl_data, reference)
cnv.plot()

short_keys = [
    "analysis_dir",
    "prep",
    "n_cpgs",
    "cpg_selection",
    "analysis_ids",
    "test_ids",
]


class HashManager:
    def __init__(self, short_keys, long_keys):
        self._internal_cpgs_hash = None
        self.short_keys = short_keys
        self.long_keys = long_keys
        self.key_cache = {x: None for x in long_keys}

    def delete(self, key):
        self.long_keys[key] = None

    def get(self, key):
        if key in short_keys:
            return key
        cache = key_cache.get(key)
        if cache is not None:
            return cache

        self.key_cache[key] = value
        return value
        return self._internal_cpgs_hash

    def get_test_files_hash(self):
        if not self.parent.test_dir.exists():
            return ""
        return input_args_id(
            extra_hash=sorted(str(x) for x in self.parent.test_dir.iterdir())
        )

    def get_vars_or_hashes(self):
        vars_hash = {key: getattr(self.parent, key) for key in self.short_keys}
        vars_hash.update(
            {
                "cpgs": self.get_cpgs_hash(),
                "test_files": self.get_test_files_hash(),
            }
        )
        return vars_hash

    def reset_cpgs_hash(self):
        self._internal_cpgs_hash = None


dependencies = ["analysis_dir", "prep", "output_dir"]


logger = logging.getLogger(__name__)


class CacheManager:
    def __init__(self, class_instance):
        self.cache = {}
        self.dependencies = {}
        self.class_instance = class_instance
        self.previous = {}
        self.previous_hashes = {}

    def set_dependencies(self, key, dependencies):
        if key not in self.dependencies:
            self.dependencies[key] = dependencies
            self._update(key, log=False)
        # for dep in dependencies:
        #     self._update(dep)

    def get(self, key):
        """Retrieve a cached value if dependencies haven't changed."""
        self._update(key)
        return self.cache.get(key)

    def set_value(self, key, value):
        """Store a value in the cache."""
        self.cache[key] = value

    def _value_or_hash(self, key):
        hash_value = self.previous_hashes.get(key)
        if hash_value:
            return hash_value
        value = getattr(self.class_instance, key)
        if hasattr(value, "__len__"):
            hash_value = input_args_id(value)
            self.previous_hashes[key] = hash_value
            return hash_value
        return value

    def _update(self, key, log=True):
        current = {
            dep: self._value_or_hash(dep) for dep in self.dependencies[key]
        }
        changed_keys = {
            key for key in current if current[key] != self.previous.get(key)
        }
        if changed_keys:
            if log:
                logger.warning(
                    "Attributes changed: %s", ", ".join(changed_keys)
                )  # TODO: del this
            for key, deps in self.dependencies.items():
                if changed_keys.intersection(deps):
                    self.cache[key] = None
            self.previous = current

    def __repr__(self):
        title = f"{self.__class__.__name__}()"
        header = title + "\n" + "*" * len(title)
        lines = [header]

        def format_value(value):
            length_info = ""
            if isinstance(value, (pd.DataFrame, pd.Series, pd.Index)):
                display_value = str(value)
            elif isinstance(value, np.ndarray):
                display_value = str(value)
                length_info = f"\n\n[{len(value)} items]"
            elif hasattr(value, "__len__"):
                display_value = str(value)[:80] + (
                    "..." if len(str(value)) > 80 else ""
                )
                if len(str(value)) > 80:
                    length_info = f"\n\n[{len(value)} items]"
            elif isinstance(value, (plotly.graph_objs.Figure)):
                data_str = (
                    str(value.data[0])[:70].replace("\n", " ")
                    if value.data
                    else "No data"
                )
                layout_str = str(value.layout)[:70].replace("\n", " ")
                data_str += "..." if len(data_str) == 70 else ""
                layout_str += "..." if len(layout_str) == 70 else ""
                display_value = (
                    f"Figure(\n"
                    f"    data: {data_str}\n"
                    f"    layout: {layout_str}\n"
                    f")"
                )
            else:
                display_value = str(value)[:80] + (
                    "..." if len(str(value)) > 80 else ""
                )
            return display_value, length_info

        for attr, value in sorted(self.__dict__.items()):
            display_value, length_info = format_value(value)
            lines.append(f"{attr}:\n{display_value}{length_info}")
        return "\n\n".join(lines)


analysis = MethylAnalysis(
    analysis_dir="~/mepylome/tutorial/tutorial_analysis",
    reference_dir="~/mepylome/tutorial/tutorial_reference",
)

analysis.cpgs = [1, 2, 3]

self = CacheManager(analysis)
self.set_dependencies("betas_dir", ["n_cpgs", "analysis_dir", "cpgs"])
self.set_value("betas_dir", 999)
self.get("betas_dir")

key = "betas_dir"
dependencies = ["n_cpgs", "analysis_dir", "cpgs"]

analysis.n_cpgs += 1
self.get("betas_dir")


@property
def betas_dir(self):
    if not cache_manager.get("betas_dir"):
        dependencies = ["analysis_dir", "prep", "output_dir"]
        betas_hash_key = input_args_id(
            self.analysis_dir,
            "betas",
            self.prep,
        )
        cache_manager.set("betas_dir", self.output_dir / f"{betas_hash_key}")
    return cache_manager.get("betas_dir")


class ExampleClass:
    def __init__(self):
        self.analysis_dir = "/data/analysis"
        self.prep = "default"
        self.output_dir = "/data/output"
        self.cache_manager = CacheManager(self)

    @property
    def betas_dir(self):
        dependencies = ["analysis_dir", "prep", "output_dir"]
        cached_value = self.cache_manager.get("betas_dir", dependencies)
        if cached_value is not None:
            return cached_value
        betas_hash_key = f"{self.analysis_dir}_{self.prep}"
        new_value = f"{self.output_dir}/{betas_hash_key}"
        self.cache_manager.cache("betas_dir", new_value)
        return new_value


self = MethylAnalysis(
    analysis_dir="/mnt/storage/epidip_IDAT/",
    reference_dir="/data/ref_IDAT",
    overlap=False,
    cpgs="450k+epic+epicv2",
)

self = MethylAnalysis(
    analysis_dir="~/mepylome/data/salivary_gland_tumors/",
    reference_dir="~/mepylome/cnv_references/",
    output_dir="~/mepylome/outputs/",
)


analysis = MethylAnalysis(
    analysis_dir="~/mepylome/data/soft_tissue_tumors/",
    reference_dir="/data/ref_IDAT",
    overlap=True,
    cpgs="450k+epic+epicv2",
    load_full_betas=False,
)

self = MethylAnalysis(
    analysis_dir="/mnt/storage/epidip_IDAT/",
    reference_dir="/data/ref_IDAT",
    # annotation="/mnt/storage/annotations/PanCancer_20231026.xlsx",
    annotation="/mnt/storage/annotations/EpiDip_BTRC_20250122.xlsx",
    overlap=True,
    cpgs="450k+epic+epicv2",
    load_full_betas=False,
)


def _get_betas(cpgs):
    logger.info("Retrieving beta values...")
    return get_betas(
        idat_handler=self.idat_handler,
        cpgs=cpgs,
        prep=self.prep,
        betas_dir=self.betas_dir,
        pbar=self._prog_bar,
    )


self = analysis
betas_dir = self.betas_dir
cpgs = self.cpgs
ids = self.idat_handler.ids[:100]
ids = self.idat_handler.ids
idat_handler = self.idat_handler

betas_handler = BetasHandler(betas_dir)
self = betas_handler

X = betas_handler.get(idat_handler=idat_handler, cpgs=cpgs, ids=ids)


variances = betas_handler.columnwise_variance(
    idat_handler=idat_handler, cpgs=cpgs, ids=ids, parallel=True
)


# Define the file paths
file1 = (
    "/home/bruggerj/Downloads/All_IDAT_Annotation_at_IFP_collection_file.xlsx"
)
file2 = "/mnt/storage/cnvref_20250527/cnvref.xlsx"
file3 = "/mnt/storage/cnvref_20250527/cnvref2.xlsx"

# Read the Excel files
df1 = pd.read_excel(file1)
df2 = pd.read_excel(file2)


merged_df = df2.merge(
    df1[["IDAT_at_IFP", "Annotation_Summary"]],
    how="left",
    left_on="Sentrix_ID",
    right_on="IDAT_at_IFP",
)
merged_df = merged_df.drop_duplicates()

file3 = "/mnt/storage/cnvref_20250527/cnvref2.xlsx"
merged_df.to_excel(file3, index=False)



a = "/mnt/storage/chondrosarcoma/csa_project/annotation_CSA_project.xlsx"
b = "/mnt/storage/chondrosarcoma/csa_project/Triplicate_CSA_NL.xlsx"
c = "~/MEGA/work/projects/2024-cartilage_tumours_methylation/varia/Triplicate_CSA_NL.xlsx"
d = "~/MEGA/work/projects/2024-cartilage_tumours_methylation/varia/Triplicate_CSA_NL_old.xlsx"
# d = "/mnt/storage/chondrosarcoma/csa_project/Triplicate_CSA_NL.xlsx"

# df1 = pd.read_excel(a, nrows=115)
# df2 = pd.read_excel(b)
# df2 = df2[:115]

new = pd.read_excel(c)
old = pd.read_excel(d)

old_subset = old[['Sentrix_ID', 'cluster_brjo', 'IDH_bool']]
new_subset = new[['Sentrix_ID']]
merged = new.merge(old_subset, on='Sentrix_ID', how='left')
merged['cluster_brjo'] = merged['cluster_brjo'].fillna("")
merged['IDH_bool'] = merged['IDH_bool'].fillna("")


def print_column(column):
    index_old = old.set_index("Sentrix_ID")
    print(column)
    for id_ in new.Sentrix_ID:
        value = index_old.loc[id_][column]
        if isinstance(value, pd.Series):
            value = value.iloc[0]
        if pd.isna(value):
            value = ""
        print(value)

# def print_column(column):
#     print(column)
#     for val in merged[column]:
#         print(f"{val},")
#
print_column("cluster_brjo")
print_column("IDH_bool")


from sklearn.feature_selection import SelectKBest, f_classif

# Assume you have labels in `labels` (must be aligned with `betas.index`)
labels = merged.set_index('Sentrix_ID').loc[betas.index, 'cluster_brjo']

# Filter out rows with missing labels
mask = labels != ""
betas_filtered = betas.loc[mask]
labels_filtered = labels[mask]

# Select top 500 most discriminative CpGs using ANOVA F-score
selector = SelectKBest(f_classif, k=500)
betas_selected_array = selector.fit_transform(betas_filtered, labels_filtered)

# Get selected CpG names
selected_cpgs = betas_filtered.columns[selector.get_support()]
betas_selected = betas_filtered[selected_cpgs]



analysis.idat_handler.selected_columns = ["cluster_brjo"]
ids = analysis.idat_handler.ids
clf_out = analysis.classify(
    ids=ids,
    clf_list=[
        "vtl-kbest(k=10000)-lr(max_iter=10000)",
    ],
)
pred = clf_out[0].prediction.idxmax(axis=1)
true_values = analysis.idat_handler.samples_annotated.loc[ids][
    "cluster_brjo"
]
for idx in true_values.index:
    if true_values[idx] != pred[idx]:
        print(f"Index: {idx}, True: {true_values[idx]}, Pred: {pred[idx]}")



analysis.ids_to_highlight = [
    "5903111029_R01C01",
    "5903111029_R06C01",
    "9806233046_R06C02",
    "9721365156_R02C02",
    "9806233023_R05C02",
    "9721365019_R05C02",
    "9806233023_R03C01",
    "9806233001_R05C01",
    "9806233027_R02C01",
    "9806233037_R06C01",
    "9806233026_R04C02",
    "9806233037_R05C02",
    "206144420055_R05C01",
    "205982900061_R06C01",
    "206238130092_R06C01",
    "201508110028_R05C01",
    "204339110035_R03C01",
    "204339010114_R01C01",
    "204339110027_R03C01",
    "201496850114_R02C01",
    "202273260027_R02C01",
    "201506830054_R03C01",
    "207961480091_R06C01",
    "208404170105_R02C01",
    "208404170087_R06C01",
    "208404170087_R05C01",
    "208404170109_R01C01",
    "208404170072_R07C01",
    "207130360090_R06C01",
    "207130360143_R03C01",
    "207130360143_R07C01",
    "206644410047_R05C01",
    "206644420120_R07C01",
    "206639830020_R03C01",
    "201247480013_R03C01",
    "201869690168_R04C01",
    "201247480019_R06C01",
    "201247480005_R07C01",
    "201869690168_R06C01",
    "200406080083_R02C02",
    "9969477107_R06C01",
]

Index: 5903111029_R01C01,   True: IDH_MUT_2, Pred: IDH_WT_2
Index: 5903111029_R06C01,   True: IDH_MUT_MIX, Pred: IDH_MUT_1
Index: 9806233046_R06C02,   True: IDH_WT_1, Pred: IDH_MUT_CONT
Index: 9721365156_R02C02,   True: IDH_WT_1, Pred: IDH_WT_2
Index: 9806233023_R05C02,   True: IDH_WT_2, Pred: IDH_WT_1
Index: 9721365019_R05C02,   True: IDH_WT_1, Pred: IDH_MUT_2
Index: 9806233023_R03C01,   True: IDH_WT_1, Pred: IDH_WT_2
Index: 9806233001_R05C01,   True: IDH_WT_2, Pred: CSA_CC
Index: 9806233027_R02C01,   True: IDH_WT_1, Pred: IDH_MUT_MIX
Index: 9806233037_R06C01,   True: IDH_MUT_1, Pred: IDH_WT_2
Index: 9806233026_R04C02,   True: IDH_WT_1, Pred: IDH_WT_2
Index: 9806233037_R05C02,   True: IDH_MUT_1, Pred: IDH_MUT_MIX
Index: 206144420055_R05C01, True: IDH_MUT_MIX, Pred: IDH_MUT_1
Index: 205982900061_R06C01, True: IDH_MUT_MIX, Pred: IDH_MUT_1
Index: 206238130092_R06C01, True: IDH_WT_1, Pred: IDH_WT_2
Index: 201508110028_R05C01, True: IDH_WT_1, Pred: IDH_WT_2
Index: 204339110035_R03C01, True: IDH_MUT_MIX, Pred: IDH_MUT_CONT
Index: 204339010114_R01C01, True: IDH_MUT_1, Pred: IDH_MUT_2
Index: 204339110027_R03C01, True: IDH_MUT_CONT, Pred: IDH_MUT_MIX
Index: 201496850114_R02C01, True: IDH_MUT_1, Pred: IDH_MUT_2
Index: 202273260027_R02C01, True: CSA_CC, Pred: IDH_WT_1
Index: 201506830054_R03C01, True: IDH_MUT_MIX, Pred: IDH_MUT_1
Index: 207961480091_R06C01, True: IDH_MUT_MIX, Pred: IDH_WT_1
Index: 208404170105_R02C01, True: IDH_MUT_1, Pred: IDH_MUT_MIX
Index: 208404170087_R06C01, True: IDH_WT_2, Pred: IDH_WT_1
Index: 208404170087_R05C01, True: IDH_WT_2, Pred: IDH_WT_1
Index: 208404170109_R01C01, True: IDH_MUT_1, Pred: IDH_WT_2
Index: 208404170072_R07C01, True: IDH_WT_2, Pred: IDH_MUT_2
Index: 207130360090_R06C01, True: IDH_MUT_2, Pred: IDH_MUT_1
Index: 207130360143_R03C01, True: IDH_WT_2, Pred: IDH_WT_1
Index: 207130360143_R07C01, True: IDH_WT_2, Pred: IDH_MUT_1
Index: 206644410047_R05C01, True: IDH_WT_2, Pred: IDH_WT_1
Index: 206644420120_R07C01, True: IDH_MUT_1, Pred: IDH_MUT_2
Index: 206639830020_R03C01, True: IDH_WT_1, Pred: IDH_WT_2
Index: 201247480013_R03C01, True: IDH_MUT_MIX, Pred: CSA_CC
Index: 201869690168_R04C01, True: IDH_MUT_CONT, Pred: IDH_MUT_MIX
Index: 201247480019_R06C01, True: IDH_MUT_2, Pred: IDH_MUT_1
Index: 201247480005_R07C01, True: IDH_MUT_MIX, Pred: IDH_WT_1
Index: 201869690168_R06C01, True: CSA_CC, Pred: IDH_WT_1
Index: 200406080083_R02C02, True: IDH_WT_1, Pred: IDH_WT_2
Index: 9969477107_R06C01,   True: IDH_WT_2, Pred: IDH_WT_1




analysis.ids_to_highlight = [
    "202273260027_R02C01",
    "207961480091_R06C01",
    "208404170105_R07C01",
    "208404170109_R02C01",
    "207130360143_R03C01",
    "206644410047_R05C01",
    "206644420120_R07C01",
    "201247480013_R03C01",
]

Index: 202273260027_R02C01, True: CSA_CC, Pred: IDH_MUT_MIX
Index: 207961480091_R06C01, True: IDH_MUT_MIX, Pred: IDH_MUT_CONT
Index: 208404170105_R07C01, True: IDH_WT_2, Pred: IDH_WT_1
Index: 208404170109_R02C01, True: IDH_MUT_1, Pred: IDH_MUT_HN
Index: 207130360143_R03C01, True: IDH_WT_2, Pred: IDH_WT_1
Index: 206644410047_R05C01, True: IDH_WT_2, Pred: IDH_MUT_MIX
Index: 206644420120_R07C01, True: IDH_MUT_1, Pred: IDH_MUT_2
Index: 201247480013_R03C01, True: IDH_MUT_MIX, Pred: IDH_MUT_CONT


Wrong Prediction - True: G2, Pred: 1
Wrong Prediction - True: G3, Pred: 2
Wrong Prediction - True: G3, Pred: 4
Wrong Prediction - True: G2, Pred: 3
Wrong Prediction - True: G2, Pred: 3
Wrong Prediction - True: G2, Pred: 1
Wrong Prediction - True: G3, Pred: 4
Wrong Prediction - True: G3, Pred: 4
Wrong Prediction - True: G2, Pred: 3
Wrong Prediction - True: G2, Pred: 4
Wrong Prediction - True: G3, Pred: 0
Wrong Prediction - True: G4, Pred: 3
Wrong Prediction - True: G3, Pred: 2
Wrong Prediction - True: G4, Pred: 3
Wrong Prediction - True: G2, Pred: 3
Wrong Prediction - True: G2, Pred: 3
Wrong Prediction - True: G1, Pred: 3
Wrong Prediction - True: G0, Pred: 2
Wrong Prediction - True: G0, Pred: 2
Wrong Prediction - True: G4, Pred: 1
Wrong Prediction - True: G1, Pred: 2
Wrong Prediction - True: G2, Pred: 3
Wrong Prediction - True: G2, Pred: 3
Wrong Prediction - True: G2, Pred: 3
Wrong Prediction - True: G2, Pred: 3
Wrong Prediction - True: G2, Pred: 1
Wrong Prediction - True: G4, Pred: 3
Wrong Prediction - True: G0, Pred: 1
Wrong Prediction - True: G0, Pred: 2
Wrong Prediction - True: G1, Pred: 2
Wrong Prediction - True: G3, Pred: 2
Wrong Prediction - True: G2, Pred: 3
Wrong Prediction - True: G3, Pred: 2
Wrong Prediction - True: G3, Pred: 2
Wrong Prediction - True: G2, Pred: 1
Wrong Prediction - True: G0, Pred: 1
Wrong Prediction - True: G2, Pred: 1
Wrong Prediction - True: G2, Pred: 3
Wrong Prediction - True: G3, Pred: 2
Wrong Prediction - True: G1, Pred: 2
Wrong Prediction - True: G2, Pred: 3
Wrong Prediction - True: G4, Pred: 3
Wrong Prediction - True: G2, Pred: 3
Wrong Prediction - True: G4, Pred: 3
Wrong Prediction - True: G0, Pred: 2
Wrong Prediction - True: G3, Pred: 2
Wrong Prediction - True: G3, Pred: 2
Wrong Prediction - True: G1, Pred: 2
Wrong Prediction - True: G2, Pred: 3
Wrong Prediction - True: G0, Pred: 2
Wrong Prediction - True: G3, Pred: 2
Wrong Prediction - True: G0, Pred: 1
Wrong Prediction - True: G1, Pred: 2
Wrong Prediction - True: G2, Pred: 3
Wrong Prediction - True: G3, Pred: 2
Wrong Prediction - True: G1, Pred: 0
Wrong Prediction - True: G1, Pred: 3
Accuracy: 0.6438 (160 samples)




analysis.n_cpgs = 50000
set_methyl_cnv_feature_matrix(100, 0, None, True, random_state=random)
analysis.umap_parms = {
    "n_neighbors": 11,
    "metric": "euclidean",
    "min_dist": 0.2,
    "verbose": True,
    # "random_state": random,
}
plotly_plot = analysis.umap_plot
import os



analysis.n_cpgs = 25000
umap_parms = {
    "n_neighbors": 15,
    "metric": "euclidean",
    "min_dist": 0.2,
    "verbose": True,
}

# Random seeds to test
random_seeds = [0, 1, 42, 123, 777, 999]
random_seeds = range(30)


analysis.feature_matrix = None
analysis.umap_parms = {
    "n_neighbors": 10,
    "metric": "manhattan",
    "min_dist": 0.00001,
    "verbose": True,
    # "random_state": 1000,
}
start_gui()

def make_umap():
    import random
    n_neighbors = random.choice(range(10,16))
    metric = random.choice(["euclidean", "manhattan"])
    seed = random.choice(range(1000))
    analysis.n_cpgs = 25000
    analysis.feature_matrix = None
    analysis.umap_parms = {
        "n_neighbors": n_neighbors,
        "metric": metric,
        "min_dist": 0.001,
        "random_state": seed,
    }
    analysis.make_umap()
    seed_string = (
        f"n_neighbors={n_neighbors}_"
        f"metric={metric}_"
        f"seed={seed}"
    )
    return seed_string

def make_umap(seed):
    analysis.n_cpgs = 250000
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
    analysis.make_umap()
    return seed

for seed in range(100):
    parms_str = make_umap()
    plot = analysis.umap_plot
    plot.update_layout(title=f"Parms: {parms_str}")
    output_dir = Path.home() / "Downloads/random_umap"
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = output_dir / f"umap_seed{parms_str}.html"
    plot.write_html(filename, auto_open=False)

print(f"\nAll plots saved to: {output_dir}")
