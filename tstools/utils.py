import numpy as np
import ee
import pandas as pd
import datetime
import geopandas

# Filter collection by point and date
def collection_filtering(point, collection_name, year_range, doy_range):
    collection = ee.ImageCollection(collection_name)\
    .filterBounds(point)\
    .filter(ee.Filter.calendarRange(year_range[0], year_range[1], 'year'))\
    .filter(ee.Filter.dayOfYear(doy_range[0],doy_range[1]))
    return collection


# Cloud masking for C1, L4-L7. Operators capitalized to
# avoid confusing with internal Python operators
def cloud_mask_l4_7_C1(img):
    pqa = ee.Image(img).select(['pixel_qa'])
    mask = (pqa.eq(66)).Or(pqa.eq(130))\
    .Or(pqa.eq(68)).Or(pqa.eq(132))
    return ee.Image(img).updateMask(mask)


# Cloud masking for C1, L8
def cloud_mask_l8_C1(img):
    pqa = ee.Image(img).select(['pixel_qa'])
    mask = (pqa.eq(322)).Or(pqa.eq(386)).Or(pqa.eq(324))\
    .Or(pqa.eq(388)).Or(pqa.eq(836)).Or(pqa.eq(900))
    return ee.Image(img).updateMask(mask)


def stack_renamer_l4_7_C1(img):
    band_list = ['B1', 'B2', 'B3', 'B4', 'B5', 'B7',  'B6', 'pixel_qa']
    name_list = ['BLUE', 'GREEN', 'RED', 'NIR', 'SWIR1', 'SWIR2', 'THERMAL',
                 'pixel_qa']
    return ee.Image(img).select(band_list).rename(name_list)


def stack_renamer_l8_C1(img):
    band_list = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B10', 'pixel_qa']
    name_list = ['BLUE', 'GREEN', 'RED', 'NIR', 'SWIR1', 'SWIR2', 'THERMAL',
                 'pixel_qa']
    return ee.Image(img).select(band_list).rename(name_list)


# filter and merge collections
def get_full_collection(coords, year_range, doy_range):
    point = ee.Geometry.Point(coords)
    l8_renamed = collection_filtering(point, 'LANDSAT/LC08/C01/T1_SR', year_range, doy_range)\
        .map(stack_renamer_l8_C1)
    l8_filtered1 = l8_renamed.map(cloud_mask_l8_C1)

    l7_renamed = collection_filtering(point, 'LANDSAT/LE07/C01/T1_SR', year_range, doy_range)\
        .map(stack_renamer_l4_7_C1);
    l7_filtered1 = l7_renamed.map(cloud_mask_l4_7_C1)

    l5_renamed = collection_filtering(point, 'LANDSAT/LT05/C01/T1_SR', year_range, doy_range)\
        .map(stack_renamer_l4_7_C1)
    l5_filtered1 = l5_renamed.map(cloud_mask_l4_7_C1)


    all_scenes = ee.ImageCollection((l8_filtered1.merge(l7_filtered1))\
                .merge(l5_filtered1)).sort('system:time_start').map(doIndices)

    return all_scenes


