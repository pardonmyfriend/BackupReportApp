import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import plotly.graph_objects as go
from scipy.stats import gaussian_kde
from plotly.subplots import make_subplots


def highlight_error(row):
    if row['Status'] == 'Error':
        return ['background-color: rgba(255, 99, 71, 0.3)'] * len(row)
    if row['Status'] == 'Warning':
        return ['background-color: rgba(255, 165, 0, 0.3)'] * len(row)
    else:
        return [''] * len(row)


def status(df):
    status_counts = df['Status'].value_counts(normalize=True) * 100

    fig = px.pie(values=status_counts, names=status_counts.index, 
                title='Backup Job Status Distribution', 
                color_discrete_sequence=['#66c2a5', '#d53e4f', '#fc8d62'])
    
    fig.update_traces(hovertemplate='%{label}: %{value:.2f}%') 

    st.plotly_chart(fig)


def status_by_backup(df):
    status = df[['Backup Job', 'Status']]

    status['Success'] = status['Status'].apply(lambda x: 1 if x == 'Success' else 0)
    status['Warning'] = status['Status'].apply(lambda x: 1 if x == 'Warning' else 0)
    status['Error'] = status['Status'].apply(lambda x: 1 if x == 'Error' else 0)

    summary = status.groupby('Backup Job')[['Success', 'Warning', 'Error']].sum().reset_index()
    summary_long = summary.melt(id_vars='Backup Job', value_vars=['Success', 'Warning', 'Error'], 
                                var_name='Status', value_name='Count')

    fig = px.bar(summary_long, x='Backup Job', y='Count', color='Status', 
                color_discrete_map={'Success': '#66c2a5', 'Warning': '#fc8d62', 'Error': '#d53e4f'},
                title='Backup Results for Jobs: Count of Successes, Warnings and Errors')
    
    fig.update_traces(hovertemplate='%{x}<br>%{y}') 

    fig.update_xaxes(title_text='Backup Job', tickangle=-90)
    fig.update_yaxes(title_text='Count')

    fig.update_layout(
        height=600,
        legend_title_text='Status'
    )

    st.plotly_chart(fig)


def error(df):
    backup_stats = df.groupby('Backup Job')[['Success', 'Error', 'Warning']].sum().reset_index()
    backup_stats['Total'] = backup_stats['Error'] + backup_stats['Success'] + backup_stats['Warning']
    backup_stats['Error Rate'] = backup_stats['Error'] / backup_stats['Total']

    backup_stats = backup_stats.sort_values(by='Error Rate', ascending=False)

    colors = sns.color_palette("viridis", len(backup_stats)).as_hex()

    fig = px.bar(backup_stats, x='Backup Job', y='Error Rate', 
                color='Backup Job', 
                title='Error Rate by Backup Job', 
                color_discrete_sequence=colors)
    
    fig.update_traces(hovertemplate='%{y}') 

    fig.update_layout(
        xaxis={'tickangle': -90, 'automargin': True, 'tickmode': 'array', 'tickvals': backup_stats['Backup Job']},
        height=600,
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)


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

    st.plotly_chart(fig, use_container_width=True)


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

    st.plotly_chart(fig, use_container_width=True)


def plot_avg(df, x_col, title, x_label):
    vm_performance = df.groupby('Backup Job').agg({
        'Total Size (GB)': 'mean',
        'Backup Size (GB)': 'mean',
        'Data Read (GB)': 'mean',
        'Transferred (GB)': 'mean',
        'Duration': 'mean'
    }).reset_index()

    vm_performance['Duration'] = vm_performance['Duration'].dt.total_seconds() / 60

    fig = px.bar(vm_performance, 
                 x=x_col, 
                 y='Backup Job', 
                 color='Backup Job',
                 orientation='h',
                 color_discrete_sequence=sns.color_palette("viridis", len(vm_performance)).as_hex(),
                 title=title)
    
    fig.update_traces(hovertemplate='%{x}') 
    
    fig.update_layout(
        xaxis_title=x_label,
        yaxis_title='Backup Job',
        showlegend=False,
        height=600,
    )

    st.plotly_chart(fig, use_container_width=True)


def avg_total(df):
    plot_avg(df, 'Total Size (GB)', 'Average Total Size for Each Backup Job', 'Average Size (GB)')


