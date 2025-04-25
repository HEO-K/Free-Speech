# %%
import numpy as np
import matplotlib.pyplot as plt


def timeseries_with_error(data, x=None, label: str = False, color: any="C0", 
                          fill=True, linewidth=1, alpha=0.1, ax=None, **kwargs):
    """ Error 범위 timeseries plot
    
    Args
        data (array): (n, time) 2d array
        x (array, optional): data x축, Defaults to (0, length of data)
        label (str, optional): data's label, Defaults to True
        color (mpl.color, optional): color, Defaults to 'C0'
        fill (bool, optional): 에러 표시 방법, 직선 표시 vs 채우기
    """
    from scipy.stats import sem
    means = np.nanmean(data, axis=0)
    error = sem(data, axis=0)
    try:
        if len(x) != len(means): x = np.arange(data.shape[1])
    except: 
        x = np.arange(data.shape[1])
    
    if ax==None:
        if fill:
            plt.plot(x, means, c=color, label=label, linewidth=linewidth, **kwargs)
            plt.fill_between(x, means+error, means-error, alpha=alpha, color=color, **kwargs)
        else:
            plt.errorbar(x, means, c=color, label=label, yerr=error, linewidth=linewidth, **kwargs)
    else:
        if fill:
            ax.plot(x, means, c=color, label=label, linewidth=linewidth, **kwargs)
            ax.fill_between(x, means+error, means-error, alpha=alpha, color=color, **kwargs)
        else:
            ax.errorbar(x, means, c=color, label=label, yerr=error, linewidth=linewidth, **kwargs)

def mni_surface_plot(data, voxel="3.0", view="lateral", **kwargs):
    """ MNI surface plot, WSL의 경우 cortex.webshow, 윈도우의 경우 nilearn.view_img_on_surf의 브라우저
    
    Args:
        data (array): (x,y,z) 또는 (n,x,y,z) 데이터
        voxel (str, optional): 복셀 크기(mm), Defaults to '3.0'
        view (str, optional): pycortex view
        kwargs: cortex.Volume or nilearn.view_img_on_surf args
    """
    from Speech.tools import isWSL
    if isWSL():
        import cortex
        if len(data.shape) == 3:
            data = data.transpose(2,1,0)
        elif len(data.shape) == 4:
            data = data.transpose(0,3,2,1)
        else:
            print("Invalid data shape")
            return
        transform_name = 'mni_'+str(voxel)+"mm"
        ex = cortex.Volume(data, 
                           "cvs_avg35_inMNI152", transform_name,
                           **kwargs)
        viewer = cortex.webgl.show(ex)
        viewer.get_view("cvs_avg35_inMNI152", view)


def mni_surface_2dplot(data1, data2, voxel="3.0", view="lateral", **kwargs):
    """ MNI surface 2dplot
        
    Args:
        data1 (array): (x,y,z) 또는 (n,x,y,z) 데이터,
        data2 (array): (x,y,z) 또는 (n,x,y,z) 데이터
        voxel (str, optional): 복셀 크기(mm), Defaults to '3.0'
        view (str, optional): pycortex view
        kwargs: cortex.Volume or nilearn.view_img_on_surf args
    """
    from Speech.tools import isWSL
    if isWSL():
        import cortex
        if len(data1.shape) == 3:
            data1 = data1.transpose(2,1,0)
        elif len(data1.shape) == 4:
            data1 = data1.transpose(0,3,2,1)
        else:
            raise ValueError("Invalid data1 shape")

        if len(data2.shape) == 3:
            data2 = data2.transpose(2,1,0)
        elif len(data2.shape) == 4:
            data2 = data2.transpose(0,3,2,1)
        else:
            raise ValueError("Invalid data2 shape")

        transform_name = 'mni_'+str(voxel)+"mm"
        ex = cortex.Volume2D(data1, data2,
                           "cvs_avg35_inMNI152", transform_name,
                           **kwargs)
        viewer = cortex.webgl.show(ex)
        viewer.get_view("cvs_avg35_inMNI152", view)
    
    else:
        raise OSError("You must change to WSL environment")

