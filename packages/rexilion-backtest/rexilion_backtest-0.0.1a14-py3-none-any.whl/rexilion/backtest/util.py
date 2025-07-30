import pandas as pd
import numpy as np
import glob
import pandas as pd
from rexilion.backtest import formula

def load_data(data_path, candle_path, start_time, end_time, shift_time):
    # Check if data_path is not empty, and load the data
    if data_path:
        data = pd.read_csv(data_path)
        data_columns_to_drop = ["close"]

        # Drop columns if they exist
        data = data.drop(
            columns=[col for col in data_columns_to_drop if col in data.columns],
            axis=1,
        )

        # If 'datetime' column doesn't exist, create one from 'start_time'
        if "datetime" not in data.columns and "start_time" in data.columns:
            data["datetime"] = pd.to_datetime(data["start_time"], unit="ms", utc=True).dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        # If data_path is empty, create an empty DataFrame
        data = pd.DataFrame()

    # Load candle data
    candle = pd.read_csv(candle_path)
    candle.loc[:, "candle_ori_datetime"] = pd.to_datetime(candle["start_time"], unit="ms", utc=True).dt.strftime("%Y-%m-%d %H:%M:%S")
    candle.loc[:, "start_time"] = candle["start_time"] - shift_time * 60000

    # If data is not empty, merge it with the candle data
    if not data.empty:
        df_after_merge = pd.merge(data, candle, on="start_time", how="left")
        columns_to_drop = ["end_time_y", "end_time_x", "Unnamed: 0_x", "Unnamed: 0_y", "end_time"]

        # Drop columns if they exist
        df_after_merge = df_after_merge.drop(
            columns=[col for col in columns_to_drop if col in df_after_merge.columns],
            axis=1,
        )
    else:
        # Use candle data only if data is empty
        df_after_merge = candle.copy()

    # Rename candle_ori_datetime to datetime if the datetime column is missing
    if "datetime" not in df_after_merge.columns:
        df_after_merge = df_after_merge.rename(columns={"candle_ori_datetime": "datetime"})

    start_time_ms = int(start_time.timestamp() * 1000)
    end_time_ms = int(end_time.timestamp() * 1000)

    if start_time_ms is not None:
        df_after_merge = df_after_merge.loc[df_after_merge["start_time"] >= start_time_ms]
    if end_time_ms is not None:
        df_after_merge = df_after_merge.loc[df_after_merge["start_time"] < end_time_ms]
        
    df_after_merge = df_after_merge.reset_index(drop=True)
    df_after_merge.loc[:, "price_chg"] = df_after_merge["close"].pct_change()

    return df_after_merge

def slice_data(df: pd.DataFrame, start_time, end_time) -> pd.DataFrame:
    """
    Return only the rows whose 'start_time' (in ms) lies in [start_time, end_time).

    Parameters
    ----------
    df : pd.DataFrame
        Must contain a 'start_time' column (ms since epoch, UTC).
    start_time : datetime-like or pd.Timestamp
        Inclusive lower bound.
    end_time : datetime-like or pd.Timestamp
        Exclusive upper bound.

    Returns
    -------
    pd.DataFrame
        The filtered, index-reset DataFrame.
    """
    # 1) coerce to pandas Timestamp with UTC
    start_ts = pd.to_datetime(start_time, utc=True)
    end_ts   = pd.to_datetime(end_time,   utc=True)

    # 2) convert to millis
    start_ms = int(start_ts.timestamp() * 1000)
    end_ms   = int(end_ts.timestamp()   * 1000)

    # 3) filter and reset index
    mask = (df['start_time'] >= start_ms) & (df['start_time'] < end_ms)
    return df.loc[mask].reset_index(drop=True)

