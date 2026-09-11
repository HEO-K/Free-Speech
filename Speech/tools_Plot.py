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
    import warnings
    data = np.asarray(data, dtype=float)
    # NaN 을 빼고 평균·SEM — scipy.stats.sem 은 NaN 이 하나라도 있으면 그 시점 오차가 NaN 이 돼
    # 띠가 비었다 (가변 길이 run 을 NaN 패딩한 경우). 유효 표본이 2 미만인 시점은 SEM 이 NaN.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        means = np.nanmean(data, axis=0)
        n = np.sum(~np.isnan(data), axis=0)
        error = np.nanstd(data, axis=0, ddof=1) / np.sqrt(n)
    if x is None or len(x) != len(means):
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

def _to_pycortex_volume(data):
    """(x,y,z) 또는 (n,x,y,z) → pycortex 가 받는 (z,y,x) 또는 (n,z,y,x)"""
    data = np.asarray(data)
    if data.ndim == 3:
        return data.transpose(2, 1, 0)
    if data.ndim == 4:
        return data.transpose(0, 3, 2, 1)
    raise ValueError("data 는 (x,y,z) 또는 (n,x,y,z) 여야 한다")


def mni_surface_plot(data, voxel="3.0", view="lateral", **kwargs):
    """ MNI surface plot. WSL 은 pycortex webgl 뷰어, Windows 는 surfplot 정적 그림

    Args:
        data (array): (x,y,z) 또는 (n,x,y,z) 데이터. transpose 하지 말고 그대로 (Windows 는 3D 만)
        voxel (str, optional): 복셀 크기(mm), Defaults to '3.0'
        view (str, optional): 'lateral' · 'medial' · 'both'(Windows 격자)
        kwargs: cortex.Volume 인자 (cmap · vmin · vmax …). Windows 에서는
            tools_Surface.plot_volume 인자 (sulc · zoom · cbar_label · mapper · size …) 도 받는다

    Returns:
        WSL: pycortex viewer / Windows: matplotlib Figure
    """
    from Speech.tools import isWSL
    if isWSL():
        import cortex
        transform_name = 'mni_'+str(voxel)+"mm"
        ex = cortex.Volume(_to_pycortex_volume(data),
                           "mni152_asym_09c", transform_name,
                           **kwargs)
        viewer = cortex.webgl.show(ex)
        viewer.get_view("mni152_asym_09c", view)
        return viewer
    from Speech import tools_Surface as ts
    return ts.plot_volume(data, ts.MNI_SUBJECT, voxel, view, **kwargs)


def mni_surface_2dplot(data1, data2, voxel="3.0", view="lateral", **kwargs):
    """ MNI surface 2dplot — 두 volume 을 2D colormap 으로 색칠 (pycortex Volume2D)

    Args:
        data1 (array): (x,y,z) 데이터 → colormap 가로축 (vmin→vmax)
        data2 (array): (x,y,z) 데이터 → colormap 세로축 (vmin2→vmax2, 아래→위)
        voxel (str, optional): 복셀 크기(mm), Defaults to '3.0'
        view (str, optional): 'lateral' · 'medial' · 'both'(Windows 격자)
        kwargs: cmap(2D colormap 이름 — D:/Functions/pycortex/colormaps 의 png), vmin, vmax,
            vmin2, vmax2. Windows 는 cmap 에 png 경로나 make_colormap(save=False) 배열도 된다

    Returns:
        WSL: pycortex viewer / Windows: matplotlib Figure
    """
    from Speech.tools import isWSL
    if isWSL():
        import cortex
        transform_name = 'mni_'+str(voxel)+"mm"
        ex = cortex.Volume2D(_to_pycortex_volume(data1), _to_pycortex_volume(data2),
                           "mni152_asym_09c", transform_name,
                           **kwargs)
        viewer = cortex.webgl.show(ex)
        viewer.get_view("mni152_asym_09c", view)
        return viewer

    from Speech import tools_Surface as ts
    cmap = kwargs.pop("cmap")
    lim = {k: kwargs.pop(k, None) for k in ("vmin", "vmax", "vmin2", "vmax2")}
    _, _, _, mapk = ts.split_kwargs(kwargs)
    v1 = ts.volume_to_vertex(data1, ts.MNI_SUBJECT, voxel, **mapk)
    v2 = ts.volume_to_vertex(data2, ts.MNI_SUBJECT, voxel, **mapk)
    all1, all2 = np.r_[v1["left"], v1["right"]], np.r_[v2["left"], v2["right"]]
    vmin = np.nanmin(all1) if lim["vmin"] is None else lim["vmin"]
    vmax = np.nanmax(all1) if lim["vmax"] is None else lim["vmax"]
    vmin2 = np.nanmin(all2) if lim["vmin2"] is None else lim["vmin2"]
    vmax2 = np.nanmax(all2) if lim["vmax2"] is None else lim["vmax2"]
    rgba = {h: ts.cmap2d_to_rgba(v1[h], v2[h], cmap, vmin, vmax, vmin2, vmax2)
            for h in ("left", "right")}
    return ts.plot_rgba_vertex(rgba, ts.MNI_SUBJECT, view, **kwargs)


