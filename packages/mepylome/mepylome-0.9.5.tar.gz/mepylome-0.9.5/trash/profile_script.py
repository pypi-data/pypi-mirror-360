import types

import line_profiler

import mepylome  # Import the target module


def profile_all_functions(module):
    """Adds the @profile decorator to all functions in the given module."""
    profiler = line_profiler.LineProfiler()
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        # Profile only functions and bound methods
        if isinstance(
            attr, (types.FunctionType, types.MethodType)
        ) and attr.__module__.startswith("mepylome"):
            profiler.add_function(attr)
    return profiler


def profile_methyldata():
    from pathlib import Path

    from mepylome import MethylData, idat_basepaths

    idat_files = idat_basepaths(
        Path("/data/sarcoma_idat/csa_project/idat_CSA")
    )

    for file_ in idat_files:
        _ = MethylData(file=file_, prep="illumina")


def profile_cnv():
    from mepylome.analysis import MethylAnalysis

    analysis = MethylAnalysis(
        analysis_dir="~/mepylome/tutorial/tutorial_analysis/",
        reference_dir="~/mepylome/tutorial/tutorial_reference/",
        n_cpgs=25000,
        load_full_betas=True,
        overlap=False,
        debug=True,
        do_seg=True,
    )
    # analysis.make_umap()
    analysis.precompute_cnvs()


def main():
    profile_cnv()


if __name__ == "__main__":
    # Add profiling for all functions in the mepylome module
    profiler = profile_all_functions(mepylome)
    profiler.run("main()")
    profiler.print_stats()
