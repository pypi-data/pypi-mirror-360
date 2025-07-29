"""Tools module for Fesslix.

"""

# Fesslix - Stochastic Analysis
# Copyright (C) 2010-2025 Wolfgang Betz
#
# Fesslix is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Fesslix is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Fesslix.  If not, see <http://www.gnu.org/licenses/>. 

import fesslix as flx

import numpy as np
import scipy.stats
import scipy.optimize
import scipy.interpolate


##################################################
# working with files                             #
##################################################

def replace_in_template(fn_in,fn_out,dmap,var_indi_start="@{",var_indi_end="}"):
    """
    replaces expressions of the type @{VARNAME} in file fn_in with the values in dmap and writes the processed file to fn_out.

    Parameters
    ----------
    fn_in
        file name of the template input file
    fn_out
        file name of the output file to generate
    dmap
        all variables that can potentially appear in the file
    var_indi_start
        (default is '@{')
    var_indi_end
        (default is '}')
    """
    ## ===================
    ## Read the file fn_in
    ## ===================
    with open(fn_in, 'r') as fs:
        fstr = fs.read()

    ## =============================
    ## iterate over file and replace
    ## =============================
    while True:
        ## ------------------------------
        ## identify expression to replace
        ## ------------------------------
        pos1 = fstr.find(var_indi_start)
        if pos1 < 0:
            break
        pos2 = fstr.find(var_indi_end,pos1+len(var_indi_start))
        if pos2 < 0:
            raise NameError(f"ERROR 202505061220: opening '{var_indi_start}' without closing '{var_indi_end}'.")
        rexpr = fstr[pos1:pos2+len(var_indi_end)]
        ## ---------------------------
        ## identify property to insert
        ## ---------------------------
        vname = fstr[pos1+len(var_indi_start):pos2]
        if len(vname)==0:
            raise NameError(f"ERROR 202505061335: key must have a length larger then zero.")
        ## ---------------------------
        ## identify property to insert
        ## ---------------------------
        if vname[0]=='!':  ## value of a random variable
            rv_name = vname[1:]
            rvval = flx.get_rv_from_set(rv_name.lower()).get_value()
            vval = flx.Double2String(rvval)
        else:             ## key in dmap
            vval  = dmap[vname]
            if isinstance(vval,float):
                vval = flx.Double2String(vval)
        fstr = fstr.replace(rexpr, vval)
    ## =========================
    ## Save the processed string
    ## =========================
    with open(fn_out, 'w') as fs:
        fs.write(fstr)



##################################################
# discretization                                 #
##################################################

def detect_bounds_x(rv, config_dict, q_low=1e-3, q_up=None, mode='ignore'):
    """Makes sure that x_low and x_up are assigned in config_dict.

    """
    if q_up is None:
        q_up = 1.-q_low
    if 'x_low' not in config_dict:
        config_dict['x_low'] = rv.icdf(q_low)
    else:
        if (config_dict['x_low'] is None):
            config_dict['x_low'] = rv.icdf(q_low)
        else:
            if mode=='overwrite':
                config_dict['x_low'] = rv.icdf(q_low)
            elif mode=='minmax':
                config_dict['x_low'] = min(config_dict['x_low'], rv.icdf(q_low))
    if 'x_up' not in config_dict:
        config_dict['x_up'] = rv.icdf(q_up)
    else:
        if (config_dict['x_up'] is None):
            config_dict['x_up'] = rv.icdf(q_up)
        else:
            if mode=='overwrite':
                config_dict['x_up'] = rv.icdf(q_up)
            elif mode=='minmax':
                config_dict['x_up'] = max(config_dict['x_up'], rv.icdf(q_up))


def discretize_x(x_low, x_up, x_disc_N=int(1e3), x_disc_shift=False, x_disc_on_log=False):
    """Returns an array with discretized values for the x-axis."""
    if x_disc_on_log:
        if x_low<0. or x_up<0.:
            raise NameError(f'ERROR 202202071550: {x_low} {x_up}')
        x_low = np.log(x_low)
        x_up = np.log(x_up)
    x, dx = np.linspace(x_low,x_up,num=x_disc_N,endpoint=(not x_disc_shift),retstep=True)
    if x_disc_shift:
        x += dx/2
    if x_disc_on_log:
        x = np.exp(x)
    return x