def mni_to_fsaverage(data, voxel="3.0", **kwargs):
    """ MNI volume 을 fsaverage 정점값으로

    Args:
        data (array): (x,y,z) 또는 (n,x,y,z)
        voxel (str, optional): 복셀 크기(mm), Defaults to '3.0'
        kwargs: WSL 은 cortex.Vertex 인자, Windows 는 volume_to_vertex 의 mapper · depth

    Returns:
        WSL: cortex.Vertex (curvature 위에 blend) / Windows: {'left','right'} 정점 배열 (없는 곳 NaN)
    """
    from Speech.tools import isWSL
    if isWSL():
        import cortex
        from scipy.sparse import csr_matrix
        transform_name = 'mni_'+str(voxel)+"mm"
        ex = cortex.Volume(_to_pycortex_volume(data), "mni152_asym_09c", transform_name)
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
        return vertex_data

    from Speech import tools_Surface as ts
    _, _, _, mapk = ts.split_kwargs(kwargs)
    return ts.mni_to_fsaverage_vertex(ts.volume_to_vertex(data, ts.MNI_SUBJECT, voxel, **mapk))


def mni_surface_fsaverage_plot(data, voxel="3.0", view="lateral", **kwargs):
    """ MNI volume 을 fsaverage 표면에 plot (mni_surface_plot 의 fsaverage 판)

    Args:
        data (array): (x,y,z) 데이터
        voxel (str, optional): 복셀 크기(mm), Defaults to '3.0'
        view (str, optional): 'lateral' · 'medial' · 'both'(Windows 격자)
        kwargs: cortex.Vertex 인자 / Windows 는 tools_Surface.plot_volume 인자

    Returns:
        WSL: pycortex viewer / Windows: matplotlib Figure
    """
    from Speech.tools import isWSL
    if isWSL():
        import cortex
        vertex_data = mni_to_fsaverage(data, voxel, **kwargs)
        viewer = cortex.webgl.show(vertex_data)
        viewer.get_view("fsaverage", view)
        return viewer

    from Speech import tools_Surface as ts
    return ts.plot_volume(data, ts.MNI_SUBJECT, voxel, view, surface="fsaverage", **kwargs)


