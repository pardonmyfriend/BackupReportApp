import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import plotly.graph_objects as go

def status(df):
    status_counts = df['Status'].value_counts(normalize=True) * 100

    fig = px.pie(values=status_counts, names=status_counts.index, 
                title='Backup Job Status Distribution', 
                color_discrete_sequence=['#66c2a5', '#d53e4f', '#fc8d62'])

    st.plotly_chart(fig)


def status_by_backup(df):
    summary = df.groupby('Backup Job')[['Success', 'Warning', 'Error']].sum().reset_index()
    summary_long = summary.melt(id_vars='Backup Job', value_vars=['Success', 'Warning', 'Error'], 
                                var_name='Status', value_name='Count')

    fig = px.bar(summary_long, x='Backup Job', y='Count', color='Status', 
                color_discrete_map={'Success': '#66c2a5', 'Warning': '#fc8d62', 'Error': '#d53e4f'},
                title='Backup Results for Jobs: Count of Successes, Warnings and Errors')

    fig.update_xaxes(title_text='Backup Job', tickangle=-45)
    fig.update_yaxes(title_text='Count')

    fig.update_layout(
        # margin=dict(l=40, r=40, t=40, b=100),
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

    fig.update_layout(
        xaxis={'tickangle': -45, 'automargin': True, 'tickmode': 'array', 'tickvals': backup_stats['Backup Job']},
        height=600,
        # width=800,
        # margin=dict(l=40, r=40, t=40, b=100),
        showlegend=False
    )

    st.plotly_chart(fig)


def error_daily(df):
    daily_stats = df.groupby('Date')[['Success', 'Error', 'Warning']].sum().reset_index()
    daily_stats['Total'] = daily_stats['Error'] + daily_stats['Success'] + daily_stats['Warning']
    daily_stats['Error Rate'] = daily_stats['Error'] / daily_stats['Total']

    fig = px.line(daily_stats, x='Date', y='Error Rate', 
                title='Daily Trend of Error Rate',
                markers=True)

    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Error Rate'
    )

    st.plotly_chart(fig)


def error_hour(df):
    hourly_stats = df.groupby('Hour')[['Success', 'Error', 'Warning']].sum().reset_index()
    hourly_stats['Total'] = hourly_stats['Error'] + hourly_stats['Success'] + hourly_stats['Warning']
    hourly_stats['Error Rate'] = hourly_stats['Error'] / hourly_stats['Total']

    fig = px.line(hourly_stats, x='Hour', y='Error Rate', 
                title='Hourly Trend of Error Rate',
                markers=True)

    fig.update_layout(
        xaxis_title='Hour',
        yaxis_title='Error Rate'
    )

    st.plotly_chart(fig)


def perfomance(df):
    backup_jobs = df['Backup Job'].unique()
    palette = sns.color_palette("bright", 5).as_hex()

    for job in backup_jobs:
        job_df = df[df['Backup Job'] == job]
        job_df = job_df.sort_values(by='Start Datetime')

        col1, col2 = st.columns(2)

        # Wykres dla Backup Size, Data Read, Transferred
        with col1:
            fig1 = px.line(job_df, x='Start Datetime', 
                        y=['Backup Size (GB)', 'Data Read (GB)', 'Transferred (GB)'],
                        title=f'{job} - Backup Size, Data Read, Transferred',
                        labels={'value': 'Size (GB)', 'variable': 'Metric'},
                        markers=True,
                        color_discrete_sequence=palette[:3])

            fig1.update_layout(
                xaxis=dict(tickformat='%d-%m %H:%M', tickangle=30),
                legend=dict(orientation="h", yanchor="top", y=-0.4, xanchor="left", x=0)
            )

            st.plotly_chart(fig1)

        # Wykres dla Dedupe, Compression
        with col2:
            fig2 = px.line(job_df, x='Start Datetime', 
                        y=['Dedupe', 'Compression'],
                        title=f'{job} - Dedupe, Compression',
                        labels={'value': 'Ratio', 'variable': 'Metric'},
                        markers=True,
                        color_discrete_sequence=palette[3:])

            fig2.update_layout(
                xaxis=dict(tickformat='%d-%m %H:%M', tickangle=30),
                legend=dict(orientation="h", yanchor="top", y=-0.4, xanchor="left", x=0)
            )

            st.plotly_chart(fig2)


def size(df):
    fig = px.line(df, x='Start Datetime', y='Total Size (GB)', color='Backup Job', 
                title='Total Size Over Time for Each Backup Job', markers=True)

    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='Total Size (GB)')

    st.plotly_chart(fig)


def efficiency(df):
    fig1 = px.scatter(df, x='Backup Size (GB)', y='Dedupe', color='Backup Job', 
                    title='Efficiency of Deduplication vs Backup Size',
                    labels={'Backup Size (GB)': 'Backup Size (GB)', 'Dedupe': 'Dedupe Ratio'})

    fig2 = px.scatter(df, x='Backup Size (GB)', y='Compression', color='Backup Job', 
                    title='Efficiency of Compression vs Backup Size',
                    labels={'Backup Size (GB)': 'Backup Size (GB)', 'Compression': 'Compression Ratio'})

    st.plotly_chart(fig1)
    st.plotly_chart(fig2)


