import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import plotly.graph_objects as go
from scipy.stats import gaussian_kde


def status_by_obj(df):
    summary = df.groupby('Object')[['Success', 'Warning', 'Error']].sum().reset_index()
    summary_long = summary.melt(id_vars='Object', value_vars=['Success', 'Warning', 'Error'], 
                                var_name='Status', value_name='Count')

    fig = px.bar(summary_long, x='Object', y='Count', color='Status', 
                color_discrete_map={'Success': '#66c2a5', 'Warning': '#fc8d62', 'Error': '#d53e4f'},
                title='Backup Results for Objects: Count of Successes, Warnings and Errors')

    fig.update_traces(hovertemplate='%{x}<br>%{y}') 

    fig.update_xaxes(title_text='Object', tickangle=-90)
    fig.update_yaxes(title_text='Count')

    fig.update_layout(
        height=600,
        legend_title_text='Status'
    )

    st.plotly_chart(fig)


def error_obj(df):
    backup_stats = df.groupby('Object')[['Success', 'Error', 'Warning']].sum().reset_index()
    backup_stats['Total'] = backup_stats['Error'] + backup_stats['Success'] + backup_stats['Warning']
    backup_stats['Error Rate'] = backup_stats['Error'] / backup_stats['Total']

    backup_stats = backup_stats.sort_values(by='Error Rate', ascending=False)

    colors = sns.color_palette("viridis", len(backup_stats)).as_hex()

    fig = px.bar(backup_stats, x='Object', y='Error Rate', 
                color='Object', 
                title='Error Rate by Object', 
                color_discrete_sequence=colors)
    
    fig.update_traces(hovertemplate='%{y}') 

    fig.update_layout(
        xaxis={'tickangle': -90, 'automargin': True, 'tickmode': 'array', 'tickvals': backup_stats['Object']},
        height=600,
        showlegend=False
    )

    st.plotly_chart(fig)


def plot_avg(df, x_col, title, x_label):
    vm_performance = df.groupby('Object').agg({
        'Size (GB)': 'mean',
        'Read (GB)': 'mean',
        'Duration': 'mean'
    }).reset_index()

    vm_performance['Duration'] = vm_performance['Duration'].dt.total_seconds() / 60

    fig = px.bar(vm_performance, 
                 x=x_col, 
                 y='Object', 
                 color='Object',
                 orientation='h',
                 color_discrete_sequence=sns.color_palette("viridis", len(vm_performance)).as_hex(),
                 title=title)
    
    fig.update_traces(hovertemplate='%{x}') 
    
    fig.update_layout(
        xaxis_title=x_label,
        yaxis_title='Object',
        showlegend=False,
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)


def avg_total_obj(df):
    plot_avg(df, 'Size (GB)', 'Average Total Size for Each Object', 'Average Size (GB)')


def size_obj(df):
    fig = px.line(df, x='Start Datetime', y='Size (GB)', color='Object', 
                title='Total Size Over Time for Each Object', markers=True)
    
    fig.update_traces(hovertemplate='%{x}<br>%{y} GB') 

    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='Size (GB)')

    st.plotly_chart(fig)


def avg_duration_obj(df):
    plot_avg(df, 'Duration', 'Average Backup Duration for Each Backup Job', 'Average Duration (minutes)')


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

    st.plotly_chart(fig, use_container_width=True)


def duration_box_obj(df):
    df['Duration (minutes)'] = df['Duration'].dt.total_seconds() / 60

    avg_duration = df.groupby('Object')['Duration'].mean().reset_index()
    avg_duration['Duration'] = avg_duration['Duration'].dt.total_seconds() / 60

    fig = px.box(df, x='Object', y='Duration (minutes)',
                title='Distribution of Backup Durations for Each Object',
                color='Object',
                color_discrete_sequence=px.colors.sequential.Viridis
                )

    fig.update_layout(
        xaxis_title='Object',
        yaxis_title='Duration (minutes)',
        xaxis_tickangle=-90,
        showlegend=False,
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)


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

    st.plotly_chart(fig, use_container_width=True)


def backup_speed_obj(df):
    fig = px.line(df, x='Start Datetime', y='Backup Speed (GB/min)', color='Object', 
                title='Backup Speed Over Time',
                labels={'Start datetime': 'Date', 'Backup Speed (GB/min)': 'Backup Speed (GB/min)'},
                markers=True)
    
    fig.update_traces(hovertemplate='%{x}<br>%{y} GB/min')

    st.plotly_chart(fig, use_container_width=True)


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

    st.plotly_chart(fig, use_container_width=True)


def speed_box_obj(df):
    fig = px.box(df, x='Object', y='Backup Speed (GB/min)',
                title='Distribution of Backup Speed for Each Object',
                color='Object',
                color_discrete_sequence=px.colors.sequential.Viridis
                )

    fig.update_layout(
        xaxis_title='Object',
        yaxis_title='Backup Speed (GB/min)',
        xaxis_tickangle=-90,
        showlegend=False,
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)


def perfomance_obj(df):
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

        st.plotly_chart(fig)


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

    st.plotly_chart(fig, use_container_width=True)