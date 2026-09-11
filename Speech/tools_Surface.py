# %%
"""surfplot 기반 surface 렌더링 백엔드.

pycortex 를 쓸 수 없는 Windows 에서 `tools_Plot` 의 surface 함수들이 이 모듈로 분기한다.
표면(GIFTI) · 곡률 · surf2surf 행렬 · transform 은 pycortex DB(`D:/Functions/pycortex/db`)의
것을 그대로 읽으므로 pycortex 와 **같은 표면**(mni152_asym_09c · fsaverage · MEBRAIN)에 그린다.

흐름
    volume (x,y,z) ──volume_to_vertex──▶ {'left','right'} 정점값
        ──(선택) mni_to_fsaverage_vertex──▶ fsaverage 정점값
        ──make_plot + add_scalar_layer / add_rgba_layer + build──▶ matplotlib Figure

한 줄 호출은 `plot_volume` · `plot_vertex` · `plot_rgba_volume` · `plot_rgba_vertex`.

pycortex 와 다른 점
    - 정적 이미지(matplotlib Figure)다. webgl 뷰어처럼 돌려볼 수 없다.
    - 4D (n,x,y,z) 데이터는 정점값까지만 만들고, 플롯은 3D 한 장씩 한다.
    - view 는 'lateral' · 'medial' · 'both'(= lateral+medial 격자) 또는 surfplot view 리스트
      ('dorsal' 'ventral' 'anterior' 'posterior' 포함).
"""
import os
import glob
import warnings
import numpy as np

MNI_SUBJECT = "mni152_asym_09c"
PANEL_SIZE = (800, 520)      # view 하나의 픽셀 크기 (build 의 scale=(2,2) 로 두 배 렌더)
DEFAULT_ZOOM = 1.25
LUT_SIZE = 256               # brainspace lookup table 크기 — RGBA 레이어 양자화 상한

# 인자 분류: pycortex 스타일 kwargs 를 surfplot 의 어디로 보낼지
_PLOT_KEYS = {"layout", "size", "zoom", "brightness", "sulc", "surf", "mirror_views",
              "flip", "background", "label_text"}
_LAYER_KEYS = {"cmap", "vmin", "vmax", "cbar", "cbar_label", "alpha", "zero_transparent",
               "as_outline"}
_BUILD_KEYS = {"colorbar", "cbar_kws", "scale"}
_MAP_KEYS = {"mapper", "depth"}
_IGNORED_KEYS = {"description", "state", "priority", "vmin2", "vmax2", "cmap2"}  # pycortex 전용


# ----------------------------------------------------------------------------
# pycortex DB 읽기
# ----------------------------------------------------------------------------
def db_path():
    """pycortex DB 루트. WSL 에서 불려도 같은 폴더를 가리킨다."""
    from Speech.tools import isWSL
    return "/mnt/d/Functions/pycortex/db" if isWSL() else "D:/Functions/pycortex/db"


def colormap_dir():
    """pycortex 2D/커스텀 colormap png 폴더 (`make_colormap` 저장 위치)."""
    return os.path.join(os.path.dirname(db_path()), "colormaps")


def surface_files(subject, surf="inflated"):
    """(lh, rh) GIFTI 경로. surf: inflated · pia · wm · flat"""
    base = os.path.join(db_path(), subject, "surfaces")
    files = [os.path.join(base, f"{surf}_{h}.gii") for h in ("lh", "rh")]
    for f in files:
        if not os.path.exists(f):
            raise FileNotFoundError(f"{subject} 의 {surf} 표면이 없다: {f}")
    return tuple(files)


_SURF_CACHE = {}


def load_surface(subject, surf="inflated"):
    """{'left': (coords, faces), 'right': ...}. coords (V,3) float64, faces (F,3)"""
    key = (subject, surf)
    if key not in _SURF_CACHE:
        import nibabel as nib
        out = {}
        for h, f in zip(("left", "right"), surface_files(subject, surf)):
            g = nib.load(f)
            out[h] = (g.darrays[0].data.astype(np.float64), g.darrays[1].data)
        _SURF_CACHE[key] = out
    return _SURF_CACHE[key]


