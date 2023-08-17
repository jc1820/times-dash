import base64
import datetime
import io

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

#start app with selected bootstrap theme ~ theme is used for styling
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])

#create a dictionary to translate naming convention into sectors for user's understanding
code_to_name = {
    'ATM': 'Total Emissions',
    'ELC': 'Electricity',
    'TOT': 'Total Emissions',
    'IND': 'Industry',
    'RES': 'Residential',
    'SNK': 'Sink',
    'TRA': 'Transport',
    'UPS': 'Upstream',
}

#set up initial app skeleton, this will then be populated with generated content
#dash bootstrap is used for easier styling and manipulation
app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("QATAR Energy Dashboard",
                            style={"textAlign": "center",
                                   "fontSize": "36px",
                                   "fontFamily": "Monaco, sans-serif",
                                   "color": "#007BFF",
                                   "margin": "20px 0"}), width=12)),
    
    dbc.Row(dbc.Col([
        html.H3("Welcome to the TIMES Visualization App!"),
        html.Div("Upload your data to get started."),
    ], width=12, style={'margin': '20px'})),

    dcc.Upload(
        id='upload-data-em',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=True
    ),
    
    # Display upload status
    html.Div(id='upload-status', style={'margin': '10px', 'font-size': '14px'}),

    # Dropdown for selecting scenario
    html.Div(
    "Select the scenario you wish to investigate:",
    style={
        'padding': '10px',
        'font-size': '15px',
        'text-align': 'left'
        }
    ),


    dcc.Dropdown(
        id='scenario-dropdown',
        options=[],
        value=None,  # Default value
        placeholder="Select a scenario",
        style={'width': '100%', 'margin': '10px'}
    ),
    
    # Dropdown for selecting y-axis units
    dcc.Dropdown(
        id='y-axis-units-dropdown',
        options=[
            {'label': 'kT', 'value': 'kT'},
            {'label': 'MT', 'value': 'MT'}
        ],
        value='kT',  # Default value
        placeholder="Select y-axis units",
        style={'width': '100%', 'margin': '10px'}
    ),

    dbc.Row(dbc.Col(id='tabs-content', width=12), className="mb-3"),
], className="pt-5 pb-5")

# Callback to update upload status
@app.callback(Output('upload-status', 'children'),
              Input('upload-data-em', 'filename'))
def update_upload_status(filenames_em):
    if filenames_em is None:
        return ''
    else:
        return 'Upload complete!'


def parse_contents(contents, filename, date, selected_y_units):
    """
    Parse the uploaded data file and generate graphs for each sector.

    Parameters:
        contents (str): Base64-encoded content of the uploaded file.
        filename (str): Name of the uploaded file.
        date (int): Last modified date of the uploaded file.
        selected_y_units (str): Selected y-axis units from the dropdown.

    Returns:
        dict: A dictionary containing graphs for each sector.
    """
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return None

    # Filter the data to include only rows with 'Timeslice' as 'ANNUAL'
    if 'Timeslice' in df.columns:
        df = df[df['Timeslice'] == 'ANNUAL']

    # Group the emissions data by the first three letters of the "Commodity" column and "Year" column
    if 'Commodity' in df.columns:
        df['First_Three_Letters'] = df['Commodity'].str[:3]
        df_new = df.groupby(['First_Three_Letters', 'Period'])['Pv'].sum().reset_index()

    # Create a dictionary of dataframes for each scenario
    scenario_dataframes = {}
    for scenario, scenario_df in df.groupby('Scenario'):
        scenario_dataframes[scenario] = scenario_df

    # Create a dictionary of graphs for each scenario and group
    graphs_dict = {}
    for scenario, scenario_df in scenario_dataframes.items():
        scenario_graphs = {}
        for group, group_df in scenario_df.groupby('First_Three_Letters'):
            # Sum 'Pv' values within each group
            summed_group_df = group_df.groupby('Period')['Pv'].sum().reset_index()
            
            if selected_y_units == 'MT':
                summed_group_df['Pv'] /= 1000  # Convert kT to MT

            # Create graphs for the summed group data
            group_bar_fig = px.bar(summed_group_df, x='Period', y='Pv', title=f"Bar Graph of Data ({group})", barmode='stack')
            group_bar_fig.update_xaxes(title_text='Year', dtick='Y1')
            group_bar_fig.update_yaxes(title_text='Pv')

            group_scatter_fig = px.scatter(summed_group_df, x='Period', y='Pv', title=f"Scatter Plot of Data ({group})")
            group_scatter_fig.update_xaxes(title_text='Year')
            group_scatter_fig.update_yaxes(title_text='Pv')

            group_pie_fig = px.pie(summed_group_df, names='Period', values='Pv', title=f"Pie Chart of Data ({group})")

            group_line_fig = px.line(summed_group_df, x='Period', y='Pv', title=f"Line Graph of Data ({group})")
            group_line_fig.update_xaxes(title_text='Year')
            group_line_fig.update_yaxes(title_text='Pv')

            scenario_graphs[group] = (group_bar_fig, group_scatter_fig, group_pie_fig, group_line_fig)
        graphs_dict[scenario] = scenario_graphs

    return graphs_dict



def update_scenario_dropdown(scenario_dataframes):
    if scenario_dataframes is not None:
        return [{'label': scenario, 'value': scenario} for scenario in scenario_dataframes.keys()]
    else:
        return []
    
    
@app.callback(Output('tabs-content', 'children'),
              Output('scenario-dropdown', 'options'),  # Add this line
              Input('upload-data-em', 'contents'),
              Input('scenario-dropdown', 'value'),
              Input('y-axis-units-dropdown', 'value'),
              State('upload-data-em', 'filename'),
              State('upload-data-em', 'last_modified'))
def update_tabs(contents_em, selected_scenario, selected_y_units, filenames_em, dates_em):
    tabs = []
    scenario_options = []  # List to store scenario dropdown options

    if contents_em is not None:
        scenario_dataframes = {}
        for content, filename, date in zip(contents_em, filenames_em, dates_em):
            df_dict = parse_contents(content, filename, date, selected_y_units)  # Use selected_y_units here
            if df_dict is not None:
                scenario_dataframes.update(df_dict)
                scenario_options = update_scenario_dropdown(scenario_dataframes)  # Update scenario dropdown options
        
        if selected_scenario is not None and selected_scenario in scenario_dataframes:
            for group_code, (bar_fig, scatter_fig, pie_fig, line_fig) in scenario_dataframes[selected_scenario].items():
                group_name = code_to_name.get(group_code, 'Unknown Group')
                group_tab = dcc.Tab(label=group_name, children=[
                    dbc.Row([
                        dbc.Col(dcc.Graph(figure=bar_fig), width=6),
                        dbc.Col(dcc.Graph(figure=scatter_fig), width=6),
                    ]),
                    dbc.Row([
                        dbc.Col(dcc.Graph(figure=pie_fig), width=6),
                        dbc.Col(dcc.Graph(figure=line_fig), width=6),
                    ]),
                ])
                tabs.append(group_tab)

    if len(tabs) == 0:
        tabs.append(dcc.Tab(label='Welcome', children=[
            html.Div('''This is an interactive dashboard to help you
                     visualize TIMES data, please upload a data file in
                     drag and drop above to generate dashboard.'''),
        ]))

    return dcc.Tabs(tabs), scenario_options  # Return both tabs content and scenario dropdown options




if __name__ == '__main__':
    app.run_server(debug=True, port=8058)