def size(df):
    fig = px.line(df, x='Start Datetime', y='Total Size (GB)', color='Backup Job', 
                title='Total Size Over Time for Each Backup Job', markers=True)
    
    fig.update_traces(hovertemplate='%{x}<br>%{y} GB') 

    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='Total Size (GB)')

    st.plotly_chart(fig, use_container_width=True)


def total_trends(df):
    col1, col2 = st.columns(2)

    daily_trends = df.groupby('Date').agg({
        'Total Size (GB)': 'sum',
    }).reset_index()

    fig1 = px.line(daily_trends, x='Date', y='Total Size (GB)',
                title='Daily Trends of Total Size',
                labels={'value': 'Size (GB)', 'variable': 'Metric'},
                markers=True)
    
    fig1.update_traces(hovertemplate='%{x}<br>%{y} GB') 

    fig1.update_layout(
        xaxis_title='Date',
        yaxis_title='Size (GB)'
    )
    
    with col1:
        st.plotly_chart(fig1, use_container_width=True)

    hourly_trends = df.groupby('Hour').agg({
        'Total Size (GB)': 'sum',
    }).reset_index()

    fig2 = px.line(hourly_trends, x='Hour', y='Total Size (GB)',
                title='Hourly Trend of Total Size',
                labels={'value': 'Size (GB)', 'variable': 'Metric'},
                markers=True)
    
    fig2.update_traces(hovertemplate='%{x:02d}:00<br>%{y} GB') 

    fig2.update_layout(
        xaxis_title='Hour',
        yaxis_title='Size (GB)'
    )
    
    with col2:
        st.plotly_chart(fig2, use_container_width=True)


def avg_backup(df):
    plot_avg(df, 'Backup Size (GB)', 'Average Backup Size for Each Backup Job', 'Average Size (GB)')


def heatmap(df):
    df_aggregated = df.groupby(['Date', 'Backup Job'])['Backup Size (GB)'].sum().reset_index()

    pivot_table = df_aggregated.pivot(index='Date', columns='Backup Job', values='Backup Size (GB)')
    pivot_table.index = pd.to_datetime(pivot_table.index)

    longest_xtick_label = max([len(str(label)) for label in pivot_table.columns])

    full = pd.date_range(start=pivot_table.index.min(), end=pivot_table.index.max())
    missing_dates = full.difference(pivot_table.index)

    missing_data = pd.DataFrame(index=missing_dates, columns=pivot_table.columns)
    missing_data[:] = np.nan

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

    st.plotly_chart(fig, use_container_width=True)


def backup_trends(df):
    col1, col2 = st.columns(2)

    daily_trends = df.groupby('Date').agg({
        'Backup Size (GB)': 'sum',
    }).reset_index()

    fig1 = px.line(daily_trends, x='Date', y='Backup Size (GB)',
                title='Daily Trends of Backup Size',
                labels={'value': 'Size (GB)', 'variable': 'Metric'},
                markers=True)

    fig1.update_traces(hovertemplate='%{x}<br>%{y} GB') 

    fig1.update_layout(
        xaxis_title='Date',
        yaxis_title='Size (GB)'
    )
    
    with col1:
        st.plotly_chart(fig1, use_container_width=True)

    hourly_trends = df.groupby('Hour').agg({
        'Backup Size (GB)': 'sum',
    }).reset_index()

    fig2 = px.line(hourly_trends, x='Hour', y='Backup Size (GB)',
                title='Hourly Trend of Backup Size',
                labels={'value': 'Size (GB)', 'variable': 'Metric'},
                markers=True)
    
    fig2.update_traces(hovertemplate='%{x:02d}:00<br>%{y} GB') 

    fig2.update_layout(
        xaxis_title='Hour',
        yaxis_title='Size (GB)'
    )
    
    with col2:
        st.plotly_chart(fig2, use_container_width=True)


def avg_duration(df):
    plot_avg(df, 'Duration', 'Average Backup Duration for Each Backup Job', 'Average Duration (minutes)')


