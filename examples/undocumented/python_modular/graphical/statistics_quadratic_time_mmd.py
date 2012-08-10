#
# This program is free software you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation either version 3 of the License, or
# (at your option) any later version.
#
# Written (C) 2012 Heiko Strathmann
#
from numpy import *
from pylab import *
from scipy import *

from shogun.Features import RealFeatures
from shogun.Features import DataGenerator
from shogun.Kernel import GaussianKernel
from shogun.Statistics import QuadraticTimeMMD
from shogun.Statistics import BOOTSTRAP, MMD2_SPECTRUM, MMD2_GAMMA, BIASED, UNBIASED

# parameters, change to get different results
m=100
dim=2
difference=0.5

# number of samples taken from null and alternative distribution
num_bootstrap=500

# use data generator class to produce example data
data=DataGenerator.generate_mean_data(m,dim,difference)

# create shogun feature representation
features=RealFeatures(data)

# use a kernel width of sigma=2, which is 8 in SHOGUN's parametrization
# which is k(x,y)=exp(-||x-y||^2 / tau), in constrast to the standard
# k(x,y)=exp(-||x-y||^2 / (2*sigma^2)), so tau=2*sigma^2
kernel=GaussianKernel(10,8)

# use biased statistic
mmd=QuadraticTimeMMD(kernel,features, m)
mmd.set_statistic_type(BIASED)

# sample alternative distribution
alt_samples=zeros(num_bootstrap)
for i in range(len(alt_samples)):
	data=DataGenerator.generate_mean_data(m,dim,difference)
	features.set_feature_matrix(data)
	alt_samples[i]=mmd.compute_statistic()

# sample from null distribution
# bootstrapping, biased statistic
mmd.set_null_approximation_method(BOOTSTRAP)
mmd.set_statistic_type(BIASED)
mmd.set_bootstrap_iterations(num_bootstrap)
null_samples_boot=mmd.bootstrap_null()

# sample from null distribution
# spectrum, biased statistic
if "sample_null_spectrum" in dir(QuadraticTimeMMD):
		mmd.set_null_approximation_method(MMD2_SPECTRUM)
		mmd.set_statistic_type(BIASED)
		null_samples_spectrum=mmd.sample_null_spectrum(num_bootstrap, m-10)/m
		
# fit gamma distribution, biased statistic
mmd.set_null_approximation_method(MMD2_GAMMA)
mmd.set_statistic_type(BIASED)
gamma_params=mmd.fit_null_gamma()
# sample gamma with parameters
null_samples_gamma=array([gamma(gamma_params[0], gamma_params[1]) for _ in range(num_bootstrap)])/m


# plot
figure()
title('Quadratic Time MMD')

# plot data of p and q
subplot(2,3,1)
plot(data[0][0:m], data[1][0:m], 'ro', label='$x$')
plot(data[0][m+1:2*m], data[1][m+1:2*m], 'bo', label='$x$')
legend()
title('Data')
xlabel('$x_1, y_1$')
ylabel('$x_2, y_2$')
grid(True)

# histogram of first data dimension and pdf
subplot(2,3,2)
hist(data[0], bins=50, alpha=0.5, facecolor='r', normed=True)
hist(data[1], bins=50, alpha=0.5, facecolor='b', normed=True)
xs=linspace(min(data[0])-1,max(data[0])+1, 50)
plot(xs,normpdf( xs, 0, 1), 'r', linewidth=3)
plot(xs,normpdf( xs, difference, 1), 'b', linewidth=3)
title('Data: $x_1, y_1$')
grid(True)

# compute threshold for test level
alpha=0.05
null_samples_boot.sort()
null_samples_spectrum.sort()
null_samples_gamma.sort()
thresh_boot=null_samples_boot[floor(len(null_samples_boot)*(1-alpha))];
thresh_spectrum=null_samples_spectrum[floor(len(null_samples_spectrum)*(1-alpha))];
thresh_gamma=null_samples_gamma[floor(len(null_samples_gamma)*(1-alpha))];

type_one_error_boot=sum(null_samples_boot<thresh_boot)/float(num_bootstrap)
type_one_error_spectrum=sum(null_samples_spectrum<thresh_boot)/float(num_bootstrap)
type_one_error_gamma=sum(null_samples_gamma<thresh_boot)/float(num_bootstrap)

# plot alternative distribution with threshold
subplot(2,3,4)
hist(alt_samples, 20, normed=True);
axvline(thresh_boot, 0, 1, linewidth=2, color='red')
type_two_error=sum(alt_samples<thresh_boot)/float(num_bootstrap)
title('Alternative Dist.\n' + 'Type II error is ' + str(type_two_error))
grid(True)

# compute range for all null distribution histograms
hist_range=[min([min(null_samples_boot), min(null_samples_spectrum), min(null_samples_gamma)]), max([max(null_samples_boot), max(null_samples_spectrum), max(null_samples_gamma)])]

# plot null distribution with threshold
subplot(2,3,3)
hist(null_samples_boot, 20, range=hist_range, normed=True);
axvline(thresh_boot, 0, 1, linewidth=2, color='red')
title('Bootstrapped Null Dist.\n' + 'Type I error is '  + str(type_one_error_boot))
grid(True)

# plot null distribution spectrum
subplot(2,3,5)
hist(null_samples_spectrum, 20, range=hist_range, normed=True);
axvline(thresh_spectrum, 0, 1, linewidth=2, color='red')
title('Null Dist. Spectrum\nType I error is '  + str(type_one_error_spectrum))
grid(True)

# plot null distribution gamma
subplot(2,3,6)
hist(null_samples_gamma, 20, range=hist_range, normed=True);
axvline(thresh_gamma, 0, 1, linewidth=2, color='red')
title('Null Dist. Gamma\nType I error is '  + str(type_one_error_gamma))
grid(True)

# pull plots a bit apart
subplots_adjust(hspace=0.5)
subplots_adjust(wspace=0.5)
show()