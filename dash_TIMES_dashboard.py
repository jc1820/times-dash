#import all necessary packages and libraries, dash has even more features that can be incorporated
import base64
import datetime
import io
import traceback

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

#Initialise the app, the LUX theme is applied, there are several Dash themes to choose from
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX], suppress_callback_exceptions=True)

#Set colour theme
colors = {
    'background': '#f9f9f9',
    'text': '#333'
}

#Define short codes according to naming convention, translates TIMES output to standard language
naming_convention = {
    'ATM': 'Total Emissions',
    'ELC': 'Electricity',
    'TOT': 'Total Emissions',
    'IND': 'Industry',
    'RES': 'Residential',
    'SNK': 'Sink',
    'TRA': 'Transport',
    'UPS': 'Upstream',
    'TIA': 'Jet Fuel',
    'DST': 'Diesel',
    'PET': 'Petrol',
    'ELC': 'Electricity',
    'HYG': 'Hydrogen',
    'DNG': 'Natural Gas',
    'NGF': 'Natural Gas',
    'LPG': 'Liquefied Petroleum Gas',
    'CUD': 'Electricity',
    'DCD': 'District Cooling',
    'RDC': 'District Cooling',
    'RNG': 'Natural Gas'
    
}

#Content to the 'About' tab
about_content = dbc.Modal(
    [
        dbc.ModalHeader("About the App"),
        dbc.ModalBody(
            "This is the TIMES Visualization App, designed to help you visualize energy data. "
            "It provides interactive graphs and customization options for data analysis."
            "\n\nDeveloped by Your Name.",
        ),
        dbc.ModalFooter(
            dbc.Button("Close", id="close-about", className="ml-auto")
        ),
    ],
    id="about-modal",
    size="lg",  # Set modal size (lg = large)
)

#Build the navigation bar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="#")),
        dbc.NavItem(dbc.NavLink("About", id="open-about")),
    ],
    brand="QATAR Energy Dashboard",
    brand_href="#",
    color="primary",
    dark=True,
)

#Container for uploac area
upload_area = dbc.Container([
    dbc.Row(dbc.Col([
        html.H3("Welcome to the TIMES Visualization App!", style={"color": colors['text']}),
        html.Div("Upload your data below to generate the dashboard.", style={"color": colors['text']}),
    ], width=12, style={'margin': '20px'})),

#Dash upload button
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
        multiple=False  # Allow only one file upload for Excel
    ),

    # Display upload status message
    html.Div(id='upload-status', style={'margin': '10px', 'fontSize': '14px', 'color': colors['text']}),

    # Display the generated graphs in two columns
    dbc.Row(id='graph-container', style={'margin-top': '20px'}),

], style={'backgroundColor': colors['background']}, className="pt-5 pb-5")

#Set up the app layout
app.layout = dbc.Container([
    navbar,
    upload_area,
], style={'backgroundColor': colors['background']})


#callback for navigation bar
@app.callback(
    Output("about-modal", "is_open"),
    [Input("open-about", "n_clicks"), Input("close-about", "n_clicks")],
    [State("about-modal", "is_open")],
)
def toggle_about_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


#function that reads through file and creates the dictionary of the dataframes
def parse_contents(contents):
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)

        
        if 'openxml' in content_type:
            xls = pd.ExcelFile(io.BytesIO(decoded))
            dataframes_dict = {}  # Dictionary to store DataFrames

            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name)
                print(f"Loaded DataFrame for sheet '{sheet_name}':\n{df.head()}")
                dataframes_dict[sheet_name] = df

            return dataframes_dict

    except Exception as e:
        print(f"An error occurred while parsing contents: {str(e)}")

    print("No DataFrame found.")
    return {}

