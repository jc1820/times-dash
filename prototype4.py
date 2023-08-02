import base64
import datetime
import io

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

#initialise app with selected bootstrap theme ~ theme is used for styling
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])

#create a dictionary to translate naming convention into sectors for user's understanding
code_to_name = {
    'ATM': 'Atmospheric',
    'ELC': 'Electricity',
    'IND': 'Industry',
    'RES': 'Reserve',
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
        html.H3("Welcome to the Data Visualization App!"),
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
        # Allow multiple files to be uploaded
        multiple=True
    ),

    dbc.Row(dbc.Col(id='tabs-content', width=12), className="mb-3"),
], className="pt-5 pb-5")


def parse_contents(contents, filename, date):
    """
    Parse the uploaded data file and generate graphs for each sector.

    Parameters:
        contents (str): Base64-encoded content of the uploaded file.
        filename (str): Name of the uploaded file.
        date (int): Last modified date of the uploaded file.

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

    # Group the emissions data by the first three letters of the "Commodity" column and "Year" column
    if 'Commodity' in df.columns:
        df['First_Three_Letters'] = df['Commodity'].str[:3]
        df_new = df.groupby(['First_Three_Letters', 'Period'])['Pv'].sum().reset_index()

        # Create a dictionary of graphs for each group
        graphs_dict = {}
        for group, group_df in df_new.groupby('First_Three_Letters'):
            group_bar_fig = px.bar(group_df, x='Period', y='Pv', title=f"Bar Graph of Data ({group})", barmode='stack')
            group_scatter_fig = px.scatter(group_df, x='Period', y='Pv', title=f"Scatter Plot of Data ({group})")
            group_pie_fig = px.pie(group_df, names='Period', values='Pv', title=f"Pie Chart of Data ({group})")
            group_line_fig = px.line(group_df, x='Period', y='Pv', title=f"Line Graph of Data ({group})")
            graphs_dict[group] = (group_bar_fig, group_scatter_fig, group_pie_fig, group_line_fig)

        return graphs_dict
    else:
        return None


@app.callback(Output('tabs-content', 'children'),
              Input('upload-data-em', 'contents'),
              State('upload-data-em', 'filename'),
              State('upload-data-em', 'last_modified'))
def update_tabs(contents_em, filenames_em, dates_em):
    """
    Update the content of the tabs based on the uploaded data.

    Parameters:
        contents_em (list): List of base64-encoded contents of the uploaded files.
        filenames_em (list): List of filenames of the uploaded files.
        dates_em (list): List of last modified dates of the uploaded files.

    Returns:
        list: A list of Dash Tab components with updated content.
    """
    tabs = []

    if contents_em is not None:
        for content, filename, date in zip(contents_em, filenames_em, dates_em):
            df_dict = parse_contents(content, filename, date)
            if df_dict is not None:
                for group_code, (bar_fig, scatter_fig, pie_fig, line_fig) in df_dict.items():
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
                     visualise TIMES data, please upload a data file in
                     drag and drop above to generate dashboard.'''),
        ]))

    return dcc.Tabs(tabs)

if __name__ == '__main__':
    app.run_server(debug=True, port=8057)

