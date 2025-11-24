from scipy.stats import norm
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def logistic(x, L, k, x0, sigma=None):
    """Logistic function."""
    y = L / (1 + np.exp(-k * (x - x0)))
    if sigma is not None:
        y += norm(0, sigma).rvs(len(x))
    return y

# generate data
n = 20
sigma = 3
x = np.linspace(0, 8, n)
L = 10
k = 1
x0 = 4
y = logistic(x, L, k, x0, sigma=sigma)

# define priors
L_mean = 10
L_std = 1
k_mean = 1
k_std = 0.3
x0_mean = 4
x0_std = 1



# calculate likelihoods and posteriors by sampling from priors
df = pd.DataFrame(columns=['L', 'k', 'x0', 'likelihood', 'posterior'])
n = 10000
# allocate df
df = pd.DataFrame(index=range(n), columns=['L', 'k', 'x0', 'likelihood', 'posterior'])
for i in range(n):
    L_sample = norm(L_mean, L_std).rvs()
    k_sample = norm(k_mean, k_std).rvs()
    x0_sample = norm(x0_mean, x0_std).rvs()
    y_pred = logistic(x, L_sample, k_sample, x0_sample)
    likelihood = norm(y_pred, sigma).pdf(y).prod()
    df.loc[i, 'L'] = L_sample
    df.loc[i, 'k'] = k_sample
    df.loc[i, 'x0'] = x0_sample
    df.loc[i, 'likelihood'] = likelihood

    prior = (norm(L_mean, L_std).pdf(L_sample) *
             norm(k_mean, k_std).pdf(k_sample) *
             norm(x0_mean, x0_std).pdf(x0_sample))
    posterior = prior * likelihood
    df.loc[i, 'posterior'] = posterior
    

# normalize posteriors
df['posterior'] /= df['posterior'].sum()

# MPE, MLE estimates
mpe_idx = df['posterior'].astype(float).idxmax()
mle_idx = df['likelihood'].astype(float).idxmax()
mpe_params = df.loc[mpe_idx, ['L', 'k', 'x0']]
mle_params = df.loc[mle_idx, ['L', 'k', 'x0']]

# plot

plt.figure(figsize=(12, 8))
x_fit = np.linspace(0, 8, 100)
y_mpe = logistic(x_fit, mpe_params['L'], mpe_params['k'], mpe_params['x0'])
y_mle = logistic(x_fit, mle_params['L'], mle_params['k'], mle_params['x0'])
plt.scatter(x, y, label='Data', color='black')
plt.plot(x_fit, y_mpe, label='MPE Fit', color='red')
plt.plot(x_fit, y_mle, label='MLE Fit', color='blue', linestyle='--')

y_true = logistic(x_fit, L, k, x0)
plt.plot(x_fit, y_true, label='True Curve', color='orange', linestyle='-.')

plt.xlabel('x')
plt.ylabel('y')
plt.title('Bayesian S-Curve Regression: MPE vs MLE')
plt.legend()
plt.show()