def save_mni_img(data, view="both", voxel="3.0", filename='now',
                     path='/mnt/c/Users/Kwon/Downloads', **kwargs):
    """ Save pycortex image

    Args:
        data (array): 3d brain array, should be MNI
        view (str, optional): pycortex view ("lateral", "medial"). Defaults to "both".
        voxel (str, optional): MNI voxel size. Defaults to "3.0".
        filename (str, optional): Save image name (no extension). Defaults to 'now', current time.
        path (str, optional): Save path. Defaults to '/mnt/c/Users/Kwon/Downloads'.

    Raises:
        Exception: Raise error if it is not WSL environment.
    """
    
    from Speech.tools import isWSL
    if isWSL():
        import cortex
        if len(data.shape) == 3:
            data = data.transpose(2,1,0)
        elif len(data.shape) == 4:
            data = data.transpose(0,3,2,1)
        else:
            print("Invalid data shape")
            return
        transform_name = 'mni_'+str(voxel)+"mm"
        ex = cortex.Volume(data, 
                        "cvs_avg35_inMNI152", transform_name,
                        **kwargs)
        
        import os
        if filename=="now":
            from datetime import datetime
            img_base =  datetime.today().strftime("%Y%m%d-%H%M%S")
        else:
            img_base = filename
        
        viewer = cortex.webgl.show(ex)
        if view=="both":
            viewer.get_view("cvs_avg35_inMNI152","lateral")
            img_name = os.path.join(path, img_base+"_lateral.png")
            viewer.getImage(img_name)
            viewer.get_view("cvs_avg35_inMNI152", "medial")
            img_name = os.path.join(path, img_base+"_medial.png")
            viewer.getImage(img_name)   
        else:
            viewer.get_view("cvs_avg35_inMNI152",view)     
            img_name = os.path.join(path, img_base+f"_{view}.png")
            viewer.getImage(img_name)
    else:
        raise Exception("Not WSL environment")
                        
def plot_3d_render(mask, data, view_angle=[30,45], **kwargs):
    """ mask에 해당하는 복셀을 3d scatter plot
    
    Args:
        mask (bool array): (x,y,z) 의 bool array
        data (array): 플롯할 array, (x,y,z) or 1d
        view_angle (list, optional): 보여지는 각도 [z방향, xy방향], Defaults to [30,45]
        **kwargs: for plt.scatter 
        
    Returns:
        ax data
    """
    from mpl_toolkits.mplot3d import Axes3D
    plt.close()
    fig = plt.figure()
    ax = Axes3D(fig)
    if len(data.shape) == 1:
        f = ax.scatter(np.where(mask)[0], 
                    np.where(mask)[1],
                    np.where(mask)[2],
                    c = data,
                    **kwargs)
        ax.view_init(view_angle[0], view_angle[1])
    else:
        f = ax.scatter(np.where(mask)[0], 
                    np.where(mask)[1],
                    np.where(mask)[2],
                    c = data[mask],
                    **kwargs)
        ax.view_init(view_angle[0], view_angle[1]) 
        
    return(ax)



