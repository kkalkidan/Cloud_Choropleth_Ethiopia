import sys
from shapely.geometry import Polygon, box
import csv 
import pandas as pd
from shapely import wkt
import geopandas as gdp
import geoplot
import matplotlib as mpl
import matplotlib.pyplot as plt

def polygon(p):
    
    poly = list(map(float, p))
    xy =()
    for i in range(len(poly)):
        if(i%2 == 0):
            xy+= (((poly[i+1]),poly[i]), )
    return xy

def main(csv_file, year):

    with open(csv_file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count =0
        accq_start_dict= {'date' :[], 'tile':[], 'cloud':[], 'geometry': []}
        
        for row in csv_reader:
            if(line_count == 0):
                # print(f'Column names are \n {", ".join(row)}')
                line_count += 1
                first_row = row[57:67]
            else:
                geo = row[58:68]  
                # print(row[0][10:16])
                # return
                gg = polygon(geo)
                gg= gg[0:3] + (gg[4],) + (gg[3],)
                pp = Polygon(gg[1:])  
                accq_start_dict['date'].append(row[2])
                accq_start_dict['tile'].append(row[0][10:16])
                accq_start_dict['cloud'].append(row[15])
                accq_start_dict['geometry'].append(pp)

    df = pd.DataFrame(data=accq_start_dict)
    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d")
    df['cloud'] = df['cloud'].astype(float)

    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    months = [0] * 12
    for i in range(1, 13):
        m = df.loc[(df['month'] == i) & (df['year'] == year)]
        m['geometry'] = m['geometry'].astype(str)
        m = m.groupby(['tile', 'geometry'])['cloud'].mean().to_frame().reset_index()
        m['geometry'] = m['geometry'].apply(wkt.loads)
        m = gdp.GeoDataFrame(m.drop(['geometry'], axis=1), crs={'init': 'epsg:4326'}, geometry=m.geometry)
        months[i-1] = m
    norm = mpl.colors.Normalize(vmin=0, vmax=100)
    cmap = mpl.cm.ScalarMappable(norm=norm, cmap='Reds').cmap

    fig, axarr = plt.subplots(4, 3, figsize=(30, 30))
    mon_name = ['January', 'February', 'March',
                'April', 'May', 'June', 'July', 
                'August', 'September', 'October', 'November', 'December' ]

    fig.suptitle("Ethiopia: Landsat Cloud Cover percentage Choropleth " + str(year), fontsize=35)
    # print(months[0])
    for i in range(12):
        x = (i) // 3
        y = (i) % 3
        geoplot.choropleth(
            months[i], hue= months[i]['cloud'],
            cmap=cmap, norm=norm, legend=True, ax=axarr[x, y]
        ) 
        axarr[x, y].set_title(mon_name[i], fontsize=30)
    fig.savefig("landsat7_coverage_" + str(year), dpi=None, facecolor='w', edgecolor='w',
        orientation='portrait')

# count the arguments
arguments = len(sys.argv) - 1

# output argument-wise
position = 1
csv_file = sys.argv[1]
year = int(sys.argv[2])
if(arguments < 2):
    print("Too few arguments, exit")
    exit(0)




main(csv_file, year)
