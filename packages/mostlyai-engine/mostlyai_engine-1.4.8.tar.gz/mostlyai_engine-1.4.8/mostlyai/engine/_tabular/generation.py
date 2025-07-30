# Copyright 2025 MOSTLY AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import random
import time
import uuid
from functools import partial
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd
import torch

from mostlyai.engine._common import (
    ARGN_COLUMN,
    ARGN_PROCESSOR,
    ARGN_TABLE,
    CTXFLT,
    CTXSEQ,
    SDEC_SUB_COLUMN_PREFIX,
    SIDX_SUB_COLUMN_PREFIX,
    SLEN_SIDX_SDEC_COLUMN,
    SLEN_SUB_COLUMN_PREFIX,
    FixedSizeSampleBuffer,
    ProgressCallback,
    ProgressCallbackWrapper,
    apply_encoding_type_dtypes,
    decode_slen_sidx_sdec,
    encode_slen_sidx_sdec,
    get_argn_name,
    get_cardinalities,
    get_columns_from_cardinalities,
    get_ctx_sequence_length,
    get_sequence_length_stats,
    get_sub_columns_from_cardinalities,
    get_sub_columns_nested_from_cardinalities,
    is_sequential,
    persist_data_part,
    trim_sequences,
)
from mostlyai.engine._encoding_types.tabular.categorical import (
    CATEGORICAL_NULL_TOKEN,
    CATEGORICAL_SUB_COL_SUFFIX,
    CATEGORICAL_UNKNOWN_TOKEN,
    decode_categorical,
)
from mostlyai.engine._encoding_types.tabular.character import decode_character
from mostlyai.engine._encoding_types.tabular.datetime import decode_datetime
from mostlyai.engine._encoding_types.tabular.itt import decode_itt
from mostlyai.engine._encoding_types.tabular.lat_long import decode_latlong
from mostlyai.engine._encoding_types.tabular.numeric import (
    NUMERIC_BINNED_NULL_TOKEN,
    NUMERIC_BINNED_SUB_COL_SUFFIX,
    NUMERIC_BINNED_UNKNOWN_TOKEN,
    NUMERIC_DISCRETE_NULL_TOKEN,
    NUMERIC_DISCRETE_SUB_COL_SUFFIX,
    NUMERIC_DISCRETE_UNKNOWN_TOKEN,
    decode_numeric,
)
from mostlyai.engine._memory import get_available_ram_for_heuristics, get_available_vram_for_heuristics
from mostlyai.engine._tabular.argn import (
    FlatModel,
    ModelSize,
    SequentialModel,
    get_no_of_model_parameters,
)
from mostlyai.engine._tabular.common import load_model_weights
from mostlyai.engine._tabular.encoding import encode_df, pad_horizontally
from mostlyai.engine._tabular.fairness import FairnessTransforms, get_fairness_transforms
from mostlyai.engine._workspace import Workspace, ensure_workspace_dir, reset_dir
from mostlyai.engine.domain import (
    FairnessConfig,
    ImputationConfig,
    ModelEncodingType,
    RareCategoryReplacementMethod,
    RebalancingConfig,
)

_LOG = logging.getLogger(__name__)

DUMMY_CONTEXT_KEY = "__dummy_context_key"


CodeProbabilities = dict[int, float]  # CategoryProbabilities after encoding, e.g. {0: 0.3, 1: 0.4}


def _resolve_gen_column_order(
    column_stats: dict,
    cardinalities: dict,
    rebalancing: RebalancingConfig | None = None,
    imputation: ImputationConfig | None = None,
    sample_seed: pd.DataFrame | None = None,
    fairness: FairnessConfig | None = None,
):
    column_order = get_columns_from_cardinalities(cardinalities)

    # Reorder columns in the following order:
    # 0. SLEN/SIDX column
    # 1. Sample seed columns
    # 2. Rebalancing column
    # 3. Fairness sensitive columns (which are not imputation columns)
    # 4. Fairness sensitive columns (which are imputation columns as well)
    # 5. The rest of the columns
    # 6. Imputation columns (which are not fairness sensitive columns)
    # 7. Fairness target column

    if imputation:
        # imputed columns should be at the end in the generation model
        imputation_argn = [
            get_argn_name(
                argn_processor=column_stats[col][ARGN_PROCESSOR],
                argn_table=column_stats[col][ARGN_TABLE],
                argn_column=column_stats[col][ARGN_COLUMN],
            )
            for col in imputation.columns
            if col in column_stats
        ]
        column_order = [c for c in column_order if c not in imputation_argn] + imputation_argn
    else:
        imputation_argn = []

    if fairness:
        # bring sensitive columns to the front and target column to the back
        sensitive_columns_argn = [
            get_argn_name(
                argn_processor=column_stats[col][ARGN_PROCESSOR],
                argn_table=column_stats[col][ARGN_TABLE],
                argn_column=column_stats[col][ARGN_COLUMN],
            )
            for col in fairness.sensitive_columns
            if col in column_stats
        ]
        # imputed sensitive columns should be after other usual sensitive columns
        sensitive_columns_argn = [c for c in sensitive_columns_argn if c not in imputation_argn] + [
            c for c in sensitive_columns_argn if c in imputation_argn
        ]

        target_column_argn = get_argn_name(
            argn_processor=column_stats[fairness.target_column][ARGN_PROCESSOR],
            argn_table=column_stats[fairness.target_column][ARGN_TABLE],
            argn_column=column_stats[fairness.target_column][ARGN_COLUMN],
        )
        column_order = (
            sensitive_columns_argn
            + [c for c in column_order if c not in sensitive_columns_argn + [target_column_argn]]
            + [target_column_argn]
        )

    if rebalancing:
        # rebalance column should be at the beginning in the generation model
        # rebalancing has higher priority than imputation
        if rebalancing.column in column_stats:
            rebalance_column_argn = get_argn_name(
                argn_processor=column_stats[rebalancing.column][ARGN_PROCESSOR],
                argn_table=column_stats[rebalancing.column][ARGN_TABLE],
                argn_column=column_stats[rebalancing.column][ARGN_COLUMN],
            )
            column_order = [rebalance_column_argn] + [c for c in column_order if c != rebalance_column_argn]

    if sample_seed is not None:
        # sample_seed columns should be at the beginning in the generation model
        # sample_seed has higher priority than rebalancing and imputation
        seed_columns_argn = [
            get_argn_name(
                argn_processor=column_stats[col][ARGN_PROCESSOR],
                argn_table=column_stats[col][ARGN_TABLE],
                argn_column=column_stats[col][ARGN_COLUMN],
            )
            for col in sample_seed.columns
            if col in column_stats
        ]
        column_order = seed_columns_argn + [c for c in column_order if c not in seed_columns_argn]

    if SLEN_SIDX_SDEC_COLUMN in column_order:
        # SLEN/SIDX column needs to be the first one in the generation model
        column_order = [SLEN_SIDX_SDEC_COLUMN] + [c for c in column_order if c != SLEN_SIDX_SDEC_COLUMN]

    return column_order


