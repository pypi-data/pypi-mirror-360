# meu_tabplot_lib.py

# Necessary imports for binning and plotting functions
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- Helper Function: truncate_label ---
def truncate_label(label, max_len=20):
    """Truncates a string if too long, adding '...'"""
    if len(label) > max_len:
        return label[:max_len-3] + '...'
    return label

# --- PART 1: Binning Function (simulate_tabplot_binning) ---
def simulate_tabplot_binning(df, nbins=100, sort_col=None, decreasing=True, max_levels=50):
    """
    Simulates the binning and aggregation process of R's tabplot.
    This function is an INTERPRETATION, not a direct line-by-line translation,
    due to the complexity and dependencies of R packages (`ff`, `ffbase`, `grid`).
    
    Arguments:
        df (pd.DataFrame): Input DataFrame.
        nbins (int): Desired number of bins.
        sort_col (str): Column name for sorting.
        decreasing (bool): True for descending order, False for ascending.
        max_levels (int): Maximum number of levels for re-binning high-cardinality categories.
                          In R, bin_hcc_data handles this.
    
    Returns:
        tuple: (binned_data, bin_sizes, total_rows)
            binned_data (dict): Dictionary with aggregated data per column and bin.
            bin_sizes (list): Size of each bin.
            total_rows (int): Total number of rows processed.
    """
    if df.empty:
        raise ValueError("Empty DataFrame. No data to process.")

    # Adjust: If sort_col is None, try to use the first numeric column.
    # If 'ID_Cliente' is present and numeric, prioritize it as default.
    if sort_col is None:
        if 'ID_Cliente' in df.columns and pd.api.types.is_numeric_dtype(df['ID_Cliente']):
            sort_col = 'ID_Cliente'
        else:
            numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
            sort_col = numeric_cols[0] if numeric_cols else df.columns[0]

    if sort_col not in df.columns:
        raise ValueError(f"Sort column '{sort_col}' not found in DataFrame.")

    df_sorted = df.sort_values(by=sort_col, ascending=not decreasing).reset_index(drop=True)
    total_rows = len(df_sorted)

    if total_rows < 2:
        raise ValueError("Insufficient rows to create at least 2 bins.")

    unique_rows_for_qcut = df_sorted.index.nunique()
    actual_nbins = min(nbins, unique_rows_for_qcut)
    
    # Adding a fallback if qcut fails (e.g., due to highly repetitive data)
    try:
        if actual_nbins < 2:
            df_sorted['bin'] = pd.cut(df_sorted.index, bins=max(2, actual_nbins), labels=False, include_lowest=True)
            actual_nbins = df_sorted['bin'].nunique()
        else:
            # Tries qcut, which creates bins with approximately equal numbers of elements
            df_sorted['bin'] = pd.qcut(df_sorted.index, actual_nbins, labels=False, duplicates='drop')
    except Exception as e:
        print(f"Warning: pd.qcut failed with {e}. Using pd.cut as fallback.")
        # Fallback to pd.cut, which creates equally sized bins along the index
        df_sorted['bin'] = pd.cut(df_sorted.index, bins=max(2, actual_nbins), labels=False, include_lowest=True)
        actual_nbins = df_sorted['bin'].nunique()
        if actual_nbins < 2:
            raise ValueError(f"Could not create at least 2 bins with the provided data, even with fallback. Consider increasing 'nbins' or checking data diversity.")

    bin_sizes_raw = df_sorted['bin'].value_counts().sort_index().tolist()
    normalized_bin_sizes = np.array(bin_sizes_raw) / total_rows

    # Natural bin order (smallest at top, largest at bottom)
    bin_y_starts_normalized = np.insert(np.cumsum(normalized_bin_sizes)[:-1], 0, 0)
    bar_heights_normalized = normalized_bin_sizes

    binned_data = {}

    for col_name in df.columns: # Iterate over columns of the original df
        is_categorical = isinstance(df_sorted[col_name].dtype, pd.CategoricalDtype) or df_sorted[col_name].dtype == 'object'

        if col_name not in df_sorted.columns: # Check if column exists in df_sorted after sorting/binning
            continue

        if pd.api.types.is_numeric_dtype(df_sorted[col_name]): # Use df_sorted for type check
            grouped = df_sorted.groupby('bin')[col_name]
            mean_values = grouped.mean().values
            std_values = grouped.std().values
            median_values = grouped.median().values
            completeness = grouped.apply(lambda x: x.count() / len(x)).values * 100

            is_log_scale = False
            # Adjustment to avoid log of zero or very small values, and check for variety.
            if df_sorted[col_name].min() >= 0 and df_sorted[col_name].max() > df_sorted[col_name].min() + 1e-6: # Add small tolerance
                pos_values = df_sorted[col_name][df_sorted[col_name] > 0]
                if not pos_values.empty:
                    log_min_val = pos_values.min()
                    log_max_val = df_sorted[col_name].max()
                    if log_min_val > 0: # Ensures minimum is greater than zero for log
                        log_min = np.log10(log_min_val + 1)
                        log_max = np.log10(log_max_val + 1)
                        if (log_max - log_min) > 1.5:
                            is_log_scale = True

            def get_log_transform(arr):
                log_arr = np.empty_like(arr, dtype=float)
                log_arr[pd.isna(arr)] = np.nan
                pos_mask = (arr >= 0) & (~pd.isna(arr))
                neg_mask = (arr < 0) & (~pd.isna(arr))
                log_arr[pos_mask] = np.log10(arr[pos_mask] + 1)
                log_arr[neg_mask] = -np.log10(np.abs(arr[neg_mask]) + 1)
                return log_arr

            mean_scaled = get_log_transform(mean_values) if is_log_scale else mean_values
            std_scaled = get_log_transform(std_values) if is_log_scale else std_values
            median_scaled = get_log_transform(median_values) if is_log_scale else median_values

            tooltip_text = [
                f"Bin: {bin_idx}<br>"
                f"Mean {col_name}: {mean_values[bin_idx]:.2f}<br>"
                f"Median {col_name}: {median_values[bin_idx]:.2f}<br>"
                f"Standard Deviation {std_values[bin_idx]:.2f}<br>" # Corrected here
                f"Completeness: {completeness[bin_idx]:.2f}%"
                for bin_idx in range(actual_nbins)
            ]

            binned_data[col_name] = {
                'type': 'numeric',
                'mean': mean_values,
                'sd': std_values,
                'median': median_values,
                'completeness': completeness,
                'mean_scaled': mean_scaled,
                'sd_scaled': std_scaled,
                'median_scaled': median_scaled,
                'is_log_scale': is_log_scale,
                'tooltip': tooltip_text,
                'y_positions': bin_y_starts_normalized,
                'bar_heights': bar_heights_normalized
            }

        elif is_categorical: # Use the new is_categorical variable
            temp_series = df_sorted[col_name].astype(str)
            value_counts_per_bin = temp_series.groupby(df_sorted['bin']).value_counts(normalize=False).unstack(fill_value=0)

            current_categories = value_counts_per_bin.columns.tolist()
            if len(current_categories) > max_levels:
                top_categories = df_sorted[col_name].value_counts().nlargest(max_levels - 1).index.tolist()
                value_counts_per_bin['Outros'] = value_counts_per_bin.apply(
                    lambda row: row[[c for c in current_categories if c not in top_categories]].sum(), axis=1
                )
                value_counts_per_bin = value_counts_per_bin[top_categories + ['Outros']]
                current_categories = top_categories + ['Outros']

            missing_counts_per_bin = df_sorted.groupby('bin')[col_name].apply(lambda x: x.isna().sum())
            total_per_bin = df_sorted.groupby('bin').size()

            freq_table = value_counts_per_bin.div(total_per_bin, axis=0).fillna(0)
            freq_missing = missing_counts_per_bin.div(total_per_bin, axis=0).fillna(0)

            widths_with_missing = pd.concat([freq_table, freq_missing.rename('missing')], axis=1).values
            categories_with_missing = current_categories + ['missing']

            x_starts = np.zeros_like(widths_with_missing, dtype=float)
            if widths_with_missing.shape[1] > 1:
                x_starts[:, 1:] = np.cumsum(widths_with_missing[:, :-1], axis=1)

            tooltip_text = []
            for bin_idx in range(actual_nbins):
                bin_tip = f"Bin: {bin_idx}<br>"
                for cat_idx, cat in enumerate(categories_with_missing):
                    bin_tip += f"{cat}: {widths_with_missing[bin_idx, cat_idx]:.2%}<br>"
                tooltip_text.append(bin_tip)

            binned_data[col_name] = {
                'type': 'categorical',
                'categories': categories_with_missing,
                'widths': widths_with_missing,
                'x_starts': x_starts,
                'tooltip': tooltip_text,
                'y_positions': bin_y_starts_normalized,
                'bar_heights': bar_heights_normalized
            }

        else:
            binned_data[col_name] = {'type': 'unsupported'}

    return binned_data, bin_sizes_raw, total_rows

