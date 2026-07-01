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
                           "mni152_asym_09c", transform_name,
                           **kwargs)
        viewer = cortex.webgl.show(ex)
        viewer.get_view("mni152_asym_09c", view)
        return viewer


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
                           "mni152_asym_09c", transform_name,
                           **kwargs)
        viewer = cortex.webgl.show(ex)
        viewer.get_view("mni152_asym_09c", view)
        return viewer
    
    else:
        raise OSError("You must change to WSL environment")



def mni_to_fsaverage(data, voxel="3.0",  **kwargs):
    from Speech.tools import isWSL
    from scipy.sparse import csr_matrix
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
        ex = cortex.Volume(data, "mni152_asym_09c", transform_name)
        mapper = cortex.get_mapper("mni152_asym_09c", transform_name, 'nearest')
        vertex_map = mapper(ex)
        mats = cortex.db.get_mri_surf2surf_matrix(subject="mni152_asym_09c",
                                            surface_type='inflated',
                                            target_subj='fsaverage')
        left_transform = csr_matrix(mats[0])
        right_transform = csr_matrix(mats[1])
        vertex_map_fs_left = left_transform.dot(vertex_map.left)
        vertex_map_fs_right = right_transform.dot(vertex_map.right)
        vertex_map_fs = np.concatenate([vertex_map_fs_left, vertex_map_fs_right])
        alpha_maps = np.zeros(len(vertex_map_fs))
        alpha_maps[~np.isnan(vertex_map_fs)] = 1
        vertex_data = cortex.Vertex(vertex_map_fs, 'fsaverage', **kwargs)
        vertex_data = vertex_data.blend_curvature(alpha_maps, brightness=0.00, contrast=0.001, smooth=20)
    return(vertex_data)





def mni_surface_fsaverage_plot(data, voxel="3.0", view="lateral", **kwargs):
    from Speech.tools import isWSL
    from scipy.sparse import csr_matrix
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
        ex = cortex.Volume(data, "mni152_asym_09c", transform_name)
        mapper = cortex.get_mapper("mni152_asym_09c", transform_name, 'nearest')
        vertex_map = mapper(ex)
        mats = cortex.db.get_mri_surf2surf_matrix(subject="mni152_asym_09c",
                                            surface_type='inflated',
                                            target_subj='fsaverage')
        left_transform = csr_matrix(mats[0])
        right_transform = csr_matrix(mats[1])
        vertex_map_fs_left = left_transform.dot(vertex_map.left)
        vertex_map_fs_right = right_transform.dot(vertex_map.right)
        vertex_map_fs = np.concatenate([vertex_map_fs_left, vertex_map_fs_right])
        alpha_maps = np.zeros(len(vertex_map_fs))
        alpha_maps[~np.isnan(vertex_map_fs)] = 1
        vertex_data = cortex.Vertex(vertex_map_fs, 'fsaverage', **kwargs)
        vertex_data = vertex_data.blend_curvature(alpha_maps, brightness=0.00, contrast=0.001, smooth=20)
        viewer = cortex.webgl.show(vertex_data)
        # viewer.get_view("fsaverage", view)
        return viewer
        
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
                        "mni152_asym_09c", transform_name,
                        **kwargs)
        
        import os
        if filename=="now":
            from datetime import datetime
            img_base =  datetime.today().strftime("%Y%m%d-%H%M%S")
        else:
            img_base = filename
        
        viewer = cortex.webgl.show(ex)
        if view=="both":
            viewer.get_view("mni152_asym_09c","lateral")
            img_name = os.path.join(path, img_base+"_lateral.png")
            viewer.getImage(img_name)
            viewer.get_view("mni152_asym_09c", "medial")
            img_name = os.path.join(path, img_base+"_medial.png")
            viewer.getImage(img_name)   
        else:
            viewer.get_view("mni152_asym_09c",view)     
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



