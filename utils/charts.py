import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import plotly.graph_objects as go
from scipy.stats import gaussian_kde
from plotly.subplots import make_subplots
import warnings


def status(df):
    status_counts = df['Status'].value_counts(normalize=True) * 100

    fig = px.pie(values=status_counts, names=status_counts.index, 
                title='Backup Job Status Distribution', 
                color_discrete_sequence=['#66c2a5', '#d53e4f', '#fc8d62'])
    
    fig.update_traces(hovertemplate='%{label}: %{value:.2f}%') 

    return fig


def status_by_backup(df):
    status = df[['Backup Job', 'Status']]
    status = status.copy()

    status['Success'] = status['Status'].apply(lambda x: 1 if x == 'Success' else 0)
    status.loc[:, 'Warning'] = status['Status'].apply(lambda x: 1 if x == 'Warning' else 0)
    status.loc[:, 'Error'] = status['Status'].apply(lambda x: 1 if x == 'Error' else 0)

    summary = status.groupby('Backup Job')[['Success', 'Warning', 'Error']].sum().reset_index()
    summary_long = summary.melt(id_vars='Backup Job', value_vars=['Success', 'Warning', 'Error'], 
                                var_name='Status', value_name='Count')

    fig = px.bar(summary_long, x='Count', y='Backup Job', color='Status', orientation='h',
                color_discrete_map={'Success': '#66c2a5', 'Warning': '#fc8d62', 'Error': '#d53e4f'},
                title='Backup Results for Jobs: Count of Successes, Warnings and Errors')
    
    fig.update_traces(hovertemplate='%{y}<br>%{x}') 

    fig.update_xaxes(title_text='Count')
    fig.update_yaxes(title_text='Backup Job')

    fig.update_layout(
        height=600,
        legend_title_text='Status'
    )

    return fig


def error(df):
    backup_stats = df.groupby('Backup Job')[['Success', 'Error', 'Warning']].sum().reset_index()
    backup_stats['Total'] = backup_stats['Error'] + backup_stats['Success'] + backup_stats['Warning']
    backup_stats['Error Rate'] = backup_stats['Error'] / backup_stats['Total']

    backup_stats = backup_stats.sort_values(by='Error Rate', ascending=False)

    colors = sns.color_palette("viridis", len(backup_stats)).as_hex()

    fig = px.bar(backup_stats, x='Error Rate', y='Backup Job',
                color='Backup Job', 
                orientation='h',
                title='Error Rate by Backup Job', 
                color_discrete_sequence=colors)
    
    fig.update_traces(hovertemplate='%{x}') 

    fig.update_layout(
        yaxis={'tickvals': backup_stats['Backup Job']},
        height=600,
        showlegend=False
    )

    return fig


def error_daily(df):
    daily_stats = df.groupby('Date')[['Success', 'Error', 'Warning']].sum().reset_index()
    daily_stats['Total'] = daily_stats['Error'] + daily_stats['Success'] + daily_stats['Warning']
    daily_stats['Error Rate'] = daily_stats['Error'] / daily_stats['Total']

    fig = px.line(daily_stats, x='Date', y='Error Rate', 
                title='Daily Trend of Error Rate',
                markers=True)
    
    fig.update_traces(hovertemplate='%{x}<br>%{y}') 

    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Error Rate'
    )

    return fig


def error_hour(df):
    hourly_stats = df.groupby('Hour')[['Success', 'Error', 'Warning']].sum().reset_index()
    hourly_stats['Total'] = hourly_stats['Error'] + hourly_stats['Success'] + hourly_stats['Warning']
    hourly_stats['Error Rate'] = hourly_stats['Error'] / hourly_stats['Total']

    fig = px.line(hourly_stats, x='Hour', y='Error Rate', 
                title='Hourly Trend of Error Rate',
                markers=True)
    
    fig.update_traces(hovertemplate='%{x:02d}:00<br>%{y}') 

    fig.update_layout(
        xaxis_title='Hour',
        yaxis_title='Error Rate'
    )

    return fig


def plot_avg(df, x_col, title, x_label):
    performance = df.groupby('Backup Job')[x_col].mean().reset_index()

    fig = px.bar(performance, 
                 x=x_col, 
                 y='Backup Job', 
                 color='Backup Job',
                 orientation='h',
                 color_discrete_sequence=sns.color_palette("viridis", len(performance)).as_hex(),
                 title=title)
    
    fig.update_traces(hovertemplate='%{x}')
    
    fig.update_layout(
        xaxis_title=x_label,
        yaxis_title='Backup Job',
        showlegend=False,
        height=600
    )

    return fig