def plot_roi(atlas_name, rois, rgba, voxel="3.0", view="lateral", **kwargs):
    """ roi를 pycortex로 원하는 색으로 plot
    
    Args:
        atlas_name (str): atlas 이름 
            - "Brainnetome"
            - "Schaefer2018_<N>Parcels_<7/17>Networks"
            - "Yeo2011_<7/17>Networks"
        rois (double list): roi index ex) [roi1:[101,102], roi2:[201,202]...]
        rgba (double list): RGBA (0~255) ex) [roi1:[r,g,b,a], roi2:[r,g,b,a]...]
        voxel (str, optional): voxel size, default is "3.0"
        view (str, optional): pycortex view, lateral or medial
        **kwargs: cortex.Volume parameters
        
    Returns:
        pycortex volume data
    """
    
    from Speech.tools_EPI import get_atlas   
    import cortex
    
    atlas = get_atlas(atlas_name)[1]
    r_map = np.zeros(atlas.shape).astype(np.uint8)
    g_map = np.zeros(atlas.shape).astype(np.uint8)
    b_map = np.zeros(atlas.shape).astype(np.uint8)
    a_map = np.zeros(atlas.shape).astype(np.uint8)
    
    for roi, color in zip(rois, rgba):
        for r in roi:
            r_map[atlas==r] = color[0]
            g_map[atlas==r] = color[1]
            b_map[atlas==r] = color[2]
            a_map[atlas==r] = color[3]
            
    red = cortex.Volume(r_map.transpose(2,1,0),"cvs_avg35_inMNI152", f'mni_{voxel}mm')
    green = cortex.Volume(g_map.transpose(2,1,0),"cvs_avg35_inMNI152", f'mni_{voxel}mm')
    blue = cortex.Volume(b_map.transpose(2,1,0),"cvs_avg35_inMNI152", f'mni_{voxel}mm')
    vol_data = cortex.VolumeRGB(red, green, blue, "cvs_avg35_inMNI152", f'mni_{voxel}mm',
                                alpha=a_map.transpose(2,1,0), **kwargs)
    
    # cortex.webshow(vol_data)
    viewer = cortex.webgl.show(vol_data)
    viewer.get_view("cvs_avg35_inMNI152", view)   
    
    
    
         
def plot_mask(masks, rgba, voxel="3.0", **kwargs):
    """ Overay multiple masks
    
    Args:
        masks (list of 3d array): mask index list, it would be binary volume 
        rgba (list of colorcode): RGBA (0~255) ex) [roi1:[r,g,b,a], roi2:[r,g,b,a]...]
        voxel (str, optional): voxel size, default is "3.0"
        **kwargs: cortex.Volume parameters
        
    Returns:
        pycortex volume data
    """
    import cortex
    from tqdm import tqdm
    
                
        
    masks = np.array(masks)
    rgba = np.array(rgba)
    
    if len(masks.shape)!=4:
        masks = np.array([masks])
        if len(masks.shape)!=4:
            raise Exception("Mask sould be list of 3d array")
    
    colormap = np.zeros((4,masks.shape[1],masks.shape[2],masks.shape[3]))
    for mask, color in tqdm(zip(masks, rgba), "Adding masks"):
        mask = mask.astype(int)
        new_mask = np.zeros_like(colormap)
        new_mask[0,mask == 1] = color[0]
        new_mask[1,mask == 1] = color[1]
        new_mask[2,mask == 1] = color[2]
        new_mask[3,mask == 1] = color[3]

        
        base_a = colormap[3,:,:,:]/255
        new_a = new_mask[3,:,:,:]/255
        
        sums = base_a+new_a
        ratio = base_a/sums
        ratio[sums==0] = 0.5
        sum_r = (colormap[0,:,:,:]*ratio+new_mask[0,:,:,:]*(1-ratio)).astype(int)
        sum_g = (colormap[1,:,:,:]*ratio+new_mask[1,:,:,:]*(1-ratio)).astype(int)
        sum_b = (colormap[2,:,:,:]*ratio+new_mask[2,:,:,:]*(1-ratio)).astype(int)
        sum_a = 1-(1-base_a)*(1-new_a)
        sum_a = (sum_a*255).astype(int)
        colormap = np.array([sum_r, sum_g, sum_b, sum_a], int)
        colormap[colormap>255] = 255
        
        
    
    
    r_map = colormap[0,:,:,:].astype(np.uint8)
    g_map = colormap[1,:,:,:].astype(np.uint8)
    b_map = colormap[2,:,:,:].astype(np.uint8)
    a_map = colormap[3,:,:,:].astype(np.uint8)
    
    red = cortex.Volume(r_map.transpose(2,1,0),"cvs_avg35_inMNI152", f'mni_{voxel}mm')
    green = cortex.Volume(g_map.transpose(2,1,0),"cvs_avg35_inMNI152", f'mni_{voxel}mm')
    blue = cortex.Volume(b_map.transpose(2,1,0),"cvs_avg35_inMNI152", f'mni_{voxel}mm')
    vol_data = cortex.VolumeRGB(red, green, blue, "cvs_avg35_inMNI152", f'mni_{voxel}mm',
                                alpha=a_map.transpose(2,1,0), **kwargs)
    
    cortex.webshow(vol_data)   
    