def discretize_x_get_diff(x_low, x_up, x_disc_N=int(1e3), x_disc_on_log=False):
    """Returns an array with discretized values for the x-axis and additionally returns an vector with the size of the elements."""
    x = discretize_x(x_low=x_low, x_up=x_up, x_disc_N=x_disc_N, x_disc_shift=True, x_disc_on_log=x_disc_on_log)
    N = len(x)
    dx = np.empty(N)
    x_prev = x_low
    for i in range(N):
        if i+1<N:
            x_next = (x[i]+x[i+1])/2
        else:
            x_next = x_up
        dx[i] = (x_next-x_prev)
        x_prev = x_next
    return x, dx

def discretize_stdNormal_space(q_low=1e-3, q_up=None, x_disc_N=int(1e3)):
    """Returns an array with discretized values on U-space (standard Normal space).

    """
    if q_up is None:
        q_up = 1. - q_low
    xl = flx.cdfn_inv(q_low)
    xu = flx.cdfn_inv(q_up)
    return discretize_x(x_low=xl, x_up=xu, x_disc_N=x_disc_N, x_disc_shift=False, x_disc_on_log=False)



##################################################
# Working with float arrays                      #
##################################################

def fit_tail_to_data(tail_data_transformed, bound=None):
    res = { 'models':{} }
    def neg_log_likelihood(dist, data, params):
        return -np.sum(dist.logpdf(data, *params))
    ## ======================
    ## Fit generalized pareto
    ## ======================
    ## Fit GPD to the tail data
    gpd_params = scipy.stats.genpareto.fit(tail_data_transformed,floc=0.)
    res_ = { 'type':'genpareto', 'xi':gpd_params[0], 'scale':gpd_params[2] }
    res_['pdf_0'] = scipy.stats.genpareto.pdf(0., *gpd_params)
    ## Kolmogorov–Smirnov Test
    D_gpd, p_gpd = scipy.stats.kstest(tail_data_transformed, 'genpareto', args=gpd_params)
    res_['kstest_D'] = D_gpd
    res_['kstest_p'] = p_gpd
    ## Log-Likelihood
    res_['nll'] = neg_log_likelihood(scipy.stats.genpareto, tail_data_transformed, gpd_params)
    ## store results
    res['models']['genpareto'] = res_
    ## ==========================
    ## Fit lognormal distribution
    ## ==========================
    ## Fit log-Normal distribution to the tail data
    logn_params = scipy.stats.lognorm.fit(tail_data_transformed,floc=0.)
    res_ = { 'type':'logn', 'lambda':logn_params[2], 'zeta':logn_params[0] }
    ## Kolmogorov–Smirnov Test
    D_logn, p_logn = scipy.stats.kstest(tail_data_transformed, 'lognorm', args=logn_params)
    res_['kstest_D'] = D_logn
    res_['kstest_p'] = p_logn
    ## Log-Likelihood
    res_['nll'] = neg_log_likelihood(scipy.stats.lognorm, tail_data_transformed, logn_params)
    ## store results
    res['models']['logn'] = res_
    ## ==========================
    ## fit beta distribution in case there is a bound
    ## ==========================
    if bound is not None:
        beta_params = scipy.stats.beta.fit(tail_data_transformed,floc=0.,fscale=bound)
        res_ = { 'type':'beta', 'alpha':beta_params[0], 'beta':beta_params[1], 'a':beta_params[2], 'b':beta_params[3] }
        ## Kolmogorov–Smirnov Test
        D_beta, p_beta = scipy.stats.kstest(tail_data_transformed, 'beta', args=beta_params)
        res_['kstest_D'] = D_beta
        res_['kstest_p'] = p_beta
        ## Log-Likelihood
        res_['nll'] = neg_log_likelihood(scipy.stats.beta, tail_data_transformed, beta_params)
        ## store results
        res['models']['beta'] = res_
    ## ==========================
    ## Select model with best fit
    ## ==========================
    best_fit = None
    best_model = None
    for model_type, model in res['models'].items():
        if best_fit is None:
            best_fit = model['nll']
            best_model = model_type
        else:
            if best_fit > model['nll']:
                best_fit = model['nll']
                best_model = model_type
    res['best_model'] = best_model  ## model with best fit
    res['use_model'] = best_model   ## use the model with best fit
    return res