# --- PART 2: Interactive Plotting Function ---
def plot_tabplot_interactive(binned_data, title="Dynamic Tableplot"):
    column_names = [col for col, data in binned_data.items() if data['type'] != 'unsupported']
    if not column_names:
        print("No supported columns for plotting found in the processed data.")
        return

    num_cols = len(column_names)
    nbins = len(binned_data[column_names[0]]['y_positions'])

    subplot_titles_display = ["%"] + [
        f"{col} (log)" if binned_data[col]['type'] == 'numeric' and binned_data[col]['is_log_scale'] else col
        for col in column_names
    ]

    # Define column width proportions
    column_widths_proportions = [0.05] + [1.0/num_cols] * num_cols

    # Calculate cumulative positions for x-axes in 'paper' coordinates
    x_paper_starts = [0]
    for prop in column_widths_proportions[:-1]:
        x_paper_starts.append(x_paper_starts[-1] + prop)

    # Adjust bottom margin and total height to accommodate legends
    initial_bottom_margin = 250 
    fig_height = 700 + initial_bottom_margin

    fig = make_subplots(
        rows=1, cols=num_cols + 1,
        column_widths=column_widths_proportions,
        shared_yaxes=True,
        horizontal_spacing=0.01,
        subplot_titles=subplot_titles_display
    )

    y_tick_vals = np.linspace(0, 1, 11)
    fig.update_yaxes(
        title_text="%",
        range=[1, 0], 
        tickvals=y_tick_vals,
        ticktext=[f"{int(p*100)}%" for p in y_tick_vals],
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgray',
        row=1, col=1
    )

    fig.add_trace(go.Scatter(
        x=[0.8, 0.8],
        y=[0, 1],
        mode='lines',
        line=dict(color='gray', width=1),
        showlegend=False,
        hoverinfo='none'
    ), row=1, col=1)

    # Default colors for categorical, including 'missing'
    default_category_colors = px.colors.qualitative.Plotly
    
    for i, col_name in enumerate(column_names):
        data = binned_data[col_name]
        current_col_idx_in_layout = i + 2 
        
        # Get the x-axis domain for the current subplot in 'paper' coordinates
        current_xaxis_domain_start = fig.layout[f'xaxis{current_col_idx_in_layout}'].domain[0]
        current_xaxis_domain_end = fig.layout[f'xaxis{current_col_idx_in_layout}'].domain[1]
        domain_width = current_xaxis_domain_end - current_xaxis_domain_start


        fig.add_shape(type="rect",
                      xref=f"x{current_col_idx_in_layout}", yref=f"y{current_col_idx_in_layout}",
                      x0=0, y0=0, x1=1, y1=1,
                      fillcolor="#F0F0F0", layer="below", line_width=0,
                      row=1, col=current_col_idx_in_layout)

        if data['type'] == 'numeric':
            x_range_min = np.nanmin(data['mean_scaled'])
            x_range_max = np.nanmax(data['mean_scaled'])
            padding = 0.1 * (x_range_max - x_range_min)

            fig.update_xaxes(
                title_text="",
                range=[x_range_min - padding, x_range_max + padding],
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray',
                row=1, col=current_col_idx_in_layout
            )

            # --- Define colors for mean, median, and standard deviation ---
            mean_bar_color = 'blue'  
            median_marker_color = 'lightgray' 
            sd_line_color = 'dimgray' 

            for bin_idx in range(nbins):
                y = data['y_positions'][bin_idx]
                h = data['bar_heights'][bin_idx]

                # Mean Bar 
                fig.add_trace(go.Bar(
                    x=[data['mean_scaled'][bin_idx]],
                    y=[y],
                    width=[h],
                    orientation='h',
                    marker_color=mean_bar_color,
                    marker_line_color='rgba(0,0,0,0.1)',
                    marker_line_width=0.5,
                    hovertemplate=data['tooltip'][bin_idx] + "<extra></extra>",
                    showlegend=False
                ), row=1, col=current_col_idx_in_layout)

                # Standard Deviation 
                if not np.isnan(data['sd_scaled'][bin_idx]) and data['sd_scaled'][bin_idx] > 0:
                    x_sd_start = data['mean_scaled'][bin_idx] - data['sd_scaled'][bin_idx]
                    x_sd_end = data['mean_scaled'][bin_idx] + data['sd_scaled'][bin_idx]

                    fig.add_trace(go.Scatter(
                        x=[x_sd_start, x_sd_end],
                        y=[y + h / 2] * 2,
                        mode='lines',
                        line=dict(color=sd_line_color, width=2),
                        hoverinfo='none',
                        showlegend=False
                    ), row=1, col=current_col_idx_in_layout)

                # Median 
                if not np.isnan(data['median_scaled'][bin_idx]):
                    fig.add_trace(go.Scatter(
                        x=[data['median_scaled'][bin_idx]],
                        y=[y + h / 2],
                        mode='markers',
                        marker=dict(symbol='line-ns', size=10, color=median_marker_color, line=dict(width=2)),
                        hoverinfo='none',
                        showlegend=False
                    ), row=1, col=current_col_idx_in_layout)

        elif data['type'] == 'categorical':
            fig.update_xaxes(
                title_text="",
                range=[0, 1],
                tickformat=".0%",
                showgrid=False,
                row=1, col=current_col_idx_in_layout
            )

            # Color mapping for categories
            category_colors = {}
            for cat_idx, cat in enumerate(data['categories']):
                if cat == 'missing':
                    category_colors['missing'] = '#FF1414' 
                else:
                    category_colors[cat] = default_category_colors[cat_idx % len(default_category_colors)]

            for bin_idx in range(nbins):
                y = data['y_positions'][bin_idx]
                h = data['bar_heights'][bin_idx]

                for cat_idx, cat in enumerate(data['categories']): # Iterate directly over data['categories']
                    w = data['widths'][bin_idx, cat_idx]
                    x0 = data['x_starts'][bin_idx, cat_idx]

                    if w > 0:
                        fig.add_trace(go.Bar(
                            x=[w],
                            y=[y],
                            base=[x0],
                            width=[h],
                            orientation='h',
                            marker_color=category_colors.get(cat, '#333'),
                            marker_line_color='rgba(0,0,0,0.1)',
                            marker_line_width=0.5,
                            hovertemplate=data['tooltip'][bin_idx] + "<extra></extra>",
                            showlegend=False
                        ), row=1, col=current_col_idx_in_layout)

            fig.update_layout(barmode='stack')

            # --- Add legends as annotations for categorical columns ---
            y_pos_start = -0.12 
            line_height = 0.025 
            marker_size = 8
            text_x_offset = 0.012 

            categories_for_legend = data.get('categories', []) 
            num_categories = len(categories_for_legend)
            
            # Try 2 columns for legend if space allows and many categories
            num_legend_cols = 1
            if domain_width > 0.15 and num_categories > 4: 
                num_legend_cols = 2
            
            # Available width for the legend within the axis domain (in paper coordinates)
            available_legend_width = domain_width 
            col_width_for_legend_items = available_legend_width / num_legend_cols

            min_y_annotation = y_pos_start 

            for cat_idx, cat in enumerate(categories_for_legend):
                color = category_colors.get(cat, '#333')
                truncated_cat = truncate_label(cat, max_len=27) 
                
                legend_col_idx = cat_idx % num_legend_cols
                legend_row_idx = cat_idx // num_legend_cols

                # X position for legend marker and text (based on x-axis domain)
                marker_x = current_xaxis_domain_start + (legend_col_idx * col_width_for_legend_items) + 0.005 
                text_x = marker_x + text_x_offset 

                # Y position for legend item (below the graph, new lines for each item)
                item_y = y_pos_start - (legend_row_idx * line_height)
                min_y_annotation = min(min_y_annotation, item_y) 

                # Add the marker (colored square)
                fig.add_annotation(
                    xref='paper', yref='paper',
                    x=marker_x, y=item_y,
                    showarrow=False,
                    text='',
                    xanchor='left', yanchor='middle',
                    # Use a shape for the legend marker
                    bordercolor=color, borderwidth=1, borderpad=0,
                    bgcolor=color,
                    width=marker_size, 
                    height=marker_size 
                )

                # Add the category text
                fig.add_annotation(
                    xref='paper', yref='paper',
                    x=text_x, y=item_y,
                    text=truncated_cat,
                    showarrow=False,
                    font=dict(size=15, color='black'), 
                    xanchor='left', yanchor='middle',
                    align='left'
                )
            
            # --- Add rectangular box for the legend ---
            # Calculate the overall bounding box for the current legend
            legend_box_x0 = current_xaxis_domain_start + 0.002 
            legend_box_x1 = current_xaxis_domain_end - 0.002 
            legend_box_y0 = min_y_annotation - line_height / 2.0 
            legend_box_y1 = y_pos_start + line_height / 2.0 

            fig.add_shape(
                type="rect",
                xref="paper", yref="paper",
                x0=legend_box_x0, y0=legend_box_y0,
                x1=legend_box_x1, y1=legend_box_y1,
                fillcolor="rgba(240, 240, 240, 0.7)", 
                line=dict(color="gray", width=1),
                layer="below" 
            )

    # Set font size for subplot titles
    for annot in fig.layout.annotations:
        if annot.text in subplot_titles_display and annot.xref == 'paper' and annot.yref == 'paper':
            annot.font.size = 19 

    # Final layout configurations - Main title and Tooltip
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>", 
            x=0.5, 
            font=dict(
                size=25, 
                color='black' 
            )
        ),
        hoverlabel=dict( # Tooltip configuration
            font_size=17, # Tooltip font size changed to 17
            bgcolor="white", 
            bordercolor="gray" 
        ),
        height=fig_height, 
        showlegend=False, 
        margin=dict(l=50, r=50, t=80, b=initial_bottom_margin), 
        template="plotly_white"
    )
    
    fig.show()


