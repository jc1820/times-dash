import base64
import io
import traceback

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Output, State, Input
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.LUX], suppress_callback_exceptions=True)

colors = {
    'background': '#f9f9f9',
    'text': '#333'
}

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="#")),
        dbc.NavItem(dbc.NavLink("About", href="#")),
    ],
    brand="QATAR Energy Dashboard",
    brand_href="#",
    color="primary",
    dark=True,
)

upload_area = dbc.Container([
    dbc.Row(dbc.Col([
        html.H3("Welcome to the TIMES Visualization App!", style={"color": colors['text']}),
        html.Div("Upload your data to get started.", style={"color": colors['text']}),
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
        multiple=False  # Allow only one file upload for Excel
    ),

    html.Div(id='upload-status', style={'margin': '10px', 'fontSize': '14px', 'color': colors['text']}),
    html.Div(id='graphs-container')  # This will hold the generated graphs

], style={'backgroundColor': colors['background']}, className="pt-5 pb-5")


app.layout = dbc.Container([
    navbar,
    upload_area,
], style={'backgroundColor': colors['background']})


def parse_contents(contents):
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        if 'xls' in content_type:
            xls = pd.ExcelFile(io.BytesIO(decoded))
            dataframes_dict = {}  # Dictionary to store DataFrames
            
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name)
                dataframes_dict[sheet_name] = df
            
            return dataframes_dict
    except Exception as e:
        print(f"An error occurred while parsing contents: {str(e)}")
    
    return {}


@app.callback(Output('graphs-container', 'children'),
              Input('upload-data-em', 'contents'),
              State('upload-data-em', 'filename'))
def update_graphs(contents_em, filenames_em):
    all_graphs = []  # Define the 'all_graphs' list to hold the generated graphs
    
    try:
        if contents_em is not None:
            for content, filename in zip(contents_em, filenames_em):
                content_type, content_string = content.split(',')
                if 'xls' in content_type:
                    df_dict = parse_contents(content_string)  # Use content_string directly
                    if df_dict is not None:
                        for sheet_name, df in df_dict.items():
                            if sheet_name == 'emission':
                                bar_fig1 = px.line(df, x='Period', y='Pv', title=f"Bar Graph for {sheet_name}")
                                all_graphs.append(bar_fig1)


                            elif sheet_name == 'co2price':
                                bar_fig2 = px.line(df, x='Period', y='Pv', title=f"Bar Graph for {sheet_name}")
                                all_graphs.append(bar_fig2)
                                
                            elif sheet_name == 'eleccap':
                                bar_fig3 = px.line(df, x='Period', y='Pv', title=f"Bar Graph for {sheet_name}")
                                all_graphs.append(bar_fig3)
                                
                            elif sheet_name == 'elecgen':
                                bar_fig4 = px.line(df, x='Period', y='Pv', title=f"Bar Graph for {sheet_name}")
                                all_graphs.append(bar_fig4)
                                
                            elif sheet_name == 'transemix':
                                bar_fig5 = px.line(df, x='Period', y='Pv', title=f"Bar Graph for {sheet_name}")
                                all_graphs.append(bar_fig5)
                                
                            elif sheet_name == 'indemix':
                                bar_fig6 = px.line(df, x='Period', y='Pv', title=f"Bar Graph for {sheet_name}")
                                all_graphs.append(bar_fig6)
                                
                            elif sheet_name == 'resmix':
                                bar_fig7 = px.line(df, x='Period', y='Pv', title=f"Bar Graph for {sheet_name}")
                                all_graphs.append(bar_fig7)
                                
                            elif sheet_name == 'sermix':
                                bar_fig8 = px.line(df, x='Period', y='Pv', title=f"Bar Graph for {sheet_name}")
                                all_graphs.append(bar_fig8)

                            pass

        if len(all_graphs) == 0:
            all_graphs.append(html.Div('No data available.'))
        
        return html.Div(all_graphs)
    except Exception as e:
        traceback_str = traceback.format_exc()
        error_msg = f"Callback error: {str(e)}\n{traceback_str}"
        print(error_msg)
        return html.Div("An error occurred while updating the graphs.")


if __name__ == '__main__':
    app.run_server(debug=True)

# if sheet_name == 'emission':
#     bar_fig1 = px.line(df, x='Period', y='Pv', title=f"Bar Graph for {sheet_name}")
#     all_graphs.append(bar_fig1)


# elif sheet_name == 'co2price':
#     bar_fig2 = px.line(df, x='Period', y='Pv', title=f"Bar Graph for {sheet_name}")
#     all_graphs.append(bar_fig2)
    
# elif sheet_name == 'eleccap':
#     bar_fig3 = px.line(df, x='Period', y='Pv', title=f"Bar Graph for {sheet_name}")
#     all_graphs.append(bar_fig3)
    
# elif sheet_name == 'elecgen':
#     bar_fig4 = px.line(df, x='Period', y='Pv', title=f"Bar Graph for {sheet_name}")
#     all_graphs.append(bar_fig4)
    
# elif sheet_name == 'transemix':
#     bar_fig5 = px.line(df, x='Period', y='Pv', title=f"Bar Graph for {sheet_name}")
#     all_graphs.append(bar_fig5)
    
# elif sheet_name == 'indemix':
#     bar_fig6 = px.line(df, x='Period', y='Pv', title=f"Bar Graph for {sheet_name}")
#     all_graphs.append(bar_fig6)
    
# elif sheet_name == 'resmix':
#     bar_fig7 = px.line(df, x='Period', y='Pv', title=f"Bar Graph for {sheet_name}")
#     all_graphs.append(bar_fig7)
    
# elif sheet_name == 'sermix':
#     bar_fig8 = px.line(df, x='Period', y='Pv', title=f"Bar Graph for {sheet_name}")
#     all_graphs.append(bar_fig8)

# pass