def plot_roi(atlas_name, rois, rgba, voxel="3.0", view="lateral", surface='mni', **kwargs):
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
    
    transform_name = 'mni_'+str(voxel)+"mm"
            
    red = cortex.Volume(r_map.transpose(2,1,0),"mni152_asym_09c", transform_name)
    green = cortex.Volume(g_map.transpose(2,1,0),"mni152_asym_09c", transform_name)
    blue = cortex.Volume(b_map.transpose(2,1,0),"mni152_asym_09c", transform_name)
    
    
    # cortex.webshow(vol_data)
    if surface == 'mni':
        vol_data = cortex.VolumeRGB(red, green, blue, "mni152_asym_09c", transform_name,
                            alpha=a_map.transpose(2,1,0), **kwargs)
        viewer = cortex.webgl.show(vol_data)
        viewer.get_view("mni152_asym_09c", view)
    elif surface == 'fsaverage':
        from scipy.sparse import csr_matrix
        mapper = cortex.get_mapper("mni152_asym_09c", transform_name, 'nearest')
        vertex_r = mapper(red)
        vertex_g = mapper(green)
        vertex_b = mapper(blue)
        vol_a = cortex.Volume(a_map.transpose(2,1,0), "mni152_asym_09c", transform_name)
        vertex_a = mapper(vol_a)
        mats = cortex.db.get_mri_surf2surf_matrix(subject="mni152_asym_09c",
                                            surface_type='inflated',
                                            target_subj='fsaverage')
        left_transform = csr_matrix(mats[0])
        right_transform = csr_matrix(mats[1])
        
        vertex_r_fs = np.concatenate([left_transform.dot(vertex_r.left),
                                   right_transform.dot(vertex_r.right)])
        vertex_g_fs = np.concatenate([left_transform.dot(vertex_g.left),
                                   right_transform.dot(vertex_g.right)])
        vertex_b_fs = np.concatenate([left_transform.dot(vertex_b.left),
                                   right_transform.dot(vertex_b.right)])
        vertex_a_fs = np.concatenate([left_transform.dot(vertex_a.left),
                                   right_transform.dot(vertex_a.right)])       
        
        vertex_data = cortex.VertexRGB(vertex_r_fs, vertex_g_fs, vertex_b_fs, 'fsaverage', 
                                       alpha = vertex_a_fs, **kwargs)
        viewer = cortex.webgl.show(vertex_data)
        viewer.get_view("fsaverage", view)
        return viewer
  
    
def plot_fsaverage_atlas(atlas_name, data, view="lateral", **kwargs):
    """ fsaverage atlas plot
    
    Args:
        atlas_name (str): atlas 이름 
            - "Schaefer2018_<N>Parcels_<7/17>Networks"
            - "Yeo2011_<7/17>Networks"
        data (dictionary): [index: plot_data] dictionary, 없는 index는 투명으로 표시
        view (str, optional): pycortex view, lateral or medial
        **kwargs: cortex.Vertex parameters
        
    Returns:
        pycortex volume data
    """
    
    from nibabel.freesurfer.io import read_annot
    import cortex
    from Speech.tools import isWSL
    if isWSL():
        labels = []
        if "Yeo2011" in atlas_name:
            annot_file = f"/mnt/d/Functions/pycortex/db/fsaverage/label/lh.{atlas_name}_N1000.annot"
            labels.append(read_annot(annot_file)[0])
            annot_file = f"/mnt/d/Functions/pycortex/db/fsaverage/label/rh.{atlas_name}_N1000.annot"
            labels.append(read_annot(annot_file)[0])
        else:
            annot_file = f"/mnt/d/Functions/pycortex/db/fsaverage/label/lh.{atlas_name}_order.annot"
            labels.append(read_annot(annot_file)[0])
            annot_file = f"/mnt/d/Functions/pycortex/db/fsaverage/label/rh.{atlas_name}_order.annot"
            labels.append(read_annot(annot_file)[0]+np.max(labels)*(read_annot(annot_file)[0] > 0.1))
        labels = np.array(labels).flatten()
        
        if isinstance(data[list(data.keys())[0]].item(), (int, float)):
            plotting_data = np.zeros_like(labels).astype(float)
            plotting_data[:] = np.nan
            for k in data.keys():
                k = int(k)
                plotting_data[labels==k] = data[k]
            alpha_map = np.ones_like(plotting_data)
            alpha_map[np.isnan(plotting_data)] = 0
            vertex_data = cortex.Vertex(plotting_data, 'fsaverage', **kwargs)
            vertex_data = vertex_data.blend_curvature(alpha=alpha_map, threshold=0.5, brightness=0)
        else:
            r_map = np.zeros_like(labels).astype(np.uint8)
            g_map = np.zeros_like(labels).astype(np.uint8)
            b_map = np.zeros_like(labels).astype(np.uint8)
            a_map = np.zeros_like(labels).astype(np.uint8)
            for k in data.keys():
                k = int(k)
                color = data[k]
                if isinstance(color[0],(float)): color = color*255
                r_map[labels==k] = color[0]
                g_map[labels==k] = color[1]
                b_map[labels==k] = color[2]
                try:
                    a_map[labels==k] = color[3]
                except:
                    a_map[labels==k] = 255
            vertex_data = cortex.VertexRGB(r_map, g_map, b_map, 'fsaverage', alpha=a_map, **kwargs)
        viewer = cortex.webgl.show(vertex_data)
        return viewer
    else:
        raise OSError("You must change to WSL environment")
    
    

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


