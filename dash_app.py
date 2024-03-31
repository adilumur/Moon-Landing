'''
    How to run the app:
        1. open terminal 
        2. write in terminal "python3 dash_app.py"
    
    Required libraries:
        pip install pandas==2.1.1
        pip install plotly==5.17.0
        pip install openpyxl==3.1.2
        pip install dash==2.14.1
'''
import os
import pandas as pd 
import plotly.express as px 
import plotly.graph_objects as go
import openpyxl # used to convert data to excel format (.xlsx)
import numpy as np

import dash 
from dash import html, dcc
from dash.dependencies import Input, Output, State
from dash import dash_table 

import warnings 
warnings.simplefilter("ignore", category=FutureWarning)

# Create a dash application
app = dash.Dash(__name__)

#-------------------------------------------------------------------------------------------------------------
# Data taken from kaggle (https://www.kaggle.com/datasets/anoopjohny/moon-landings)
# File existence check before reading the CSV file
csv_file_path = "data.csv"
if os.path.exists(csv_file_path):
    data = pd.read_csv(csv_file_path)
else:
    raise FileNotFoundError("Data file not found")

# convert Launch Date to datetime dtype
def validate_date_input(date):
    try:
        parsed_date = pd.to_datetime(date)
        if parsed_date.year > 2023:
            parsed_date = parsed_date.replace(year=parsed_date.year - 100)
        return parsed_date
    except ValueError:
        return np.nan

data['Launch Date'] = data['Launch Date'].apply(validate_date_input)
dataf = data.copy()
dataf['Launch Date'] = dataf['Launch Date'].astype(str)
#-------------------------------------------------------------------------------------------------------------

# define a lists of allowed countries and file formats
allowed_countries = ['All Countries', 'United States', 'Soviet Union', 'Japan', 'European Union', 'China', 'India', 'Luxembourg', 'Israel', 'South Korea', 'Italy', 'UAE', 'Russia']
allowed_file_formats = ['csv', 'json', 'excel']

# create options for dropdown menus
country_options = [{'label':c, 'value':c} for c in allowed_countries]
file_format_options = [{'label':f.upper(), 'value':f} for f in allowed_file_formats]

# min and max years 
min_allowed_year = data["Launch Date"].min().year
max_allowed_year = data["Launch Date"].max().year

# year slider marks
year_marks={y:f'{y}' for y in range(1955,2025,5)}

# styles for menues
menu_style = {
    'textAlign':'center', 
    'width':'80%',
    'padding':'0, 10px', 
    'font-size':'20px',
    'margin':'auto'
}

# radioitems for failure outcome
fail = data[data['Outcome'].str.contains('fail')].copy()
allowed_fails = fail['Outcome'].unique()
for i, name in enumerate(allowed_fails):
    allowed_fails[i] = name.split(' ')[0]    
failure_items = [{'label':f'{f}', 'value':f'{f}'} for f in allowed_fails]