def duration_trends(df):
    col1, col2 = st.columns(2)

    daily_trends = df.groupby('Date').agg({
        'Duration': 'mean',
    }).reset_index()

    daily_trends['Duration (minutes)'] = daily_trends['Duration'].dt.total_seconds() / 60

    fig1 = px.line(daily_trends, x='Date', y='Duration (minutes)',
                title='Daily Trends of Backup Duration',
                labels={'value': 'Duration (minutes)', 'variable': 'Metric'},
                markers=True)
    
    fig1.update_traces(hovertemplate='%{x}<br>%{y} minutes') 

    fig1.update_layout(
        xaxis_title='Date',
        yaxis_title='Duration (minutes)'
    )
    
    with col1:
        st.plotly_chart(fig1, use_container_width=True)

    hourly_trends = df.groupby('Hour').agg({
        'Duration': 'mean',
    }).reset_index()

    hourly_trends['Duration (minutes)'] = hourly_trends['Duration'].dt.total_seconds() / 60

    fig2 = px.line(hourly_trends, x='Hour', y='Duration (minutes)',
                title='Hourly Trend of Backup Duration',
                labels={'value': 'Duration (minutes)', 'variable': 'Metric'},
                markers=True)
    
    fig2.update_traces(hovertemplate='%{x:02d}:00<br>%{y} minutes') 

    fig2.update_layout(
        xaxis_title='Hour',
        yaxis_title='Duration (minutes)'
    )
    
    with col2:
        st.plotly_chart(fig2, use_container_width=True)


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

    st.plotly_chart(fig, use_container_width=True)


def duration_box(df):
    df['Duration (minutes)'] = df['Duration'].dt.total_seconds() / 60

    avg_duration = df.groupby('Backup Job')['Duration'].mean().reset_index()
    # avg_duration = avg_duration.sort_values(by='Duration', ascending=False)
    avg_duration['Duration'] = avg_duration['Duration'].dt.total_seconds() / 60

    # job_order = avg_duration['Backup Job'].tolist()

    fig = px.box(df, x='Backup Job', y='Duration (minutes)',
                title='Distribution of Backup Durations for Each Backup Job',
                color='Backup Job',
                color_discrete_sequence=px.colors.sequential.Viridis
                # category_orders={'Backup Job': job_order}
                )

    fig.update_layout(
        xaxis_title='Backup Job',
        yaxis_title='Duration (minutes)',
        xaxis_tickangle=-90,
        showlegend=False,
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)


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

    st.plotly_chart(fig, use_container_width=True)


def backup_speed(df):
    fig = px.line(df, x='Start Datetime', y='Backup Speed (GB/min)', color='Backup Job', 
                title='Backup Speed Over Time',
                labels={'Start datetime': 'Date', 'Backup Speed (GB/min)': 'Backup Speed (GB/min)'},
                markers=True)
    
    fig.update_traces(hovertemplate='%{x}<br>%{y} GB/min')

    st.plotly_chart(fig, use_container_width=True)


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

    st.plotly_chart(fig, use_container_width=True)


def speed_box(df):
    fig = px.box(df, x='Backup Job', y='Backup Speed (GB/min)',
                title='Distribution of Backup Speed for Each Backup Job',
                color='Backup Job',
                color_discrete_sequence=px.colors.sequential.Viridis
                )

    fig.update_layout(
        xaxis_title='Backup Job',
        yaxis_title='Backup Speed (GB/min)',
        xaxis_tickangle=-90,
        showlegend=False,
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)


def speed_heatmap(df):
    df['Day of Week'] = pd.to_datetime(df['Date']).dt.day_name()

    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df['Day of Week'] = pd.Categorical(df['Day of Week'], categories=day_order, ordered=True)

    heatmap_data = df.pivot_table(values='Backup Speed (GB/min)', index='Day of Week', columns='Hour', aggfunc='mean')

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

    st.plotly_chart(fig, use_container_width=True)


def perfomance(df):
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

        st.plotly_chart(fig, use_container_width=True)


def efficiency(df):
    fig1 = px.scatter(df, x='Backup Size (GB)', y='Dedupe', color='Backup Job', 
                    title='Efficiency of Deduplication vs Backup Size',
                    labels={'Backup Size (GB)': 'Backup Size (GB)', 'Dedupe': 'Dedupe Ratio'})
    
    fig1.update_traces(hovertemplate='Backup Size (GB): %{x}<br>Dedupe: %{y}x')

    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.scatter(df, x='Backup Size (GB)', y='Compression', color='Backup Job', 
                    title='Efficiency of Compression vs Backup Size',
                    labels={'Backup Size (GB)': 'Backup Size (GB)', 'Compression': 'Compression Ratio'})

    fig2.update_traces(hovertemplate='Backup Size (GB): %{x}<br>Compression: %{y}x')

    st.plotly_chart(fig2, use_container_width=True)


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

    st.plotly_chart(fig, use_container_width=True)