def generate_report(df, param1, param2, fees, sr_multiplier, start_time, end_time):
    # Calculate trades and PnL
    df["trades"] = abs(df["pos"] - df["pos"].shift(1))
    df["pnl"] = df["price_chg"] * df["pos"].shift(1) - df["trades"] * fees / 100.0
    df = slice_data(df, start_time, end_time)
    df["cumu"] = df["pnl"].cumsum()

    # Sharpe Ratio
    sharp_ratio = df["pnl"].mean() / df["pnl"].std() * np.sqrt(365 * sr_multiplier) if df["pnl"].std() != 0 else 0

    # Maximum drawdown and recovery period
    df["cumu_max"] = df["cumu"].cummax()
    df["drawdown"] = df["cumu"] - df["cumu_max"]
    mdd = df["drawdown"].min()

    recovery_period_days = None  # Default when no recovery occurs
    if mdd < 0:  # Proceed only if a drawdown exists
        # Find the start of the maximum drawdown
        mdd_start_idx = df[df["drawdown"] == mdd].index[0]

        # Find recovery index (if exists)
        recovery_idxs = df[(df.index > mdd_start_idx) & (df["cumu"] >= df.loc[mdd_start_idx, "cumu_max"])].index

        if len(recovery_idxs) > 0:
            recovery_period = recovery_idxs[0] - mdd_start_idx

            # Convert to days
            if isinstance(df.index, pd.DatetimeIndex):
                recovery_period_days = recovery_period.total_seconds() / (3600 * 24)
            else:
                recovery_period_days = recovery_period / 24  # Assume each step in the index represents 1 hour

    # Annualized return and Calmar Ratio
    ar = df["pnl"].mean() * 365 * sr_multiplier
    cr = ar / abs(mdd) if mdd != 0 else float('inf')

    # Total trades
    trades_count = df["trades"].sum()

    # Generate report
    report = {
        "param1": param1,
        "param2": param2,
        "SR": sharp_ratio,
        "CR": cr,
        "MDD": mdd,
        "Recovery Period (days)": recovery_period_days,
        "Trades": trades_count,
        "AR": ar,
        "Trades Ratio": trades_count / len(df),
    }
    return report, df

def merge_csv_files(folder_path, output_file):
    """
    Merges multiple CSV files based on 'start_time' and 'datetime', keeping the first 'close' column
    encountered and removing 'close' and 'endtime' from all other files.
    
    :param folder_path: Path to the folder containing CSV files.
    :param output_file: Path to save the merged CSV file.
    """
    try:
        csv_files = glob.glob(f"{folder_path}/*.csv")
        if not csv_files:
            print("No CSV files found in the folder. Skipping merge.")
            return

        dfs = {}
        required_columns = {'start_time', 'datetime'}
        close_file = None  # Track the file with the first 'close' column
        
        for file in csv_files:
            try:
                df = pd.read_csv(file, usecols=lambda col: col not in ['Unnamed: 0'])
                if not required_columns.issubset(df.columns):
                    print(f"Skipping {file}: Required columns {required_columns} not found.")
                    continue
                df = df.drop_duplicates(subset=['start_time', 'datetime'])
                df = df.drop(columns=['endtime'], errors='ignore')  # Drop 'endtime' column
                dfs[file] = df
                
                # Check for 'close' column and set the first one found
                if 'close' in df.columns and close_file is None:
                    close_file = file
            except Exception as e:
                print(f"Error reading {file}: {str(e)}")
                continue

        if not dfs:
            print("No valid CSV files found. Skipping merge.")
            return

        # Use the DataFrame with the first 'close' as the base (if found), otherwise the first file
        if close_file:
            base_file = close_file
            print(f"Using 'close' from {base_file}")
        else:
            base_file = list(dfs.keys())[0]
            print(f"No 'close' column found in any file; using {base_file} as base without 'close'.")
        
        merged_df = dfs[base_file]

        # Merge with remaining DataFrames, dropping their 'close' columns if not the base
        for file, df in dfs.items():
            if file == base_file:
                continue
            df_no_close = df.drop(columns=['close'], errors='ignore')  # Drop 'close' if not base
            suffix = f"_{file.split('/')[-1].replace('.csv', '')}"
            merged_df = merged_df.merge(df_no_close, on=['start_time', 'datetime'], 
                                        how='inner', suffixes=(None, suffix))

        # Save result
        merged_df.to_csv(output_file, index=False)
        print(f"Merged data saved to {output_file}")

    except Exception as e:
        print(f"Error during merge: {str(e)}")