def _generate_primary_keys(size: int, type: Literal["uuid", "int"] = "uuid") -> pd.Series:
    if type == "uuid":
        # generate watermarked 36-chars UUIDv4s
        # e.g. mostly2b-d87c-4825-884f-611b309c3c55
        return pd.Series(
            [f"mostly{str(uuid.UUID(int=random.getrandbits(128), version=4))[6:]}" for _ in range(size)], dtype="string"
        )
    else:
        return pd.Series(range(size), dtype="int")


def _batch_df(df: pd.DataFrame, no_of_batches: int) -> pd.DataFrame:
    rows_per_batch = len(df) / no_of_batches
    running_total = pd.Series(range(len(df))) / rows_per_batch
    df = df.assign(__BATCH=running_total.astype(int) + 1)
    return df


def _pad_vertically(df: pd.DataFrame, batch_size: int, primary_key: str) -> pd.DataFrame:
    """
    Append rows with zeros so that `df` has `batch_size` rows.
    """
    # determine number of required padded rows
    no_of_pad_rows = batch_size - df.shape[0]
    if no_of_pad_rows <= 0:
        return df

    # create padded rows with zeros
    def pad_flat(c):
        return pd.Series(np.repeat([0], no_of_pad_rows), name=c)

    def pad_seq(c):
        return pd.Series(np.empty((no_of_pad_rows, 0)).tolist(), name=c)

    pads = pd.concat(
        [pad_seq(c) if is_sequential(df[c]) else pad_flat(c) for c in df.columns],
        axis=1,
    )
    # flag padded rows by setting its key column to None
    pads[primary_key] = None
    # concatenate the padded rows to original data
    df = pd.concat([df, pads], axis=0)
    df.reset_index(drop=True, inplace=True)
    return df


def _reshape_pt_to_pandas(
    data: list[torch.Tensor], sub_cols: list[str], keys: list[pd.Series], key_name: str
) -> pd.DataFrame:
    # len(data)=seq_len, data[0].shape=(1<=x<=batch_size, n_sub_cols, 1)
    # len(keys)=seq_len, keys[0].shape=(1<=x<=batch_size,)
    # len(sub_cols)=n_sub_cols
    assert len(data) == len(keys)
    for step_data, step_keys in zip(data, keys):
        assert step_data.shape[0] == step_keys.shape[0]
    seq_len = len(data)
    if seq_len == 0:
        return pd.DataFrame(columns=[key_name] + sub_cols)
    # transform from list[torch.Tensor] to pd.DataFrame, by concatenating sequence steps
    # df.shape=(sum(1<=x<=batch_size), n_sub_cols)
    df = pd.concat(
        [
            pd.DataFrame(
                step_tensor.squeeze(-1).detach().cpu().numpy(),
                columns=sub_cols,
                dtype="int32",
            )
            for step_tensor in data
        ],
        axis=0,
    ).reset_index(drop=True)
    # transform keys from list[pd.Series] to pd.Series, by concatenating sequence steps
    # keys.shape=(sum(1<=x<=batch_size),)
    keys = pd.concat(keys, axis=0).rename(key_name).reset_index(drop=True)
    return pd.concat([keys, df], axis=1)


def _continue_sequence_mask(
    step_output: torch.Tensor,
    sub_cols: list[str],
    step_keys: pd.Series,
    key_name: str,
    seq_len_min: int,
    seq_len_max: int,
):
    # reshape tensor to pandas
    syn = _reshape_pt_to_pandas(
        data=[step_output],
        sub_cols=sub_cols,
        keys=[step_keys],
        key_name=key_name,
    )
    # decode SLEN/SIDX columns
    syn[SIDX_SUB_COLUMN_PREFIX] = decode_slen_sidx_sdec(syn, seq_len_max, prefix=SIDX_SUB_COLUMN_PREFIX)
    syn[SLEN_SUB_COLUMN_PREFIX] = decode_slen_sidx_sdec(syn, seq_len_max, prefix=SLEN_SUB_COLUMN_PREFIX)
    syn[SLEN_SUB_COLUMN_PREFIX] = np.maximum(seq_len_min, syn[SLEN_SUB_COLUMN_PREFIX])
    # calculate stop sequence mask (True=continue, False=stop)
    return syn[SIDX_SUB_COLUMN_PREFIX] < syn[SLEN_SUB_COLUMN_PREFIX]


def _post_process_decoding(
    syn: pd.DataFrame,
    tgt_primary_key: str | None = None,
) -> pd.DataFrame:
    # remove dummy context key (if exists)
    if DUMMY_CONTEXT_KEY in syn:
        syn = syn.drop(columns=DUMMY_CONTEXT_KEY)

    # generate primary keys, if they are not present
    if tgt_primary_key and tgt_primary_key not in syn:
        syn[tgt_primary_key] = _generate_primary_keys(len(syn), type="uuid")

    return syn


##################
### HEURISTICS ###
##################


