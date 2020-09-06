import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import sys,os,dash
from dash.dash import no_update
import pivotpy as pp
from app import app
from pages import bands, dos, home, fermi, input, locpot
from pages.re_usable import graph_config
import dash_bootstrap_components as dbc

TOP_NAV = 142   # height and top of content. Important inline style
COLOR_NAV = 'whitesmoke' #'#bdc4d8' # Navbar color
active_style   = {"color":  "#1f2c56","font-weight": "bold", "border-bottom": "3px solid  #1f2c56"}
inactive_style = {"float": "left","color": "blue", "text-align": "center",
                  "padding": "0", "text-decoration": "none", "font-size": "1em",
                  "box-shadow": "inset 0 -2px 0 0 #f9fdfcee"}
navigation = html.Div(className='Navigation',children=[])
menu_items = [
            html.Div([dcc.Link('Home',className='CenHeader', href='/pages/home')],id='home'),
            html.Div([dcc.Link('Bands',className='CenHeader', href='/pages/bands')],id='bands'),
            html.Div([dcc.Link('DOS',className='CenHeader', href='/pages/dos')],id='dos'),
            html.Div([dcc.Link('Fermi Surface',className='CenHeader', href='/pages/fermi')],id='fermi'),
            html.Div([dcc.Link('LOCPOT',className='CenHeader', href='/pages/locpot')],id='locpot'),
            html.Div([dcc.Link('Input',className='CenHeader', href='/pages/input')],id='input')
            ]
navigation.children.append(
    html.Div(
        [
    html.Div(
            menu_items,
        className='topnavbar')
        ])
    )
header = html.Div(className='AppHeader',id="app-header",children=[])
header.children.append(
    html.Div(className='CenHeader',children=html.H6('Path'))
    )
# This dropdown is updated through Home.

header.children.append(
   html.Div(id='page-content',children=[dcc.Dropdown(id='dd',clearable=False,persistence=True)]) 
    )
header.children.append(html.Div(className='CenHeader',id="counting",children=[html.H6('')]))


progressbar = html.Div(id='progressbar',className="progress",children=html.Div(
                        style={"width":"100vw","left":"0px","right":"0px"}
                        )
                    )

prev_t=html.Button(id='prev-btn',n_clicks=0, className="prev",style={"position": "fixed", "left": "0px", "top": "0px"},children=u'\u2039') #u'\u2b9c'+
next_t=html.Button(id='next-btn',n_clicks=0,className="next",style={"position": "fixed", "right": "0px", "top": "0px"},children=u'\u203a') #u'\u2b9e'+


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dbc.Button('≡',id="navbar-toggler",className='btn-simple',
               style={"width":"40px","height":"40px","border-radius":"20px","z-index":"99999999","position":"fixed","top":"10px","right":"10px"}
               ),
    dbc.Collapse([
        dbc.Navbar([
            html.H3('Pivotpy-Dash'),header,navigation
            ],className='my-navbar',color=COLOR_NAV,
            style={"top":"0px","height":"{}px".format(TOP_NAV)}
            ),
        ],id="navbar-collapse",is_open=True),
    html.Div(id = 'display-page',className='content',children=[],
             style={"top":"0px"}),
    progressbar,
    prev_t,
    next_t,
    ])

# add callback for toggling the collapse on small screens
@app.callback(
    [Output("navbar-collapse", "is_open"),
     Output('display-page','style')],
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open"),
     State("display-page", "style")],
)
def toggle_navbar_collapse(n, is_open,style):
    current_value = float(style["top"].split('p')[0])
    top = {"top":"{}px".format(abs(TOP_NAV-current_value))}
    if n:
        return not is_open,top
    return is_open,top

# Changing values with button
@app.callback([Output('counting','children'),
               Output('progressbar','children')],
              [Input('dd','value'),
               Input('dd','options')])
def update_count(value,options):
    if options != None:
        values = [opt['value'] for opt in options]
        size = pp.get_file_size(value)
        return html.H6("{}: {}/{}".format(size,values.index(value)+1,len(options))), html.Div(
            style={"width":"{}vw".format((100*(values.index(value)+1))/len(options)),"left":"0px","right":"0px"})
    else:
        return no_update,no_update
    
# Changing directories
@app.callback(Output('dd','value'),
              [Input('next-btn', 'n_clicks'),
               Input('prev-btn', 'n_clicks'),
               Input('dd','options')],
              [State('dd','value')])
def update_file_index(next,prev,options,value):
    if options != None:
        values = [opt['value'] for opt in options]
        try:
            count_dir = values.index(value)
        except ValueError:
            count_dir = 0
        ctx = dash.callback_context
        if not ctx.triggered:
            button_id = 'No clicks yet'
            return no_update
        else:
            button_id = ctx.triggered[0]['prop_id']
            if(button_id in "next-btn.n_clicks"):
                count_dir = values.index(value)+1
                if(count_dir>len(values)-1):
                    count_dir=len(values)-1
            if(button_id in "prev-btn.n_clicks"):
                count_dir = values.index(value)-1
                if(count_dir<0):
                    count_dir=0
        return options[count_dir]['value']
    else:
        return no_update

#Serve pages
@app.callback([Output('display-page', 'children'),
               Output('home','style'),
               Output('bands','style'),
               Output('dos','style'),
               Output('fermi','style'),
               Output('locpot','style'),
               Output('input','style')],
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/pages/home' or pathname == '/':
        return (home.layout,
                active_style,
                inactive_style,
                inactive_style,
                inactive_style,
                inactive_style,
                inactive_style
                )
    elif pathname == '/pages/bands':
        return (bands.layout,
                inactive_style,
                active_style,
                inactive_style,
                inactive_style,
                inactive_style, 
                inactive_style
                )
    elif pathname == '/pages/dos':
        return (dos.layout, 
                inactive_style,
                inactive_style,
                active_style,
                inactive_style,
                inactive_style, 
                inactive_style
                )
    elif pathname == '/pages/fermi':
        return (fermi.layout,
                inactive_style,
                inactive_style,
                inactive_style,
                active_style,
                inactive_style,
                inactive_style
                )
    elif pathname == '/pages/locpot':
        return (locpot.layout,
                inactive_style,
                inactive_style,
                inactive_style,
                inactive_style,
                active_style,
                inactive_style
                )
    elif pathname == '/pages/input':
        return (input.layout,
                inactive_style,
                inactive_style,
                inactive_style,
                inactive_style,
                inactive_style, 
                active_style
                )
    
if len(sys.argv) > 1:
    port = sys.argv[1]
else:
    port = 8050
    

#==========================
if __name__ == '__main__':
    app.run_server(debug=True,port=port)