def plot_corrmat_and_boundary(ax, data_matrix, bounds, patchset={}, is_corrmat=False, **kwargs):
    """ Plot correlaiton matrix & boundary patch

    Args:
        ax : matplotlib axis
        data_matrix (array): raw data. correlation is first axis
        bounds (lists of 1d list): boundaries, [[boundaries1], [boundaries2]] 
        patchset (dict, optional): mpl.patches params. Defaults to {}.
        is_corrmat (bool, optional): Is data correlation matrix. Defaults to False.
    """
    import matplotlib.patches as patches
    defaultwidth = 2
    defaultedgecolor = ["w", "r", "k", "b"]
    defaultfacecolor = "none"
    
    if is_corrmat:
        ax.imshow(data_matrix, **kwargs)
    else:
        ax.imshow(np.corrcoef(data_matrix.T), **kwargs)
    # plot the boundaries 
    bounds = list(bounds)
    
    if isinstance(bounds[0], list):
        for i in range(len(bounds)):
            bounds[i] = list(bounds[i])
            if 0 not in bounds[i]: bounds[i] = [0] + bounds[i]
            if data_matrix.shape[1] not in bounds[i]: bounds[i] = bounds[i] + [data_matrix.shape[1]]
            bounds[i].sort()            
  
            try: width = patchset[i]["linewidth"]
            except: width = defaultwidth

            try: edgecolor = patchset[i]["edgecolor"]
            except: edgecolor = defaultedgecolor[i%4]
            
            try: facecolor = patchset[i]["facecolor"]
            except: facecolor = defaultfacecolor         
            
            for n in range(len(bounds[i])-1):
                rect = patches.Rectangle(
                    (bounds[i][n],bounds[i][n]),
                    bounds[i][n+1]-bounds[i][n],
                    bounds[i][n+1]-bounds[i][n],
                    linewidth=width,edgecolor=edgecolor,facecolor=facecolor
                )
                ax.add_patch(rect)  
    
    else:
        if 0 not in bounds: bounds = [0] + bounds
        if data_matrix.shape[1] not in bounds: bounds = bounds + [data_matrix.shape[1]]
        bounds.sort()
        
        for i in range(len(bounds)-1):
            rect = patches.Rectangle(
                (bounds[i],bounds[i]),
                bounds[i+1]-bounds[i],
                bounds[i+1]-bounds[i],
                linewidth=defaultwidth,edgecolor=defaultedgecolor[0],facecolor=defaultfacecolor
            )
            ax.add_patch(rect)     
    

def plot_colorline(x, y, z=None, cmap='copper', **kwargs):
    import matplotlib.collections as mcoll
    # Default colors equally spaced on [0,1]:
    if z is None:
        z = np.linspace(0.0, 1.0, len(x))

    # Special case if a single number:
    # to check for numerical input -- this is a hack
    if not hasattr(z, "__iter__"):
        z = np.array([z])

    z = np.asarray(z)

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    lc = mcoll.LineCollection(segments, array=z, cmap=cmap, norm=plt.Normalize(0.0, 1.0), **kwargs)

    ax = plt.gca()
    ax.add_collection(lc)

    return lc


def plot_star(p, x, y, plot_dagger=False, **kwargs):
    if len(kwargs) == 0:
        kwargs = {'ha':'center', 'fontdict':{'font':'DejaVu Sans', 'size': 9}}
    if p<0.001: plt.text(x, y, "***", **kwargs)
    elif p<0.01: plt.text(x, y, "**", **kwargs)
    elif p<0.05: plt.text(x, y, "*", **kwargs)
    elif p<0.1:
        if plot_dagger: plt.text(x, y, "†", **kwargs)
# %%