def avg_total(df):
    return plot_avg(df, 'Total Size (GB)', 'Average Total Size for Each Backup Job', 'Average Size (GB)')


def size(df):
    fig = px.line(df, x='Start Datetime', y='Total Size (GB)', color='Backup Job', 
                title='Total Size Over Time for Each Backup Job', markers=True)
    
    fig.update_traces(hovertemplate='%{x}<br>%{y} GB') 

    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='Total Size (GB)')

    return fig


def total_daily_trends(df):
    daily_trends = df.groupby('Date').agg({
        'Total Size (GB)': 'sum',
    }).reset_index()

    fig = px.line(daily_trends, x='Date', y='Total Size (GB)',
                title='Daily Trends of Total Size',
                labels={'value': 'Size (GB)', 'variable': 'Metric'},
                markers=True)
    
    fig.update_traces(hovertemplate='%{x}<br>%{y} GB') 

    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Size (GB)'
    )

    return fig


def total_hourly_trends(df):
    hourly_trends = df.groupby('Hour').agg({
        'Total Size (GB)': 'sum',
    }).reset_index()

    fig = px.line(hourly_trends, x='Hour', y='Total Size (GB)',
                title='Hourly Trend of Total Size',
                labels={'value': 'Size (GB)', 'variable': 'Metric'},
                markers=True)
    
    fig.update_traces(hovertemplate='%{x:02d}:00<br>%{y} GB') 

    fig.update_layout(
        xaxis_title='Hour',
        yaxis_title='Size (GB)'
    )
    
    return fig


def avg_backup(df):
    return plot_avg(df, 'Backup Size (GB)', 'Average Backup Size for Each Backup Job', 'Average Size (GB)')


def heatmap(df):
    df_aggregated = df.groupby(['Date', 'Backup Job'])['Backup Size (GB)'].sum().reset_index()

    pivot_table = df_aggregated.pivot(index='Date', columns='Backup Job', values='Backup Size (GB)')
    pivot_table.index = pd.to_datetime(pivot_table.index)

    longest_xtick_label = max([len(str(label)) for label in pivot_table.columns])

    full = pd.date_range(start=pivot_table.index.min(), end=pivot_table.index.max())
    missing_dates = full.difference(pivot_table.index)

    missing_data = pd.DataFrame(index=missing_dates, columns=pivot_table.columns)
    missing_data[:] = np.nan

    warnings.simplefilter("ignore", category=FutureWarning)
    pivot_table = pd.concat([pivot_table, missing_data])

    pivot_table = pivot_table.sort_index()

    text_data = pivot_table.map(lambda x: '' if pd.isnull(x) else f'{x:.0f}')

    fig = go.Figure(data=go.Heatmap(
        z=pivot_table.values,
        x=pivot_table.columns,
        y=pivot_table.index,
        colorscale='RdBu_r',
        hoverongaps=False,
        showscale=True,
        text=text_data.values,
        texttemplate="%{text}",
        textfont={"size": 11, "color": "white"},
        hovertemplate="%{x}<br>%{y}<br>%{z} GB<extra></extra>"
    ))

    fig.update_layout(
        title='Heatmap of Backup Sizes Over Time',
        xaxis_title='Backup Job',
        yaxis_title='Date',
        xaxis=dict(tickangle=-90, showgrid=False),
        yaxis=dict(autorange="reversed", showgrid=False),
        xaxis_nticks=len(pivot_table.columns),
        yaxis_nticks=len(pivot_table.index),
        height=50 * len(pivot_table.index) + longest_xtick_label * 5
    )

    return fig


def backup_daily_trends(df):
    daily_trends = df.groupby('Date').agg({
        'Backup Size (GB)': 'sum',
    }).reset_index()

    fig = px.line(daily_trends, x='Date', y='Backup Size (GB)',
                title='Daily Trends of Backup Size',
                labels={'value': 'Size (GB)', 'variable': 'Metric'},
                markers=True)

    fig.update_traces(hovertemplate='%{x}<br>%{y} GB') 

    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Size (GB)'
    )
    
    return fig