def _generation_batch_size_heuristic(mem_available_gb: float, ctx_stats: dict, tgt_stats: dict, device: torch.device):
    tgt_cardinalities = get_cardinalities(tgt_stats)
    ctx_cardinalities = get_cardinalities(ctx_stats)
    ctxflt_cardinalities = {k: v for k, v in ctx_cardinalities.items() if k.startswith(CTXFLT)}
    ctxseq_cardinalities = {k: v for k, v in ctx_cardinalities.items() if k.startswith(CTXSEQ)}
    ctxseq_max_lengths = get_ctx_sequence_length(ctx_stats, key="max")
    ctxseq_table_sub_columns = get_sub_columns_nested_from_cardinalities(ctxseq_cardinalities, groupby="tables")

    one_hot_unit_bytes = 4
    mem_available_bytes = mem_available_gb * 1_000 * 1_000 * 1_000

    ctxflt_one_hot = sum(ctxflt_cardinalities.values())
    ctxflt_one_hot_bytes = ctxflt_one_hot * one_hot_unit_bytes

    ctxseq_one_hots = []
    for table, sub_columns in ctxseq_table_sub_columns.items():
        one_hot = sum([ctxseq_cardinalities[sub_column] for sub_column in sub_columns]) * ctxseq_max_lengths[table]
        ctxseq_one_hots.append(one_hot)
    ctxseq_one_hot = sum(ctxseq_one_hots)
    ctxseq_one_hot_bytes = ctxseq_one_hot * one_hot_unit_bytes

    tgt_one_hot = sum(tgt_cardinalities.values())
    tgt_one_hot_bytes = tgt_one_hot * one_hot_unit_bytes

    sample_bytes = ctxflt_one_hot_bytes + ctxseq_one_hot_bytes + tgt_one_hot_bytes
    sample_kb = sample_bytes / 1_000
    scaling_factor = 0.1

    batch_size = int((mem_available_bytes // max(1, sample_bytes)) * scaling_factor)
    device_max = 10_000 if device.type == "cuda" else 100_000
    batch_size = int(np.clip(batch_size, a_min=100, a_max=device_max))

    _LOG.info(
        f"batch_size heuristic: {batch_size:,} ({mem_available_gb=:.1f}GB, {sample_kb=:.1f}KB, {scaling_factor=:.1f})"
    )

    return batch_size


#########################
### PROGRAMMABLE DATA ###
#########################


def _fix_rare_token_probs(
    stats: dict,
    rare_category_replacement_method: RareCategoryReplacementMethod | None = None,
) -> dict[str, dict[str, CodeProbabilities]]:
    # suppress rare token for categorical when no_of_rare_categories == 0
    mask = {
        col: {CATEGORICAL_SUB_COL_SUFFIX: {col_stats["codes"][CATEGORICAL_UNKNOWN_TOKEN]: 0.0}}
        for col, col_stats in stats["columns"].items()
        if col_stats["encoding_type"] == ModelEncodingType.tabular_categorical
        if "codes" in col_stats
        if col_stats.get("no_of_rare_categories", 0) == 0
    }
    # suppress rare token for categorical if RareCategoryReplacementMethod is sample
    if rare_category_replacement_method == RareCategoryReplacementMethod.sample:
        mask |= {
            col: {CATEGORICAL_SUB_COL_SUFFIX: {col_stats["codes"][CATEGORICAL_UNKNOWN_TOKEN]: 0.0}}
            for col, col_stats in stats["columns"].items()
            if col_stats["encoding_type"] == ModelEncodingType.tabular_categorical
            if "codes" in col_stats
        }
    # always suppress rare token for numeric_binned
    mask |= {
        col: {NUMERIC_BINNED_SUB_COL_SUFFIX: {col_stats["codes"][NUMERIC_BINNED_UNKNOWN_TOKEN]: 0.0}}
        for col, col_stats in stats["columns"].items()
        if col_stats["encoding_type"] == ModelEncodingType.tabular_numeric_binned
        if "codes" in col_stats
    }
    # always suppress rare token for numeric_discrete
    mask |= {
        col: {NUMERIC_DISCRETE_SUB_COL_SUFFIX: {col_stats["codes"][NUMERIC_DISCRETE_UNKNOWN_TOKEN]: 0.0}}
        for col, col_stats in stats["columns"].items()
        if col_stats["encoding_type"] == ModelEncodingType.tabular_numeric_discrete
        if "codes" in col_stats
    }
    return mask


def _fix_imputation_probs(
    stats: dict,
    imputation: ImputationConfig | None = None,
) -> dict[str, dict[str, CodeProbabilities]]:
    imputation = imputation.columns if imputation is not None else []
    _LOG.info(f"imputation: {imputation}")
    fixed_probs: dict[str, dict[str, CodeProbabilities]] = {}
    for col in imputation:
        if col not in stats["columns"]:
            _LOG.info(f"imputed [{col}] not found in stats")
            continue
        col_stats = stats["columns"][col]
        encoding_type = col_stats["encoding_type"]
        # null_name will be either None, "na" or "nan"
        null_subcol = next(iter([k[4:] for k in col_stats.keys() if k in ["has_na", "has_nan"]]), None)
        if null_subcol is not None and col_stats[f"has_{null_subcol}"]:
            # column has separate null sub column and there are some nulls
            code_null = 1
            col_fixed_probs = {col: {null_subcol: {code_null: 0.0}}}
        elif encoding_type in [
            ModelEncodingType.tabular_categorical,
            ModelEncodingType.tabular_numeric_discrete,
            ModelEncodingType.tabular_numeric_binned,
        ]:
            # column is categorical-like and has single sub column
            sub_column = {
                ModelEncodingType.tabular_categorical: CATEGORICAL_SUB_COL_SUFFIX,
                ModelEncodingType.tabular_numeric_discrete: NUMERIC_DISCRETE_SUB_COL_SUFFIX,
                ModelEncodingType.tabular_numeric_binned: NUMERIC_BINNED_SUB_COL_SUFFIX,
            }[encoding_type]
            code_probs = {
                ModelEncodingType.tabular_categorical: {
                    CATEGORICAL_NULL_TOKEN: 0.0,
                    CATEGORICAL_UNKNOWN_TOKEN: 0.0,
                },
                ModelEncodingType.tabular_numeric_discrete: {NUMERIC_DISCRETE_NULL_TOKEN: 0.0},
                ModelEncodingType.tabular_numeric_binned: {NUMERIC_BINNED_NULL_TOKEN: 0.0},
            }[encoding_type]
            # map and filter out codes that did not occur (happens when there are no nulls)
            col_fixed_probs = {
                col: {
                    sub_column: {
                        col_stats["codes"][category]: probs
                        for category, probs in code_probs.items()
                        if category in col_stats["codes"]
                    }
                }
            }
        else:
            col_fixed_probs = {}
        fixed_probs |= col_fixed_probs
    return fixed_probs


def _fix_rebalancing_probs(
    stats: dict,
    rebalancing: RebalancingConfig | None = None,
) -> dict[str, dict[str, CodeProbabilities]]:
    column, probabilities = (rebalancing.column, rebalancing.probabilities) if rebalancing else (None, {})
    _LOG.info(f"rebalance_column: {column}")
    _LOG.info(f"rebalance_probabilities: {probabilities}")
    mask = {}
    if (
        column is not None
        and column in stats["columns"]
        and stats["columns"][column]["encoding_type"] == ModelEncodingType.tabular_categorical
        and "codes" in stats["columns"][column]
    ):
        col_codes = stats["columns"][column]["codes"]
        code_probabilities = {
            col_codes[category]: max(0.0, prob) for category, prob in probabilities.items() if category in col_codes
        }
        # normalize probabilities if they sum up to more than 1.0
        total_share = sum(code_probabilities.values())
        if total_share > 1.0:
            code_probabilities = {code: share / total_share for code, share in code_probabilities.items()}
        if code_probabilities:
            mask = {column: {CATEGORICAL_SUB_COL_SUFFIX: code_probabilities}}

    return mask


def _translate_fixed_probs(
    fixed_probs: dict[str, dict[str, CodeProbabilities]], stats: dict
) -> dict[str, CodeProbabilities]:
    # translate fixed probs to ARGN conventions
    mask = {
        get_argn_name(
            argn_processor=stats["columns"][col][ARGN_PROCESSOR],
            argn_table=stats["columns"][col][ARGN_TABLE],
            argn_column=stats["columns"][col][ARGN_COLUMN],
            argn_sub_column=sub_col,
        ): sub_col_mask
        for col, col_mask in fixed_probs.items()
        for sub_col, sub_col_mask in col_mask.items()
    }
    return mask


def _deepmerge(*dictionaries: dict, merged: dict | None = None) -> dict:
    merged = merged or {}
    for dictionary in dictionaries:
        for key, value in dictionary.items():
            if isinstance(value, dict):
                if key not in merged:
                    merged[key] = {}
                merged[key] |= _deepmerge(value, merged[key])
            else:
                merged[key] = value
    return merged


##################
###   DECODE   ###
##################


def _decode_df(
    df_encoded: pd.DataFrame,
    stats: dict,
    context_key: str | None = None,
    prev_steps: dict | None = None,
) -> pd.DataFrame:
    columns = []
    if context_key and context_key in df_encoded.columns:
        columns.append(df_encoded[context_key])
    for column, column_stats in stats["columns"].items():
        if column_stats.keys() == {"encoding_type"}:
            # training data was empty
            values = pd.Series(data=[], name=column, dtype="object")
            columns.append(values)
            continue
        sub_columns = [
            get_argn_name(
                argn_processor=column_stats[ARGN_PROCESSOR],
                argn_table=column_stats[ARGN_TABLE],
                argn_column=column_stats[ARGN_COLUMN],
                argn_sub_column=sub_col,
            )
            for sub_col in column_stats["cardinalities"].keys()
        ]
        # fetch column-specific sub_columns from data
        df_encoded_col = df_encoded[sub_columns]
        # remove column prefixes before decoding
        df_encoded_col.columns = [
            ocol.replace(
                # replace conventional column name without sub_column part
                get_argn_name(
                    argn_processor=column_stats[ARGN_PROCESSOR],
                    argn_table=column_stats[ARGN_TABLE],
                    argn_column=column_stats[ARGN_COLUMN],
                    argn_sub_column="",
                ),
                "",
            )
            for ocol in df_encoded_col.columns
        ]
        # handle column prev_steps
        prev_steps_col = None
        if prev_steps is not None:
            prev_steps[column] = prev_steps.get(column, {})
            prev_steps_col = prev_steps[column]
        # decode encoded sub_columns into single decoded column
        values = _decode_col(
            df_encoded=df_encoded_col,
            stats=column_stats,
            context_keys=df_encoded[context_key] if context_key in df_encoded.columns else None,
            prev_steps=prev_steps_col,
        )
        values.name = column
        columns.append(values)
    return pd.concat(columns, axis=1)


def _decode_col(
    df_encoded: pd.DataFrame,
    stats: dict,
    context_keys: pd.Series | None = None,
    prev_steps: dict | None = None,
) -> pd.Series:
    if df_encoded.empty:
        return pd.Series()

    encoding_type = stats["encoding_type"]

    if encoding_type == ModelEncodingType.tabular_categorical:
        values = decode_categorical(df_encoded=df_encoded, stats=stats)
    elif encoding_type in [
        ModelEncodingType.tabular_numeric_auto,
        ModelEncodingType.tabular_numeric_discrete,
        ModelEncodingType.tabular_numeric_binned,
        ModelEncodingType.tabular_numeric_digit,
    ]:
        values = decode_numeric(df_encoded=df_encoded, stats=stats)
    elif encoding_type == ModelEncodingType.tabular_datetime:
        values = decode_datetime(df_encoded=df_encoded, stats=stats)
    elif encoding_type == ModelEncodingType.tabular_datetime_relative:
        values = decode_itt(
            df_encoded=df_encoded,
            stats=stats,
            context_keys=context_keys,
            prev_steps=prev_steps,
        )
    elif encoding_type == ModelEncodingType.tabular_character:
        values = decode_character(df_encoded=df_encoded, stats=stats)
    elif encoding_type == ModelEncodingType.tabular_lat_long:
        values = decode_latlong(df_encoded=df_encoded, stats=stats)
    return values


def decode_buffered_samples(
    buffer: FixedSizeSampleBuffer,
    tgt_stats: dict,
    tgt_sub_columns: list[str],
    tgt_primary_key: str,
    tgt_context_key: str,
    decode_prev_steps: dict | None = None,
) -> pd.DataFrame:
    is_sequential = tgt_stats["is_sequential"]
    seq_len_stats = get_sequence_length_stats(tgt_stats)
    seq_len_min = seq_len_stats["min"]
    seq_len_max = seq_len_stats["max"]

    assert not buffer.is_empty() or seq_len_max == 0

    if is_sequential:
        data, keys = zip(*buffer.buffer) if buffer.buffer else ([], [])
        syn = _reshape_pt_to_pandas(
            data=data,
            sub_cols=tgt_sub_columns,
            keys=keys,
            key_name=tgt_context_key,
        )
        # trim sequences to min and max length
        syn = trim_sequences(
            syn=syn,
            tgt_context_key=tgt_context_key,
            seq_len_min=seq_len_min,
            seq_len_max=seq_len_max,
        )
    else:
        (data,) = zip(*buffer.buffer)
        syn = pd.concat(data, axis=0).reset_index(drop=True)

    # extract pre-defined seed columns, if provided
    seed_columns = [col for col in syn.columns if col.startswith("__seed:")]
    if seed_columns:
        df_seed = syn[seed_columns].rename(columns=lambda col: col.replace("__seed:", "", 1))
    else:
        df_seed = pd.DataFrame()

    # decode generated data
    _LOG.info(f"decode generated data {syn.shape}")
    syn = _decode_df(
        df_encoded=syn,
        stats=tgt_stats,
        context_key=tgt_context_key,
        prev_steps=decode_prev_steps,
    )

    # preserve all seed columns
    for col in df_seed.columns:
        syn[col] = df_seed[col]

    # postprocess generated data
    _LOG.info(f"post-process generated data {syn.shape}")
    syn = _post_process_decoding(
        syn,
        tgt_primary_key=tgt_primary_key,
    )
    return syn


##################
### GENERATION ###
##################


@torch.no_grad()
def generate(
    *,
    ctx_data: pd.DataFrame | None = None,
    seed_data: pd.DataFrame | None = None,
    sample_size: int | None = None,
    batch_size: int | None = None,
    rare_category_replacement_method: RareCategoryReplacementMethod | str = RareCategoryReplacementMethod.constant,
    sampling_temperature: float = 1.0,
    sampling_top_p: float = 1.0,
    rebalancing: RebalancingConfig | dict | None = None,
    imputation: ImputationConfig | dict | None = None,
    fairness: FairnessConfig | dict | None = None,
    device: torch.device | str | None = None,
    workspace_dir: str | Path = "engine-ws",
    update_progress: ProgressCallback | None = None,
) -> None:
    _LOG.info("GENERATE_TABULAR started")
    t0 = time.time()
    with ProgressCallbackWrapper(update_progress) as progress:
        # build paths based on workspace dir
        workspace_dir = ensure_workspace_dir(workspace_dir)
        workspace = Workspace(workspace_dir)
        output_path = workspace.generated_data_path
        reset_dir(output_path)

        model_configs = workspace.model_configs.read()
        tgt_stats = workspace.tgt_stats.read()
        is_sequential = tgt_stats["is_sequential"]
        _LOG.info(f"{is_sequential=}")
        has_context = workspace.ctx_stats.path.exists()
        _LOG.info(f"{has_context=}")
        ctx_stats = workspace.ctx_stats.read()

        tgt_cardinalities = get_cardinalities(tgt_stats)
        tgt_sub_columns = get_sub_columns_from_cardinalities(tgt_cardinalities)
        ctx_cardinalities = get_cardinalities(ctx_stats)
        ctx_sub_columns = get_sub_columns_from_cardinalities(ctx_cardinalities)
        if is_sequential and model_configs.get("model_units"):
            # remain backwards compatible to models trained without SDEC
            has_sdec = any([f"{SDEC_SUB_COLUMN_PREFIX}cat" in k for k in model_configs.get("model_units").keys()])
            if not has_sdec:
                _LOG.warning("SDEC not found in model_units, removing SDEC columns from tgt_cardinalities")
                del tgt_cardinalities[f"{SDEC_SUB_COLUMN_PREFIX}cat"]
                tgt_sub_columns.remove(f"{SDEC_SUB_COLUMN_PREFIX}cat")
        _LOG.info(f"{len(tgt_sub_columns)=}")
        _LOG.info(f"{len(ctx_sub_columns)=}")

        # read model config
        model_units = model_configs.get("model_units") or ModelSize.M
        _LOG.debug(f"{model_units=}")
        enable_flexible_generation = model_configs.get("enable_flexible_generation", True)
        _LOG.info(f"{enable_flexible_generation=}")

        # resolve device
        device = (
            torch.device(device)
            if device is not None
            else (torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu"))
        )
        _LOG.info(f"{device=}")

        tgt_primary_key = tgt_stats.get("keys", {}).get("primary_key")
        tgt_context_key = tgt_stats.get("keys", {}).get("context_key")
        ctx_primary_key = ctx_stats.get("keys", {}).get("primary_key")
        _LOG.info(f"{tgt_primary_key=}, {tgt_context_key=}, {ctx_primary_key=}")

        if rebalancing and isinstance(rebalancing, dict):
            rebalancing = RebalancingConfig(**rebalancing)
        if imputation and isinstance(imputation, dict):
            imputation = ImputationConfig(**imputation)
        if fairness and isinstance(fairness, dict):
            fairness = FairnessConfig(**fairness)
        _LOG.info(f"imputation: {imputation}")
        _LOG.info(f"rebalancing: {rebalancing}")
        _LOG.info(f"fairness: {fairness}")
        _LOG.info(f"sample_seed: {list(seed_data.columns) if isinstance(seed_data, pd.DataFrame) else None}")
        gen_column_order = _resolve_gen_column_order(
            column_stats=tgt_stats["columns"],
            cardinalities=tgt_cardinalities,
            rebalancing=rebalancing,
            imputation=imputation,
            sample_seed=seed_data,
            fairness=fairness,
        )
        _LOG.info(f"{gen_column_order=}")
        if not enable_flexible_generation:
            # check if resolved column order is the same as the one from training
            trn_column_order = get_columns_from_cardinalities(tgt_cardinalities)
            _LOG.info(f"{trn_column_order=}")
            if gen_column_order != trn_column_order:
                raise ValueError(
                    "The column order for generation does not match the column order from training, due to seed, rebalancing, fairness or imputation configs. "
                    "A change in column order is only permitted for models that were trained with `enable_flexible_generation=True`."
                )

        _LOG.info(f"{rare_category_replacement_method=}")
        rare_token_fixed_probs = _fix_rare_token_probs(tgt_stats, rare_category_replacement_method)
        imputation_fixed_probs = _fix_imputation_probs(tgt_stats, imputation)
        rebalancing_fixed_probs = _fix_rebalancing_probs(tgt_stats, rebalancing)
        fixed_probs = _translate_fixed_probs(
            fixed_probs=_deepmerge(
                rare_token_fixed_probs,
                imputation_fixed_probs,
                rebalancing_fixed_probs,
            ),
            stats=tgt_stats,
        )
        _LOG.info(f"{sampling_temperature=}, {sampling_top_p=}")

        if has_context:
            if ctx_data is None:
                # re-use context from training, if no new context provided
                ctx_data = pd.read_parquet(workspace.ctx_data_path)
            _LOG.info(f"generate new data based on context data `{ctx_data.shape}`")

            # read context input data
            ctx_data = ctx_data.reset_index(drop=True)
            if sample_size is None:
                sample_size = len(ctx_data)
            sample_size = min(sample_size, len(ctx_data))

            # take first `sample_size` rows of context
            ctx_data = ctx_data.head(sample_size)

            # validate context data
            ctx_column_stats = list(ctx_stats["columns"].keys())
            missing_columns = [c for c in ctx_column_stats if c not in ctx_data.columns]
            if len(missing_columns) > 0:
                raise ValueError(f"missing columns in provided context data: {', '.join(missing_columns[:5])}")
        else:
            # create on-the-fly context
            if seed_data is None:
                trn_sample_size = tgt_stats["no_of_training_records"] + tgt_stats["no_of_validation_records"]
                sample_size = trn_sample_size if sample_size is None else sample_size
            else:  # sample_seed is not None
                sample_size = len(seed_data)
            ctx_primary_key = tgt_context_key or DUMMY_CONTEXT_KEY
            tgt_context_key = ctx_primary_key
            ctx_primary_keys = _generate_primary_keys(sample_size, type="int")
            ctx_primary_keys.rename(ctx_primary_key, inplace=True)
            ctx_data = ctx_primary_keys.to_frame()

        if seed_data is None:
            # create on-the-fly sample seed
            seed_data = pd.DataFrame(index=range(sample_size))

        # ensure valid columns in sample_seed
        tgt_columns = list(tgt_stats["columns"].keys()) + ([tgt_primary_key] if tgt_primary_key else [])
        seed_data = seed_data[[c for c in tgt_columns if c in seed_data.columns]]

        # sequence lengths
        seq_len_stats = get_sequence_length_stats(tgt_stats)
        seq_len_median = seq_len_stats["median"]
        seq_len_min = seq_len_stats["min"]
        seq_len_max = seq_len_stats["max"]
        ctx_seq_len_median = get_ctx_sequence_length(ctx_stats, key="median")

        # determine batch_size for generation
        if batch_size is None:
            cpu_mem_available_gb = get_available_ram_for_heuristics() / 1024**3
            gpu_mem_available_gb = get_available_vram_for_heuristics() / 1024**3
            batch_size = _generation_batch_size_heuristic(
                mem_available_gb=cpu_mem_available_gb if device.type == "cpu" else gpu_mem_available_gb,
                ctx_stats=ctx_stats,
                tgt_stats=tgt_stats,
                device=device,
            )
        if batch_size < sample_size:
            no_of_batches = int(np.ceil(sample_size / batch_size))
        else:
            no_of_batches = 1
            batch_size = min(batch_size, sample_size)
        _LOG.info(f"{sample_size=}")
        _LOG.info(f"{list(seed_data.columns)=}")
        _LOG.info(f"{batch_size=}")
        _LOG.info(f"{no_of_batches=}")

        # init progress with total_count; +1 for the final decoding step
        progress.update(completed=0, total=no_of_batches * (seq_len_max + 1))

        _LOG.info("create generative model")
        model: FlatModel | SequentialModel
        if is_sequential:
            model = SequentialModel(
                tgt_cardinalities=tgt_cardinalities,
                tgt_seq_len_median=seq_len_median,
                tgt_seq_len_max=seq_len_max,
                ctx_cardinalities=ctx_cardinalities,
                ctxseq_len_median=ctx_seq_len_median,
                model_size=model_units,
                column_order=gen_column_order,
                device=device,
            )
        else:
            model = FlatModel(
                tgt_cardinalities=tgt_cardinalities,
                ctx_cardinalities=ctx_cardinalities,
                ctxseq_len_median=ctx_seq_len_median,
                model_size=model_units,
                column_order=gen_column_order,
                device=device,
            )

        no_of_model_params = get_no_of_model_parameters(model)
        _LOG.info(f"{no_of_model_params=}")

        load_model_weights(
            model=model,
            path=workspace.model_tabular_weights_path,
            device=device,
        )

        model.to(device)
        model.eval()

        # calculate fairness transforms only once before batch generation
        fairness_transforms: FairnessTransforms | None = None
        if fairness and isinstance(model, FlatModel):
            fairness_transforms: FairnessTransforms = get_fairness_transforms(
                fairness=fairness,
                tgt_stats=tgt_stats,
                forward_fn=partial(
                    model.forward,
                    fixed_probs=fixed_probs,
                    temperature=sampling_temperature,
                    top_p=sampling_top_p,
                ),
                device=device,
            )

        # resolve encoding types for dtypes harmonisation
        ctx_encoding_types = (
            {c_name: c_data["encoding_type"] for c_name, c_data in ctx_stats["columns"].items()} if has_context else {}
        )
        seed_encoding_types = {
            c_name: c_data["encoding_type"]
            for c_name, c_data in tgt_stats["columns"].items()
            if c_name in seed_data.columns
        }

        # add __BATCH to ctx_data
        ctx_data = _batch_df(ctx_data, no_of_batches)

        # add __BATCH to sample_seed
        seed_data = _batch_df(seed_data, no_of_batches)

        # keep at most 500k samples in memory before decoding and writing to disk
        buffer = FixedSizeSampleBuffer(capacity=500_000)

        decode_prev_steps = None

        _LOG.info(f"generate {no_of_batches} batches")
        for batch in range(1, no_of_batches + 1):
            ctx_batch = ctx_data[ctx_data["__BATCH"] == batch]
            ctx_batch = apply_encoding_type_dtypes(ctx_batch, ctx_encoding_types)
            batch_size = len(ctx_batch)

            seed_batch = seed_data[seed_data["__BATCH"] == batch]
            seed_batch = apply_encoding_type_dtypes(seed_batch, seed_encoding_types)

            if ctx_primary_key not in ctx_batch.columns:
                ctx_batch[ctx_primary_key] = pd.Series(
                    data=_generate_primary_keys(len(ctx_batch), type="int").values,
                    index=ctx_batch.index,
                )

            # encode ctx_batch
            _LOG.info(f"encode context {ctx_batch.shape}")
            ctx_batch_encoded, ctx_primary_key_encoded, _ = encode_df(
                df=ctx_batch, stats=ctx_stats, ctx_primary_key=ctx_primary_key
            )
            # pad left context sequences to ensure non-empty sequences
            ctx_batch_encoded = pad_horizontally(ctx_batch_encoded, padding_value=0, right=False)
            ctx_keys = ctx_batch_encoded[ctx_primary_key_encoded]
            ctx_keys.rename(tgt_context_key, inplace=True)

            # encode seed_batch
            _LOG.info(f"encode sample seed values {seed_batch.shape}")
            seed_batch_encoded, _, _ = encode_df(df=seed_batch, stats=tgt_stats)

            # sample data from generative model
            _LOG.info(f"sample data from model with context {ctx_batch.shape}")
            if not tgt_sub_columns:
                # there are no columns to sample, emit warning and continue to batch decoding
                _LOG.warning("no target columns to sample")
                syn = ctx_keys.to_frame().reset_index(drop=True)
                buffer.add((syn,))
            elif isinstance(model, SequentialModel):
                ctxflt_inputs = {
                    col: torch.unsqueeze(
                        torch.as_tensor(ctx_batch_encoded[col].to_numpy(), device=model.device).type(torch.int),
                        dim=-1,
                    )
                    for col in ctx_batch_encoded.columns
                    if col.startswith(CTXFLT)
                }
                ctxseq_inputs = {
                    col: torch.unsqueeze(
                        torch.nested.as_nested_tensor(
                            [torch.as_tensor(t, device=model.device).type(torch.int) for t in ctx_batch_encoded[col]],
                            device=model.device,
                        ),
                        dim=-1,
                    )
                    for col in ctx_batch_encoded.columns
                    if col.startswith(CTXSEQ)
                }
                seq_steps = model.tgt_seq_len_max
                history = None
                history_state = None
                # process context just once for all sequence steps
                context = model.context_compressor(ctxflt_inputs | ctxseq_inputs)
                # loop over sequence steps, and pass forward history to keep model state-less
                out_dct: dict[str, torch.Tensor] = {}
                decode_prev_steps = {}
                # continue sequences until they reach their predicted length
                step_ctx_keys = ctx_keys
                step_size = batch_size
                step_size_drop_threshold = max(50, batch_size // 100)
                for seq_step in range(seq_steps):
                    # exit early if nothing more to sample
                    if step_size == 0:
                        break
                    # fix SIDX by incrementing ourselves instead of sampling
                    sidx = pd.Series([seq_step] * step_size)
                    sidx_df = encode_slen_sidx_sdec(sidx, max_seq_len=seq_steps, prefix=SIDX_SUB_COLUMN_PREFIX)
                    sidx_vals = {
                        c: torch.unsqueeze(
                            torch.as_tensor(sidx_df[c].to_numpy(), device=model.device).type(torch.int),
                            dim=-1,
                        )
                        for c in sidx_df
                    }
                    # fix SLEN by propagating sampled SLEN from first step; and update SDEC accordingly
                    if seq_step > 0:
                        slen_vals = {c: v for c, v in out_dct.items() if c.startswith(SLEN_SUB_COLUMN_PREFIX)}
                        slen = decode_slen_sidx_sdec(
                            pd.DataFrame({c: [x[0].detach().cpu().numpy() for x in v] for c, v in slen_vals.items()}),
                            max_seq_len=seq_steps,
                            prefix=SLEN_SUB_COLUMN_PREFIX,
                        )
                        sdec = (
                            (10 * sidx / slen.clip(lower=1)).clip(upper=9).astype(int)
                        )  # sequence index decile; clip as during GENERATE SIDX can become larger than SLEN
                    else:
                        slen_vals = {}
                        sdec = pd.Series([0] * step_size)  # initial sequence index decile
                    sdec_vals = {
                        f"{SDEC_SUB_COLUMN_PREFIX}cat": torch.unsqueeze(
                            torch.as_tensor(sdec.to_numpy(), device=model.device).type(torch.int), dim=-1
                        )
                    }
                    fixed_values = sidx_vals | slen_vals | sdec_vals
                    out_dct, history, history_state = model(
                        x=None,  # not used in generation forward pass
                        mode="gen",
                        batch_size=step_size,
                        fixed_probs=fixed_probs,
                        fixed_values=fixed_values,
                        temperature=sampling_temperature,
                        top_p=sampling_top_p,
                        history=history,
                        history_state=history_state,
                        context=context,
                    )
                    # transform output dict to tensor for memory efficiency
                    out_pt = torch.stack(list(out_dct.values()), dim=0).transpose(0, 1)
                    # calculate continue sequence mask
                    continue_mask = _continue_sequence_mask(
                        step_output=out_pt,
                        sub_cols=tgt_sub_columns,
                        step_keys=step_ctx_keys,
                        key_name=tgt_context_key,
                        seq_len_min=seq_len_min,
                        seq_len_max=seq_len_max,
                    )
                    next_step_size = continue_mask.sum()
                    # filter next iteration inputs only when threshold is passed
                    # or there is no more data to sample on next iteration
                    if step_size - next_step_size > step_size_drop_threshold or next_step_size == 0:
                        _LOG.info(f"step_size: {step_size} -> {next_step_size}")
                        step_size = next_step_size
                        step_ctx_keys = step_ctx_keys[continue_mask].reset_index(drop=True)
                        out_dct = {k: v[continue_mask, ...] for k, v in out_dct.items()}
                        out_pt = out_pt[continue_mask, ...]
                        # filter context, if it is a sequential context then filter the list of contexts
                        context = [
                            c[continue_mask, ...]
                            if isinstance(c, torch.Tensor)
                            else [sub_c[continue_mask, ...] for sub_c in c]
                            for c in context
                        ]
                        history = history[continue_mask, ...]
                        history_state = tuple(h[:, continue_mask, ...] for h in history_state)
                    # accumulate outputs in memory
                    buffer.add((out_pt, step_ctx_keys))
                    # increment progress by 1 for each step
                    progress.update(advance=1)
                    # conditionally decode on step processing end
                    if buffer.is_full():
                        syn = decode_buffered_samples(
                            buffer=buffer,
                            tgt_stats=tgt_stats,
                            tgt_sub_columns=tgt_sub_columns,
                            tgt_primary_key=tgt_primary_key,
                            tgt_context_key=tgt_context_key,
                            decode_prev_steps=decode_prev_steps,
                        )
                        persist_data_part(syn, output_path, f"{buffer.n_clears:06}.{0:06}")
                        buffer.clear()
            else:  # isinstance(model, FlatModel)
                ctxflt_inputs = {
                    col: torch.unsqueeze(
                        torch.as_tensor(ctx_batch_encoded[col].to_numpy(), device=model.device).type(torch.int),
                        dim=-1,
                    )
                    for col in ctx_batch_encoded.columns
                    if col.startswith(CTXFLT)
                }
                ctxseq_inputs = {
                    col: torch.unsqueeze(
                        torch.nested.as_nested_tensor(
                            [torch.as_tensor(t, device=model.device).type(torch.int) for t in ctx_batch_encoded[col]],
                            device=model.device,
                        ),
                        dim=-1,
                    )
                    for col in ctx_batch_encoded.columns
                    if col.startswith(CTXSEQ)
                }
                x = ctxflt_inputs | ctxseq_inputs
                fixed_values = {
                    col: torch.as_tensor(seed_batch_encoded[col].to_numpy(), device=model.device).type(torch.int)
                    for col in seed_batch_encoded.columns
                }

                out_dct, _ = model(
                    x,
                    mode="gen",
                    batch_size=batch_size,
                    fixed_probs=fixed_probs,
                    fixed_values=fixed_values,
                    temperature=sampling_temperature,
                    top_p=sampling_top_p,
                    fairness_transforms=fairness_transforms,
                )

                syn = pd.concat(
                    [ctx_keys]
                    + [
                        pd.Series(out_dct[sub_col].detach().cpu().numpy(), dtype="int32", name=sub_col)
                        for sub_col in tgt_cardinalities.keys()
                    ],
                    axis=1,
                )
                seed_cols_df = seed_batch.loc[:, seed_batch.columns != "__BATCH"].add_prefix("__seed:")
                if not seed_cols_df.empty:
                    # keep original seed values, in order to preserve them
                    seed_cols_df.reset_index(drop=True, inplace=True)
                    syn = pd.concat([syn, seed_cols_df], axis=1)
                syn.reset_index(drop=True, inplace=True)
                buffer.add((syn,))

            # send number of processed batches / steps
            progress.update(completed=batch * (seq_len_max + 1) - 1)

            # conditionally decode on batch processing end
            if buffer.is_full():
                syn = decode_buffered_samples(
                    buffer=buffer,
                    tgt_stats=tgt_stats,
                    tgt_sub_columns=tgt_sub_columns,
                    tgt_primary_key=tgt_primary_key,
                    tgt_context_key=tgt_context_key,
                    decode_prev_steps=decode_prev_steps,
                )
                persist_data_part(syn, output_path, f"{buffer.n_clears:06}.{0:06}")
                buffer.clear()

            progress.update(completed=batch * (seq_len_max + 1))

        # decode before exit if buffer is not empty or seq_len_max is 0
        if not buffer.is_empty() or seq_len_max == 0:
            syn = decode_buffered_samples(
                buffer=buffer,
                tgt_stats=tgt_stats,
                tgt_sub_columns=tgt_sub_columns,
                tgt_primary_key=tgt_primary_key,
                tgt_context_key=tgt_context_key,
                decode_prev_steps=decode_prev_steps,
            )
            persist_data_part(syn, output_path, f"{buffer.n_clears:06}.{0:06}")
            buffer.clear()
    _LOG.info(f"GENERATE_TABULAR finished in {time.time() - t0:.2f}s")
