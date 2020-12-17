#-- my_code_hw02.py
#-- Assignment 02 GEO1015.2020
#-- [Simon Pena Pereira] 
#-- [5391210] 
#-- Daniel Dobson 
#-- 5152739 

import sys
import math
import numpy 
import rasterio
from rasterio import features

def distance(pt1, pt2):
    """Returns cartesian distance between self and other Point
    """
    dist = math.sqrt((pt1[0] - pt2[0])**2+(pt1[1] - pt2[1])**2)
    return dist 

def Bresenham_with_rasterio(d, viewpoint,horizon_point):
     # d = rasterio dataset as above
     a = viewpoint
     b = horizon_point
     ax, ay = d.xy(a[0], a[1])
     bx, by = d.xy(b[0], b[1])

     #-- create in-memory a simple GeoJSON LineString
     v = {}
     v["type"] = "LineString"
     v["coordinates"] = []
     v["coordinates"].append(d.xy(a[0], a[1]))
     v["coordinates"].append(d.xy(b[0], b[1]))
     shapes = [(v, 1)]
     re = features.rasterize(shapes, 
                             out_shape=d.shape, 
                             all_touched=True,
                             transform=d.transform)
     # re is a numpy with d.shape where the line is rasterised (values != 0)
     output = numpy.argwhere(re == 1)

     if bx >= ax and by > ay: # Upper right quadrant is ok...
        output = numpy.nonzero(re == 1)
        outputx = numpy.sort(output[0])
        outputx[::-1].sort()
        outputy = numpy.sort(output[1])
        output = [i for i in zip(outputx, outputy) if i is not None]
     elif bx <= ax and by >= ay: # Upper left quadrant is good!
        output = numpy.argwhere(re == 1)
        output = numpy.flipud(output)
     elif bx <= ax and by <= ay: # Lower left quadrant is ok...
        output = numpy.nonzero(re == 1)
        outputx = numpy.sort(output[0])
        outputy = numpy.sort(output[1])
        outputy[::-1].sort()
        output = [i for i in zip(outputx, outputy) if i is not None]
     else:                         # Lower right quadrant is good!
        output = numpy.argwhere(re == 1)
        
     return output, re


def slope(v,q,dx,zv,zq):
    """
    Function that computes slope of tangent

    Inputs:
    v:              Coordinates x, y of viewpoint
    q:              Cell q to update slope from               
    dx:             delta x or cartesian distance between points 
    zv:             height value of viewpoint 
    zq:             height       

    Output:
    m:              slope 
    """
    y = zq
    b = zv
    a = (y - b)/dx
    return a

def tangent_curr(a,x,b):
    """
    Function that computes tangent 

    Inputs:
    a:              previous slope
    x:              dx of vq (cartesian distance)
    b:              viewpoint height 

    Outputs:
    y:              tangent height at given cell q
    """
    y = (a*x) + b
    return y

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
    # These are print to help you understand the structure of the inputs
    #print('our dataset: ',d)
    #print('our viewpoints',viewpoints)
    #print('our maxdistance',maxdistance)
    #print('our output file',output_file)
    #print('our output file type', type(output_file))
    # [this code can and should be removed/modified/reutilised]
    # [it's just there to help you]

    #-- numpy of input
    npi  = d.read(1)
    #print('shape',d.shape)
    #print('type', type(d))
    #print('type', type(npi))
    #print('shape npi ',npi.shape)
    #print(npi[0][0])
    #print(npi[0,0])
    #-- fetch the 1st viewpoint
    v = viewpoints[0]
    #v2 = viewpoints[1]
    #print('viewpoint', v)
    #print('viewpoint', v2)
    #print('viewpoint x', v[0])
    #print('viewpoint y', v[1])
    #h = viewpoints[0][2]
    #print('height', h)

    #cellsize 
    cell_ul,_ = d.xy(v[0],v[1],offset='ul')
    cell_ur,_ = d.xy(v[0],v[1],offset='ur')
    cellsize = cell_ur-cell_ul
    print('cellsize', cellsize)

    #-- Radius of viewpoint
    radius = maxdistance

    #-- the results of the viewshed in npvs, all values=0
    # This is actually our 'empty' raster to start with
    #npvs = numpy.zeros(d.shape, dtype=numpy.int8)
    npvs = numpy.full(d.shape, 3, dtype=numpy.int8)
    #print('npvs', npvs)
    
    # Now fill the rows and cols according to their index,
    # with following possible values:
    # 0: not visible from the viewpoint(s) (but inside the 
    # max-distance/horizon zone(s))
    # 1: visible from the viewpoint(s)
    # 2: the pixel contains a viewpoint
    # 3: the pixel is outside the max-distance/horizon zone(s)

    for i in viewpoints:
        v = i
        vco = (v[0],v[1])
        # index of this point in the numpy raster
        vi = vrow, vcol = d.index(v[0], v[1])
        #print('vi in beginning loop',vi)
        #vi = vrow, vcol
        # This is the value of the centerpoint of the viewshed
        h = npi[vrow][vcol] + v[2]
        #print('height',h)
        npvs[vrow,vcol] = 2 
        horizon_points = []
        output_list= []
        vi_list = []
        npvs[vrow,vcol] = 2
        for row in enumerate(npvs):
            row_i = row[0]
            for col in enumerate(row[1]):
                col_i = col[0]
                pt = d.xy(row_i,col_i)
                dist = distance(v,pt)
                if dist > (radius - cellsize) and dist < radius:
                    #npvs[row_i,col_i] = 1
                    horizon_point = (row_i, col_i)
                    horizon_points.append(horizon_point)
                    vi_list.append(vi)
                    output,_ = Bresenham_with_rasterio(d,vi,horizon_point)
                    output_list.append(output)
                    slope_last = [-100]
                    for point in output:
                        cell_pt_i = ptix, ptiy = point[0], point[1]
                        cell_co_pt = cell_cx, cell_cy = d.xy(ptix,ptiy)
                        dist_vq = distance(vco,cell_co_pt)
                        zq = npi[ptix,ptiy]
                        
                        y_curr = tangent_curr(slope_last[-1],dist_vq,h)
                        if zq < y_curr and npvs[ptix,ptiy] != 2 and npvs[ptix,ptiy] != 1:
                            npvs[ptix,ptiy] = 0
                        elif zq >= y_curr and npvs[ptix,ptiy] != 2:
                            npvs[ptix,ptiy] = 1
                            slope_curr = slope(vco,cell_co_pt,dist_vq,h,zq)
                            slope_last.append(slope_curr)
                            
    #-- write this to disk
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