def backup_hourly_trends(df):
    hourly_trends = df.groupby('Hour').agg({
        'Backup Size (GB)': 'sum',
    }).reset_index()

    fig = px.line(hourly_trends, x='Hour', y='Backup Size (GB)',
                title='Hourly Trend of Backup Size',
                labels={'value': 'Size (GB)', 'variable': 'Metric'},
                markers=True)
    
    fig.update_traces(hovertemplate='%{x:02d}:00<br>%{y} GB') 

    fig.update_layout(
        xaxis_title='Hour',
        yaxis_title='Size (GB)'
    )
    
    return fig


def avg_duration(df):
    df_copy = df.copy()
    df_copy['Duration'] = df_copy['Duration'].dt.total_seconds() / 60
    return plot_avg(df_copy, 'Duration', 'Average Backup Duration for Each Backup Job', 'Average Duration (minutes)')


def duration_daily_trends(df):
    daily_trends = df.groupby('Date').agg({
        'Duration': 'mean',
    }).reset_index()

    daily_trends['Duration (minutes)'] = daily_trends['Duration'].dt.total_seconds() / 60

    fig = px.line(daily_trends, x='Date', y='Duration (minutes)',
                title='Daily Trends of Backup Duration',
                labels={'value': 'Duration (minutes)', 'variable': 'Metric'},
                markers=True)
    
    fig.update_traces(hovertemplate='%{x}<br>%{y} minutes') 

    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Duration (minutes)'
    )
    
    return fig


def duration_hourly_trends(df):
    hourly_trends = df.groupby('Hour').agg({
        'Duration': 'mean',
    }).reset_index()

    hourly_trends['Duration (minutes)'] = hourly_trends['Duration'].dt.total_seconds() / 60

    fig = px.line(hourly_trends, x='Hour', y='Duration (minutes)',
                title='Hourly Trend of Backup Duration',
                labels={'value': 'Duration (minutes)', 'variable': 'Metric'},
                markers=True)
    
    fig.update_traces(hovertemplate='%{x:02d}:00<br>%{y} minutes') 

    fig.update_layout(
        xaxis_title='Hour',
        yaxis_title='Duration (minutes)'
    )
    
    return fig


def duration_hist(df):
    df['Duration (minutes)'] = df['Duration'].dt.total_seconds() / 60

    viridis_color = px.colors.sequential.Viridis[0]
    r, g, b = px.colors.hex_to_rgb(viridis_color)
    rgba_color_transparent = f'rgba({r},{g},{b},0.5)'
    rgba_color_solid = f'rgba({r},{g},{b},1)'

    fig = px.histogram(df, 
                       x='Duration (minutes)', 
                       nbins=30,
                       color_discrete_sequence=[rgba_color_transparent],
                       title='Distribution of Backup Durations for Backup Jobs')

    for bar in fig.data:
        bar.marker.line.width = 1.5
        bar.marker.line.color = rgba_color_solid

    kde = gaussian_kde(df['Duration (minutes)'])
    x_values = np.linspace(df['Duration (minutes)'].min(), df['Duration (minutes)'].max(), 500)
    kde_values = kde(x_values)

    fig.add_trace(go.Scatter(
        x=x_values,
        y=kde_values * len(df) * (df['Duration (minutes)'].max() - df['Duration (minutes)'].min()) / 30,
        mode='lines',
        line=dict(color=rgba_color_solid),
        name='Density',
        hovertemplate='Duration (minutes)=%{x}<br>density=%{y}<extra></extra>'
    ))

    fig.update_layout(
        xaxis_title='Duration (minutes)',
        yaxis_title='Frequency',
        showlegend=False,
        height=450
    )

    return fig


def duration_box(df):
    df['Duration (minutes)'] = df['Duration'].dt.total_seconds() / 60

    avg_duration = df.groupby('Backup Job')['Duration'].mean().reset_index()
    avg_duration['Duration'] = avg_duration['Duration'].dt.total_seconds() / 60

    fig = px.box(df, x='Duration (minutes)', y='Backup Job',
                title='Distribution of Backup Durations for Each Backup Job',
                color='Backup Job',
                orientation='h',
                color_discrete_sequence=px.colors.sequential.Viridis
                )

    fig.update_layout(
        xaxis_title='Duration (minutes)',
        yaxis_title='Backup Job',
        showlegend=False,
        height=700
    )

    return fig