def plot_star(p, x, y, plot_dagger=False, ax=None, plot_ns=False, **kwargs):
    final_kwargs = {
        'ha': 'center',
        'fontdict': {'font': 'DejaVu Sans', 'size': 9}
    }
    if 'fontsize' in kwargs:
        if 'fontdict' not in kwargs: kwargs['fontdict'] = {'font': 'DejaVu Sans'}
        kwargs['fontdict']['size'] = kwargs.pop('fontsize')
    for key, value in kwargs.items():
        if isinstance(value, dict) and isinstance(final_kwargs.get(key), dict):
            final_kwargs[key].update(value)
        else:
            final_kwargs[key] = value 
    if ax==None:
        if p<0.001: plt.text(x, y, "***", **final_kwargs)
        elif p<0.01: plt.text(x, y, "**", **final_kwargs)
        elif p<0.05: plt.text(x, y, "*", **final_kwargs)
        elif p<0.1:
            if plot_dagger: plt.text(x, y, "†", **final_kwargs)
        else:
            if plot_ns: 
                final_kwargs.update({'va':'bottom'})
                final_kwargs.update({'fontdict': {'font': 'Helvetica', 'size': 8}})
                plt.text(x, y, "$\mathit{n.s.}$", **final_kwargs)
    else:
        if p<0.001: ax.text(x, y, "***", **final_kwargs)
        elif p<0.01: ax.text(x, y, "**", **final_kwargs)
        elif p<0.05: ax.text(x, y, "*", **final_kwargs)
        elif p<0.1:
            if plot_dagger: ax.text(x, y, "†", **final_kwargs)
        else:
            if plot_ns: 
                final_kwargs.update({'va':'bottom'})
                final_kwargs.update({'fontdict': {'font': 'Helvetica', 'size': 8}})
                ax.text(x, y, "$\mathit{n.s.}$", **final_kwargs)
        
        
