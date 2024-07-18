import requests
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output
from dash.dependencies import Input, Output, State
from dash_core_components import DatePickerRange  # Importing DatePickerRange component

# Replace with your actual access token
ACCESS_TOKEN = 'EAAOBIFOu4McBO0jYfmlqHBp1MkJ0uJnTHjHVL4Oq3moZAFVsFJulfMoB7eCr3h5dKhuRN8SCGFWZBONQVOwTH5rZBGAkzxDKVtapYc7tnSZBm9T1PVwaZCjvvMahS9oEUBfw2QgM4isT6T1MxbHZBbeKsZAFu4jq14oRr3bZA83Pj5mcIxN5r1rqZCzHJTdOD5gtv'
API_BASE_URL = 'https://graph.facebook.com/v20.0'

# Define your ad accounts
AD_ACCOUNTS = {
    'Flags Unlimited': 'act_10151051901257552',
    'Eley': 'act_10207752520881173',
    # Add more accounts as needed
}

def fetch_meta_ads_data(account_id, start_date=None, end_date=None):
    all_data = []
    params = {
        'access_token': ACCESS_TOKEN,
        'fields': 'spend,campaign_name,conversions,impressions,date_start,date_stop',
        'time_increment': '1',
        'level': 'campaign',
        'time_range': '{"since": "2024-6-18", "until": "2024-7-17"}',
        'limit' : 100,
    }
    response = requests.get(f"{API_BASE_URL}/{account_id}/insights", params=params)
    print(f"Request URL: {response.url}")  # Print the request URL for debugging
    print(f"Response Status Code: {response.status_code}")  # Print response status code
    if response.status_code != 200:
        print(f"Error: {response.json()}")  # Print the error message if the response is not successful
        return pd.DataFrame()
        
    data = response.json().get('data', [])
    print(f"Fetched Data: {data}")  # Print the fetched data for debugging
    df = pd.DataFrame(data)
        
        # Convert date columns to datetime
    if not df.empty:
        df['date_start'] = pd.to_datetime(df['date_start'])
        df['date_stop'] = pd.to_datetime(df['date_stop'])
        df['date'] = df['date_start']  # or another appropriate column for date
    else:
        print(f"DataFrame is empty for account {account_id}")
    return df



# Initialize the Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1("Meta Ads Dashboard"),
    
    dcc.Dropdown(
        id='account-selector',
        options=[{'label': name, 'value': acc_id} for name, acc_id in AD_ACCOUNTS.items()],
        value=list(AD_ACCOUNTS.values())[0],
        multi=False
    ),
    
    dcc.Dropdown(
        id='metric-selector',
        options=[
            {'label': 'Spend', 'value': 'spend'},
            {'label': 'Imressions', 'value': 'impressions'},
            {'label': 'Purchase Revenue', 'value': 'purchase_revenue'},
            {'label': 'Purchase ROAS', 'value': 'purchase_roas'},
            {'label': 'CPA', 'value': 'cpa'},
            {'label': 'Clicks', 'value': 'clicks(all)'},
        ],
        value='spend',
        multi=False
    ),
    
    dcc.Graph(id='line-graph'),
    
    # dcc.Checklist(
    #     id='status-filter',
    #     options=[
    #         {'label': 'Active', 'value': 'active'},
    #         {'label': 'Paused', 'value': 'paused'},
    #         {'label': 'Deleted', 'value': 'deleted'},
    #     ],
    #     value=['active', 'paused']
    # ),
    
    # dcc.Graph(id='campaign-table'),
    
    # html.Div(id='adset-detail')
])

@app.callback(
    Output('line-graph', 'figure'),
    Input('metric-selector', 'value'),
    Input('account-selector', 'value')
)
def update_line_graph(selected_metric, selected_account):
    df = fetch_meta_ads_data(selected_account)
    if df.empty:
        return px.line(title="No data available")
    
    # Print the data used for plotting the line graph
    print(f"Data for line graph:\n{df[['date', selected_metric, 'campaign_name']]}")
    
    try:
        fig = px.line(df, x='date', y=selected_metric, color='campaign_name')
        fig.update_yaxes(categoryorder="category descending")
    except Exception as e:
        print(f"Exception while creating line graph: {e}")
        return px.line(title="Error creating graph")
    return fig

# @app.callback(
#     Output('campaign-table', 'figure'),
#     Input('status-filter', 'value'),
#     Input('account-selector', 'value')
# )
# def update_campaign_table(selected_statuses, selected_account):
#     df = fetch_meta_ads_data(selected_account)
#     if df.empty:
#         return px.bar(title="No data available")
#     try:
#         print(f"Original DataFrame:\n{df}")  # Print original DataFrame for debugging
#         filtered_df = df[df['status'].isin(selected_statuses)]
#         print(f"Filtered DataFrame:\n{filtered_df}")  # Print filtered DataFrame for debugging
#         pivot_table = pd.pivot_table(filtered_df, values=['spend', 'purchases', 'purchase_revenue', 'purchase_roas', 'cpa', 'clicks'], 
#                                      index=['campaign_name', 'status'], 
#                                      aggfunc='sum').reset_index()
#         print(f"Pivot Table:\n{pivot_table}")  # Print pivot table for debugging
#         return px.bar(pivot_table, x='campaign_name', y='spend', color='status')
#     except Exception as e:
#         print(f"Exception while creating campaign table: {e}")
#         return px.bar(title="Error creating table")

# @app.callback(
#     Output('adset-detail', 'children'),
#     Input('campaign-table', 'clickData'),
#     State('account-selector', 'value')
# )
# def display_adset_details(click_data, selected_account):
#     if click_data is None:
#         return "Click on a campaign to see ad set details"
#     campaign_name = click_data['points'][0]['x']
#     df = fetch_meta_ads_data(selected_account)
#     if df.empty:
#         return html.Div("No data available")
#     filtered_df = df[df['campaign_name'] == campaign_name]
#     return html.Div([
#         html.H3(f"Ad Sets in {campaign_name}"),
#         dcc.Graph(
#             figure=px.line(filtered_df, x='date', y='spend', color='campaign_name')
#         )
#     ])

if __name__ == '__main__':
    app.run_server(debug=True)