def save_mni_img(data, view="both", voxel="3.0", filename='now', path=None, **kwargs):
    """ MNI surface 그림을 png 로 저장

    Args:
        data (array): 3d brain array, should be MNI
        view (str, optional): "lateral" · "medial" · "both". Defaults to "both".
            WSL 은 both 면 lateral·medial 두 파일, Windows 는 격자 한 파일(`_both.png`)
        voxel (str, optional): MNI voxel size. Defaults to "3.0".
        filename (str, optional): Save image name (no extension). Defaults to 'now', current time.
        path (str, optional): Save path. Defaults to Downloads 폴더
        kwargs: mni_surface_plot 인자 (cmap · vmin · vmax …)

    Returns:
        저장한 파일 경로 (list)
    """
    import os
    from Speech.tools import isWSL
    if path is None:
        path = '/mnt/c/Users/Kwon/Downloads' if isWSL() else 'C:/Users/Kwon/Downloads'
    if filename == "now":
        from datetime import datetime
        img_base = datetime.today().strftime("%Y%m%d-%H%M%S")
    else:
        img_base = filename

    if isWSL():
        import cortex
        transform_name = 'mni_'+str(voxel)+"mm"
        ex = cortex.Volume(_to_pycortex_volume(data),
                        "mni152_asym_09c", transform_name,
                        **kwargs)
        viewer = cortex.webgl.show(ex)
        views = ["lateral", "medial"] if view == "both" else [view]
        saved = []
        for v in views:
            viewer.get_view("mni152_asym_09c", v)
            img_name = os.path.join(path, img_base+f"_{v}.png")
            viewer.getImage(img_name)
            saved.append(img_name)
        return saved

    from Speech import tools_Surface as ts
    fig = mni_surface_plot(data, voxel, view, **kwargs)
    return [ts.save_figure(fig, img_base + f"_{view}", path)]


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
    plt.close()
    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")
    x, y, z = np.where(mask)
    c = data if len(data.shape) == 1 else data[mask]
    ax.scatter(x, y, z, c=c, **kwargs)
    ax.view_init(view_angle[0], view_angle[1])
    return(ax)


def plot_roi(atlas_name, rois, rgba, voxel="3.0", view="lateral", surface='mni', **kwargs):
    """ atlas 의 roi 를 원하는 색으로 surface 에 plot

    Args:
        atlas_name (str): atlas 이름
            - "Brainnetome"
            - "Schaefer2018_<N>Parcels_<7/17>Networks"
            - "Yeo2011_<7/17>Networks"
        rois (double list): roi index ex) [roi1:[101,102], roi2:[201,202]...]
        rgba (double list): RGBA (0~255) ex) [roi1:[r,g,b,a], roi2:[r,g,b,a]...]
        voxel (str, optional): atlas voxel size, default is "3.0"
        view (str, optional): 'lateral' · 'medial' · 'both'(Windows 격자)
        surface (str, optional): 'mni' 또는 'fsaverage'
        **kwargs: cortex.VolumeRGB 인자 / Windows 는 tools_Surface.plot_rgba_volume 인자

    Returns:
        WSL: pycortex viewer / Windows: matplotlib Figure
    """
    from Speech.tools_EPI import get_atlas
    from Speech.tools import isWSL

    atlas = get_atlas(atlas_name, voxel=voxel)[1]
    rgba_map = np.zeros((4,) + atlas.shape, dtype=np.uint8)
    for roi, color in zip(rois, rgba):
        for r in roi:
            rgba_map[:, atlas == r] = np.asarray(color, dtype=np.uint8)[:, None]

    if isWSL():
        return plot_RGBA(*rgba_map, voxel=voxel, surface=surface, view=view, **kwargs)
    from Speech import tools_Surface as ts
    return ts.plot_rgba_volume(rgba_map, ts.MNI_SUBJECT, voxel, view, surface=surface, **kwargs)