def n_vertices(subject):
    """(n_left, n_right)"""
    s = load_surface(subject, "inflated")
    return len(s["left"][0]), len(s["right"][0])


def surface_info(subject, name="sulcaldepth"):
    """pycortex surface-info (curvature · sulcaldepth · thickness) → {'left','right'}"""
    z = np.load(os.path.join(db_path(), subject, "surface-info", name + ".npz"))
    return {"left": z["left"], "right": z["right"]}


def coord_matrix(subject=MNI_SUBJECT, voxel="3.0", xfm=None):
    """anatomical mm 좌표 → functional voxel index 4x4 행렬(pycortex xfm 의 `coord`)과 그리드 shape.

    mni152_asym_09c 는 pycortex DB 에 3.0 mm transform 만 있으므로 `_data_Atlas` 의 MNI 그리드
    (1.5 · 2.0 · 2.6 · 3.0 mm; affine 이 pycortex reference 와 같다)에서 만든다. magnet 은
    항등에 가까워(0.5 mm 이내) 무시한다. 그 밖의 subject(MEBRAIN 등)는 `xfm` 이름으로
    `transforms/<xfm>/matrices.xfm` 을 읽는다.
    """
    import nibabel as nib
    if xfm is None:
        if subject != MNI_SUBJECT:
            raise ValueError(f"{subject} 는 xfm 이름을 줘야 한다 (예: MEBRAIN 은 'MK')")
        from Speech import tools_EPI
        atlas_dir = os.path.join(os.path.dirname(tools_EPI.__file__), "_data_Atlas",
                                 "Schaefer2018_400Parcels_17Networks")
        nii = glob.glob(os.path.join(atlas_dir, f"*_{voxel}mm.nii*"))
        if not nii:
            raise FileNotFoundError(f"{voxel} mm MNI 그리드가 _data_Atlas 에 없다")
        img = nib.load(nii[0])
        return np.linalg.inv(img.affine), tuple(img.shape[:3])
    import json
    tdir = os.path.join(db_path(), subject, "transforms", xfm)
    with open(os.path.join(tdir, "matrices.xfm")) as f:
        coord = np.array(json.load(f)["coord"], dtype=np.float64)
    shape = tuple(nib.load(os.path.join(tdir, "reference.nii.gz")).shape[:3])
    return coord, shape


# ----------------------------------------------------------------------------
# volume → vertex, mni → fsaverage
# ----------------------------------------------------------------------------
def volume_to_vertex(data, subject=MNI_SUBJECT, voxel="3.0", xfm=None,
                     mapper="nearest", depth=0.5):
    """volume 을 표면 정점값으로 샘플링.

    Args:
        data: (x,y,z) 또는 (n,x,y,z). 안 그릴 곳은 NaN 으로 둘 것 — 0 도 그려진다.
            transpose 없이 EPI/atlas 배열 그대로 넣는다 (pycortex 용 (z,y,x) 로 바꾸지 말 것).
        subject, voxel, xfm: `coord_matrix` 참고
        mapper: 'nearest' — pycortex 기본 mapper 처럼 fiducial(wm↔pia 중간) 표면에서 가장 가까운 복셀
                'linear'  — 같은 위치에서 삼선형 보간
                'line'    — wm→pia 사이 여러 깊이(`depth` 를 배열로) 평균. nilearn vol_to_surf 와 비슷
        depth: 0(wm) ~ 1(pia). 'line' 이면 배열, 예 np.linspace(0.1, 0.9, 5)

    Returns:
        {'left': (V,) 또는 (n,V), 'right': ...}
    """
    from scipy.ndimage import map_coordinates
    data = np.asarray(data, dtype=np.float32)
    if data.ndim == 3:
        data = data[None]
    elif data.ndim != 4:
        raise ValueError("data 는 (x,y,z) 또는 (n,x,y,z) 여야 한다")
    coord, shape = coord_matrix(subject, voxel, xfm)
    if tuple(data.shape[1:]) != shape:
        raise ValueError(f"data shape {data.shape[1:]} 가 {subject}/{xfm or voxel + 'mm'} 그리드 "
                         f"{shape} 와 다르다")
    pia, wm = load_surface(subject, "pia"), load_surface(subject, "wm")
    depths = np.atleast_1d(depth) if mapper == "line" else np.array([np.mean(depth)])
    order = 0 if mapper == "nearest" else 1

    out = {}
    for h in ("left", "right"):
        acc = []
        for d in depths:
            xyz = wm[h][0] + d * (pia[h][0] - wm[h][0])
            ijk = (coord @ np.c_[xyz, np.ones(len(xyz))].T)[:3]
            acc.append(np.stack([map_coordinates(v, ijk, order=order, mode="constant",
                                                 cval=np.nan) for v in data]))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)   # 전부 NaN 인 정점
            vals = np.nanmean(acc, axis=0)
        out[h] = vals[0] if vals.shape[0] == 1 else vals
    return out


