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
     #line = numpy.nonzero(re == 1)
     #line = numpy.flip(line)
     #output = numpy.argwhere(re == 1)
     #output = output[output[:,0].argsort()[::-1]]
     #output = output[output[:,1].argsort()]
     #output = output[output[:,0].argsort()]
     #output = output.sort()
     output = numpy.argwhere(re == 1)

     if bx >= ax and by >= ay:
        output = numpy.argwhere(re == 1)
        #print(ax, bx)
        output = output[output[:,0].argsort()[::-1]]
        #output = numpy.fliplr(output)
     elif bx < ax and by > ay:
        output = numpy.argwhere(re == 1)
        #output = numpy.fliplr(output)
        output = output[output[:,0].argsort()[::-1]]
     elif bx < ax and by < ay:
        output = numpy.argwhere(re == 1)
        output = output[output[:,1].argsort()[::-1]]
     else:
        output = numpy.argwhere(re == 1)
    
     # Sort on x high to low
     #output = output[output[:,0].argsort()[::-1]]
     # Sort on x low to high
     #output = output[output[:,0].argsort()]
     # Sort on y low to high
     #output = output[output[:,1].argsort()]
     # Sort on y high to low
     #output = output[output[:,1].argsort()[::-1]]
     return output, re


def slope(d,v,h,q,z):
    """
    Function that computes slope of tangent

    Inputs:
    d:              the input datasets (rasterio format) 
    v:              viewpoint coordinates (x, y)
    h:              viewpoint height 
    q:              point on line indices (x, y) 
    z:              z value point on line        

    Output:
    a:              slope 
    x:              distance  
    """
    y = z
    b = h
    pt1 = x1, y1 = v[0],v[1]
    pt2 = x2, y2 = d.xy(q[0],q[1])
    x = distance(pt1,pt2)
    a = (y - b)/x
    return a, x