def plot_fsaverage_atlas(atlas_name, data, view="lateral", **kwargs):
    """ fsaverage atlas plot — parcel 별 값 또는 색을 fsaverage 표면에

    Args:
        atlas_name (str): atlas 이름
            - "Schaefer2018_<N>Parcels_<7/17>Networks"
            - "Yeo2011_<7/17>Networks"
        data (dictionary): {index: 값} 또는 {index: [r,g,b(,a)]} (0~255 또는 0~1).
            없는 index 는 투명. Schaefer 는 rh index 가 lh 최대값만큼 밀려 있다(atlas 표와 같다)
        view (str, optional): 'lateral' · 'medial' · 'both'(Windows 격자)
        **kwargs: cortex.Vertex 인자 (cmap · vmin · vmax) / Windows 는 tools_Surface.plot_vertex 인자

    Returns:
        WSL: pycortex viewer / Windows: matplotlib Figure
    """
    import os
    from nibabel.freesurfer.io import read_annot
    from Speech.tools import isWSL
    from Speech import tools_Surface as ts

    label_dir = os.path.join(ts.db_path(), "fsaverage", "label")
    suffix = "_N1000" if "Yeo2011" in atlas_name else "_order"
    lh = read_annot(os.path.join(label_dir, f"lh.{atlas_name}{suffix}.annot"))[0]
    rh = read_annot(os.path.join(label_dir, f"rh.{atlas_name}{suffix}.annot"))[0]
    if "Yeo2011" not in atlas_name:
        rh = rh + lh.max() * (rh > 0)
    labels = {"left": lh, "right": rh}

    first = np.asarray(list(data.values())[0])
    if first.ndim == 0:                                  # parcel 별 스칼라
        vert = {h: np.full(len(lab), np.nan) for h, lab in labels.items()}
        for k, v in data.items():
            for h in vert:
                vert[h][labels[h] == int(k)] = v
        if isWSL():
            import cortex
            plotting_data = np.r_[vert["left"], vert["right"]]
            alpha_map = np.isfinite(plotting_data).astype(float)
            vertex_data = cortex.Vertex(plotting_data, 'fsaverage', **kwargs)
            vertex_data = vertex_data.blend_curvature(alpha=alpha_map, threshold=0.5, brightness=0)
            viewer = cortex.webgl.show(vertex_data)
            viewer.get_view("fsaverage", view)
            return viewer
        return ts.plot_vertex(vert, "fsaverage", view, **kwargs)

    rgba = {h: np.zeros((len(lab), 4)) for h, lab in labels.items()}   # parcel 별 색
    for k, color in data.items():
        color = np.asarray(color, dtype=float)
        if color.max() <= 1:
            color = color * 255
        if len(color) == 3:
            color = np.r_[color, 255]
        for h in rgba:
            rgba[h][labels[h] == int(k)] = color
    if isWSL():
        import cortex
        cmap = np.vstack([rgba["left"], rgba["right"]]).astype(np.uint8)
        vertex_data = cortex.VertexRGB(cmap[:, 0], cmap[:, 1], cmap[:, 2], 'fsaverage',
                                       alpha=cmap[:, 3], **kwargs)
        viewer = cortex.webgl.show(vertex_data)
        viewer.get_view("fsaverage", view)
        return viewer
    return ts.plot_rgba_vertex(rgba, "fsaverage", view, **kwargs)


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
    

def plot_colorline(x, y, z=None, cmap='copper', ax=None, norm=None, **kwargs):
    """ (x, y) 궤적을 z 값에 따라 색을 바꿔 가며 그린다.

    Args:
        z (array, optional): 선분별 색 값. 기본은 0→1 등간격 (시간 순서).
        norm (mpl.colors.Normalize, optional): 색 정규화. 기본은 z 의 min~max
            (예전엔 0~1 고정이라 z 를 직접 주면 전부 포화해 한 색으로 나왔다).
    """
    import matplotlib.collections as mcoll
    x = np.asarray(x, float); y = np.asarray(y, float)
    if z is None:
        z = np.linspace(0.0, 1.0, len(x))
    z = np.atleast_1d(np.asarray(z, float))

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    z = z[:len(segments)]            # 선분은 점보다 하나 적다
    if norm is None:
        norm = plt.Normalize(np.nanmin(z), np.nanmax(z))
    lc = mcoll.LineCollection(segments, array=z, cmap=cmap, norm=norm, **kwargs)

    if ax is None: ax = plt.gca()
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
                plt.text(x, y, r"$\mathit{n.s.}$", **final_kwargs)
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
                ax.text(x, y, r"$\mathit{n.s.}$", **final_kwargs)
        
        