def data_transformation(
    data_csv: str,
    output_csv: str,
    time_col: str = 'start_time',
    windows: list = [12, 24],
    cols_to_enrich: list = None,
    shift: int = None,
) -> pd.DataFrame:
    # 1. load & merge
    df   = pd.read_csv(data_csv)

    # 2. decide which columns to enrich
    if cols_to_enrich is None:
        # pick all numeric columns in df_data except the time_col
        cols_to_enrich = [
            c for c in df.select_dtypes(include='number').columns
            if c != time_col
        ]

    # 3. build metrics for each column
    all_metrics = {}
    for col in cols_to_enrich:
        s = df[col].shift(shift)

        all_metrics[f'{col}_{shift}'] = s
        all_metrics[f'{col}_pct_change'] = formula.pct_change(s)
        all_metrics[f'{col}_signedlog']  = formula.signed_log1p(s)
        all_metrics[f'{col}_logreturns']  = formula.log_returns(s)
        for w in range(1,4):
            all_metrics[f'{col}_diff_n_{w}'] = formula.diff_n(s, w)
            all_metrics[f'{col}_log_diff_n_{w}'] = formula.log_diff_n(s, w)

        # windowed metrics
        for w in windows:
            all_metrics[f'{col}_mean_{w}']    = formula.rolling_mean(s,w)
            all_metrics[f'{col}_std_{w}']     = formula.rolling_std(s,w)
            all_metrics[f'{col}_min_{w}']     = formula.rolling_min(s,w)
            all_metrics[f'{col}_max_{w}']     = formula.rolling_max(s,w)
            all_metrics[f'{col}_sum_{w}']     = formula.rolling_sum(s,w)
            all_metrics[f'{col}_range_{w}']   = formula.rolling_range(s,w)
            all_metrics[f'{col}_cvs_{w}']     = formula.rolling_cvs(s,w)
            all_metrics[f'{col}_var_{w}']     = formula.rolling_var(s,w)
            all_metrics[f'{col}_skew_{w}']    = formula.rolling_skew(s,w)
            all_metrics[f'{col}_kurtosis_{w}'] = formula.rolling_kurt(s,w)
            all_metrics[f'{col}_moment5_{w}'] = formula.rolling_moment(s,w,5)
            all_metrics[f'{col}_moment6_{w}'] = formula.rolling_moment(s,w,6)
            all_metrics[f'{col}_zscore_{w}']   = formula.rolling_zscore(s,w)
            all_metrics[f'{col}_zscore_mean_{w}'] = formula.rolling_zscore_mean(s,w)
            all_metrics[f'{col}_ema_{w}']     = formula.rolling_ema(s,w)
            all_metrics[f'{col}_wma_{w}']     = formula.rolling_wma(s,w)
            all_metrics[f'{col}_minmax_{w}']     = formula.rolling_minmax_normalize(s,w)
            all_metrics[f'{col}_meannorm_{w}']     = formula.rolling_mean_normalize(s,w)
            all_metrics[f'{col}_sigmoidzscore_{w}']     = formula.rolling_sigmoid_zscore(s,w)
            all_metrics[f'{col}_median_{w}'] = formula.rolling_median(s,w)
            all_metrics[f'{col}_iqr_{w}'] = formula.rolling_iqr(s,w)
            all_metrics[f'{col}_mad_{w}'] = formula.rolling_mad(s,w)
            all_metrics[f'{col}_robust_z_{w}'] = formula.rolling_robust_z(s,w)
            all_metrics[f'{col}_mdd_{w}'] = formula.rolling_max_drawdown(s,w)
            all_metrics[f'{col}_trend_slope_{w}'] = formula.rolling_trend_slope(s,w)
            all_metrics[f'{col}_entropy_{w}'] = formula.rolling_entropy(s,w)
            all_metrics[f'{col}_positive_ratio_{w}'] = formula.rolling_positive_ratio(s,w)
            all_metrics[f'{col}_direction_change_{w}'] = formula.rolling_direction_changes(s,w)
            all_metrics[f'{col}_autocorr1_{w}'] = formula.rolling_autocorr(s,w,1)
            all_metrics[f'{col}_autocorr2_{w}'] = formula.rolling_autocorr(s,w,2)
            all_metrics[f'{col}_autocorr3_{w}'] = formula.rolling_autocorr(s,w,3)
            all_metrics[f'{col}_autocorr4_{w}'] = formula.rolling_autocorr(s,w,4)
            all_metrics[f'{col}_autocorr5_{w}'] = formula.rolling_autocorr(s,w,5)
            all_metrics[f'{col}_autocorr6_{w}'] = formula.rolling_autocorr(s,w,6)
            all_metrics[f'{col}_autocorr12_{w}'] = formula.rolling_autocorr(s,w,12)
            all_metrics[f'{col}_autocorr24_{w}'] = formula.rolling_autocorr(s,w,24)
            all_metrics[f'{col}_sharpe_like_{w}'] = formula.rolling_sharpe_like(s,w)
            all_metrics[f'{col}_zscore_jump_{w}'] = formula.rolling_zscore_jump(s,w)
            # all_metrics[f'{col}_yeojohonson_{w}'] = formula.rolling_yeojohnson(s,w)
            # all_metrics[f'{col}_trend_angle_{w}'] = formula.rolling_trend_angle(s,w)
            all_metrics[f'{col}_volatility_adjusted_return_{w}'] = formula.rolling_volatility_adjusted_return(s,w)
            all_metrics[f'{col}_slope_acceleration_{w}'] = formula.rolling_slope_acceleration(s,w)

    # 4. assemble, drop warm-up, write
    df_metrics  = pd.DataFrame(all_metrics, index=df.index)
    max_w       = max(windows)
    df_enriched = pd.concat([df, df_metrics], axis=1).iloc[max_w:].reset_index(drop=True)
    df_enriched.to_csv(output_csv, index=False)
    return df_enriched