import dash
from dash import Dash, html, dcc, Output, Input, callback, ctx, State
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from funcs import create_graph_card, create_main_graph, create_map_graph, graph_highlight
from dash_bootstrap_templates import load_figure_template
import pandas as pd


app = Dash(__name__, external_stylesheets=[dbc.themes.YETI, dbc.icons.BOOTSTRAP])
main_df = pd.read_csv('cleaned_superstore.csv')
main_df = main_df[main_df['order_year'] == 2017]
load_figure_template("yeti") # using a template for consistant graphs formatting

# Creating the cards that contain the different graphs
by_category = create_graph_card('by_category')
by_segment = create_graph_card('by_segment')
by_sub_category = create_graph_card('by_sub_category')
by_state = create_graph_card('by_state')

# a dash mantine button menue to switch the column value of the graphs
choices = html.Div(
    [
        dmc.SegmentedControl(
            id="segmented",
            value="sales",
            data=[{"value": "sales", "label": "Sales"},
                  {"value": "profit", "label": "Profit"},
                  {"value": "orders", "label": "Orders"}],
            color='blue.9',
            fullWidth=True,
            className='fw-bold shadow-sm',
        ),
    ]
)


column_heigh_style = {"height": "100%"}
data = {'last_category': None, 'last_segment': None, 'last_subcategory': None,
        'last_state': None, 'category_filtered': False, 'segment_filtered': False,
         'sub_category_filtered': False, 'state_filtered': False, 'inputs': []}



app.layout = dbc.Container(
        # the dcc.Store holds 'gloabal variables' that will be used for the corss-filtering logic inside the callback
    [
        dcc.Store(id='store', data=data),
        dbc.Row(dbc.Col(choices, width={'offset': 1, "size": 2}), className='m-1'),
        dbc.Row([dbc.Col(by_category, width=5, style=column_heigh_style), dbc.Col(by_segment, width=5, style=column_heigh_style)],
                className='my-4',
                style={"height": '40vh'},
                justify='around'),
        dbc.Row([dbc.Col(by_sub_category, width=5, style=column_heigh_style), dbc.Col(by_state, width=5, style=column_heigh_style)],
                className='my-4',
                style={"height": '40vh'},
                justify='around'),
        ],
    fluid=True,
    style={'background-color': '#F8F9F9', "height": '100vh'}
)