def medbrain_surface_plot(data, view="lateral", **kwargs):
    """ MEBRAIN(원숭이) surface plot. transform 'MK' 의 (90,70,110) 그리드

    Args:
        data (array): (x,y,z) 또는 (n,x,y,z) 데이터 (Windows 는 3D 만)
        view (str, optional): 'lateral' · 'medial' · 'both'(Windows 격자)
        kwargs: cortex.Volume 인자 / Windows 는 tools_Surface.plot_volume 인자

    Returns:
        WSL: pycortex viewer / Windows: matplotlib Figure
    """
    from Speech.tools import isWSL
    if isWSL():
        import cortex
        ex = cortex.Volume(_to_pycortex_volume(data),
                           "MEBRAIN", "MK",
                           **kwargs)
        viewer = cortex.webgl.show(ex)
        return viewer
    from Speech import tools_Surface as ts
    return ts.plot_volume(data, "MEBRAIN", view=view, xfm="MK", **kwargs)


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
    """ Overlay multiple masks — 겹치는 곳은 alpha 비율로 색을 섞는다

    Args:
        masks (list of 3d array): binary volume 리스트 (하나면 3d array 도 됨)
        rgba (list of colorcode): RGBA (0~255) ex) [roi1:[r,g,b,a], roi2:[r,g,b,a]...]
        voxel (str, optional): voxel size, default is "3.0"
        surface (str, optional): 'mni' 또는 'fsaverage'. fsaverage 는 mask 를 정점으로 옮긴 뒤
            0.5 로 잘라 경계를 이진화하고 나서 색을 섞는다
        view (str, optional): 'lateral' · 'medial' · 'both'(Windows 격자)
        **kwargs: cortex.VolumeRGB / VertexRGB 인자. Windows 는 tools_Surface 인자

    Returns:
        WSL: pycortex viewer / Windows: matplotlib Figure
    """
    from Speech.tools import isWSL
    from Speech import tools_Surface as ts

    masks = np.array(masks)
    rgba = np.array(rgba, dtype=float)
    if masks.ndim == 3:
        masks = masks[None]
    if masks.ndim != 4:
        raise ValueError("masks 는 3d array 의 리스트여야 한다")

    def paint(mask, color):
        """mask 가 1 인 곳에 color 를 칠한 RGBA (4, ...) 배열"""
        out = np.zeros((4,) + mask.shape)
        out[:, mask > 0.5] = color[:, None]
        return out

    if surface == 'mni':
        colormap = np.zeros((4,) + masks.shape[1:])
        for mask, color in zip(masks, rgba):
            colormap = ts.blend_rgba(colormap, paint(mask, color))
        if isWSL():
            return plot_RGBA(*colormap.astype(np.uint8), voxel=voxel, surface="mni", view=view,
                             **kwargs)
        return ts.plot_rgba_volume(colormap, ts.MNI_SUBJECT, voxel, view, **kwargs)

    if surface != 'fsaverage':
        raise ValueError("surface 는 'mni' 또는 'fsaverage'")

    # fsaverage: mask 하나씩 정점으로 옮겨 이진화한 뒤 정점 위에서 색을 섞는다
    if isWSL():
        import cortex
        from scipy.sparse import csr_matrix
        transform_name = 'mni_' + str(voxel) + "mm"
        mapper = cortex.get_mapper("mni152_asym_09c", transform_name, 'nearest')
        mats = cortex.db.get_mri_surf2surf_matrix(subject="mni152_asym_09c",
                                                  surface_type='inflated',
                                                  target_subj='fsaverage')
        left_transform, right_transform = csr_matrix(mats[0]), csr_matrix(mats[1])

        def to_fs(mask):
            vol = cortex.Volume(_to_pycortex_volume(mask.astype(float)),
                                "mni152_asym_09c", transform_name)
            mapped = mapper(vol)
            return np.concatenate([left_transform.dot(mapped.left),
                                   right_transform.dot(mapped.right)])
    else:
        def to_fs(mask):
            vert = ts.volume_to_vertex(mask.astype(float), ts.MNI_SUBJECT, voxel)
            fs = ts.mni_to_fsaverage_vertex(vert)
            return np.r_[fs["left"], fs["right"]]

    vertex_colormap = None
    for mask, color in zip(masks, rgba):
        mask_fs = np.nan_to_num(to_fs(mask))
        new = paint(mask_fs, color)
        vertex_colormap = new if vertex_colormap is None else ts.blend_rgba(vertex_colormap, new)
    vertex_colormap = vertex_colormap.astype(np.uint8)

    if isWSL():
        vertex_data = cortex.VertexRGB(vertex_colormap[0], vertex_colormap[1], vertex_colormap[2],
                                       'fsaverage', alpha=vertex_colormap[3], **kwargs)
        viewer = cortex.webgl.show(vertex_data)
        viewer.get_view("fsaverage", view)
        return viewer
    n_left = ts.n_vertices("fsaverage")[0]
    rgba_vert = {"left": vertex_colormap[:, :n_left].T, "right": vertex_colormap[:, n_left:].T}
    return ts.plot_rgba_vertex(rgba_vert, "fsaverage", view, **kwargs)


