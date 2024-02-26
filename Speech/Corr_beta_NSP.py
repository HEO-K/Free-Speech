# %%
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from statsmodels.stats.multitest import fdrcorrection
from Speech import tools_EPI
from Speech.tools_Text import get_sentence_FA
from Speech.Custom.speech_3T import good_subs
from Speech.tools_Plot import mni_surface_plot
import json
import matplotlib as mpl
from Speech.tools_Analysis import hrf_convolution
from scipy.stats import rankdata, ttest_1samp, spearmanr
from pingouin import partial_corr
import pandas as pd

task_type = "M"
n = 10
atlas_name = 'Schaefer2018_1000Parcels_17Networks'
atlas = tools_EPI.get_atlas(atlas_name)[1]
percent = np.arange(0,100+0.0001,100/n)
window = 20
delay = 0
hrf = np.zeros(window)
hrf[0] = 1
hrf = hrf_convolution(hrf, 1).reshape(window,1)
tr = 1000 # ms

# glm function
def ols_estimator(X, Y):
    return np.dot(np.dot(np.linalg.pinv(np.dot(X.T, X)), X.T), Y)

task_betas = []
with open(f"/mnt/d/speech_3T/code/BOLD_boundary/NextSentence_{task_type}.json", 'r') as f:
    Nextsent = json.load(f)
subs = good_subs(task_type)
name = ['roi'+str(i) for i in range(len(tools_EPI.get_atlas(atlas_name)[0]))] + ['sent', 'pause']
for [Project, sub, task] in tqdm(subs, f"Task-{task_type}"):
    try:
        bolds = []
        if task_type[0] == "L": sub = "000"
        # saved prop
        fa = np.array(get_sentence_FA(Project, sub, task))[:,:-1].astype(int)
        sentence = fa[1:,0]
        nextprop = np.array(Nextsent[Project+sub+task])
        pause = np.array([fa[i,0]-fa[i-1,1] for i in range(1,fa.shape[0])])/1000

        # epi
        epi = tools_EPI.loader(Project, sub, task)
        epi_roi = tools_EPI.parcel_averaging(atlas, epi)
        bold_x = []
        # beta
        for i, t in enumerate(sentence):
            t_int = int(t/tr)
            timeseries = epi_roi[:,t_int+delay:t_int+window+delay]
            if timeseries.shape[1] == window: 
                bolds.append(ols_estimator(hrf,timeseries.T.astype("float32"))[0,:])
                bold_x.append(nextprop[i])
        bolds = np.array(bolds)
        stats = []
        for i in range(len(tools_EPI.get_atlas(atlas_name)[0])):
            stats.append(spearmanr(bolds[:,i], bold_x)[0])
            # par_corr = partial_corr(data=sub_data, x="roi"+str(i), y="sent",
            #                         covar="pause",method='spearman').to_numpy()
            # par_corr = partial_corr(data=sub_data, x="roi"+str(i), y="pause",
            #                         covar="sent",method='spearman').to_numpy()
            # stats.append([par_corr[0,1]])
        task_betas.append(stats)    
#            data = pd.concat([data, sub_data])
    except: pass
task_betas = np.array(task_betas)
brain = np.zeros_like(atlas)
brain[:] = np.nan
mask = [ttest_1samp(task_betas[:,i],0)[1] for i in range(len(tools_EPI.get_atlas(atlas_name)[0]))]
mask = fdrcorrection(mask)[0]
for i in range(len(mask)):
    if mask[i]: 
        brain[atlas==i+1] = np.mean(task_betas[:,i])
mni_surface_plot(brain, vmin=-0.2, vmax=0.2)
# %%