@callback([
Output('by_category', 'figure'), Output('by_sub_category', 'figure'),
Output('by_segment', 'figure'), Output('by_state', 'figure'), Output('by_category', 'clickData'),
Output('by_sub_category', 'clickData'),  Output('by_segment', 'clickData'), Output('by_state', 'clickData'), Output('store', 'data')
],
           [Input('segmented', 'value'), Input('by_category', 'clickData'), Input('by_sub_category', 'clickData'),
           Input('by_segment', 'clickData'), Input('by_state', 'clickData')],
State('store', 'data'))
def update_graphs(value, clicked_category, clicked_subcategory, clicked_segment, clicked_state, app_state):
   # make a copy of the dataframe for each graph
    category_df = main_df.copy()
    segment_df = main_df.copy()
    sub_cat_df = main_df.copy()
    state_df = main_df.copy()
   # get the values of the 'global variables' from the dcc.Store input
    last_category = app_state['last_category']
    last_segment = app_state['last_segment']
    last_subcategory = app_state['last_subcategory']
    last_state = app_state['last_state']
    category_filtered = app_state['category_filtered']
    segment_filtered = app_state['segment_filtered']
    sub_category_filtered = app_state['sub_category_filtered']
    state_filtered = app_state['state_filtered']
    inputs = app_state['inputs']
    graph_trigger = ctx.triggered_id # get which figure triggered the callback

    dict = {}
    if graph_trigger == 'by_category' or graph_trigger == 'by_segment' or graph_trigger == 'by_sub_category':
        dict = {'input': ctx.triggered[0]['prop_id'].split('.')[0], 'value':ctx.triggered[0]['value']['points'][0]['x']}
        inputs.append(dict)

    if graph_trigger == 'by_state':
        dict = {'input': ctx.triggered[0]['prop_id'].split('.')[0], 'value': ctx.triggered[0]['value']['points'][0]['location']}
        inputs.append(dict)

    # Keeping a list of slected values for each graph to be used for filtering
    caetgoy_list = [d.get('value') for d in inputs if d.get('input') == 'by_category']
    segment_list = [d.get('value') for d in inputs if d.get('input') == 'by_segment']
    subcat_list = [d.get('value') for d in inputs if d.get('input') == 'by_sub_category']
    state_list = [d.get('value') for d in inputs if d.get('input') == 'by_state']

    # get the current selected value for each figure
    selected_category = caetgoy_list[-1] if len(caetgoy_list) >= 1 else None
    selected_segment = segment_list[-1] if len(segment_list) >= 1 else None
    selected_sub_category = subcat_list[-1] if len(subcat_list) >= 1 else None
    selected_state = state_list[-1] if len(state_list) >= 1 else None


    if selected_category is not None:
        if category_filtered and selected_category == last_category and graph_trigger == 'by_category':
            category_filtered = False
        elif category_filtered == False and graph_trigger != 'by_category':
            category_filtered = False
        else:
            segment_df = segment_df[segment_df['category'] == selected_category]
            sub_cat_df = sub_cat_df[sub_cat_df['category'] == selected_category]
            state_df = state_df[state_df['category'] == selected_category]
            last_category = selected_category
            category_filtered = True
    else:
        category_filtered = False

    if selected_segment is not None:
        if segment_filtered and selected_segment == last_segment and graph_trigger == 'by_segment':
            segment_filtered = False
        elif segment_filtered == False and graph_trigger != 'by_segment':
            segment_filtered = False
        else:
            category_df = category_df[category_df['segment'] == selected_segment]
            sub_cat_df = sub_cat_df[sub_cat_df['segment'] == selected_segment]
            state_df = state_df[state_df['segment'] == selected_segment]
            last_segment = selected_segment
            segment_filtered = True
    else:
        segment_filtered = False

    if selected_sub_category is not None:
        if sub_category_filtered and selected_sub_category == last_subcategory and graph_trigger == 'by_sub_category':
            sub_category_filtered = False
        elif sub_category_filtered == False and graph_trigger != 'by_sub_category':
            sub_category_filtered = False
        else:
            category_df = category_df[category_df['sub_category'] == selected_sub_category]
            segment_df = segment_df[segment_df['sub_category'] == selected_sub_category]
            state_df = state_df[state_df['sub_category'] == selected_sub_category]
            last_subcategory = selected_sub_category
            sub_category_filtered = True
    else:
        sub_category_filtered = False

    if selected_state is not None:
        if state_filtered and selected_state == last_state and graph_trigger == 'by_state':
            state_filtered = False
        elif state_filtered == False and graph_trigger != 'by_state':
            state_filtered = False
        else:
            category_df = category_df[category_df['state_code'] == selected_state]
            segment_df = segment_df[segment_df['state_code'] == selected_state]
            sub_cat_df = sub_cat_df[sub_cat_df['state_code'] == selected_state]
            last_state = selected_state
            state_filtered = True
    else:
        state_filtered = False

    category_bar_graph = create_main_graph(category_df, x='category', y=value, title='Category', value=value)
    if selected_category is not None and category_filtered:
        graph_highlight(category_bar_graph, selected_category)

    segment_bar_graph = create_main_graph(segment_df, x='segment', y=value, title='Segment', value=value)
    if selected_segment is not None and segment_filtered:
        graph_highlight(segment_bar_graph, selected_segment)

    sub_category_bar_graph = create_main_graph(sub_cat_df, x='sub_category', y=value, title='Sub-Category', value=value)
    if selected_sub_category is not None and sub_category_filtered:
        graph_highlight(sub_category_bar_graph, selected_sub_category)

    state_map = create_map_graph(state_df, value)
    if selected_state is not None and state_filtered:
        graph_highlight(state_map, selected_state)

    app_state['last_category'] = last_category
    app_state['last_segment'] = last_segment
    app_state['last_subcategory'] = last_subcategory
    app_state['last_state'] = last_state
    app_state['category_filtered'] = category_filtered
    app_state['segment_filtered'] = segment_filtered
    app_state['sub_category_filtered'] = sub_category_filtered
    app_state['state_filtered'] = state_filtered
    app_state['inputs'] = inputs

    # All clickData attributes of the graph reset to None so we can 'unclick' a clicked value
    return category_bar_graph, sub_category_bar_graph, segment_bar_graph, state_map, None, None, None, None, app_state


if __name__ == '__main__':
    app.run(debug=True, port=8051)