def avg_speed(df):
    df['Backup Speed (GB/min)'] = df['Data Read (GB)'] / (df['Duration'].dt.total_seconds() / 60)
    avg_speed = df.groupby('Backup Job')['Backup Speed (GB/min)'].mean().reset_index()

    fig = px.bar(avg_speed, 
                 x='Backup Speed (GB/min)', 
                 y='Backup Job', 
                 color='Backup Job',
                 orientation='h',
                 color_discrete_sequence=sns.color_palette("viridis", len(avg_speed)).as_hex(),
                 title='Average Backup Speed for Each Backup Job')
    
    fig.update_traces(hovertemplate='%{x}') 

    fig.update_layout(
        xaxis_title='Speed (GB/min)',
        yaxis_title='Backup Job',
        showlegend=False,
        height=600
    )

    return fig


def backup_speed(df):
    fig = px.line(df, x='Start Datetime', y='Backup Speed (GB/min)', color='Backup Job', 
                title='Backup Speed Over Time',
                labels={'Start datetime': 'Date', 'Backup Speed (GB/min)': 'Backup Speed (GB/min)'},
                markers=True)
    
    fig.update_traces(hovertemplate='%{x}<br>%{y} GB/min')

    return fig


def speed_hist(df):
    viridis_color = px.colors.sequential.Viridis[0]
    r, g, b = px.colors.hex_to_rgb(viridis_color)
    rgba_color_transparent = f'rgba({r},{g},{b},0.5)'
    rgba_color_solid = f'rgba({r},{g},{b},1)'

    fig = px.histogram(df, 
                       x='Backup Speed (GB/min)', 
                       nbins=30,
                       color_discrete_sequence=[rgba_color_transparent],
                       title='Distribution of Backup Speed for Backup Jobs')
    
    for bar in fig.data:
        bar.marker.line.width = 1.5
        bar.marker.line.color = rgba_color_solid
    
    kde = gaussian_kde(df['Backup Speed (GB/min)'])
    x_values = np.linspace(df['Backup Speed (GB/min)'].min(), df['Backup Speed (GB/min)'].max(), 500)
    kde_values = kde(x_values)

    fig.add_trace(go.Scatter(
        x=x_values,
        y=kde_values * len(df) * (df['Backup Speed (GB/min)'].max() - df['Backup Speed (GB/min)'].min()) / 30,
        mode='lines',
        line=dict(color=rgba_color_solid),
        name='Density',
        hovertemplate='Duration (minutes)=%{x}<br>density=%{y}<extra></extra>'
    ))

    fig.update_layout(
        xaxis_title='Duration (minutes)',
        yaxis_title='Frequency',
        showlegend=False,
        height=450
    )

    return fig


def speed_box(df):
    fig = px.box(df, x='Backup Speed (GB/min)', y='Backup Job',
                title='Distribution of Backup Speed for Each Backup Job',
                color='Backup Job',
                orientation='h',
                color_discrete_sequence=px.colors.sequential.Viridis
                )

    fig.update_layout(
        xaxis_title='Backup Speed (GB/min)',
        yaxis_title='Backup Job',
        showlegend=False,
        height=700
    )

    return fig


def speed_heatmap(df):
    df['Day of Week'] = pd.to_datetime(df['Date']).dt.day_name()

    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df['Day of Week'] = pd.Categorical(df['Day of Week'], categories=day_order, ordered=True)

    heatmap_data = df.pivot_table(values='Backup Speed (GB/min)', index='Day of Week', columns='Hour', aggfunc='mean', observed=False)

    required_columns = set(range(24))
    existing_columns = set(heatmap_data.columns)
    missing_columns = required_columns - existing_columns

    for col in missing_columns:
        heatmap_data[col] = np.nan
    heatmap_data = heatmap_data.fillna(np.nan)

    for day in day_order:
        if day not in heatmap_data.index:
            heatmap_data.loc[day] = [np.nan] * len(heatmap_data.columns)

    heatmap_data = heatmap_data[sorted(heatmap_data.columns)]

    text_data = heatmap_data.map(lambda x: '' if pd.isnull(x) else f'{x:.1f}')
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        zmin=heatmap_data.values.min(),
        zmax=heatmap_data.values.max(),
        colorscale='RdBu_r',
        hoverongaps=False,
        showscale=True,
        text=text_data.values,
        texttemplate="%{text}",
        textfont={"size": 11, "color": "white"},
        hovertemplate="%{y}, %{x}:00<br>%{z} GB/min<extra></extra>"
    ))

    fig.update_layout(
        title='Heatmap of Backup Speed by Day of the Week and Hour',
        xaxis_title='Hour',
        yaxis_title='Day of Week',
        xaxis=dict(showgrid=False),
        yaxis=dict(autorange="reversed", showgrid=False),
        xaxis_nticks=len(heatmap_data.columns),
        yaxis_nticks=len(heatmap_data.index),
        height=60 * len(heatmap_data.index)
    )

    return fig


