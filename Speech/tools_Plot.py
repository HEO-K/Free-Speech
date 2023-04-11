# %%
import numpy as np
import matplotlib.pyplot as plt


def timeseries_with_error(data, label=False, color="C0", fill=False, linewidth=1):
    """ Error 범위 timeseries plot
    
    Args:
        data (array): (time, n) 2d array
        label (str, optional): data's label, Defaults to False
        color (str, optional): color, Defaults to 'C0'
        fill (bool, optional): 에러 표시 방법, 직선 표시 vs 채우기
    """
    from scipy.stats import sem
    means = np.nanmean(data, axis=1)
    error = sem(data, axis=1)
    if fill:
        plt.plot(means, c=color, label=label, linewidth=linewidth)
        plt.fill_between(np.arange(data.shape[0]), means+error, 
                            means-error, alpha=0.1, color=color)
    else:
        plt.errorbar(np.arange(0,data.shape[0]), means, c=color, label=label, yerr=error)
    return


def mni_surface_plot(data, voxel="3.0", **kwargs):
    """ MNI surface plot, WSL의 경우 cortex.webshow, 윈도우의 경우 nilearn.view_img_on_surf의 브라우저
    
    Args:
        data (array): (x,y,z) 또는 (n,x,y,z) 데이터
        voxel (str, optional): 복셀 크기(mm), Defaults to '3.0'
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
        cortex.webshow(ex)
    
    else:
        from . import tools_EPI
        from nilearn.plotting import view_img_on_surf
        from nltools.data import Brain_Data
        
        data = tools_EPI.data_to_MNI_nltools(data, voxel_size = voxel)
        plot_data = view_img_on_surf(data.to_nifti(), 
                                     **kwargs)
        plot_data.open_in_browser()
        
        
        
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
                        **({"data": data} if data is not None else {}), **kwargs)
        ax.view_init(view_angle[0], view_angle[1])
    else:
        f = ax.scatter(np.where(mask)[0], 
                    np.where(mask)[1],
                    np.where(mask)[2],
                    c = data[mask],
                        **({"data": data} if data is not None else {}), **kwargs)
        ax.view_init(view_angle[0], view_angle[1]) 
        
    return(ax)



def plot_roi(atlas_name, rois, rgba, **kwargs):
    """ roi를 pycortex로 원하는 색으로 plot
    
    Args:
        atlas_name (str): atlas 이름 
            - "Brainnetome"
            - "Schaefer2018_<N>Parcels_<7/17>Networks"
            - "Yeo2011_<7/17>Networks"
        rois (double list): roi 번호 ex) [roi1:[101,102], roi2:[201,202]...]
        rgba (double list): RGBA 값 (0~255) ex) [roi1:[r,g,b,a], roi2:[r,g,b,a]...]
        **kwargs: cortex.Volume 변수들
        
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
            
    red = cortex.Volume(r_map.transpose(2,1,0),"cvs_avg35_inMNI152", 'mni_3mm')
    green = cortex.Volume(g_map.transpose(2,1,0),"cvs_avg35_inMNI152", 'mni_3mm')
    blue = cortex.Volume(b_map.transpose(2,1,0),"cvs_avg35_inMNI152", 'mni_3mm')
    vol_data = cortex.VolumeRGB(red, green, blue, "cvs_avg35_inMNI152", 'mni_3mm', 
                                alpha=a_map.transpose(2,1,0), **kwargs)
    
    cortex.webshow(vol_data)
# %%
