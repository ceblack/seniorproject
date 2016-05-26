#!/usr/bin/env python3
import sys
import os
sys.path.insert(1,os.path.join(sys.path[0], '..'))
import numpy as np
import pandas as pd
from pykalman import KalmanFilter

class Regression(object):
    """
    y = beta * x + alpha
    """

    def __init__(self, initial_x, initial_y, date, delta=1e-5):
        trans_cov = delta / (1 - delta) * np.eye(2)
        xList = []
        for x in initial_x:
            xList.append([[x,1.]])
        obs_mat = np.vstack([xList])

        self.kf = KalmanFilter(n_dim_obs=1, n_dim_state=2,
                               initial_state_mean=np.zeros(2),
                               initial_state_covariance=np.ones((2, 2)),
                               transition_matrices=np.eye(2),
                               observation_matrices=obs_mat,
                               observation_covariance=1.0,
                               transition_covariance=trans_cov)
        state_means, state_covs = self.kf.filter(np.array(initial_y))
        self.means = pd.DataFrame(state_means,
                                  columns=['beta', 'alpha'])
        self.state_cov = state_covs[-1]

    def update(self, observations, date):
        x = observations[0]
        y = observations[1]
        mu, self.state_cov = self.kf.filter_update(self.state_mean, self.state_cov, y,
                                                   observation_matrix=np.array([[x, 1.0]]))
        mu = pd.Series(mu, index=['beta', 'alpha'],
                       name=date)
        self.means = self.means.append(mu)

    def get_spread(self, observations):
        x = observations[0]
        y = observations[1]
        return y - (self.means.beta * x + self.means.alpha)

    @property
    def state_mean(self):
        return self.means.iloc[-1]