def perfomance(df):
    figs = []
    backup_jobs = df['Backup Job'].unique()
    palette = sns.color_palette("bright", 5).as_hex()

    for job in backup_jobs:
        job_df = df[df['Backup Job'] == job]
        job_df = job_df.sort_values(by='Start Datetime')

        fig = make_subplots(rows=1, cols=2, 
                            subplot_titles=(f'Backup Size, Data Read, Transferred', 
                                            f'Dedupe and Compression'),
                            shared_xaxes=True)
        
        fig.add_trace(go.Scatter(x=job_df['Start Datetime'], 
                                 y=job_df['Backup Size (GB)'],
                                 mode='lines+markers',
                                 name='Backup Size (GB)',
                                 marker=dict(color=palette[0])),
                      row=1, col=1)
        fig.add_trace(go.Scatter(x=job_df['Start Datetime'], 
                                 y=job_df['Data Read (GB)'],
                                 mode='lines+markers',
                                 name='Data Read (GB)',
                                 marker=dict(color=palette[1])),
                      row=1, col=1)
        fig.add_trace(go.Scatter(x=job_df['Start Datetime'], 
                                 y=job_df['Transferred (GB)'],
                                 mode='lines+markers',
                                 name='Transferred (GB)',
                                 marker=dict(color=palette[2])),
                      row=1, col=1)

        fig.add_trace(go.Scatter(x=job_df['Start Datetime'], 
                                 y=job_df['Dedupe'],
                                 mode='lines+markers',
                                 name='Dedupe',
                                 marker=dict(color=palette[3])),
                      row=1, col=2)
        fig.add_trace(go.Scatter(x=job_df['Start Datetime'], 
                                 y=job_df['Compression'],
                                 mode='lines+markers',
                                 name='Compression',
                                 marker=dict(color=palette[4])),
                      row=1, col=2)
        
        fig.update_layout(
            title_text=job,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="left", x=0),
        )

        fig.update_xaxes(tickformat='%d-%m %H:%M', tickangle=30)

        figs.append(fig)

    return figs


def dedupe_efficiency(df):
    df_jobs = df.groupby('Backup Job')[['Backup Size (GB)', 'Dedupe']].mean().reset_index()
    fig = px.scatter(df_jobs, x='Backup Size (GB)', y='Dedupe', color='Backup Job', 
                    title='Efficiency of Deduplication vs Backup Size',
                    labels={'Backup Size (GB)': 'Backup Size (GB)', 'Dedupe': 'Dedupe Ratio'})
    
    fig.update_traces(hovertemplate='Backup Size (GB): %{x}<br>Dedupe: %{y}x')

    return fig


def compression_efficiency(df):
    df_jobs = df.groupby('Backup Job')[['Backup Size (GB)', 'Compression']].mean().reset_index()
    fig = px.scatter(df_jobs, x='Backup Size (GB)', y='Compression', color='Backup Job', 
                    title='Efficiency of Compression vs Backup Size',
                    labels={'Backup Size (GB)': 'Backup Size (GB)', 'Compression': 'Compression Ratio'})

    fig.update_traces(hovertemplate='Backup Size (GB): %{x}<br>Compression: %{y}x')

    return fig


def gantt(df):
    df = df.sort_values(by='Start Datetime').reset_index(drop=True)

    fig = px.timeline(df, x_start="Start Datetime", x_end="End Datetime", y="Backup Job")
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        height=600,
        xaxis=dict(
            rangeslider=dict(visible=True),
            type="date",
            range=[df['Start Datetime'].min(), df['End Datetime'].max()]
        )
    )

    return fig


