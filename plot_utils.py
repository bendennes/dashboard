import pandas as pd
import datetime
import matplotlib.pyplot as plt
import numpy as np

import matplotlib.patches as patches

def get_delta(s, # pandas series of relevant values (p_t / mean_sim / n_t)
    release_date, #datetime.datetime.date() of release
    pre_n, post_n, # n days in pre/post regions (release date included in post region)
    include_day_before_in_post=False
    ):
    
    text_date_ind = s.index.get_loc(release_date)

    if include_day_before_in_post:
        pre = s.iloc[text_date_ind-1-pre_n : text_date_ind-1]
        post = s.iloc[text_date_ind-1 : text_date_ind-1+post_n]
    else:
        pre = s.iloc[text_date_ind-pre_n : text_date_ind]
        post = s.iloc[text_date_ind : text_date_ind+post_n]

    # print(len(pre), len(post))

    delta = post.mean() - pre.mean()
    return delta, pre, post


def add_time_to_date(date, hour_diff):
    return datetime.datetime.combine(date, datetime.datetime.min.time())+datetime.timedelta(hours=hour_diff)


### ! need to change how displaying post window works
def plot_sim_timeseries(p_t, delta, pre, post, show_pre_post, show_means, show_delta, 
                            n_dp=0, include_day_before_in_post=False, alpha=0.3):
        # fig, ax = plt.subplots(figsize=(10,5))
        fig, ax = plt.subplots(figsize=(10,5))

        # basic plot of points
        ax.plot(p_t.index, p_t.values, c='k', marker='o')

        ax.set_xlabel('date')
        ax.set_ylabel('similar tweets')

        # pre post regions
        if show_pre_post:
                ax.axvspan(add_time_to_date(post.index[0], -12),
                        add_time_to_date(post.index[-1],  12),
                        alpha=alpha, label='post', color='tab:blue')

                if include_day_before_in_post:
                        release_day = post.index[1]
                else:
                        release_day = post.index[0]

                ax.axvspan(add_time_to_date(release_day, -12),
                        add_time_to_date(release_day,  12),
                        alpha=alpha, color='tab:blue')
                
                # if include_day_before_in_post: # if we're including the day before the release date in the post window
                #         if len(post) > 1:
                #                 ax.axvspan(add_time_to_date(post.index[1], -12),
                #                         add_time_to_date(post.index[-1],  12),
                #                         alpha=0.4, label='post', color='tab:blue')

                #         ax.axvspan(add_time_to_date(post.index[0], -12),
                #                 add_time_to_date(post.index[0],  12),
                #                 alpha=0.6, label='post (release date)', color='tab:blue')

                # else: # if we're not (i.e. day before release date is in the pre window)
                #         if len(post) > 1:
                #                 ax.axvspan(add_time_to_date(post.index[1], -12),
                #                         add_time_to_date(post.index[-1],  12),
                #                         alpha=0.4, label='post', color='tab:blue')

                #         ax.axvspan(add_time_to_date(post.index[0], -12),
                #                 add_time_to_date(post.index[0],  12),
                #                 alpha=0.6, label='post (release date)', color='tab:blue')

                # whether the day before the release date is in the pre window doesn't effect how we display pre window
                # only matters for the post window (different colour)
                ax.axvspan(add_time_to_date(pre.index[0], 0),
                        add_time_to_date(pre.index[-1],  12),
                        alpha=alpha, label='pre', color='tab:orange')

        if show_means:
                ax.plot([add_time_to_date(post.index[0], -12), add_time_to_date(post.index[-1], 12)],
                        [post.mean(), post.mean()],
                        c='tab:blue', linestyle='--', label='post mean')

                ax.plot([add_time_to_date(pre.index[0], 0), add_time_to_date(pre.index[-1], 12)],
                        [pre.mean(), pre.mean()],
                        c='tab:orange', linestyle='--', label='pre mean')

        # doesn't make sense to show delta without means
        if show_means and show_delta:
                arrow = patches.FancyArrowPatch((add_time_to_date(post.index[0],-12), pre.mean()), (add_time_to_date(post.index[0],-12), post.mean()), 
                                                arrowstyle='<->', mutation_scale=20, color='r')
                ax.add_artist(arrow)
                # ax.annotate('test', xy=(.46, .3), xycoords='figure fraction', color='r')
                ax.annotate(rf'$\Delta$={np.around(delta, n_dp)}', xy=(add_time_to_date(post.index[0],-10), (pre.mean()+post.mean())/2 ), color='r', fontsize=12)

        ax.set_ylim(0,)

        plt.legend()
        return fig, ax