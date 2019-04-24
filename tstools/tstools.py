# Classes for individual projects

import tstools.utils as utils
import tstools.leaflet_tools as lft
import tstools.ccd as ccd_tools
import ipyleaflet
import datetime
import pandas as pd
import tstools.plots as plots
import ipywidgets as widgets


# Sample interpretation to collect training data for MEaSUREs
class TSTools(object):

    def __init__(self):

        TSTools.band_index2 = 4
        TSTools.pyccd_flag2 = False
        TSTools.minv = 0
        TSTools.maxv = 6000
        TSTools.b1 = 'SWIR1'
        TSTools.b2 = 'NIR'
        TSTools.b3 = 'RED'


    ####### Starting Variables #######

    pyccd_flag2 = False
    current_band = ''
    band_index2 = 4
    click_col = ''
    point_color = ['#43a2ca']
    click_df = pd.DataFrame()
    click_geojson = ''
    PyCCDdf = pd.DataFrame()
    results = ''
    band_list = ['BLUE', 'GREEN', 'RED', 'NIR', 'SWIR1', 'SWIR2', 'BRIGHTNESS',
                 'GREENNESS', 'WETNESS', 'NDVI', 'NDFI', 'EVI', 'GV', 'Shade',
                 'NPV', 'Soil', ]
    doy_range = [1, 365]
    step = 1  #in years


    ###### Widgets ######
    ylim2 = plots.make_range_slider([0, 4000], -10000, 10000, 500, 'YLim:')
    xlim2 = plots.make_range_slider([2000, 2020], 1984, 2020, 1, 'XLim:')

    band_selector2 = plots.make_drop('SWIR1', band_list, 'Select band')
    image_band_1 = plots.make_drop('SWIR1', band_list, 'Red:')
    image_band_2 = plots.make_drop('NIR', band_list, 'Green:')
    image_band_3 = plots.make_drop('RED', band_list, 'Blue:')

    # Checkbox
    color_check = plots.make_checkbox(False, 'Color DOY', False)

    stretch_min = plots.make_text_float(0, 0, 'Min:')
    stretch_max = plots.make_text_float(6000, 6000, 'Max:')

    # Buttons
    pyccd_button2 = plots.make_button(False, 'Run PyCCD 2', icon='')
    toggle_pyccd_button2 = plots.make_button(False, 'Clear PyCCD', icon='')
    clear_layers = plots.make_button(False, 'Clear Map', icon='')

    # HTML
    hover_label = plots.make_html('Test Value')

    ###### Plots ######

    # Scales
    # Dates
    lc1_x2 = plots.make_bq_scale('date', datetime.date(xlim2.value[0], 2, 1), 
                                 datetime.date(xlim2.value[1], 1, 1))

    # DOY
    lc1_x3 = plots.make_bq_scale('linear', 0, 365)

    # Reflectance
    lc2_y2 = plots.make_bq_scale('linear', ylim2.value[0], ylim2.value[1])

    # plots
    lc3 = plots.make_bq_plot('scatter', [], [], {'x': lc1_x2, 'y': lc2_y2}, 
                             [1, 1],
                             {'click': 'select', 'hover': 'tooltip'},
                             {'opacity': 1.0, 'fill': 'DarkOrange', 
                              'stroke': 'Red'},
                             {'opacity': 0.5}, display_legend=True, 
                             labels=['Clicked point'])

    lc6 = plots.make_bq_plot('lines', [], [], {'x': lc1_x2, 'y': lc2_y2},
                             [1, 1], {}, {}, {}, colors=['black'],
                             stroke_width=3, labels=['PyCCD Model'],
                             display_legend=False)

    lc7 = plots.make_bq_plot('scatter', [], [], {'x': lc1_x2, 'y': lc2_y2},
                             [1, 1], {}, {}, {}, labels=['Model Endpoint'],
                             colors=['red'], marker='triangle-up')

    lc8 = plots.make_bq_plot('scatter', [], [], {'x': lc1_x3, 'y': lc2_y2},
                             [1, 1],
                             {'click': 'select', 'hover': 'tooltip'},
                             {'opacity': 1.0, 'fill': 'DarkOrange',
                              'stroke': 'Red'},
                             {'opacity': 0.5}, display_legend=True,
                             labels=['Clicked point'])

    # Axis
    x_ax2 = plots.make_bq_axis('Date', lc1_x2, num_ticks=6, tick_format='%Y',
                               orientation='horizontal')
    x_ax3 = plots.make_bq_axis('DOY', lc1_x3, num_ticks=6,
                               orientation='horizontal')

    y_ay2 = plots.make_bq_axis('SWIR1', lc2_y2, orientation='vertical')

    # Figures
    fig2 = plots.make_bq_figure([lc3, lc6, lc7], [x_ax2, y_ay2],
                                {'height': '300px', 'width': '100%'},
                                'Clicked TS')
    fig3 = plots.make_bq_figure([lc8], [x_ax3, y_ay2], {'height': '300px',
                                'width': '100%'}, 'Clicked DOY')

    ###### Functions ######

    # Change y axis for the clicked point
    def change_yaxis2(value):

        TSTools.lc2_y2.min = TSTools.ylim2.value[0]
        TSTools.lc2_y2.max = TSTools.ylim2.value[1]

    # Change x axis for the clicked point
    def change_xaxis2(value):

        TSTools.lc1_x2.min = datetime.date(TSTools.xlim2.value[0], 2, 1)
        TSTools.lc1_x2.max = datetime.date(TSTools.xlim2.value[1], 2, 1)

    # Display date of observation when hovering on scatterplot
    def hover_event(self, target):

        TSTools.hover_label.value = str(target['data']['x'])

    # Functions for changing image stretch
    def change_image_band1(change):
        new_band = change['new']
        TSTools.b1 = new_band

    def change_image_band2(change):
        new_band = change['new']
        TSTools.b2 = new_band

    def change_image_band3(change):
        new_band = change['new']
        TSTools.b3 = new_band

   # Band selection for clicked point
    def on_band_selection2(change):
        new_band = change['new']
        band_index = change['owner'].index
        TSTools.band_index2 = band_index
        TSTools.lc3.x = TSTools.click_df['datetime']
        TSTools.lc3.y = TSTools.click_df[new_band]
        TSTools.plot_ts(TSTools.lc3, 'ts')
        TSTools.plot_ts(TSTools.lc8, 'doy')
        TSTools.y_ay2.label = new_band
        if TSTools.pyccd_flag2:
            TSTools.do_pyccd2(0)

    # Clear everything on map
    def clear_map(b):
        lft.clear_map(TSTools.m, streets=True)

    def add_image2(self, target):
        m = TSTools.m
        df = TSTools.click_df
        current_band = TSTools.band_list[TSTools.band_index2]
        sample_col = TSTools.click_col
        stretch_min = TSTools.stretch_min.value
        stretch_max = TSTools.stretch_max.value
        b1 = TSTools.b1
        b2 = TSTools.b2
        b3 = TSTools.b3
        lft.click_event(target, m, current_band, df, sample_col, stretch_min,
                        stretch_max, b1, b2, b3)

    # Plot ts for point
    def do_draw(self, action, geo_json):
        current_band = TSTools.band_list[TSTools.band_index2]
        doy_range = TSTools.doy_range
        _col, _df = utils.handle_draw(action, geo_json, current_band, 
                                      list(TSTools.xlim2.value), doy_range)
        TSTools.click_geojson = geo_json
        TSTools.click_df = _df
        TSTools.click_col = _col

        TSTools.plot_ts(TSTools.lc3, 'ts')
        TSTools.plot_ts(TSTools.lc8, 'doy')

    # Add time series data to plots
    def plot_ts(plot, plottype):
        df = TSTools.click_df

        if TSTools.color_check.value is True:
            color_marks = list(df['color'].values)
        else:
            color_marks = None

        band = TSTools.band_list[TSTools.band_index2]

        if plottype == 'ts':
            plots.add_plot_ts(df, plot, band=band, color_marks=color_marks)
        else:
            plots.add_plot_doy(df, plot, band=band, color_marks=color_marks)

        if TSTools.pyccd_flag2:
            TSTools.do_pyccd2(0)

    # Run pyccd for the clicked location
    def do_pyccd2(b):

        TSTools.pyccd_flag2 = True
        display_legend = TSTools.lc7.display_legend
        dfPyCCD = TSTools.click_df
        band_index = TSTools.band_index2
        TSTools.results = ccd_tools.run_pyccd(display_legend, dfPyCCD, band_index)
        if band_index > 5:
            TSTools.lc6.y = []
            TSTools.lc6.x = []
            TSTools.lc7.y = []
            TSTools.lc7.x = []
            TSTools.lc7.display_legend = False
            return
        else:
            ccd_tools.plot_pyccd(dfPyCCD, TSTools.results, band_index, (0, 4000),
                                 TSTools.lc6, TSTools.lc7)
            TSTools.lc7.display_legend = True


    # Clear pyccd results
    def clear_pyccd2(b):
        TSTools.lc6.x = []
        TSTools.lc7.y = []

    ####### Widget Interactions #######
    dc = ipyleaflet.DrawControl(marker={'shapeOptions': {'color': '#ff0000'}},
                                polygon={}, circle={}, circlemarker={},
                                polyline={})

    zoom = 5
    layout = widgets.Layout(width='50%')
    center = (3.3890701010382958, -67.32297252983098)
    m = lft.make_map(zoom, layout, center)

    # Display controls
    ylim2.observe(change_yaxis2)
    xlim2.observe(change_xaxis2)
    clear_layers.on_click(clear_map)
    band_selector2.observe(on_band_selection2, names='value')
    image_band_1.observe(change_image_band1, names='value')
    image_band_2.observe(change_image_band2, names='value')
    image_band_3.observe(change_image_band3, names='value')

    # pyccd
    pyccd_button2.on_click(do_pyccd2)
    toggle_pyccd_button2.on_click(clear_pyccd2)

    # Plots
    lc3.on_element_click(add_image2)
    lc3.tooltip = hover_label
    lc3.on_hover(hover_event)
    lc8.on_element_click(add_image2)
    lc8.tooltip = hover_label
    lc8.on_hover(hover_event)

    # Mapping
    measure = ipyleaflet.MeasureControl(position='bottomleft',
                                        active_color = 'orange',
                                        primary_length_unit = 'kilometers'
                                        )
    measure.completed_color = 'red'
    
    dc.on_draw(do_draw)
    m.add_control(dc)
    m.add_control(measure)
    m.add_control(ipyleaflet.LayersControl())