def status_by_obj(df):
    summary = df.groupby('Object')[['Success', 'Warning', 'Error']].sum().reset_index()
    summary_long = summary.melt(id_vars='Object', value_vars=['Success', 'Warning', 'Error'], 
                                var_name='Status', value_name='Count')

    fig = px.bar(summary_long, x='Count', y='Object', color='Status', orientation='h',
                color_discrete_map={'Success': '#66c2a5', 'Warning': '#fc8d62', 'Error': '#d53e4f'},
                title='Backup Results for Objects: Count of Successes, Warnings and Errors')

    fig.update_traces(hovertemplate='%{y}<br>%{x}') 

    fig.update_xaxes(title_text='Count')
    fig.update_yaxes(title_text='Object')

    fig.update_layout(
        height=600,
        legend_title_text='Status'
    )

    return fig


def error_obj(df):
    backup_stats = df.groupby('Object')[['Success', 'Error', 'Warning']].sum().reset_index()
    backup_stats['Total'] = backup_stats['Error'] + backup_stats['Success'] + backup_stats['Warning']
    backup_stats['Error Rate'] = backup_stats['Error'] / backup_stats['Total']

    backup_stats = backup_stats.sort_values(by='Error Rate', ascending=False)

    colors = sns.color_palette("viridis", len(backup_stats)).as_hex()

    fig = px.bar(backup_stats, x='Error Rate', y='Object', 
                color='Object', 
                orientation='h',
                title='Error Rate by Object', 
                color_discrete_sequence=colors)
    
    fig.update_traces(hovertemplate='%{x}') 

    fig.update_layout(
        yaxis={'tickvals': backup_stats['Object']},
        height=600,
        showlegend=False
    )

    return fig


def plot_avg_obj(df, x_col, title, x_label):
    performance = df.groupby('Object')[x_col].mean().reset_index()

    fig = px.bar(performance, 
                 x=x_col, 
                 y='Object', 
                 color='Object',
                 orientation='h',
                 color_discrete_sequence=sns.color_palette("viridis", len(performance)).as_hex(),
                 title=title)
    
    fig.update_traces(hovertemplate='%{x}') 
    
    fig.update_layout(
        xaxis_title=x_label,
        yaxis_title='Object',
        showlegend=False,
        height=600
    )

    return fig


def avg_total_obj(df):
    return plot_avg_obj(df, 'Size (GB)', 'Average Total Size for Each Object', 'Average Size (GB)')


def size_obj(df):
    fig = px.line(df, x='Start Datetime', y='Size (GB)', color='Object', 
                title='Total Size Over Time for Each Object', markers=True)
    
    fig.update_traces(hovertemplate='%{x}<br>%{y} GB') 

    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='Size (GB)')

    return fig


def avg_duration_obj(df):
    df_copy = df.copy()
    df_copy['Duration'] = df_copy['Duration'].dt.total_seconds() / 60
    return plot_avg_obj(df_copy, 'Duration', 'Average Backup Duration for Each Backup Job', 'Average Duration (minutes)')


def duration_hist_obj(df):
    df['Duration (minutes)'] = df['Duration'].dt.total_seconds() / 60

    viridis_color = px.colors.sequential.Viridis[0]
    r, g, b = px.colors.hex_to_rgb(viridis_color)
    rgba_color_transparent = f'rgba({r},{g},{b},0.5)'
    rgba_color_solid = f'rgba({r},{g},{b},1)'

    fig = px.histogram(df, 
                       x='Duration (minutes)', 
                       nbins=30,
                       color_discrete_sequence=[rgba_color_transparent],
                       title='Distribution of Backup Durations for Objects')
    
    for bar in fig.data:
        bar.marker.line.width = 1.5
        bar.marker.line.color = rgba_color_solid
    
    kde = gaussian_kde(df['Duration (minutes)'])
    x_values = np.linspace(df['Duration (minutes)'].min(), df['Duration (minutes)'].max(), 500)
    kde_values = kde(x_values)

    fig.add_trace(go.Scatter(
        x=x_values,
        y=kde_values * len(df) * (df['Duration (minutes)'].max() - df['Duration (minutes)'].min()) / 30,
        mode='lines',
        line=dict(color=rgba_color_solid),
        name='Density',
        hovertemplate='Duration (minutes)=%{x}<br>density=%{y}<extra></extra>'
    ))

    fig.update_layout(
        xaxis_title='Duration (minutes)',
        yaxis_title='Frequency',
        showlegend=False,
        height=450
    )

    return fig