# Create an app layout
app.layout = html.Div(children=[
    html.H1(
        'Moon Missions Records Dashboard',
        style={
            'textAlign': 'center',
            'color': '#503D36',
            'font-size': 40
        }
    ),

    # User Input Section
    html.Div([
        html.Div([
            html.Label("Select Country"),
            dcc.Dropdown(
                id='country-dropdown-id',
                options=country_options,
                value='All Countries',
                placeholder="All Countries",
                searchable=False,
                clearable=False,
                multi=False,
            )
        ], style=menu_style),

        html.Div([
            html.Label('Select year:'),
            dcc.RangeSlider(
                id='year-slider-id',
                min=min_allowed_year,
                max=max_allowed_year,
                step=1,
                marks=year_marks,
                value=[min_allowed_year, max_allowed_year],
                tooltip={"placement": "bottom", "always_visible": True}
            ),
        ], style=menu_style),
    ]),

    # Graphs Section
    html.Div([
        html.Div([], id='pie-chart-id', style={'width': '40%', 'margin-left': '10%'}),
        html.Div([], id='heatmap-id', style={'width': '40%'}),
    ], style={
        'display': 'flex',
        'textAlign': 'center',
        'font-size': '20px',
        'margin': 'auto',
        'width': '80%',
    }),

    html.Div([], id='scatter-plot-id', style={'width': '80%', 'margin': 'auto'}),

    # Failure Graph Section
    html.Div([
        html.Label('Select Fail:', style={'margin-right': '2em'}),
        dcc.RadioItems(failure_items, value="Launch", id='fails-id', inline=True),
    ], style={
        'textAlign': 'center',
        'width': '80%',
        'padding': '10px, 10px',
        'font-size': '20px',
        'margin': 'auto'
    }),

    html.Div([], id='bar-chart-id', style={'width': '80%', 'margin': 'auto', }),

    # File Download Section
    html.Div([
        html.Label("Select File format to Download:"),
        dcc.Dropdown(
            id="file-format",
            options=file_format_options,
            value='CSV',
            placeholder="CSV",
            searchable=False,
            clearable=False,
            multi=False,
        ),
        html.Button("Download", id="btn-download", style={'width': '150px', 'height': '50px', 'margin': '10px'}),
    ], style={
        'textAlign': 'center',
        'width': '20%',
        'padding': '0, 10px',
        'font-size': '20px',
        'margin': 'auto'
    }),

    dcc.Download(id="download"),  # Download component

    # Table Display Section
    html.Div(
        dash_table.DataTable(
            id='datatable-id',
            data=dataf.to_dict('records'),
            columns=[
                {'name': i, 'id': i, 'deletable': False, 'selectable': True}
                for i in dataf.columns[:dataf.shape[1] - 1]  # every column except `Additional information`
            ],
            # Table formatting and configuration
            editable=False,
            filter_action='native',
            sort_action='native',
            sort_mode='multi',
            row_selectable=False,
            row_deletable=False,
            page_action='native',
            page_current=0,
            page_size=10,
            style_cell={
                'padding': '7px',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                'maxWidth': 0
            },
            style_header={
                'backgroundColor': 'rgb(220, 220, 220)',
                'fontWeight': 'bold'
            },
            style_cell_conditional=[
                {
                    'if': {'column_id': c},
                    'textAlign': 'left',
                } for c in data.columns
            ],
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(220, 220, 220)',
                }
            ],
        ),
        style={'width': '80%', 'margin': 'auto'}
    ),
],)
    
def create_pie(df: pd.Series, title: str):
    """
    Creates a Pie chart based on given data and title.

    Args:
    - df (pd.Series): Data for the Pie chart.
    - title (str): Title of the Pie chart.

    Returns:
    - dcc.Graph: Pie chart plotly figure wrapped in a Dash component.
    """
    return dcc.Graph(
        figure=px.pie(
            values=df.values,
            names=df.index,
            title=title
        )
    )
def create_scatter(df: pd.DataFrame, title: str):
    """
    Creates a Scatter plot based on given data and title.

    Args:
    - df (pd.DataFrame): Data for the Scatter plot.
    - title (str): Title of the Scatter plot.

    Returns:
    - dcc.Graph: Scatter plot plotly figure wrapped in a Dash component.
    """
    return dcc.Graph(
        figure=px.scatter(
            x=df["Launch Date"].unique(),
            y=df['Launch Date'].value_counts(),
            title=title
        ).update_layout(xaxis_title="Years", yaxis_title="Number of Launches")
    )
def create_bar(cd: dict):
    """
    Creates a Bar chart based on given data.

    Args:
    - cd (dict): Data for the Bar chart.

    Returns:
    - dcc.Graph: Bar chart plotly figure wrapped in a Dash component.
    """
    return dcc.Graph(
        figure=px.bar(
            x=list(cd.keys()),
            y=list(cd.values()),
            title="Number of fails"
        ).update_layout(xaxis_title="", yaxis_title="")
    )
def create_heatmap(df: pd.DataFrame):
    """
    Creates a Heatmap based on given data.

    Args:
    - df (pd.DataFrame): Data for the Heatmap.

    Returns:
    - dcc.Graph: Heatmap plotly figure wrapped in a Dash component.
    """
    return dcc.Graph(
        figure=px.imshow(
            df,
            text_auto=True,
            aspect='auto',
            title='Mission Type vs. Mission Outcome'
        )
    )
def create_matrix_for_heatmap(df: pd.DataFrame):
    """
    Creates a matrix for Heatmap data based on given data.

    Args:
    - df (pd.DataFrame): Data for the Heatmap matrix creation.

    Returns:
    - pd.DataFrame: Matrix for Heatmap.
    """
    series = df.groupby('Outcome')['Mission Type'].value_counts()
    ne = pd.DataFrame(0, columns=data['Outcome'].unique(), index=data['Mission Type'].unique())

    for column in ne.columns:
        if column in series.keys():
            ne[column] = ne[column] + series[column]

    return ne.fillna(0).astype(int)