def discretize_x_from_data(data,config={}, data_is_sorted=False, lower_bound=None, upper_bound=None):
    """discretize parameter space based on a data array"""
    res = {}
    ## ===============
    ## Sort data array
    ## ===============
    if data_is_sorted:
        sdata = data
    else:
        sdata = np.sort(data, axis=None)
    N_total = sdata.size
    res['N_total'] = N_total    ## total number of samples considered
    ## ========================
    ## Assemble p_vec and q_vec
    ## ========================
    mode = 'adaptive'
    if 'mode' in config:
        mode = config['mode']

    def assemble_q_from_p(p_vec):
        N_bins = len(p_vec)-1
        q_vec = np.empty(N_bins+1)
        for i in range(N_bins+1):
            p = p_vec[i]
            if p<=0.:
                if lower_bound is None:
                    q_vec[i] = sdata[0] - (sdata[1]-sdata[0])/2
                else:
                    q_vec[i] = lower_bound
                    if lower_bound>sdata[0]:
                        raise NameError(f"ERROR 202504250831: lower bound is larger than minimum in data. {lower_bound = }, {sdata[0] = }")
            elif p>=1.:
                if upper_bound is None:
                    q_vec[i] = sdata[-1] + (sdata[-1]-sdata[-2])/2
                else:
                    q_vec[i] = upper_bound
                    if upper_bound<sdata[-1]:
                        raise NameError(f"ERROR 202504250832: upper bound is smaller than maximum in data. {upper_bound = }, {sdata[-1] = }")
            else:
                ## linear interpolation
                nf = p*N_total - 0.5
                j = int(nf)
                nf -= j
                q_vec[i] = sdata[j] + (sdata[j+1]-sdata[j])*nf
        return q_vec

    ## -----------------
    ## equidistant p_vec
    ## -----------------
    if mode=='equidist_p':
        ## ---------------------
        ## select number of bins
        ## ---------------------
        if 'N_bins' in config:
            N_bins = config['N_bins']
        else:
            N_points_per_bin = 100 # default
            if 'N_points_per_bin' in config:
                N_points_per_bin = config['N_points_per_bin']
            if N_total < N_points_per_bin*5:
                raise NameError(f'ERROR 202504241439: Not enough data. {N_total = }, {N_points_per_bin = }')
            N_bins = int(N_total / N_points_per_bin)
        ## --------------------
        ## assign probabilities
        ## --------------------
        p_vec = discretize_x(x_low=0., x_up=1., x_disc_N=N_bins+1, x_disc_shift=False, x_disc_on_log=False)
        q_vec = assemble_q_from_p(p_vec)
    ## -------------------
    ## pre-specified p_vec
    ## -------------------
    elif mode=='fixed_p':
        ## ensure pre-specified p_vec is sorted
        p_vec = np.sort(config['p_vec'], axis=None)
        N_bins = p_vec.size()-1
        q_vec = assemble_q_from_p(p_vec)
    ## ----------------
    ## adaptive spacing
    ## ----------------
    elif mode=='adaptive':
        ## --------------------------
        ## retrieve input from config
        ## --------------------------
        ## minimum number of points per bin
        N_points_per_bin_min = 100
        if 'N_points_per_bin_min' in config:
            N_points_per_bin_min = config['N_points_per_bin_min']
        ## minimum bin size
        if 'dx_min' in config:
            dx_min = config['dx_min']
        else:
            dx_min = (sdata[int(0.75*N_total)]-sdata[int(0.25*N_total)])/8
        ## --------------------------
        ## assemble q_vec
        ## --------------------------
        ## ........................
        ## define helping functions
        ## ........................
        N_sum = 0
        N_low = 0
        q_vec_low = []
        b_state_low = False
        N_up  = 0
        q_vec_up  = []
        b_state_up = False
        adapt_finalize = False
        def add2lower():
            nonlocal N_sum
            nonlocal N_low
            nonlocal b_state_low
            nonlocal adapt_finalize
            ## propose next bin size
            N_next = N_points_per_bin_min
            ## ensure that it is larger than dx_min
            while True:
                x_up = (sdata[N_next+N_low-1]+sdata[N_next+N_low])/2
                dx = x_up - q_vec_low[-1]
                if dx>dx_min:
                    break
                if N_sum+N_next>=N_total:
                    adapt_finalize = True
                    break
                N_next += 1
            if not adapt_finalize:
                q_vec_low.append(x_up)
            N_low += N_next
            N_sum += N_next
            b_state_low = N_next>N_points_per_bin_min
            return b_state_low
        def add2upper():
            nonlocal N_sum
            nonlocal N_up
            nonlocal b_state_up
            nonlocal adapt_finalize
            ## propose next bin size
            N_next = N_points_per_bin_min
            ## ensure that it is larger than dx_min
            while True:
                x_low = (sdata[-(N_next+N_up)]+sdata[-(N_next+N_up+1)])/2
                dx = q_vec_up[-1] - x_low
                if dx>dx_min:
                    break
                if N_sum+N_next>=N_total:
                    adapt_finalize = True
                    break
                N_next += 1
            if not adapt_finalize:
                q_vec_up.append(x_low)
            N_up += N_next
            N_sum += N_next
            b_state_up = N_next>N_points_per_bin_min
            return b_state_up
        ## ..........................
        ## » start with bounds
        ## ..........................
        if lower_bound is None:
            q_vec_low.append( sdata[0] - (sdata[1]-sdata[0])/2 )
        else:
            q_vec_low.append( lower_bound )
            if lower_bound>sdata[0]:
                raise NameError(f"ERROR 202504282026: lower bound is larger than minimum in data. {lower_bound = }, {sdata[0] = }")
        if upper_bound is None:
            q_vec_up.append( sdata[-1] + (sdata[-1]-sdata[-2])/2 )
        else:
            q_vec_up.append( upper_bound )
            if upper_bound<sdata[-1]:
                raise NameError(f"ERROR 202504282113: upper bound is smaller than minimum in data. {upper_bound = }, {sdata[-1] = }")
        ## ............................
        ## » gradually decrease the main body
        ## ............................
        while not adapt_finalize:
            ## ........................
            ## make sure that we have enough remaining space for discretization
            ## ........................
            if N_sum+2*N_points_per_bin_min>N_total:
                adapt_finalize = True
            if q_vec_up[-1]-q_vec_low[-1]<2*dx_min:
                adapt_finalize = True
            if adapt_finalize:
                break
            ## ........................
            ## decrease from below and from up
            ## ........................
            if not b_state_low:
                add2lower()
                if adapt_finalize:
                    break
            if not b_state_up:
                add2upper()
                if adapt_finalize:
                    break
            ## ........................
            ## attempt discretization of main body
            ## ........................
            if b_state_low and b_state_up:
                N_ = int((q_vec_up[-1]-q_vec_low[-1])/dx_min)
                mesh_vec = discretize_x(x_low=q_vec_low[-1], x_up=q_vec_up[-1], x_disc_N=N_+1, x_disc_shift=False, x_disc_on_log=False)[1:-1]
                for mesh_point in mesh_vec:
                    if np.count_nonzero( np.logical_and( sdata>q_vec_low[-1], sdata<mesh_point) )<N_points_per_bin_min:
                        b_state_low = False
                        break
                    if np.count_nonzero( np.logical_and( sdata<q_vec_up[-1], sdata>mesh_point) )<N_points_per_bin_min:
                        b_state_up = False
                        break
                    q_vec_low.append( mesh_point )
                if b_state_low and b_state_up:
                    adapt_finalize = True
        ## ........................
        ## do the actual assembly
        ## ........................
        q_vec = np.empty( len(q_vec_low)+len(q_vec_up) )
        i = 0
        for q in q_vec_low:
            q_vec[i] = q
            i += 1
        for q in reversed(q_vec_up):
            q_vec[i] = q
            i += 1
        ## --------------------------
        ## assemble p_vec
        ## --------------------------
        p_vec = np.empty( len(q_vec) )
        for i in range(0,len(q_vec)):
            p_vec[i] = np.count_nonzero( sdata<=q_vec[i] )/float(N_total)
        if p_vec[0] != 0.:
            raise NameError(f"ERROR 202504290823: {p_vec[0]}, {q_vec}")
        if p_vec[-1]!=1.:
            raise NameError(f"ERROR 202504290822: {p_vec[-1]-1.}")
        N_bins = len(p_vec)-1
    ## -----------------
    ## unknown mode
    ## -----------------
    else:
        raise NameError(f"ERROR 202504280813: unknown mode ('{mode}' in config.")
    ## ========================
    ## take tail-specific properties into account
    ## ========================
    ## ----------
    ## upper tail
    ## ----------
    if 'tail_upper' in config:
        tail_prop = config['tail_upper']
        tail_p = tail_prop['p']
        tail_x = tail_prop['x']
        j = None
        for i in range(len(p_vec)):
            if p_vec[i]>=tail_p or q_vec[i]>=tail_x:
                j = i
                break
        if j==None:
            raise NameError(f"ERROR 202505081442")
        p_vec_ = p_vec
        q_vec_ = q_vec
        N_bins = j+1
        p_vec = np.empty( N_bins+1 )
        p_vec[:j] = p_vec_[:j]
        p_vec[-1] = 1.
        p_vec[-2] = tail_p
        q_vec = np.empty( N_bins+1 )
        q_vec[:j] = q_vec_[:j]
        q_vec[-2] = tail_x
        q_vec[-1] = q_vec_[-1]
        if q_vec[-1]<=q_vec[-2]:
            q_vec[-1] = q_vec[-2] + 1e-6
    ## ----------
    ## lower tail
    ## ----------
    if 'tail_lower' in config:
        tail_prop = config['tail_lower']
        tail_p = tail_prop['p']
        tail_x = tail_prop['x']
        j = None
        for i in range(len(p_vec)):
            if p_vec[i]>tail_p or q_vec[i]>tail_x:
                j = i
                break
        if j==None:
            raise NameError(f"ERROR 202505081535")
        p_vec_ = p_vec
        q_vec_ = q_vec
        N_bins = j+1
        N_bins = N_bins + 2 - j
        p_vec = np.empty( N_bins+1 )
        p_vec[2:] = p_vec_[j:]
        p_vec[0]  = 0.
        p_vec[1]  = tail_p
        q_vec = np.empty( N_bins+1 )
        q_vec[2:] = q_vec_[j:]
        q_vec[1]  = tail_x
        q_vec[0]  = q_vec_[0]
        if q_vec[1]<=q_vec[0]:
            q_vec[0] = q_vec[1] - 1e-6
    ## ========================
    ## general consistency checks
    ## ========================
    ## -----
    ## p_vec
    ## -----
    ## check bounds of p_vec
    if p_vec[0]!=0. or p_vec[-1]!=1.:
        raise NameError(f"ERROR 202504241513: First and last value of 'p_vec' must be 0.0 and 1.0, respectively.")
    ## check values of p_vec
    rc_end = N_bins+1
    rc_start = 0
    if 'tail_lower' in config:
        rc_start = 2
    if 'tail_upper' in config:
        rc_end -= 2
    for i in range(rc_start,rc_end) :
        p_target = np.count_nonzero(sdata<=q_vec[i])/float(N_total)
        if abs(p_vec[i]-p_target)>1e-5:
            raise NameError(f"ERROR 202504280845: {i = }, {N_bins = }, {(p_vec[i]-p_target)}, {p_vec[i]}, {p_target}")
    res['p_vec'] = p_vec    ## vector of probabilities (for quantile evaluation)
    ## ------
    ## N_bins
    ## ------
    ## ensure 'sufficient' number of bins
    if N_bins < 5:
        raise NameError(f'ERROR 202504250716: Not enough bins. {N_bins = }')
    res['N_bins'] = N_bins
    ## -----
    ## q_vec
    ## -----
    ## make sure that only unique values are in q_vec
    for i in range(N_bins):
        if q_vec[i]==q_vec[i+1]:
            raise NameError(f"ERROR 202504250837: quantiles are not unique. {i = }")
    res['q_vec'] = q_vec    ## vector of quantiles (associated with p_vec)
    ## ========================
    ## Assemble N_vec
    ## ========================
    N_vec = np.empty(N_bins,dtype=int)
    for i in range(N_bins):
        N_vec[i] = np.count_nonzero( np.logical_and( (sdata>q_vec[i]), (sdata<=q_vec[i+1]) ) )
    ## make sure total number of samples is consistent
    if sum(N_vec)!=N_total:
        raise NameError(f"ERROR 202504250841: {sum(N_vec)}, {N_vec = }")
    res['N_vec'] = N_vec
    ## ===============================================
    ## fit beta/linear distribution to individual bins
    ## ===============================================
    def _fit_linear_inclined(x_data):
        def neg_log_likelihood(m):
            # Keep inside domain to avoid log of negative numbers
            if not (-1 <= m <= 1):
                return np.inf
            pdf_values = 1 + m * (2 * x_data - 1)
            if np.any(pdf_values <= 0):
                return np.inf
            return -np.sum(np.log(pdf_values))

        result = scipy.optimize.minimize_scalar(neg_log_likelihood, bounds=(-1., 1.), method='bounded')
        return result.x
    bin_rvbeta_params = np.ones(N_bins*2)*-1.
    bin_rvlinear_params = np.zeros(N_bins)
    for i in range(N_bins):
        ## transform bin-data to [0.,1.] values
        x_low = q_vec[i]
        x_up  = q_vec[i+1]
        if (x_up-x_low)<1e-12: ## avoid fit if values are 'almost' equivalent
            continue
        data_bin = sdata[np.logical_and( (x_low<sdata), (x_up>sdata) )]
        data_bin -= x_low
        data_bin /= (x_up-x_low)
        ## fit distribution
        beta_params = scipy.stats.beta.fit(data_bin,floc=0.,fscale=1.)
        bin_rvbeta_params[i*2] = beta_params[0]
        bin_rvbeta_params[i*2+1] = beta_params[1]
        ## fit linear distribution
        bin_rvlinear_params[i] = _fit_linear_inclined(data_bin)
    res['bin_rvbeta_params'] = bin_rvbeta_params
    res['bin_rvlinear_params'] = bin_rvlinear_params
    ## ==============================================
    ## fit upper tail
    ## ==============================================
    Q_tail = q_vec[-2]
    ## transform data
    tail_data_transformed = None
    if 'tail_upper' in config:
        if 'data' in config['tail_upper']:
            tail_data_transformed = config['tail_upper']['data']
    if tail_data_transformed is None:
        tail_data_transformed = sdata
    tail_data_transformed = tail_data_transformed[tail_data_transformed>Q_tail] - Q_tail
    ## consistency checks
    if np.count_nonzero(tail_data_transformed<=0.)>0:
        raise NameError(f"ERROR 202505081612: {np.count_nonzero(tail_data_transformed<=0.)}")
    ## identify if there is a bound
    if upper_bound is None:
        bound_transformed = upper_bound
    else:
        bound_transformed = upper_bound - Q_tail
    ## perform the fitting
    res['tail_upper'] = fit_tail_to_data(tail_data_transformed,bound_transformed)
    ## ==============================================
    ## fit lower tail
    ## ==============================================
    Q_tail = q_vec[1]
    ## transform data
    tail_data_transformed = None
    if 'tail_lower' in config:
        if 'data' in config['tail_lower']:
            tail_data_transformed = config['tail_lower']['data']
    if tail_data_transformed is None:
        tail_data_transformed = sdata
    tail_data_transformed = Q_tail - tail_data_transformed[tail_data_transformed<Q_tail]
    ## consistency checks
    if np.count_nonzero(tail_data_transformed<=0.)>0:
        raise NameError(f"ERROR 202505081613")
    ## identify if there is a bound
    if lower_bound is None:
        bound_transformed = lower_bound
    else:
        bound_transformed = Q_tail - lower_bound
    ## perform the fitting
    res['tail_lower'] = fit_tail_to_data(tail_data_transformed,bound_transformed)
    ## ==============================================
    ## return
    ## ==============================================
    res['type'] = 'quantiles'
    res['interpol'] = "uniform"
    res['use_tail_fit'] = True
    return res



