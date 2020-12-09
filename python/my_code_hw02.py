#-- my_code_hw02.py
#-- Assignment 02 GEO1015.2020
#-- [Simon Pena Pereira] 
#-- [5391210] 
#-- [YOUR NAME] 
#-- [YOUR STUDENT NUMBER] 

import sys
import math
import numpy
import rasterio
from rasterio import features

pt_1 = (3, 4)
pt_2 = (5,6)

def distance(pt1, pt2):
    """Returns cartesian distance between self and other Point
    """
    dist = math.sqrt((pt1[0] - pt2[0])**2+(pt1[1] - pt2[1])**2)
    return dist 



def output_viewshed(d, viewpoints, maxdistance, output_file):
    """
    !!! TO BE COMPLETED !!!
     
    Function that writes the output raster
     
    Input:
        d:            the input datasets (rasterio format)  
        viewpoints:   a list of the viewpoints (x, y, height)
        maxdistance:  max distance one can see
        output_file:  path of the file to write as output
        
    Output:
        none (but output GeoTIFF file written to 'output-file')
    """  
    #print('our dataset: ',d)
    #print('our viewpoints',viewpoints)
    #print('our maxdistance',maxdistance)
    #print('our output file',output_file)
    # [this code can and should be removed/modified/reutilised]
    # [it's just there to help you]

    #-- numpy of input
    npi  = d.read(1)
    #print('shape',d.shape)
    
    
    #-- fetch the 1st viewpoint
    v = viewpoints[0]
    
    #-- index of this point in the numpy raster
    vrow, vcol = d.index(v[0], v[1])
    #print('vrow, vcol',vrow, vcol)
    #print('reverse: ', (npi[0][vrow], npi[1][vcol]))
    #print('successful reverse indexing: ', d.xy(vrow,vcol))
    radius = maxdistance
    #-- the results of the viewshed in npvs, all values=0
    npvs = numpy.zeros(d.shape, dtype=numpy.int8)
    #npvs2 = numpy.zeros(d.shape, dtype=numpy.int8)
    #print('npvs', npvs)
    #-- put that pixel with value 2
    npvs[vrow , vcol] = 2
    #-- write this to disk
    #print(npvs)
    #print('height',d.height)
    #print('width', d.width)
    #print(npvs[300, 280])
    #print(d.index)
    #distance(v,)
    #print('coordinate v',v)
    #pt_x = d.xy(300, 280)
    #print('x, y of index 300,280',pt_x)
    #print(distance(v,pt_x))
    cellsize = distance(d.xy(0,0), d.xy(0,1))
    
    for row in enumerate(npvs):
        row_i = row[0]
        for col in enumerate(row[1]):
            col_i = col[0]
            pt = d.xy(row_i,col_i)
            dist = distance(v,pt)
            if dist > maxdistance:
                npvs[row_i,col_i] = 3
            elif dist > (maxdistance - cellsize) and dist < maxdistance:
                npvs[row_i,col_i] = 1
    
    
        
    with rasterio.open(output_file, 'w', 
                       driver='GTiff', 
                       height=npi.shape[0],
                       width=npi.shape[1], 
                       count=1, 
                       dtype=rasterio.uint8,
                       crs=d.crs, 
                       transform=d.transform) as dst:
        dst.write(npvs.astype(rasterio.uint8), 1)

    print("Viewshed file written to '%s'" % output_file)




# def Bresenham_with_rasterio():
#     # d = rasterio dataset as above
#     a = (10, 10)
#     b = (100, 50)
#     #-- create in-memory a simple GeoJSON LineString
#     v = {}
#     v["type"] = "LineString"
#     v["coordinates"] = []
#     v["coordinates"].append(d.xy(a[0], a[1]))
#     v["coordinates"].append(d.xy(b[0], b[1]))
#     shapes = [(v, 1)]
#     re = features.rasterize(shapes, 
#                             out_shape=d.shape, 
#                             # all_touched=True,
#                             transform=d.transform)
#     # re is a numpy with d.shape where the line is rasterised (values != 0)