def medbrain_surface_plot(data, **kwargs):
    """medbrain surface plot
    
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
        ex = cortex.Volume(data, 
                           "MEBRAIN", "MK",
                           **kwargs)
        viewer = cortex.webgl.show(ex)
        return viewer
    
def _adjust_hue(h, h_ref):
    """2D HSL 보간을 위해 기준 색조(h_ref)와의 최단 경로로 색조(h)를 조정합니다."""
    diff = h - h_ref
    if diff > 0.5:
        h -= 1.0
    elif diff < -0.5:
        h += 1.0
    return h


def _make_1d_gradient(colors, method, width=256):
    import colorsys
    """1x256 선형 그라데이션 이미지를 생성합니다."""
    # c1: 우측, c2: 좌측 -> 보간 방향: c2에서 c1으로
    c2, c1 = colors 
    
    if method == "RGB":
        gradient = np.linspace(c2, c1, width)
    
    elif method == "HSL":
        c1_hls = colorsys.rgb_to_hls(*c1)
        c2_hls = colorsys.rgb_to_hls(*c2)
        
        h1, l1, s1 = c1_hls
        h2, l2, s2 = c2_hls
        
        # 색조 최단 경로 보간
        diff = h1 - h2
        if diff > 0.5: h1 -= 1.0
        elif diff < -0.5: h1 += 1.0
            
        h_grad = np.linspace(h2, h1, width) % 1.0 # 0-1 범위로 래핑
        l_grad = np.linspace(l2, l1, width)
        s_grad = np.linspace(s2, s1, width)
        
        rgb_gradient = []
        for i in range(width):
            rgb_gradient.append(colorsys.hls_to_rgb(h_grad[i], l_grad[i], s_grad[i]))
        gradient = np.array(rgb_gradient)
        
    else:
        raise ValueError("Method는 'RGB' 또는 'HSL'이어야 합니다.")
        
    # (1, 256, 3) 형태로 변환
    return gradient[np.newaxis, :, :]

def _make_2d_gradient(colors, method, size=256):
    from scipy.interpolate import RegularGridInterpolator
    import colorsys
    """256x256 2D 그라데이션 이미지를 생성합니다."""
    # c1: 1사(우상), c2: 2사(좌상), c3: 3사(좌하), c4: 4사(우하)
    c1, c2, c3, c4 = colors
    
    # 보간을 위한 좌표 설정
    y_coords = np.array([0, 1]) # 0: 상단, 1: 하단
    x_coords = np.array([0, 1]) # 0: 좌측, 1: 우측
    
    x_new = np.linspace(0, 1, size)
    y_new = np.linspace(0, 1, size)
    yy, xx = np.meshgrid(y_new, x_new, indexing='ij')
    points_to_interpolate = np.stack([yy, xx], axis=-1)
    
    if method == "RGB":
        
        # 각 채널별 2x2 코너 매트릭스
        R = np.array([[c2[0], c1[0]], [c3[0], c4[0]]]) # [[좌상, 우상], [좌하, 우하]]
        G = np.array([[c2[1], c1[1]], [c3[1], c4[1]]])
        B = np.array([[c2[2], c1[2]], [c3[2], c4[2]]])
        
        f_R = RegularGridInterpolator((y_coords, x_coords), R, method='linear')
        f_G = RegularGridInterpolator((y_coords, x_coords), G, method='linear')
        f_B = RegularGridInterpolator((y_coords, x_coords), B, method='linear')
        
        R_interp = f_R(points_to_interpolate)
        G_interp = f_G(points_to_interpolate)
        B_interp = f_B(points_to_interpolate)
        
        return np.stack([R_interp, G_interp, B_interp], axis=-1)
    
    elif method == "HSL":
        # 4개 코너를 HLS로 변환
        c1_hls, c2_hls, c3_hls, c4_hls = [colorsys.rgb_to_hls(*c) for c in colors]
        
        # c2(좌상)를 기준으로 Hue 조정
        h_ref = c2_hls[0]
        h1 = _adjust_hue(c1_hls[0], h_ref)
        h2 = h_ref
        h3 = _adjust_hue(c3_hls[0], h_ref)
        h4 = _adjust_hue(c4_hls[0], h_ref)
        
        # H, L, S 채널별 2x2 코너 매트릭스
        H = np.array([[h2, h1], [h3, h4]])
        L = np.array([[c2_hls[1], c1_hls[1]], [c3_hls[1], c4_hls[1]]])
        S = np.array([[c2_hls[2], c1_hls[2]], [c3_hls[2], c4_hls[2]]])

        f_H = RegularGridInterpolator((y_coords, x_coords), H, method='linear')
        f_L = RegularGridInterpolator((y_coords, x_coords), L, method='linear')
        f_S = RegularGridInterpolator((y_coords, x_coords), S, method='linear')

        H_interp = f_H(points_to_interpolate) % 1.0 # 0-1 래핑
        L_interp = f_L(points_to_interpolate)
        S_interp = f_S(points_to_interpolate)
        
        # HLS -> RGB 변환 (벡터화가 안되므로 픽셀별 처리)
        image_data = np.zeros((size, size, 3))
        for i in range(size):
            for j in range(size):
                image_data[i, j, :] = colorsys.hls_to_rgb(H_interp[i, j], L_interp[i, j], S_interp[i, j])
        return image_data
        
    else:
        raise ValueError("Method는 'RGB' 또는 'HSL'이어야 합니다.")

def make_colormap(colors, save_path, method="RGB", save=True):
    """
    주어진 색상 리스트로 1D 또는 2D 컬러맵 이미지를 생성하고 저장합니다.

    Args:
        colors (list): 2개 또는 4개의 색상 요소. 
                       (예: "#FF0000", (255,0,0), (1.0, 0, 0))
        save_path (str): 이미지를 저장할 경로.
        method (str, optional): 보간 방법. "RGB" (기본값) 또는 "HSL".
    """
    from .tools import to_rgb_01

    # 1. 모든 색상 입력을 0-1 RGB로 정규화
    normalized_colors = [to_rgb_01(c) for c in colors]
    
    # 2. 색상 개수에 따라 1D 또는 2D 그라데이션 생성
    if len(normalized_colors) == 2:
        image_data = _make_1d_gradient(normalized_colors, method)
    elif len(normalized_colors) == 4:
        image_data = _make_2d_gradient(normalized_colors, method)
    else:
        raise ValueError("colors 리스트는 2개 또는 4개의 요소만 지원합니다.")
        
    # 3. 0-1 float 이미지를 0-255 uint8로 스케일링
    image_final = np.clip(image_data * 255, 0, 255).astype(np.uint8)
    
    # 4. 이미지 저장
    if save:
        plt.imsave(save_path, image_final)
        print(f"Save to {save_path}")
    else: return(image_final)




def plot_mask(masks, rgba, voxel="3.0", surface="mni", view="lateral", **kwargs):
    """ Overlay multiple masks
    
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
    
    if len(masks.shape) != 4:
        masks = np.array([masks])
        if len(masks.shape) != 4:
            raise Exception("Mask should be list of 3d array")
            
    transform_name = 'mni_' + str(voxel) + "mm"
    
    # ====================================================
    # 1. Volume 렌더링 (surface == 'mni')
    # ====================================================
    if surface == 'mni':
        colormap = np.zeros((4, masks.shape[1], masks.shape[2], masks.shape[3]))
        
        for mask, color in tqdm(zip(masks, rgba), desc="Adding volume masks"):
            mask = mask.astype(int)
            new_mask = np.zeros_like(colormap)
            new_mask[0, mask == 1] = color[0]
            new_mask[1, mask == 1] = color[1]
            new_mask[2, mask == 1] = color[2]
            new_mask[3, mask == 1] = color[3]
            
            base_a = colormap[3,:,:,:] / 255.0
            new_a = new_mask[3,:,:,:] / 255.0
            
            sums = base_a + new_a
            
            # RuntimeWarning(0으로 나누기) 방지를 위한 안전한 처리
            ratio = np.zeros_like(base_a)
            valid = sums > 0
            ratio[valid] = base_a[valid] / sums[valid]
            ratio[~valid] = 0.5
            
            sum_r = (colormap[0,:,:,:] * ratio + new_mask[0,:,:,:] * (1 - ratio))
            sum_g = (colormap[1,:,:,:] * ratio + new_mask[1,:,:,:] * (1 - ratio))
            sum_b = (colormap[2,:,:,:] * ratio + new_mask[2,:,:,:] * (1 - ratio))
            sum_a = 1.0 - (1.0 - base_a) * (1.0 - new_a)
            sum_a = sum_a * 255.0
            
            colormap = np.array([sum_r, sum_g, sum_b, sum_a])
            colormap[colormap > 255] = 255
            
        r_map = colormap[0,:,:,:].astype(np.uint8)
        g_map = colormap[1,:,:,:].astype(np.uint8)
        b_map = colormap[2,:,:,:].astype(np.uint8)
        a_map = colormap[3,:,:,:].astype(np.uint8)
        
        red = cortex.Volume(r_map.transpose(2,1,0), "mni152_asym_09c", transform_name)
        green = cortex.Volume(g_map.transpose(2,1,0), "mni152_asym_09c", transform_name)
        blue = cortex.Volume(b_map.transpose(2,1,0), "mni152_asym_09c", transform_name)
        
        vol_data = cortex.VolumeRGB(red, green, blue, "mni152_asym_09c", transform_name,
                                    alpha=a_map.transpose(2,1,0), **kwargs)
        viewer = cortex.webgl.show(vol_data)
        viewer.get_view("mni152_asym_09c", view)
        return viewer

    # ====================================================
    # 2. Surface 렌더링 (surface == 'fsaverage')
    # ====================================================
    elif surface == 'fsaverage':
        from scipy.sparse import csr_matrix
        
        mapper = cortex.get_mapper("mni152_asym_09c", transform_name, 'nearest')
        mats = cortex.db.get_mri_surf2surf_matrix(subject="mni152_asym_09c",
                                                  surface_type='inflated',
                                                  target_subj='fsaverage')
        left_transform = csr_matrix(mats[0])
        right_transform = csr_matrix(mats[1])
        
        # fsaverage 표면의 총 정점(Vertex) 개수 확인
        total_vertices = left_transform.shape[0] + right_transform.shape[0]
        
        # 정점 배열을 위한 빈 컬러맵 (4 x total_vertices) 생성
        vertex_colormap = np.zeros((4, total_vertices), dtype=float)
        
        for mask, color in tqdm(zip(masks, rgba), desc="Mapping & Coloring fsaverage"):
            # a. 볼륨 마스크(0과 1) 자체를 먼저 mni -> fsaverage로 매핑합니다.
            transposed_mask = mask.transpose(2, 1, 0).astype(float)
            vol_mask = cortex.Volume(transposed_mask, "mni152_asym_09c", transform_name)
            mapped_mask = mapper(vol_mask)
            
            mask_left_fs = left_transform.dot(mapped_mask.left)
            mask_right_fs = right_transform.dot(mapped_mask.right)
            mask_fs = np.concatenate([mask_left_fs, mask_right_fs])
            
            # b. [핵심] 보간되어 흐릿해진 경계를 0.5를 기준으로 칼같이 잘라서 완벽한 이진(Binary) 마스크로 만듭니다.
            binary_mask_fs = (mask_fs > 0.5).astype(float)
            
            # c. 잘라낸 마스크 위에 내가 원하는 색상(color)을 입힙니다.
            new_vertex_mask = np.zeros_like(vertex_colormap)
            new_vertex_mask[0, binary_mask_fs == 1] = color[0]
            new_vertex_mask[1, binary_mask_fs == 1] = color[1]
            new_vertex_mask[2, binary_mask_fs == 1] = color[2]
            new_vertex_mask[3, binary_mask_fs == 1] = color[3]
            
            # d. 겹치는 부위의 알파 블렌딩 처리 (1D Vertex 기준)
            base_a = vertex_colormap[3, :] / 255.0
            new_a = new_vertex_mask[3, :] / 255.0
            
            sums = base_a + new_a
            
            ratio = np.zeros_like(base_a)
            valid = sums > 0
            ratio[valid] = base_a[valid] / sums[valid]
            ratio[~valid] = 0.5
            
            sum_r = vertex_colormap[0, :] * ratio + new_vertex_mask[0, :] * (1 - ratio)
            sum_g = vertex_colormap[1, :] * ratio + new_vertex_mask[1, :] * (1 - ratio)
            sum_b = vertex_colormap[2, :] * ratio + new_vertex_mask[2, :] * (1 - ratio)
            sum_a = 1.0 - (1.0 - base_a) * (1.0 - new_a)
            sum_a = sum_a * 255.0
            
            vertex_colormap[0, :] = sum_r
            vertex_colormap[1, :] = sum_g
            vertex_colormap[2, :] = sum_b
            vertex_colormap[3, :] = sum_a
            
        # e. 최종 컬러맵 데이터 타입 보정
        vertex_colormap = np.clip(vertex_colormap, 0, 255).astype(np.uint8)
        
        # f. VertexRGB 객체 생성 및 반환
        vertex_data = cortex.VertexRGB(vertex_colormap[0], 
                                       vertex_colormap[1], 
                                       vertex_colormap[2], 
                                       'fsaverage', 
                                       alpha=vertex_colormap[3], 
                                       **kwargs)
        viewer = cortex.webgl.show(vertex_data)
        viewer.get_view("fsaverage", view)
        return viewer
    
    