def duration_box_obj(df):
    df['Duration (minutes)'] = df['Duration'].dt.total_seconds() / 60

    avg_duration = df.groupby('Object')['Duration'].mean().reset_index()
    avg_duration['Duration'] = avg_duration['Duration'].dt.total_seconds() / 60

    fig = px.box(df, x='Duration (minutes)', y='Object', orientation='h',
                title='Distribution of Backup Durations for Each Object',
                color='Object',
                color_discrete_sequence=px.colors.sequential.Viridis
                )

    fig.update_layout(
        xaxis_title='Duration (minutes)',
        yaxis_title='Object',
        showlegend=False,
        height=700
    )

    return fig


def avg_speed_obj(df):
    df['Backup Speed (GB/min)'] = np.where(df['Duration'].dt.total_seconds() == 0, 0, df['Read (GB)'] / (df['Duration'].dt.total_seconds() / 60))
    avg_speed = df.groupby('Object')['Backup Speed (GB/min)'].mean().reset_index()

    fig = px.bar(avg_speed, 
                 x='Backup Speed (GB/min)', 
                 y='Object', 
                 color='Object',
                 orientation='h',
                 color_discrete_sequence=sns.color_palette("viridis", len(avg_speed)).as_hex(),
                 title='Average Backup Speed for Each Object')
    
    fig.update_traces(hovertemplate='%{x}') 
    
    fig.update_layout(
        xaxis_title='Speed (GB/min)',
        yaxis_title='Object',
        showlegend=False,
        height=600
    )

    return fig


def backup_speed_obj(df):
    fig = px.line(df, x='Start Datetime', y='Backup Speed (GB/min)', color='Object', 
                title='Backup Speed Over Time',
                labels={'Start datetime': 'Date', 'Backup Speed (GB/min)': 'Backup Speed (GB/min)'},
                markers=True)
    
    fig.update_traces(hovertemplate='%{x}<br>%{y} GB/min')

    return fig


def speed_hist_obj(df):
    viridis_color = px.colors.sequential.Viridis[0]
    r, g, b = px.colors.hex_to_rgb(viridis_color)
    rgba_color_transparent = f'rgba({r},{g},{b},0.5)'
    rgba_color_solid = f'rgba({r},{g},{b},1)'

    fig = px.histogram(df, 
                       x='Backup Speed (GB/min)', 
                       nbins=30,
                       color_discrete_sequence=[rgba_color_transparent],
                       title='Distribution of Backup Speed for Objects')
    
    for bar in fig.data:
        bar.marker.line.width = 1.5
        bar.marker.line.color = rgba_color_solid
    
    kde = gaussian_kde(df['Backup Speed (GB/min)'])
    x_values = np.linspace(df['Backup Speed (GB/min)'].min(), df['Backup Speed (GB/min)'].max(), 500)
    kde_values = kde(x_values)

    fig.add_trace(go.Scatter(
        x=x_values,
        y=kde_values * len(df) * (df['Backup Speed (GB/min)'].max() - df['Backup Speed (GB/min)'].min()) / 30,
        mode='lines',
        line=dict(color=rgba_color_solid),
        name='Density',
        hovertemplate='Duration (minutes)=%{x}<br>density=%{y}<extra></extra>'
    ))

    fig.update_layout(
        xaxis_title='Duration (minutes)',
        yaxis_title='Frequency',
        showlegend=False,
        height=450
    )

    return fig


def speed_box_obj(df):
    fig = px.box(df, x='Backup Speed (GB/min)', y='Object', orientation='h',
                title='Distribution of Backup Speed for Each Object',
                color='Object',
                color_discrete_sequence=px.colors.sequential.Viridis
                )

    fig.update_layout(
        xaxis_title='Backup Speed (GB/min)',
        yaxis_title='Object',
        showlegend=False,
        height=700
    )

    return fig


def perfomance_obj(df):
    figs = []
    backup_objs = df['Object'].unique()
    palette = sns.color_palette("bright", 5).as_hex()

    for obj in backup_objs:
        obj_df = df[df['Object'] == obj]
        obj_df = obj_df.sort_values(by='Start Datetime')

 
        fig = px.line(obj_df, x='Start Datetime', 
                    y=['Read (GB)', 'Transferred (GB)'],
                    title=f'{obj} - Read, Transferred',
                    labels={'value': 'Size (GB)', 'variable': 'Metric'},
                    markers=True,
                    color_discrete_sequence=palette[:2])
        
        fig.update_traces(hovertemplate='%{x}<br>%{y} GB')

        fig.update_layout(
            xaxis=dict(tickformat='%d-%m %H:%M', tickangle=30),
            legend=dict(orientation="h", yanchor="top", y=-0.4, xanchor="left", x=0)
        )

        figs.append(fig)

    return figs