def plot_RGBA(r_map, g_map, b_map, a_map, voxel="3.0", surface='mni', view='lateral', **kwargs):
    """ RGBA volume 네 장(0~255)을 surface 에 plot

    Args:
        r_map, g_map, b_map, a_map (array): (x,y,z) 0~255
        voxel (str, optional): voxel size, default is "3.0"
        surface (str, optional): 'mni' 또는 'fsaverage'
        view (str, optional): 'lateral' · 'medial' · 'both'(Windows 격자)
        **kwargs: cortex.VolumeRGB / VertexRGB 인자. Windows 는 tools_Surface 인자

    Returns:
        WSL: pycortex viewer / Windows: matplotlib Figure
    """
    from Speech.tools import isWSL
    if not isWSL():
        from Speech import tools_Surface as ts
        rgba = np.stack([r_map, g_map, b_map, a_map])
        return ts.plot_rgba_volume(rgba, ts.MNI_SUBJECT, voxel, view, surface=surface, **kwargs)

    import cortex
    transform_name = 'mni_' + str(voxel) + "mm"
    red = cortex.Volume(_to_pycortex_volume(r_map), "mni152_asym_09c", transform_name)
    green = cortex.Volume(_to_pycortex_volume(g_map), "mni152_asym_09c", transform_name)
    blue = cortex.Volume(_to_pycortex_volume(b_map), "mni152_asym_09c", transform_name)

    if surface == 'mni':
        vol_data = cortex.VolumeRGB(red, green, blue, "mni152_asym_09c", transform_name,
                                    alpha=_to_pycortex_volume(a_map), **kwargs)
        viewer = cortex.webgl.show(vol_data)
        viewer.get_view("mni152_asym_09c", view)
        return viewer
    elif surface == 'fsaverage':
        from scipy.sparse import csr_matrix
        mapper = cortex.get_mapper("mni152_asym_09c", transform_name, 'nearest')
        vertex_r = mapper(red)
        vertex_g = mapper(green)
        vertex_b = mapper(blue)
        vol_a = cortex.Volume(_to_pycortex_volume(a_map), "mni152_asym_09c", transform_name)
        vertex_a = mapper(vol_a)
        mats = cortex.db.get_mri_surf2surf_matrix(subject="mni152_asym_09c",
                                            surface_type='inflated',
                                            target_subj='fsaverage')
        left_transform = csr_matrix(mats[0])
        right_transform = csr_matrix(mats[1])

        def to_fs(v):
            fs = np.concatenate([left_transform.dot(v.left), right_transform.dot(v.right)])
            return np.clip(np.nan_to_num(fs), 0, 255).astype(np.uint8)

        vertex_data = cortex.VertexRGB(to_fs(vertex_r), to_fs(vertex_g), to_fs(vertex_b),
                                       'fsaverage', alpha=to_fs(vertex_a), **kwargs)
        viewer = cortex.webgl.show(vertex_data)
        viewer.get_view("fsaverage", view)
        return viewer
    raise ValueError("surface 는 'mni' 또는 'fsaverage'")


def set_matplotlib():
    """평소 쓰는 matplotlib 세팅
    """
    import matplotlib as mpl
    import matplotlib.font_manager as fm

    from Speech.tools import isWSL
    if isWSL():
        fname = '/mnt/c/Users/Kwon/AppData/Local/Microsoft/Windows/Fonts/Helvetica.ttf'
    else:
        fname = 'C:/Users/Kwon/AppData/Local/Microsoft/Windows/Fonts/Helvetica.ttf'

    fe = fm.FontEntry(
        fname=fname,
        name="Helvetica")
    fm.fontManager.ttflist.insert(0, fe) # or append is fine
    mpl.rcParams['font.family'] = fe.name
    mpl.rc('font', family = 'Helvetica', size = 10)
    mpl.rc('savefig', transparent = True)
    spines = {"top": False, "right": False}
    mpl.rc('axes.spines', **spines)



# %%