def fit_pdf_based_on_qvec(data, config):
    """Fit PDF by linear interpolation based on q_vec."""
    data_in = data
    Pr_in   = 1.
    x_vec   = config['q_vec']
    i_start = 0
    i_end   = len(x_vec)
    pdf_vec = np.ones(len(x_vec))
    ## ==============================================
    ## handle tails
    ## ==============================================
    if config['use_tail_fit']:
        p_vec = config['p_vec']
        ## ----------
        ## lower tail
        ## ----------
        has_lower = False
        if 'tail_lower' in config:
            tail_dict = config['tail_lower']
            tail_config = tail_dict['models'][tail_dict['use_model']]
            Pr_in -= p_vec[1]
            data_in = data_in[ data_in>x_vec[1] ]
            x_vec = x_vec[1:]
            i_end -= 1
            pdf_vec = pdf_vec[1:]
            has_lower = True
            if 'pdf_0' in tail_config:
                pdf_vec[0] = tail_config['pdf_0']*p_vec[1]
                i_start = 1
        ## ----------
        ## upper tail
        ## ----------
        has_upper = False
        if 'tail_upper' in config:
            tail_dict = config['tail_upper']
            tail_config = tail_dict['models'][tail_dict['use_model']]
            Pr_in -= p_vec[-1] - p_vec[-2]
            data_in = data_in[ data_in<=x_vec[-2] ]
            x_vec = x_vec[:-1]
            i_end -= 1
            pdf_vec = pdf_vec[:-1]
            has_upper = True
            if 'pdf_0' in tail_config:
                pdf_vec[-1] = tail_config['pdf_0']*(p_vec[-1] - p_vec[-2])
                i_end -= 1
    if len(pdf_vec)!=len(x_vec):
        raise NameError(f"ERROR 202504280926")
    ## ==============================================
    ## initial value
    ## ==============================================
    p0 = pdf_vec[i_start:i_end]
    p0 /= x_vec[i_end] - x_vec[i_start]
    ## ==============================================
    ## define negative log likelihood
    ## ==============================================
    def neg_log_likelihood(p):
        pdf_vec[i_start:i_end] = p
        # if p contains negative values, set negative log-likelihood to +∞
        if np.any(pdf_vec < 0.):
            return np.inf
        # define the linear interpolation
        pdf_interp = scipy.interpolate.interp1d(x_vec, pdf_vec, kind='linear', fill_value=0.0, bounds_error=False)
        # get values at data-points
        pdf_vals = pdf_interp(data_in)
        # if pdf_vals  <= 0, the log is not defined
        if np.any(pdf_vals <= 0):
            return np.inf
        return -np.sum(np.log(pdf_vals))
    ## ==============================================
    ## define constraint
    ## ==============================================
    # constraint: integral over PDF = 1
    def integral_constraint(p):
        pdf_vec[i_start:i_end] = p
        return np.trapz(pdf_vec, x_vec) - Pr_in
    constraints = ({
        'type': 'eq',
        'fun': integral_constraint
    })
    bounds = [(0., None) for _ in range(len(p0))]  # for all p in pdf_vec >= 0
    ## ==============================================
    ## perform the optimization
    ## ==============================================
    result = scipy.optimize.minimize(
        neg_log_likelihood,
        p0,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints,
        options={'disp': True}
    )
    if not result.success:
        raise RuntimeError("202504280945: optimization failed » " + result.message)
    pdf_vec[i_start:i_end] = result.x
    ## ==============================================
    ## store result in config
    ## ==============================================
    config['pdf_vec'] = np.zeros(len(config['q_vec']))
    if has_lower:
        i_start = 1
    else:
        i_start = 0
    i_end = len(config['q_vec'])
    if has_upper:
        i_end -= 1
    config['pdf_vec'][i_start:i_end] = pdf_vec
    config['interpol'] = 'pdf_linear'
    return None