# def heatmap_obj(df):
#     df_aggregated = df.groupby(['Date', 'Object'])['Read (GB)'].sum().reset_index()

#     pivot_table = df_aggregated.pivot(index='Date', columns='Object', values='Read (GB)')

#     height = 60 * len(pivot_table.index)

#     text_data = pivot_table.applymap(lambda x: '' if pd.isnull(x) else f'{x:.0f}')

#     fig = go.Figure(data=go.Heatmap(
#         z=pivot_table.values,
#         x=pivot_table.columns,
#         y=pivot_table.index,
#         colorscale='RdBu_r',
#         hoverongaps=False,
#         showscale=True,
#         text=text_data.values,
#         texttemplate="%{text}",
#         textfont={"size": 11, "color": "white"},
#         hovertemplate="%{x}<br>%{y}<br>%{z}"
#     ))

#     fig.update_layout(
#         title='Heatmap of Backup Sizes Over Time',
#         xaxis_title='Object',
#         yaxis_title='Date',
#         xaxis=dict(tickangle=-90, showgrid=False),
#         yaxis=dict(autorange="reversed", showgrid=False),
#         xaxis_nticks=len(pivot_table.columns),
#         yaxis_nticks=len(pivot_table.index),
#         height=height
#     )

#     st.plotly_chart(fig, use_container_width=True)


def efficiency_obj(df):
    df_objects = df.groupby('Object')[['Transferred (GB)', 'Read (GB)']].sum().reset_index()
    df_objects['Efficiency'] = df_objects['Read (GB)'] / df_objects['Transferred (GB)']

    fig = px.scatter(df_objects, x='Transferred (GB)', y='Efficiency', color='Object', 
                    title='Efficiency of Data Reduction vs Data Transferred',
                    labels={'Transferred (GB)': 'Transferred (GB)', 'Efficiency': 'Data Reduction Efficiency Ratio'})

    fig.update_traces(hovertemplate='Transferred (GB): %{x}<br>Reduction: %{y}x')

    return fig


def generate_all_charts(backup, obj):
    charts = {
                'status': status(backup),
                'status_by_backup': status_by_backup(backup),
                'error': error(backup),
                'error_daily': error_daily(backup),
                'error_hour': error_hour(backup),
                'avg_total': avg_total(backup),
                'size': size(backup),
                'total_daily_trends': total_daily_trends(backup),
                'total_hourly_trends': total_hourly_trends(backup),
                'avg_backup': avg_backup(backup),
                'heatmap': heatmap(backup),
                'backup_daily_trends': backup_daily_trends(backup),
                'backup_hourly_trends': backup_hourly_trends(backup),
                'avg_duration': avg_duration(backup),
                'duration_daily_trends': duration_daily_trends(backup),
                'duration_hourly_trends': duration_hourly_trends(backup),
                'duration_hist': duration_hist(backup),
                'duration_box': duration_box(backup),
                'avg_speed': avg_speed(backup),
                'backup_speed': backup_speed(backup),
                'speed_hist': speed_hist(backup),
                'speed_box': speed_box(backup),
                'speed_heatmap': speed_heatmap(backup),
                'performance': perfomance(backup),
                'dedupe_efficiency': dedupe_efficiency(backup),
                'compression_efficiency': compression_efficiency(backup),
                'gantt': gantt(backup),
                'status_obj': status(obj),
                'status_by_obj': status_by_obj(obj),
                'error_obj': error_obj(obj),
                'avg_total_obj': avg_total_obj(obj),
                'size_obj': size_obj(obj),
                'avg_duration_obj': avg_duration_obj(obj),
                'duration_hist_obj': duration_hist_obj(obj),
                'duration_box_obj': duration_box_obj(obj),
                'avg_speed_obj': avg_speed_obj(obj),
                'backup_speed_obj': backup_speed_obj(obj),
                'speed_hist_obj': speed_hist_obj(obj),
                'speed_box_obj': speed_box_obj(obj),
                'perfomance_obj': perfomance_obj(obj),
                'efficiency_obj': efficiency_obj(obj)
    }

    return charts