_S2S_CACHE = {}


def surf2surf_matrix(subject=MNI_SUBJECT, target="fsaverage", surf="inflated"):
    """pycortex 가 저장한 subject→target 정점 매핑 CSR 행렬 (left, right)"""
    key = (subject, target, surf)
    if key not in _S2S_CACHE:
        import h5py
        from scipy.sparse import csr_matrix
        f = os.path.join(db_path(), subject, "surf2surf", f"{subject}_to_{target}",
                         f"matrices_{surf}.hdf")
        if not os.path.exists(f):
            raise FileNotFoundError(f"surf2surf 행렬이 없다: {f}")
        with h5py.File(f, "r") as h:
            _S2S_CACHE[key] = tuple(
                csr_matrix((h[f"{p}_data"][:], h[f"{p}_indices"][:], h[f"{p}_indptr"][:]),
                           shape=tuple(h[f"{p}_shape"][:]))
                for p in ("lh", "rh"))
    return _S2S_CACHE[key]


def mni_to_fsaverage_vertex(vert, subject=MNI_SUBJECT):
    """{'left','right'} 정점값(subject 표면) → fsaverage 정점값. (n,V) 도 된다.
    pycortex `get_mri_surf2surf_matrix` 와 같은 행렬이라 NaN 도 같은 방식으로 번진다."""
    mats = surf2surf_matrix(subject, "fsaverage")
    out = {}
    for h, m in zip(("left", "right"), mats):
        v = np.asarray(vert[h], dtype=np.float64)
        out[h] = (m @ v.T).T if v.ndim == 2 else m @ v
    return out


# ----------------------------------------------------------------------------
# colormap
# ----------------------------------------------------------------------------
def load_cmap_image(cmap):
    """colormap png → (H,W,4) float 0~1. png 경로 · pycortex colormap 이름 · 배열 을 받는다."""
    if isinstance(cmap, np.ndarray):
        img = cmap.astype(np.float64)
        if img.max() > 1:
            img = img / 255.0
    else:
        import matplotlib.pyplot as plt
        path = cmap
        if not os.path.exists(path):
            path = os.path.join(colormap_dir(), cmap if cmap.endswith(".png") else cmap + ".png")
        if not os.path.exists(path):
            raise FileNotFoundError(f"colormap 이미지가 없다: {cmap} ({colormap_dir()})")
        img = plt.imread(path).astype(np.float64)
        if img.max() > 1:
            img = img / 255.0
    if img.ndim == 2:
        img = np.repeat(img[:, :, None], 3, axis=2)
    if img.shape[2] == 3:
        img = np.concatenate([img, np.ones(img.shape[:2] + (1,))], axis=2)
    return img