# --- PART 3: New tableplot function for simplified use ---
def tableplot(df, sort_by="*", nbins=100, decreasing=True, max_levels=50, title="My 'tableplot' Package in Action!"):
    """
    Simplified function to generate an interactive tableplot.
    
    Arguments:
        df (pd.DataFrame): Input table.
        sort_by (str): Column name for sorting, or "*" for auto-detection,
                       or None to use the first numeric column (or 'ID_Cliente' if present).
        nbins (int): Number of bins (groups).
        decreasing (bool): If True, sorts from largest to smallest.
        max_levels (int): Maximum number of unique categories to show.
        title (str): Plot title.
    """
    df_copy = df.copy() # Create a copy to avoid modifying the original DataFrame
    sort_col = None

    # 🔍 Detect column with *Name+ or *Name-
    special_col = [col for col in df_copy.columns if isinstance(col, str) and col.startswith("*")]

    if special_col:
        raw_col = special_col[0]
        col_clean = raw_col.strip("*").strip("+").strip("-")
        sort_col = col_clean

        if raw_col.endswith("+"):
            decreasing = False
        elif raw_col.endswith("-"):
            decreasing = True
        else:
            decreasing = True  # default

        df_copy.rename(columns={raw_col: col_clean}, inplace=True)

    elif sort_by == "*":
        # If '*' is passed and no special column is found, use default logic
        # (first numeric, or 'ID_Cliente' if present and numeric)
        if 'ID_Cliente' in df_copy.columns and pd.api.types.is_numeric_dtype(df_copy['ID_Cliente']):
            sort_col = 'ID_Cliente'
        else:
            numeric_cols = df_copy.select_dtypes(include="number").columns.tolist()
            sort_col = numeric_cols[0] if numeric_cols else df_copy.columns[0] # Fallback to the first column
        
        print(f"Sort_by='*' detected '{sort_col}' as default sort column.")

    elif sort_by is not None and sort_by in df_copy.columns:
        sort_col = sort_by
    else:
        # If sort_by is not '*', not a valid column name, or is None, 
        # it will fall back to simulate_tabplot_binning's default logic for sort_col=None
        sort_col = None
        print(f"Sort column '{sort_by}' not found or is invalid. Using default detection.")


    # 🧠 Generate binned data and plot
    binned_data, _, _ = simulate_tabplot_binning(
        df_copy, nbins=nbins, sort_col=sort_col, decreasing=decreasing, max_levels=max_levels
    )

    plot_tabplot_interactive(binned_data, title=title)