def plot_RGBA(r_map, g_map, b_map, a_map, voxel="3.0", surface='mni', view='lateral', **kwargs):
    import cortex
    transform_name = 'mni_' + str(voxel) + "mm"
    red = cortex.Volume(r_map.transpose(2,1,0), "mni152_asym_09c", transform_name)
    green = cortex.Volume(g_map.transpose(2,1,0), "mni152_asym_09c", transform_name)
    blue = cortex.Volume(b_map.transpose(2,1,0), "mni152_asym_09c", transform_name)
    
    if surface == 'mni':
        vol_data = cortex.VolumeRGB(red, green, blue, "mni152_asym_09c", transform_name,
                                    alpha=a_map.transpose(2,1,0), **kwargs)
        viewer = cortex.webgl.show(vol_data)
        viewer.get_view("mni152_asym_09c", view)
        return viewer
    elif surface == 'fsaverage':
        from scipy.sparse import csr_matrix
        mapper = cortex.get_mapper("mni152_asym_09c", transform_name, 'nearest')
        vertex_r = mapper(red)
        vertex_g = mapper(green)
        vertex_b = mapper(blue)
        vol_a = cortex.Volume(a_map.transpose(2,1,0), "mni152_asym_09c", transform_name)
        vertex_a = mapper(vol_a)
        mats = cortex.db.get_mri_surf2surf_matrix(subject="mni152_asym_09c",
                                            surface_type='inflated',
                                            target_subj='fsaverage')
        left_transform = csr_matrix(mats[0])
        right_transform = csr_matrix(mats[1])
        
        vertex_r_fs = np.concatenate([left_transform.dot(vertex_r.left),
                                   right_transform.dot(vertex_r.right)])
        vertex_g_fs = np.concatenate([left_transform.dot(vertex_g.left),
                                   right_transform.dot(vertex_g.right)])
        vertex_b_fs = np.concatenate([left_transform.dot(vertex_b.left),
                                   right_transform.dot(vertex_b.right)])
        vertex_a_fs = np.concatenate([left_transform.dot(vertex_a.left),
                                   right_transform.dot(vertex_a.right)])       
        vertex_r_fs = np.clip(vertex_r_fs, 0, 255).astype(np.uint8)
        vertex_g_fs = np.clip(vertex_g_fs, 0, 255).astype(np.uint8)
        vertex_b_fs = np.clip(vertex_b_fs, 0, 255).astype(np.uint8)
        vertex_a_fs = np.clip(vertex_a_fs, 0, 255).astype(np.uint8)
        vertex_data = cortex.VertexRGB(vertex_r_fs, vertex_g_fs, vertex_b_fs, 'fsaverage', 
                                       alpha = vertex_a_fs, **kwargs)
        viewer = cortex.webgl.show(vertex_data)
        viewer.get_view("fsaverage", view)
        return viewer
  
# %%