def resolve_cmap(cmap):
    """matplotlib 이름 · Colormap 객체 · png 경로 · pycortex colormap 이름 → Colormap"""
    import matplotlib as mpl
    if isinstance(cmap, mpl.colors.Colormap):
        return cmap
    if isinstance(cmap, str):
        try:
            return mpl.colormaps[cmap]
        except KeyError:
            pass
    img = load_cmap_image(cmap)
    if img.shape[0] > 4:
        raise ValueError("2D colormap 은 scalar 레이어에 못 쓴다 — `cmap2d_to_rgba` 로 RGBA 를 만들 것")
    return mpl.colors.ListedColormap(img[img.shape[0] // 2], name=str(cmap))


def cmap2d_to_rgba(data1, data2, cmap, vmin, vmax, vmin2, vmax2):
    """pycortex Volume2D 처럼 두 값을 2D colormap 이미지로 색칠.
    data1 → 가로축(vmin→vmax, 왼→오른쪽), data2 → 세로축(vmin2→vmax2, 아래→위).
    둘 중 하나라도 NaN 이면 투명. 반환 (…,4) float 0~1"""
    img = load_cmap_image(cmap)
    H, W = img.shape[:2]
    d1, d2 = np.asarray(data1, float), np.asarray(data2, float)
    ok = np.isfinite(d1) & np.isfinite(d2)
    u = np.clip((np.nan_to_num(d1) - vmin) / (vmax - vmin), 0, 1)
    v = np.clip((np.nan_to_num(d2) - vmin2) / (vmax2 - vmin2), 0, 1)
    col = np.round(u * (W - 1)).astype(int)
    row = np.round((1 - v) * (H - 1)).astype(int)
    rgba = img[row, col]
    rgba[~ok, 3] = 0
    return rgba


# ----------------------------------------------------------------------------
# surfplot 래핑
# ----------------------------------------------------------------------------
def split_kwargs(kwargs):
    """pycortex 스타일 kwargs 를 (plot, layer, build, map) 네 묶음으로. 모르는 키는 경고 후 버린다."""
    plot, layer, build, mapk = {}, {}, {}, {}
    for k, v in kwargs.items():
        if k in _PLOT_KEYS:
            plot[k] = v
        elif k in _LAYER_KEYS:
            layer[k] = v
        elif k in _BUILD_KEYS:
            build[k] = v
        elif k in _MAP_KEYS:
            mapk[k] = v
        elif k not in _IGNORED_KEYS:
            warnings.warn(f"surfplot 백엔드가 모르는 인자라 무시한다: {k}")
    return plot, layer, build, mapk


def _views(view):
    if isinstance(view, (list, tuple)):
        return list(view)
    if view == "both":
        return ["lateral", "medial"]
    return [view]


def make_plot(subject=MNI_SUBJECT, view="lateral", surf="inflated", sulc=False, layout=None,
              size=None, zoom=DEFAULT_ZOOM, brightness=0.5, **kwargs):
    """surfplot.Plot 생성. 기본은 튜토리얼처럼 광택 없는 중간 회색 표면.

    Args:
        view: 'lateral' · 'medial' · 'both' · surfplot view 리스트
        surf: 'inflated' · 'pia' · 'wm' · 'flat'
        sulc: True 면 sulcal depth 를 회색조로 깔아 굴곡을 보여준다
        layout: 'grid'(view 여러 개일 때 기본) · 'row'(view 하나일 때 기본) · 'column'
        size: 전체 픽셀 크기. 기본은 PANEL_SIZE × 패널 수
        brightness: 빈 표면 밝기 0(검정)~1(흰색)
        kwargs: surfplot.Plot 의 나머지 인자 (mirror_views · flip · background · label_text)
    """
    from surfplot import Plot
    views = _views(view)
    if layout is None:
        layout = "grid" if len(views) > 1 else "row"
    if layout == "grid":
        rows, cols = len(views), 2
    elif layout == "row":
        rows, cols = 1, 2 * len(views)
    else:
        rows, cols = 2 * len(views), 1
    if size is None:
        size = (PANEL_SIZE[0] * cols, PANEL_SIZE[1] * rows)
    lh, rh = surface_files(subject, surf)
    p = Plot(lh, rh, layout=layout, views=views, size=size, zoom=zoom, brightness=brightness,
             **kwargs)
    if sulc:
        # 깊은 곳(값 큼)을 조금 어둡게 — 기본 회색(brightness) 주변 ±0.15 안에서만 움직인다
        import matplotlib as mpl
        s = surface_info(subject, "sulcaldepth")
        lo, hi = np.nanpercentile(np.r_[s["left"], s["right"]], [2, 98])
        shades = np.linspace(min(brightness + 0.15, 1), max(brightness - 0.15, 0), 256)
        cmap = mpl.colors.ListedColormap(np.repeat(shades[:, None], 3, axis=1), name="sulc")
        p.add_layer(s, cmap=cmap, color_range=(lo, hi), cbar=False, zero_transparent=False)
    return p


def add_scalar_layer(p, vert, cmap="viridis", vmin=None, vmax=None, cbar=True, cbar_label=None,
                     alpha=1, zero_transparent=False, as_outline=False):
    """{'left','right'} 스칼라 정점값을 한 레이어로. NaN 은 투명.
    pycortex 와 같이 0 도 색으로 그린다 — 숨기려면 NaN 으로 두거나 zero_transparent=True."""
    data = {}
    for h in ("left", "right"):
        v = np.array(vert[h], dtype=np.float64)
        if v.ndim != 1:
            raise ValueError("플롯은 3D 한 장씩 — (n,V) 정점값이면 프레임을 골라서 줄 것")
        data[h] = v
    allv = np.r_[data["left"], data["right"]]
    if vmin is None:
        vmin = np.nanmin(allv)
    if vmax is None:
        vmax = np.nanmax(allv)
    p.add_layer(data, cmap=resolve_cmap(cmap), color_range=(float(vmin), float(vmax)),
                cbar=cbar, cbar_label=cbar_label, alpha=alpha,
                zero_transparent=zero_transparent, as_outline=as_outline)
    return p


def add_rgba_layer(p, rgba):
    """정점별 색 레이어. rgba: {'left': (V,3|4), 'right': ...}, 0~255 또는 0~1.
    alpha 0 또는 NaN 인 정점은 투명.

    surfplot 은 정점별 RGB 를 직접 받지 못하므로 색을 ≤255 개로 양자화해
    ListedColormap + 정수 인덱스로 넘긴다 (brainspace LUT 가 256 칸). 색이 255 개를 넘으면
    PIL median-cut 으로 줄인다 — 2D colormap 처럼 연속색이면 미세한 계단이 생길 수 있다.
    """
    import matplotlib as mpl
    parts = []
    for h in ("left", "right"):
        c = np.array(rgba[h], dtype=np.float64)
        if c.ndim != 2 or c.shape[1] not in (3, 4):
            raise ValueError("rgba 는 (V,3) 또는 (V,4)")
        if c.shape[1] == 3:
            c = np.c_[c, np.ones(len(c))]
        parts.append(c)
    n_left = len(parts[0])
    c = np.vstack(parts)
    if np.nanmax(c) > 1:
        c = c / 255.0
    c = np.clip(c, 0, 1)
    valid = np.all(np.isfinite(c), axis=1) & (c[:, 3] > 0)

    q = np.round(c[valid] * 255).astype(np.uint8)
    palette, inv = np.unique(q, axis=0, return_inverse=True)
    inv = inv.ravel()
    if len(palette) > LUT_SIZE - 1:
        from PIL import Image
        im = Image.fromarray(palette[None, :, :3], "RGB").quantize(LUT_SIZE - 1)
        pal_rgb = np.array(im.getpalette()[: 3 * (LUT_SIZE - 1)]).reshape(-1, 3)
        pidx = np.array(im).ravel()                       # 옛 팔레트 → 새 팔레트
        pal_a = np.array([palette[pidx == i, 3].mean() if np.any(pidx == i) else 255
                          for i in range(len(pal_rgb))])
        palette = np.c_[pal_rgb, np.round(pal_a)].astype(np.uint8)
        inv = pidx[inv]

    table = np.zeros((LUT_SIZE, 4))
    table[1:len(palette) + 1] = palette / 255.0
    idx = np.full(len(c), np.nan)
    idx[valid] = inv + 1
    p.add_layer({"left": idx[:n_left], "right": idx[n_left:]},
                cmap=mpl.colors.ListedColormap(table), color_range=(0, LUT_SIZE - 1),
                cbar=False, zero_transparent=True)
    # 이 레이어의 정점값은 팔레트 index 라 face 안에서 보간되면 안 된다 — build() 가 mapper 의
    # interpolateScalarsBeforeMapping 을 끈다 (surfplot 이 값을 float 로 바꿔 discrete 감지가 안 걸린다)
    if not hasattr(p, "_index_layers"):
        p._index_layers = set()
    p._index_layers.add(p.layers[-1])
    return p


def _disable_index_interpolation(plotter, layer_names):
    """렌더된 brainspace Plotter 에서 index 레이어 actor 의 scalar 보간을 끈다.
    켜 두면 인접 정점 index 1·3 사이 픽셀이 index 2 색으로 칠해져 parcel 경계마다 엉뚱한 윤곽선이 생긴다."""
    if not layer_names:
        return
    for rens in plotter.renderers.values():
        for ren in rens:
            actors = ren.actors
            for i in range(actors.n_items):
                actor = actors[i]
                if actor is None:
                    break
                mapper = actor.mapper
                if mapper.arrayName in layer_names:
                    mapper.interpolateScalarsBeforeMapping = False


def build(p, colorbar=True, cbar_kws=None, scale=(2, 2)):
    """렌더링해 matplotlib Figure 로. 기본 colorbar 는 아래쪽 가로.

    surfplot.Plot.build 와 같지만 render 와 screenshot 사이에서 index 레이어(add_rgba_layer)의
    보간을 끈다 — surfplot 은 그 사이에 끼어들 자리가 없어 본문을 옮겨 왔다."""
    import matplotlib.pyplot as plt
    kws = {"location": "bottom", "shrink": 0.25, "pad": 0.02, "fontsize": 12, "draw_border": False}
    kws.update(cbar_kws or {})
    plotter = p.render()
    _disable_index_interpolation(plotter, getattr(p, "_index_layers", set()))
    plotter._check_offscreen()
    img = plotter.to_numpy(transparent_bg=True, scale=scale)
    fig, ax = plt.subplots(figsize=tuple((np.array(p.size) / 100) + 1))
    ax.imshow(img)
    ax.axis("off")
    if colorbar:
        p._add_colorbars(**kws)
    return fig


def save_figure(fig, filename="now", path=None, dpi=200, transparent=True):
    """png 저장. filename='now' 면 현재 시각. 반환: 저장 경로"""
    if path is None:
        from Speech.tools import isWSL
        path = "/mnt/c/Users/Kwon/Downloads" if isWSL() else "C:/Users/Kwon/Downloads"
    if filename == "now":
        from datetime import datetime
        filename = datetime.today().strftime("%Y%m%d-%H%M%S")
    if not filename.lower().endswith(".png"):
        filename += ".png"
    out = os.path.join(path, filename)
    fig.savefig(out, dpi=dpi, bbox_inches="tight", transparent=transparent)
    return out


# ----------------------------------------------------------------------------
# 한 줄 호출
# ----------------------------------------------------------------------------
def plot_vertex(vert, subject=MNI_SUBJECT, view="lateral", **kwargs):
    """{'left','right'} 스칼라 정점값 → Figure. kwargs 는 make_plot · add_scalar_layer · build 인자"""
    plot, layer, bld, _ = split_kwargs(kwargs)
    p = make_plot(subject, view, **plot)
    add_scalar_layer(p, vert, **layer)
    return build(p, **bld)


def plot_rgba_vertex(rgba, subject=MNI_SUBJECT, view="lateral", **kwargs):
    """{'left','right'} (V,4) 정점 색 → Figure"""
    plot, _, bld, _ = split_kwargs(kwargs)
    p = make_plot(subject, view, **plot)
    add_rgba_layer(p, rgba)
    return build(p, **bld)


def plot_volume(data, subject=MNI_SUBJECT, voxel="3.0", view="lateral", xfm=None,
                surface=None, **kwargs):
    """(x,y,z) volume → Figure. surface='fsaverage' 면 surf2surf 로 옮겨 fsaverage 에 그린다.
    kwargs: cmap · vmin · vmax · cbar · cbar_label · mapper · depth · sulc · zoom · size …"""
    _, _, _, mapk = split_kwargs(kwargs)
    vert = volume_to_vertex(data, subject, voxel, xfm, **mapk)
    if surface == "fsaverage" and subject != "fsaverage":
        vert, subject = mni_to_fsaverage_vertex(vert, subject), "fsaverage"
    return plot_vertex(vert, subject, view, **kwargs)


def rgba_volume_to_vertex(rgba, subject=MNI_SUBJECT, voxel="3.0", xfm=None, surface=None,
                          alpha_threshold=0.5):
    """(4,x,y,z) 0~255 RGBA volume → {'left','right'} (V,4) 0~1.
    nearest 로 샘플링하고, fsaverage 로 옮길 때는 alpha 가 alpha_threshold(0~1) 미만이면 지운다."""
    rgba = np.asarray(rgba, dtype=np.float32)
    if rgba.shape[0] != 4 or rgba.ndim != 4:
        raise ValueError("rgba 는 (4,x,y,z)")
    vert = volume_to_vertex(rgba, subject, voxel, xfm, mapper="nearest")
    if surface == "fsaverage" and subject != "fsaverage":
        vert = mni_to_fsaverage_vertex(vert, subject)
    out = {}
    for h in ("left", "right"):
        c = np.nan_to_num(vert[h].T) / 255.0
        c[c[:, 3] < alpha_threshold, 3] = 0
        out[h] = c
    return out


def plot_rgba_volume(rgba, subject=MNI_SUBJECT, voxel="3.0", view="lateral", xfm=None,
                     surface=None, **kwargs):
    """(4,x,y,z) 0~255 RGBA volume → Figure (pycortex VolumeRGB 대응)"""
    vert = rgba_volume_to_vertex(rgba, subject, voxel, xfm, surface)
    target = "fsaverage" if surface == "fsaverage" else subject
    return plot_rgba_vertex(vert, target, view, **kwargs)


def blend_rgba(base, new):
    """RGBA(0~255) 두 장을 alpha 비율로 섞는다 — plot_mask 의 겹침 처리. 배열 첫 축이 채널."""
    base = np.asarray(base, dtype=np.float64)
    new = np.asarray(new, dtype=np.float64)
    base_a, new_a = base[3] / 255.0, new[3] / 255.0
    sums = base_a + new_a
    ratio = np.full_like(base_a, 0.5)
    valid = sums > 0
    ratio[valid] = base_a[valid] / sums[valid]
    out = np.empty_like(base)
    out[:3] = base[:3] * ratio + new[:3] * (1 - ratio)
    out[3] = (1.0 - (1.0 - base_a) * (1.0 - new_a)) * 255.0
    return np.clip(out, 0, 255)
