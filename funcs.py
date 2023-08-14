from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd


def create_main_graph(df, x, y, title, value):
    if value == 'orders':
        df = df.groupby(x, as_index=False)[y].nunique().sort_values(by=value, ascending=False)
    else:
        df = df.groupby(x, as_index=False)[y].sum().sort_values(by=value, ascending=False)
    fig = px.bar(df, x=x, y=y, text_auto='0.2s', hover_data={x: True, value:':,.0f'},
                 title=f'<b>{value.capitalize()}</b> by {title}').update_layout(yaxis_title=None,
                 xaxis_title=None, margin=dict(l=0, r=0, t=30, b=0), yaxis=dict(showticklabels=False, visible=False),
                 title=dict(font=dict(family='Arial', size=16), x=0.5))
    return fig


def create_graph_card(id, className='p-2'):
    height = "100%"
    card = dbc.Card(
    [dcc.Graph(id=id, style={'height': height}, config={'doubleClick': 'reset'})],
    style={'height': height},
    className=className
)
    return card



# Calculate the indices that correspond to 70% of the color scale
full_color_scale = px.colors.sequential.Blues
start_index = int(len(full_color_scale) * 0.3)
end_index = int(len(full_color_scale) * 1)
custom_color_scale = full_color_scale[start_index:end_index]

def create_map_graph(df, value):
    if value == 'orders':
        grouped_by_state = df.groupby(['state', 'state_code'], as_index=False)[value].nunique()
    else:
        grouped_by_state = df.groupby(['state', 'state_code'], as_index=False)[value].sum()
    fig = px.choropleth(
        data_frame=grouped_by_state,
        locationmode='USA-states',
        locations='state_code',
        color=value,
        scope='usa',
        custom_data=value,
        hover_name='state',
        # hover_data={'state': True, 'state_code': False, value:':.0f'},
        color_continuous_scale=px.colors.sequential.Blues,
        range_color=[grouped_by_state[value].min(), grouped_by_state[value].max()],
        title=f'<b>{value.capitalize()}</b> by State',
        labels={value: value},
    ).update_layout(margin=dict(l=0, r=0, t=30, b=0), coloraxis_showscale=True, coloraxis_colorbar_x=0.9,
                    title=dict(font=dict(family='Arial', size=16), x=0.5), hoverlabel=dict(bgcolor="#2471a1"))\
        .update_traces(marker_line_color='lightgrey', hovertemplate='<b>%{hovertext}</b><br><br>value=%{customdata:,.0f}<extra></extra>')

    return fig
