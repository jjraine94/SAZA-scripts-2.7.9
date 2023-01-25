def InROI(file, Coordinates, TMin, TMax):
    from matplotlib import path
    import numpy as np
    from scipy import spatial as sp

    K = sp.ConvexHull(Coordinates).vertices
    K = np.append(K, K[0])
    XVert = Coordinates[K,0]
    YVert = Coordinates[K,1]
    XY = np.stack((XVert, YVert), axis=1)

    data_in = [0]*len(file['T'])
    data_out = [0]*len(file['T'])
    for i in range(len(file['X'])):
        # is it in the prescribed interval
        if i >= TMin and i <= TMax:
            p = path.Path(XY)
            if p.contains_points([(file['X'][i], file['Y'][i])]):
                data_in[i]=1
            else:
                data_out[i]=1

    for i, number in enumerate(data_in):
        data_in[i] = number > 0
    for i, number in enumerate(data_out):
        data_out[i] = number > 0
    return data_in, data_out