def daily_trends(df):
    daily_trends = df.groupby('Date').agg({
        'Total Size (GB)': 'sum',
        'Duration': 'sum',
        'Data Read (GB)': 'sum',
        'Transferred (GB)': 'sum'
    }).reset_index()

    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.line(daily_trends, x='Date', y=['Total Size (GB)', 'Data Read (GB)', 'Transferred (GB)'],
                    title='Daily Trends of Backup Sizes',
                    labels={'value': 'Size (GB)', 'variable': 'Metric'},
                    markers=True)

        fig1.update_layout(
            xaxis_title='Date',
            yaxis_title='Size (GB)'
        )

        st.plotly_chart(fig1)

    with col2:
        daily_trends['Duration (minutes)'] = daily_trends['Duration'].dt.total_seconds() / 60

        fig2 = px.line(daily_trends, x='Date', y='Duration (minutes)',
                    title='Daily Trends of Backup Duration',
                    labels={'Duration (minutes)': 'Duration (minutes)'},
                    markers=True)

        fig2.update_layout(
            xaxis_title='Date',
            yaxis_title='Duration (minutes)'
        )

        st.plotly_chart(fig2)


def hour_trends(df):
    hourly_trends = df.groupby('Hour').agg({
        'Total Size (GB)': 'sum',
        'Duration': 'sum',
        'Data Read (GB)': 'sum',
        'Transferred (GB)': 'sum'
    }).reset_index()

    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.line(hourly_trends, x='Hour', y=['Total Size (GB)', 'Data Read (GB)', 'Transferred (GB)'],
                    title='Hourly Trend of Backup Sizes',
                    labels={'value': 'Size (GB)', 'variable': 'Metric'},
                    markers=True)

        fig1.update_layout(
            xaxis_title='Hour',
            yaxis_title='Size (GB)'
        )

        st.plotly_chart(fig1)

    with col2:
        hourly_trends['Duration (minutes)'] = hourly_trends['Duration'].dt.total_seconds() / 60

        fig2 = px.line(hourly_trends, x='Hour', y='Duration (minutes)',
                    title='Hourly Trend of Backup Duration',
                    labels={'Duration (minutes)': 'Duration (minutes)'},
                    markers=True)

        fig2.update_layout(
            xaxis_title='Hour',
            yaxis_title='Duration (minutes)'
        )

        st.plotly_chart(fig2)


def heatmap(df):
    df_aggregated = df.groupby(['Date', 'Backup Job'])['Backup Size (GB)'].sum().reset_index()

    pivot_table = df_aggregated.pivot(index='Date', columns='Backup Job', values='Backup Size (GB)')

    fig = go.Figure(data=go.Heatmap(
        z=pivot_table.values,
        x=pivot_table.columns,
        y=pivot_table.index,
        zmin=0,
        zmax=pivot_table.values.max(),
        colorbar=dict(title="Backup Size (GB)")
    ))

    fig.update_layout(
        title='Heatmap of Backup Sizes Over Time',
        xaxis_title='Backup Job',
        yaxis_title='Date',
        xaxis=dict(tickangle=-45)
    )

    st.plotly_chart(fig)


def duration_hist(df):
    df['Duration (minutes)'] = df['Duration'].dt.total_seconds() / 60

    fig1 = px.histogram(df, x='Duration (minutes)', nbins=30, 
                        title='Distribution of Backup Durations for Backup Jobs',
                        labels={'Duration (minutes)': 'Duration (minutes)'},
                        color_discrete_sequence=[sns.color_palette("viridis")[0]])

    fig1.update_traces(histnorm='density')
    fig1.add_trace(px.line(df['Duration (minutes)'], y=df['Duration (minutes)']).data[0])

    fig1.update_layout(yaxis_title='Frequency')

    st.plotly_chart(fig1)


def duration_bar(df):
    avg_duration = df.groupby('Backup Job')['Duration'].mean().reset_index()
    avg_duration = avg_duration.sort_values(by='Duration', ascending=False)
    avg_duration['Duration'] = avg_duration['Duration'].dt.total_seconds() / 60

    fig2 = px.bar(avg_duration, x='Backup Job', y='Duration',
                title='Average Backup Duration for Each Backup Job',
                labels={'Duration': 'Average Duration (minutes)'},
                color='Backup Job',
                color_discrete_sequence=px.colors.sequential.Viridis)

    fig2.update_layout(
        xaxis_title='Backup Job',
        yaxis_title='Average Duration (minutes)',
        xaxis_tickangle=-90
    )

    st.plotly_chart(fig2)


def duration_box(df):
    df['Duration (minutes)'] = df['Duration'].dt.total_seconds() / 60

    avg_duration = df.groupby('Backup Job')['Duration'].mean().reset_index()
    avg_duration = avg_duration.sort_values(by='Duration', ascending=False)
    avg_duration['Duration'] = avg_duration['Duration'].dt.total_seconds() / 60

    job_order = avg_duration['Backup Job'].tolist()

    fig3 = px.box(df, x='Backup Job', y='Duration (minutes)',
                title='Distribution of Backup Durations for Each Backup Job',
                color='Backup Job',
                color_discrete_sequence=px.colors.sequential.Viridis,
                category_orders={'Backup Job': job_order})

    fig3.update_layout(
        xaxis_title='Backup Job',
        yaxis_title='Duration (minutes)',
        xaxis_tickangle=-90
    )

    st.plotly_chart(fig3)


def gantt(df):
    df = df.sort_values(by='Start Datetime').reset_index(drop=True)

    fig = px.timeline(df, x_start="Start Datetime", x_end="End Datetime", y="Backup Job")
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        width=2000,
        height=600,
        xaxis=dict(
            rangeslider=dict(visible=True),
            type="date",
            range=[df['Start Datetime'].min(), df['End Datetime'].max()]
        )
    )

    st.plotly_chart(fig)