def tangent_curr(a,x,b):
    """
    Function that computes tangent 

    Inputs:
    a:              slope
    x:              x coordinate point
    b:              viewpoint height 

    Outputs:
    y:              tangent height
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
    print('shape',d.shape)
    print('type', type(d))
    print('type', type(npi))
    print('shape npi ',npi.shape)
    print(npi[0][0])
    print(npi[0,0])
    #-- fetch the 1st viewpoint
    v = viewpoints[0]
    #v2 = viewpoints[1]
    print('viewpoint', v)
    #print('viewpoint', v2)
    print('viewpoint x', v[0])
    print('viewpoint y', v[1])
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

    #v = i
    # index of this point in the numpy raster
    vi = vrow, vcol = d.index(v[0], v[1])
    print('vi in beginning loop',vi)
    #vi = vrow, vcol
    # This is the value of the centerpoint of the viewshed
    h = npi[vrow][vcol] + v[2]
    print('height',h)
    npvs[vrow,vcol] = 2 
    horizon_points = []
    output_list= []
    vi_list = []
    xy_lists = []
    for row in enumerate(npvs):
        row_i = row[0]
        for col in enumerate(row[1]):
            col_i = col[0]
            pt = x,y = d.xy(row_i,col_i)
            dist = distance(v,pt)
            if dist > (radius - cellsize) and dist < radius:
                #npvs[row_i,col_i] = 1
                horizon_point = (row_i, col_i)
                horizon_points.append(horizon_point)
                vi_list.append(vi)
                output,_ = Bresenham_with_rasterio(d,vi,horizon_point)
                #print(output)
                output_list.append(output)
                    
                slope_last = [-100]
                xy_list = []
                count = 0
                for point in output:
                    #print(output)
                    count += 1
                    cell_pt = cx, cy = point[0], point[1]
                    #print(cx,cy)
                    npvs[cx][cy] = count
                    #xy_list.append(cell_pt)
                    #print(slope_last[-1])
                    #print(x, y)
                    cell_cx, cell_cy = d.xy(cx, cy)
                    #npvs[cx,cy] = 1
                    slope_curr, dist_x = slope(d,v,h,cell_pt,npi[cx][cy])
                    y_curr = tangent_curr(slope_last[-1],dist_x,h)
                    #print(y_curr)
                    #dont use now t_curr = slope(d,v,h,cell_pt,npi[x][y])
                    '''
                    if npi[cx][cy] < y_curr:                      
                        npvs[cx,cy] = 0
                    elif npi[cx][cy] >= y_curr:
                        npvs[cx,cy] = 1
                        #a_curr,_ = slope(d,v,h,cell_pt,npi[cx][cy])
                        slope_last.append(slope_curr)
                    '''
                #xy_lists.append(xy_list)

    '''            
    for i in range(0,2):
        print('horizon points', horizon_points[i])
        print('output list', output_list[i])
        print('vi',vi_list[i])
        print('xy in output', xy_lists[i])
    '''

    '''
    for i in viewpoints:
        v = i
        # index of this point in the numpy raster
        vi = vrow, vcol = d.index(v[0], v[1])
        print('vi in beginning loop',vi)
        #vi = vrow, vcol
        # This is the value of the centerpoint of the viewshed
        h = npi[vrow][vcol] + v[2]
        print('height',h)
        npvs[vrow,vcol] = 2 
        horizon_points = []
        output_list= []
        vi_list = []
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
                    #print(output)
                    output_list.append(output)
                     
                    slope_last = [-100]
                    
                    for point in output:
                        #print(output)
                        cell_pt = x, y = point[0], point[1]
                        #print(x, y)
                        dx,_ = d.xy(x, y)
                        _, dist_x = slope(d,v,h,cell_pt,npi[x][y])
                        y_curr = tangent_curr(slope_last[-1],dist_x,h)
                        #print(y_curr)
                        #dont use now t_curr = slope(d,v,h,cell_pt,npi[x][y])
                        if npi[x][y] < y_curr:                      
                            npvs[x,y] = 0
                        elif npi[x][y] >= y_curr:
                            npvs[x,y] = 1
                            a_curr,_ = slope(d,v,h,cell_pt,npi[x][y])
                            slope_last.append(a_curr)
                    #print(slope_last)
    
        npvs[vrow,vcol] = 2
                
    print('length horizon points',len(horizon_points))

    
    vt = viewpoints[0]
    vti = vtrow, vtcol = d.index(vt[0], vt[1])
    print('vti', vti)
    test_line1,test_re1 = Bresenham_with_rasterio(d,vti,horizon_points[0])
    test_line2,test_re2 = Bresenham_with_rasterio(d,vti,horizon_points[13])
    test_line3,test_re3 = Bresenham_with_rasterio(d,vti,horizon_points[177])
    test_line4,test_re4 = Bresenham_with_rasterio(d,vti,horizon_points[180])
    print(test_line1)
    print(test_line2)
    print(test_line3)
    print(test_line4)
    print('horizon point 0',horizon_points[0])
    print('horizon point 13',horizon_points[13])
    print('horizon point 177',horizon_points[177])
    print('horizon point 180',horizon_points[180])
    print('vti', vti)
    cell_walk = v[0], v[1]+cellsize
    print('cell_walk coordinates',cell_walk)
    cell_walk_i = d.index(cell_walk[0], cell_walk[1])
    print('cell walk indices', cell_walk_i)
    print('dataset corresponding indices for cell walk coordinates: ', d.index(cell_walk[0],cell_walk[1]))
    #print(cell_walk in test_line)
    #npvs[341,320] = 2
    print('output list', output_list[0])
    print('output list', output_list[1])
    #print([340, 320] in output_list[0])
    
    for i in range(0,2):
        print('horizon points', horizon_points[i])
        print('output list', output_list[i])
        print('vi',vi_list[i])
    '''
    print('first vi',vi_list[0])
    print('flast vi',vi_list[-1])
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
    '''
    with rasterio.open('test_re1.tif', 'w', 
                    driver='GTiff', 
                    height=npi.shape[0],
                    width=npi.shape[1], 
                    count=1, 
                    dtype=rasterio.uint8,
                    crs=d.crs, 
                    transform=d.transform) as dst:
        dst.write(test_re1.astype(rasterio.uint8), 1)
    
    with rasterio.open('test_re2.tif', 'w', 
                    driver='GTiff', 
                    height=npi.shape[0],
                    width=npi.shape[1], 
                    count=1, 
                    dtype=rasterio.uint8,
                    crs=d.crs, 
                    transform=d.transform) as dst:
        dst.write(test_re2.astype(rasterio.uint8), 1)

    with rasterio.open('test_re3.tif', 'w', 
                    driver='GTiff', 
                    height=npi.shape[0],
                    width=npi.shape[1], 
                    count=1, 
                    dtype=rasterio.uint8,
                    crs=d.crs, 
                    transform=d.transform) as dst:
        dst.write(test_re3.astype(rasterio.uint8), 1)
    
    with rasterio.open('test_re4.tif', 'w', 
                    driver='GTiff', 
                    height=npi.shape[0],
                    width=npi.shape[1], 
                    count=1, 
                    dtype=rasterio.uint8,
                    crs=d.crs, 
                    transform=d.transform) as dst:
        dst.write(test_re4.astype(rasterio.uint8), 1)
    '''

    print("Viewshed file written to '%s'" % output_file)








