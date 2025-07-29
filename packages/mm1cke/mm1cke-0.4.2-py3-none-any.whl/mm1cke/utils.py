import logging

import polars as pl
from rich.console import Console

console = Console()

log = logging.getLogger(__name__)


def calculate_performance_measures(probs_df: pl.DataFrame):
    return probs_df.group_by("t", maintain_order=True).agg(
        pl.col("l_s").dot(pl.col("p")).alias("e_l_s"),
        pl.when(pl.col("l_s").dot(pl.col("p")).eq(0))
        .then(pl.lit(None))
        .otherwise(
            pl.col("p")
            .dot((pl.col("l_s") - pl.col("p").dot(pl.col("l_s"))) ** 2)
            .sqrt()
            .truediv(pl.col("p").dot(pl.col("l_s")))
        )
        .alias("cv_l_s"),
    )