# Utility function for calculating spectral indices
def doIndices(fullImage):

    image = fullImage.select(['BLUE', 'GREEN', 'RED', 'NIR', 'SWIR1', 'SWIR2'])

    # Parameters
    cfThreshold = 20000
    soil = [2000, 3000, 3400, 5800, 6000, 5800]
    gv = [500, 900, 400, 6100, 3000, 1000]
    npv = [1400, 1700, 2200, 3000, 5500, 3000]
    shade = [0, 0, 0, 0, 0, 0]
    cloud = [9000, 9600, 8000, 7800, 7200, 6500]
    cfThreshold = ee.Image.constant(cfThreshold)

    #  Do spectral unmixing on a single image  */
    unmixImage = ee.Image(image).unmix([gv, shade, npv, soil, cloud], True,True).multiply(ee.Image(10000))\
                 .rename(['band_0', 'band_1', 'band_2','band_3','band_4'])
    newImage = ee.Image(fullImage).addBands(unmixImage)

    ndfi = ee.Image(unmixImage).expression(
      '((GV / (10000 - SHADE)) - (NPV + SOIL)) / ((GV / (10000 - SHADE)) + NPV + SOIL)', {
        'GV': ee.Image(unmixImage).select('band_0'),
        'SHADE': ee.Image(unmixImage).select('band_1'),
        'NPV': ee.Image(unmixImage).select('band_2'),
        'SOIL': ee.Image(unmixImage).select('band_3')
      })
    ndvi = ee.Image(image).normalizedDifference(['NIR','RED']).rename('NDVI')
    evi = ee.Image(image).expression(
          'float(2.5*(((B4/10000) - (B3/10000)) / ((B4/10000) + (6 * (B3/10000)) - (7.5 * (B1/10000)) + 1)))',
          {
              'B4': ee.Image(image).select(['NIR']),
              'B3': ee.Image(image).select(['RED']),
              'B1': ee.Image(image).select(['BLUE'])
          }).rename('EVI')

    brightness = ee.Image(image).expression(
        '(L1 * BLUE) + (L2 * GREEN) + (L3 * RED) + (L4 * NIR) + (L5 * SWIR1) + (L6 * B6)',
        {
            'L1': ee.Image(image).select('BLUE'), 'BLUE': 0.2043,
            'L2': ee.Image(image).select('GREEN'),'GREEN': 0.4158,
            'L3': ee.Image(image).select('RED'), 'RED': 0.5524,
            'L4': ee.Image(image).select('NIR'), 'NIR': 0.5741,
            'L5': ee.Image(image).select('SWIR1'), 'SWIR1': 0.3124,
            'L6': ee.Image(image).select('SWIR2'), 'B6': 0.2303
        }).rename('BRIGHTNESS')
    greenness = ee.Image(image).expression(
        '(L1 * BLUE) + (L2 * GREEN) + (L3 * RED) + (L4 * NIR) + (L5 * SWIR1) + (L6 * B6)',
        {
            'L1': image.select('BLUE'), 'BLUE': -0.1603,
            'L2': image.select('GREEN'), 'GREEN': -0.2819,
            'L3': image.select('RED'), 'RED': -0.4934,
            'L4': image.select('NIR'), 'NIR': 0.7940,
            'L5': image.select('SWIR1'), 'SWIR1': -0.0002,
            'L6': image.select('SWIR2'), 'B6': -0.1446
        }).rename('GREENNESS')
    wetness = ee.Image(image).expression(
        '(L1 * BLUE) + (L2 * GREEN) + (L3 * RED) + (L4 * NIR) + (L5 * SWIR1) + (L6 * B6)',
        {
            'L1': image.select('BLUE'), 'BLUE': 0.0315,
            'L2': image.select('GREEN'), 'GREEN': 0.2021,
            'L3': image.select('RED'), 'RED': 0.3102,
            'L4': image.select('NIR'), 'NIR': 0.1594,
            'L5': image.select('SWIR1'), 'SWIR1': -0.6806,
            'L6': image.select('SWIR2'), 'B6': -0.6109
        }).rename('WETNESS')

    return ee.Image(newImage)\
        .addBands([ndfi.rename(['NDFI']).multiply(10000), ndvi.multiply(10000),\
                   evi.multiply(10000), brightness, greenness, wetness])\
        .select(['band_0','band_1','band_2','band_3','NDFI','NDVI','EVI','BLUE',\
                 'GREEN', 'RED', 'NIR', 'SWIR1', 'SWIR2','THERMAL', 'BRIGHTNESS',\
                 'GREENNESS', 'WETNESS', 'pixel_qa'])\
        .rename(['GV','Shade','NPV','Soil','NDFI','NDVI','EVI','BLUE', 'GREEN', \
                 'RED', 'NIR', 'SWIR1', 'SWIR2','THERMAL', 'BRIGHTNESS', \
                 'GREENNESS', 'WETNESS', 'pixel_qa'])


# Get time series for location as a pandas dataframe
def get_df_full(collection, coords):

    point = ee.Geometry.Point(coords)
    # Sample for a time series of values at the point.
    filtered_col = collection.filterBounds(point)
    geom_values = filtered_col.getRegion(geometry=point, scale=30)
    geom_values_list = ee.List(geom_values).getInfo()
    # Convert to a Pandas DataFrame.
    header = geom_values_list[0]
    data = pd.DataFrame(geom_values_list[1:], columns=header)
    data['datetime'] = pd.to_datetime(data['time'], unit='ms', utc=True)
    data['doy'] = pd.DatetimeIndex(data['datetime']).dayofyear
    color_list = get_color_list()
    data['color'] = [color_list[i] for i in data['doy']]
    data.set_index('time')
    data = data.sort_values('datetime')
    data['ord_time'] = data['datetime'].apply(datetime.date.toordinal)
    data = data[['id', 'datetime', 'ord_time', 'BLUE', 'GREEN', 'RED', 'NIR',
                 'SWIR1', 'SWIR2', 'BRIGHTNESS', 'GREENNESS', 'WETNESS',
                 'THERMAL', 'GV', 'Shade', 'NPV', 'Soil', 'NDFI', 'NDVI', 'EVI',
                'pixel_qa', 'doy', 'color']]
    data = data.dropna()
    return data

# make color list for all 365 days of year
def get_color_list():

    colors = [['#000000'] * 79 \
             + ['#41b6c4'] * 93 \
             + ['#41ab5d'] * 94 \
             + ['#e31a1c'] * 89 \
             + ['#000000'] * 11][0]

    return colors


# Get the URL for an earth engine image. TODO: Wrong file
def GetTileLayerUrl(ee_image_object):

    map_id = ee.Image(ee_image_object).getMapId()
    return map_id["tile_fetcher"].url_format


# Convert a FeatureCollection into a geopandas DataFrame
# Features is a list of dict with the output
def fc2dfgeo(fc):

    features = ee.FeatureCollection(fc).getInfo()['features']

    dictarr = []

    for f in features:
        # Store all attributes in a dict
        attr = f['properties']
        # and treat geometry separately
        attr['geometry'] = f['geometry']
        dictarr.append(attr)

    df = geopandas.GeoDataFrame(dictarr)
    return df

# Check if there's an ID field, if not assign index
def check_id(fc_df):

    if 'ID' not in fc_df.columns:
        first_index = fc_df.index.min()
        fc_df['ID'] = fc_df.index
    else:
        first_index = fc_df['ID'].min()
    fc_df = fc_df.set_index('ID')

    return fc_df, first_index

# Plot TS from clicked point
def handle_draw(action, geo_json, current_band, year_range, doy_range):

    # Get the selected coordinates from the map's drawing control.
    coords = geo_json['geometry']['coordinates']
    click_col = get_full_collection(coords, year_range, doy_range)
    click_df = get_df_full(click_col, coords)

    return click_col, click_df
