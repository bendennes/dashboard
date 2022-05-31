import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

from plot_utils import get_delta, plot_sim_timeseries

st.set_page_config(layout="wide")

## set-up and load data
st.title('Messaging Convergence')
st.header('Examine Press Release')

col1, col2, col3 = st.columns([2,2,3])
# 1: press release details & metric
# 2: parameters
# 3: plot

metadata_fname = 'press_releases_embedded.pkl'

@st.cache(allow_output_mutation=True)
def load_metadata():
    '''
    Load the dataframe of press releases, containing text, title, date, etc.
    '''
    metadata = pd.read_pickle(metadata_fname)
    return metadata

# load the metadata
data_load_state = st.text('Loading metadata...')
metadata = load_metadata()
data_load_state.text('')

# find all pkl files in working directory (excluding metadata file)
# i.e. get all fnames for press release similarity dataframes
fnames = [f for f in os.listdir() if f.endswith('pkl') and f != metadata_fname]
# generate dicts mapping id to fname and title to id (id as int for metadata dataframe indexing)
pr_id_to_fname = {int(f.split('.')[0].split('_')[1]) : f for f in fnames} # string id ('137') : fname ('pr_137.pkl')
title_to_pr_id = {metadata.loc[i, 'title'] : i for i in pr_id_to_fname.keys()}

with col1:
    st.subheader('Press Release Details')
    # choose press release
    pr_title = st.selectbox(
        'Choose Press Release',
        list(title_to_pr_id.keys())
    )
    pr_id = title_to_pr_id[pr_title]

    st.text(f'{metadata.loc[pr_id, "org"]}, {metadata.loc[pr_id, "date"].date()} (id: {str(pr_id)})')

tweet_data_fname = pr_id_to_fname[pr_id]

@st.cache
def load_data(fname=tweet_data_fname):
    data = pd.read_pickle(fname).set_index('tweet_id')
    return data

data_load_state = st.text('Loading data...')
data = load_data()
data_load_state.text('')

with col2:
    st.subheader('Parameters')
    ## threshold by similarity
    sim_threshold = st.slider('tweet similarity sensitivity (threshold)', 0.5, 0.85, 0.725, step=0.005, format='%.3f')
    data_t = data.loc[data.sim > sim_threshold]

    correct_baseline = st.checkbox('Correct for baseline tweet volume')

    include_day_before_in_post = st.checkbox('Include day before release date in post window')
    if include_day_before_in_post:
        pre_params = (1,6,6)
        post_params = (2,9,3)
    else:
        pre_params = (1,7,7)
        post_params = (1,7,3)

    pre_n = st.slider('pre window (days)',*pre_params)
    post_n = st.slider('post window (days)',*post_params)


with col3:
    timeseries = data_t.date.value_counts().reindex(pd.Index(data.date.unique()), fill_value=0)
    
    if correct_baseline:
        timeseries = timeseries / data.groupby('date').count()['sim']
        n_dp = 5
        st.subheader('Proportion of convergent tweets')
    else:
        n_dp = 0
        st.subheader('Number of convergent tweets')

    release_date = metadata.loc[int(pr_id), 'date']

    delta, pre, post = get_delta(timeseries, release_date=release_date.date(), 
                                pre_n=pre_n, post_n=post_n, include_day_before_in_post=include_day_before_in_post)

    fig, ax = plot_sim_timeseries(timeseries, delta, pre, post, show_pre_post=True, show_means=True, show_delta=True, 
                                n_dp=n_dp, include_day_before_in_post=include_day_before_in_post, alpha=0.15)

    # st.subheader('Daily Tweets with convergent messaging')
    st.pyplot(fig)
    st.text(f'avg. before:\t{np.around(pre.mean(), n_dp)}')
    st.text(f'avg. after:\t{np.around(post.mean(), n_dp)}')

with col1:
    st.metric('delta', value=np.around(delta, n_dp), delta=None)
    st.write(" ".join(metadata.loc[pr_id, 'sents'][:2]) + ' ...')

st.header('Compare all Press Releases')
st.write('Press to calculate delta for all Press Releases (with current parameters)')

if st.button('Calculate'):
    bar = st.progress(0.0)

    deltas = pd.Series([], name='deltas', dtype='float64')

    pr_ids = [int(f.split('.')[0].split('_')[1]) for f in fnames]
    for i, (pr_id, fname) in enumerate(zip(pr_ids, fnames)):
        data = load_data(fname=fname)
        data_t = data.loc[data.sim > sim_threshold]
        timeseries = data_t.date.value_counts().reindex(pd.Index(data.date.unique()), fill_value=0)

        delta, pre, post = get_delta(timeseries, release_date=metadata.loc[int(pr_id), 'date'].date(), 
                                pre_n=pre_n, post_n=post_n, include_day_before_in_post=include_day_before_in_post)

        deltas[pr_id] = delta
        bar.progress((i+1)/len(fnames))

    metadata['delta'] = deltas
    st.dataframe( metadata.loc[pr_ids, ['title', 'org', 'date', 'url', 'text', 'delta']].sort_values('delta', ascending=False) )