#Callback which takes the data input and produces the graphs
@app.callback(
    [Output('upload-status', 'children'), Output('graph-container', 'children')],
    [Input('upload-data-em', 'contents')]
)
def update_graph(contents_em):
    try:
        if contents_em is None:
            return "Upload your data to get started.", []

        df_dict = parse_contents(contents_em)
        if not df_dict:
            return "No data available.", []

        graph_list = []

        for sheet_name, df in df_dict.items():
            if sheet_name not in ['elecgen', 'sermix', 'resmix']:
                if 'Timeslice' in df.columns:
                    df = df[df['Timeslice'] == 'ANNUAL'] #filtering so only annual timeslice is considered
                    
            # Modify the 'Period' column to include only every 5 years
            df['Period'] = df['Period'].apply(lambda x: x if x % 5 == 0 else pd.NaT)

                
            fig1 = None
            fig2 = None
            #.... if more figures are required from one dataframe
                
    
            if sheet_name == 'emission':
                df['First_Three_Letters'] = df['Commodity'].str[:3]
                df_new = df.groupby(['First_Three_Letters', 'Period'])['Pv'].sum().reset_index()
                fig1 = px.line(df_new, x='Period', y='Pv', color='First_Three_Letters', line_dash='First_Three_Letters',)
                fig1.update_layout( #customise the axes and the title, plenty more customisations possible with Dash
                    title="Emissions",
                    xaxis_title="Year",
                    yaxis_title="Mt",
                    legend_title="Industry",  # Customize legend title if needed
                )
            
                # Modify legend labels based on the first 3 letters of Commodity codes
                for trace in fig1.data:
                    trace_name = trace.name  # Original trace name (Commodity code)
                    legend_label = naming_convention.get(trace_name, trace_name)  # Get corresponding label from dictionary
                    trace.name = legend_label  # Set the modified legend label

                    
            elif sheet_name == 'co2price':
                fig1 = px.line(df, x='Period', y='Pv_update', title=f'Line Chart for {sheet_name}')
                fig1.update_layout(
                    title="Carbon Price Over Time",
                    xaxis_title="Year",
                    yaxis_title="Price (currency)",
                    )
            elif sheet_name == 'eleccap':
                df_new = df.groupby('Period')['Pv'].sum().reset_index()
                fig1 = px.line(df_new, x='Period', y='Pv', title=f'Line Chart for {sheet_name}')
                fig1.update_layout(
                    title="Electricity Capacity",
                    xaxis_title="Year",
                    yaxis_title="Total Capacity (GW)",
                    )
            elif sheet_name == 'elecgen':
                df_new = df.groupby('Period')['Pv'].sum().reset_index()
                fig1 = px.line(df_new, x='Period', y='Pv', title=f'Line Chart for {sheet_name}')
                fig1.update_layout(
                    title = "Electricity Generated",
                    xaxis_title="Year",
                    yaxis_title="Electricity Generated (PJ)",
                )

                
            
            
            elif sheet_name == 'transemix':
                df['Last_Three_Letters'] = df['Commodity'].str[-3:]
                df_new = df.groupby(['Last_Three_Letters', 'Period'])['Pv'].sum().reset_index()
                fig1 = px.bar(df_new, x='Period', y='Pv', color='Last_Three_Letters', barmode='stack', title=f'Stacked Bar Chart for {sheet_name}')
                fig1.update_layout(
                    title="Transport Sector Energy Mix",
                    xaxis_title="Year",
                    yaxis_title="PJ",
                    legend_title="Industry",  # Customize legend title if needed
                )
            
                # Modify legend labels based on the first 3 letters of Commodity codes
                for trace in fig1.data:
                    trace_name = trace.name  # Original trace name (Commodity code)
                    legend_label = naming_convention.get(trace_name, trace_name)  # Get corresponding label from naming convention
                    trace.name = legend_label  # Set the updated legend label
                    
                    
            elif sheet_name == 'indemix':
                df['Last_Three_Letters'] = df['Commodity'].str[-3:]
                df_new = df.groupby(['Last_Three_Letters', 'Period'])['Pv'].sum().reset_index()
                fig1 = px.bar(df_new, x='Period', y='Pv', color='Last_Three_Letters', barmode='stack', title=f'Stacked Bar Chart for {sheet_name}')
                fig1.update_layout(
                    title="Industrial Sector Energy Mix",
                    xaxis_title="Year",
                    yaxis_title="PJ",
                    legend_title="Industry",  # Customize legend title if needed
                )
            
                # Modify legend labels based on the last 3 letters of Commodity codes
                for trace in fig1.data:
                    trace_name = trace.name  # Original trace name (Commodity code)
                    legend_label = naming_convention.get(trace_name, trace_name)  # Get corresponding label from dictionary
                    trace.name = legend_label  # Set the modified legend label
                    
            elif sheet_name == 'resmix':
                # Apply the filter to remove 'HOUSE' from the end of 'Commodity'
                df['Commodity'] = df['Commodity'].apply(lambda x: x[:-5] if x.endswith('HOUSE') else x)

                df['Last_Three_Letters'] = df['Commodity'].str[-3:]
                df_new = df.groupby(['Last_Three_Letters', 'Period'])['Pv'].sum().reset_index()
                fig1 = px.bar(df_new, x='Period', y='Pv', color='Last_Three_Letters', barmode='stack', title=f'Stacked Bar Chart for {sheet_name}')
                fig1.update_layout(
                    title="Residential Sector Energy Mix",
                    xaxis_title="Year",
                    yaxis_title="PJ",
                    legend_title="Industry",  # Customize legend title if needed
                )
            
                # Modify legend labels based on the last 3 letters of Commodity codes
                for trace in fig1.data:
                    trace_name = trace.name  # Original trace name (Commodity code)
                    legend_label = naming_convention.get(trace_name, trace_name)  # Get corresponding label from dictionary
                    trace.name = legend_label  # Set the modified legend label
                    
            elif sheet_name == 'sermix':
                df['Commodity'] = df['Commodity'].apply(lambda x: x[:-5] if x.endswith('BUILD') else x)
                df['Last_Three_Letters'] = df['Commodity'].str[-3:]
                df_new = df.groupby(['Last_Three_Letters', 'Period'])['Pv'].sum().reset_index()
                fig1 = px.bar(df_new, x='Period', y='Pv', color='Last_Three_Letters', barmode='stack', title=f'Stacked Bar Chart for {sheet_name}')
                fig1.update_layout(
                    title="Service Sector Energy Mix",
                    xaxis_title="Year",
                    yaxis_title="Mt",
                    legend_title="Industry",  # Customize legend title if needed
                )
            
                # Modify legend labels based on the last 3 letters of Commodity codes
                for trace in fig1.data:
                    trace_name = trace.name  # Original trace name (Commodity code)
                    legend_label = naming_convention.get(trace_name, trace_name)  # Get corresponding label from dictionary
                    trace.name = legend_label  # Set the modified legend label
                    
            
            
            if fig1 is not None:
                graph_list.append(
                    dbc.Col(
                        dcc.Graph(figure=fig1),
                        width=6  # Each graph takes half the width
                    )
                )

            if fig2 is not None: #this allows you to plot several figures from one dataframe
                graph_list.append(
                    dbc.Col(
                        dcc.Graph(figure=fig2),
                        width=6  # Each graph takes half the width
                    )
                )



        return "Data uploaded successfully.", graph_list

    except Exception as e:
        traceback_str = traceback.format_exc()
        error_msg = f"Callback error: {str(e)}\n{traceback_str}"
        print(error_msg)
        return "An error occurred while processing the data.", []


if __name__ == '__main__':
    app.run_server(debug=True, port = 8152)