# Validation function for country selection
def validate_country_input(value):
    if value in allowed_countries:
        return value
    else:
        # I won't send an error and stop the application
        return 'All Countries' 
# Validation function for year range
def validate_year_range(start_year, end_year):
    # Ensure the years are within the dataset's range
    if min_allowed_year <= start_year <= max_allowed_year and min_allowed_year <= end_year <= max_allowed_year:
        return [start_year, end_year]
    else:
        # I won't send an error and stop the application
        return [min_allowed_year, max_allowed_year]



# Callback function for generating charts based on country and year range
@app.callback(
    [
        Output(component_id='pie-chart-id', component_property='children'),
        Output(component_id='scatter-plot-id', component_property='children'),
        Output(component_id='heatmap-id', component_property='children')
    ],
    [
        Input(component_id='country-dropdown-id', component_property='value'),
        Input(component_id='year-slider-id', component_property='value')
    ]
)
def get_charts_by_country(entered_country: str, entered_years: list):
    # Validate user-selected country and year range
    entered_country = validate_country_input(entered_country)
    entered_years = validate_year_range(*entered_years)
    
    try:
        # Filter data based on the selected year range
        year_df = data[
            (data["Launch Date"].dt.strftime("%Y") >= str(entered_years[0])) &
            (data["Launch Date"].dt.strftime("%Y") <= str(entered_years[1]))
        ]  
    except Exception as e:
        # Log error and display an error message
        print(f"Error occurred: {str(e)}")
        return html.Div(html.P("An error occurred during data manipulation."))
    
    if entered_country == 'All Countries':
        # Generate charts for all countries within the selected year range
        pie_df = year_df['Outcome'].value_counts()
        return [
            create_pie(pie_df, 'Total Mission Outcomes'), 
            create_scatter(year_df, "Launch Date vs. Number of Launches in Total"),
            create_heatmap(create_matrix_for_heatmap(year_df))
        ] 
    else:
        # Generate charts specifically for the selected country within the chosen year range
        pie_df = year_df[year_df['Operator'].str.contains(entered_country)]['Outcome'].value_counts()
        country_df = year_df[year_df['Operator'].str.contains(entered_country)]
        return [
            create_pie(pie_df, f"Mission outcomes for {entered_country}"),
            create_scatter(country_df, f"Launch Date vs. Number of Launches for {entered_country}"),
            create_heatmap(create_matrix_for_heatmap(country_df))
        ]    

# Validation function for selected failure input
def validate_fail_input(value):
    # Check if the selected value is in the allowed list of failures
    if value in allowed_fails:
        return value
    else:
        # Return the first failure in the list if the input isn't valid
        return allowed_fails[0]

# Callback function to update the bar chart based on selected failure
@app.callback(
    Output(component_id='bar-chart-id', component_property='children'),
    Input(component_id='fails-id', component_property='value')
)
def get_bar_chart(entered_fail: str):
    # Validate the selected failure input
    entered_fail = validate_fail_input(entered_fail)

    # Filter data based on selected failure
    choosen_fail = fail[fail['Outcome'].str.contains(entered_fail)]

    # Initialize a dictionary to count failures per country
    cd = {f'{c}': 0 for c in allowed_countries}

    # Count failures for each country
    for country in cd.keys():
        cd[country] = len(choosen_fail[choosen_fail['Operator'].str.contains(country)])
    
    # Generate and return the bar chart based on failure counts per country
    return create_bar(cd)

@app.callback(
    Output('download', 'data'),
    [Input('btn-download', "n_clicks")],
    [State(component_id='file-format', component_property='value')],
    prevent_initial_call=True,
)
def get_download(n_clicks, entered_file_format: str):
    # Check if the selected file format is allowed
    if entered_file_format.lower() in allowed_file_formats:
        # Generate the file in the specified format
        if entered_file_format.lower() == 'csv':
            return dcc.send_data_frame(data.to_csv, "Moonlanding.csv")
        elif entered_file_format.lower() == 'json':
            return dcc.send_data_frame(data.to_json, "Moonlanding.json")
        elif entered_file_format.lower() == 'excel':
            return dcc.send_data_frame(data.to_excel, "Moonlanding.xlsx")
    else:
        return None # error in future     

# Run the app
if __name__ == '__main__':
    app.run_server()
