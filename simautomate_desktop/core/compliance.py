import pandas as pd
import numpy as np
import glob
import os

def calculate_deviations(df_real, df_sim):
    # Align columns and lengths
    common_cols = [col for col in df_real.columns if col in df_sim.columns and col.lower() not in ['time', 'time (s)']]
    min_len = min(len(df_real), len(df_sim))
    df_real = df_real.iloc[:min_len]
    df_sim = df_sim.iloc[:min_len]
    # Avoid division by zero
    safe_real = df_real[common_cols].replace(0, np.nan)
    difference = df_sim[common_cols] - df_real[common_cols]
    percentage_deviation = np.where(~np.isnan(safe_real), (difference / safe_real) * 100, 0)
    absolute_percentage_deviation = np.where(~np.isnan(safe_real), (difference.abs() / safe_real) * 100, 0)
    df_results = df_real[common_cols].copy()
    for idx, col in enumerate(common_cols):
        df_results[f'{col}_percentage_deviation'] = percentage_deviation[:, idx]
        df_results[f'{col}_absolute_percentage_deviation'] = absolute_percentage_deviation[:, idx]
    # Add time column if present
    for tcol in ['Time (s)', 'time', 'Time']:
        if tcol in df_real.columns:
            df_results[tcol] = df_real[tcol].values[:min_len]
            break
    return df_results

def analyze_compliance(df_results):
    percentage_cols = [col for col in df_results.columns if col.endswith('_percentage_deviation')]
    if not percentage_cols:
        return {"status": "UNKNOWN", "summary": "No deviation data available for compliance analysis."}
    max_deviations = {}
    avg_deviations = {}
    for col in percentage_cols:
        max_dev = abs(df_results[col]).max()
        avg_dev = abs(df_results[col]).mean()
        param_name = col.replace('_percentage_deviation', '').replace('_', ' ').title()
        max_deviations[param_name] = max_dev
        avg_deviations[param_name] = avg_dev
    critical_threshold = 10.0
    warning_threshold = 5.0
    critical_params = [param for param, dev in max_deviations.items() if dev > critical_threshold]
    warning_params = [param for param, dev in max_deviations.items() if warning_threshold < dev <= critical_threshold]
    compliant_params = [param for param, dev in max_deviations.items() if dev <= warning_threshold]
    report = {
        'status': 'CRITICAL' if critical_params else ('WARNING' if warning_params else 'COMPLIANT'),
        'max_deviations': max_deviations,
        'avg_deviations': avg_deviations,
        'critical_params': critical_params,
        'warning_params': warning_params,
        'compliant_params': compliant_params,
        'summary': f"Analysis complete. {len(compliant_params)} parameters compliant, {len(warning_params)} with warnings, {len(critical_params)} critical."
    }
    return report 

# Compliance mapping: parameter -> (section, max_limit, mean_limit, units)
COMPLIANCE_SECTIONS = {
    'Northing':    {'section': '2.1', 'max': 0.05, 'mean': 0.02, 'units': '%'},
    'Easting':     {'section': '2.1', 'max': 0.05, 'mean': 0.02, 'units': '%'},
    'Altitude':    {'section': '2.1', 'max': 0.05, 'mean': 0.02, 'units': '%'},
    'Roll':        {'section': '3.1', 'max': 3.0,  'mean': 1.5, 'units': 'deg'},
    'Pitch':       {'section': '3.1', 'max': 3.0,  'mean': 1.5, 'units': 'deg'},
    'Heading':     {'section': '3.1', 'max': 3.0,  'mean': 1.5, 'units': 'deg'},
    'x':           {'section': '4.1', 'max': 0.10, 'mean': 0.05, 'units': '%'},
    'y':           {'section': '4.1', 'max': 0.10, 'mean': 0.05, 'units': '%'},
    'z':           {'section': '4.1', 'max': 0.10, 'mean': 0.05, 'units': '%'},
    'Tot':         {'section': '4.1', 'max': 0.10, 'mean': 0.05, 'units': '%'},
}

def generate_compliance_mapping_report(df_results):
    """
    Given a DataFrame with deviation columns, generate a compliance mapping report.
    Returns: (report_table, summary)
    """
    import numpy as np
    report = []
    non_compliant_sections = set()
    for param, info in COMPLIANCE_SECTIONS.items():
        max_col = f'{param}_absolute_percentage_deviation'
        if max_col not in df_results.columns:
            continue
        max_dev = np.nanmax(np.abs(df_results[max_col])) / 100.0  # convert % to fraction
        mean_dev = np.nanmean(np.abs(df_results[max_col])) / 100.0
        status = 'Compliant'
        details = ''
        if max_dev > info['max']:
            status = 'Non-Compliant'
            details = f'Max deviation {max_dev*100:.2f}% exceeds allowed {info["max"]*100:.2f}%.'
            non_compliant_sections.add(info['section'])
        elif mean_dev > info['mean']:
            status = 'Warning'
            details = f'Mean deviation {mean_dev*100:.2f}% exceeds allowed {info["mean"]*100:.2f}%.'
            non_compliant_sections.add(info['section'])
        report.append({
            'Compliance Section': info['section'],
            'Parameter': param,
            'Max Deviation (%)': f'{max_dev*100:.2f}',
            'Allowed Max (%)': f'{info["max"]*100:.2f}' if info['units'] == '%' else f'{info["max"]:.2f}',
            'Mean Deviation (%)': f'{mean_dev*100:.2f}',
            'Allowed Mean (%)': f'{info["mean"]*100:.2f}' if info['units'] == '%' else f'{info["mean"]:.2f}',
            'Status': status,
            'Details/Reasoning': details
        })
    summary = f"Non-compliance detected in Sections: {', '.join(sorted(non_compliant_sections))}" if non_compliant_sections else "All parameters compliant."
    return report, summary 

def aggregate_all_deviations(report_folder):
    """
    Aggregate deviations for all parameters from all df_chart_X_real/simulated.csv files in a report folder.
    Returns a single DataFrame for compliance mapping.
    """
    all_results = []
    chart_files = sorted(glob.glob(os.path.join(report_folder, 'df_chart_*_real.csv')))
    for real_file in chart_files:
        sim_file = real_file.replace('_real.csv', '_simulated.csv')
        if not os.path.exists(sim_file):
            continue
        df_real = pd.read_csv(real_file)
        df_sim = pd.read_csv(sim_file)
        df_results = calculate_deviations(df_real, df_sim)
        all_results.append(df_results)
    if all_results:
        return pd.concat(all_results, axis=1)
    else:
        return pd.DataFrame() 