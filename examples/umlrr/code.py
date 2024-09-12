
'''Parameters'''

params = dict()

#Data pertaining to one-group energy neutron balance
params['gen_time']     = 1.0e-4  # s
params['beta']         = 6.5e-3  # 
#params['diff_coeff']   = 0.84 # cm
#params['core radius']  = 1.8e+2 # cm
#params['core_height']  = 2.8e+2 # cm
#params['k_infty']      = 1.118
#params['Sigma_a']      = 2.74e-4 # 1/cm

#Delayed neutron emission
params['species_decay']     = [0.0124, 0.0305, 0.111, 0.301, 1.14, 3.01] # 1/sec
params['species_rel_yield'] = [0.033, 0.219, 0.196, 0.395, 0.115, 0.042]

params['alpha_n'] = -5e-4 # control rod reactivity worth
params['alpha_tn_fake'] = -1e-4/20# -1.0e-6

params['n_dens_ss_operation'] = 1e15 * 1e4 / 2200  # neutrons/m^2

#Data pertaining to two-temperature heat balances
params['fis_energy']           = 180 * 1.602e-13 # J/fission 
#params['enrich']               = 3./100.
#params['fuel_mat_mass_dens']   = 10.5 # g/cc
#params['moderator_fuel_ratio'] = 387 # atomic number concentration ratio
params['sigma_f_o']            = 586.2 * 100 * 1e-30 # m2
params['temp_o']               = 20 + 273.15 # K
params['temp_c_ss_operation']  = 550 + 273.15 # K desired ss operation temp of coolant
params['temp_f_safe_max']      = 1100 + 273.15 # K
params['thermal_neutron_velo'] = 2200 # m/s

params['fis_nuclide_num_dens_fake'] = 1e17/40 * 1.0e+6 # (fissile nuclei)/m3

#params['q_c'] = 0  # volumetric flow rate

params['fuel_dens']   = 2500 # kg/m3
params['cp_fuel']     = 720 # J/(kg K)
params['fuel_volume'] = 1.5 # m3

params['coolant_dens']   = 0.1786 #  kg/m3
params['cp_coolant']     = 20.78 / 4e-3 # J/(mol K) - > J/(kg K)
params['coolant_volume'] = 0.8 # m3

params['ht_coeff'] = 800 # W/K

#params['fis_prod_beta_energy_rate']  = 1.26 * 1.602e-13 # J/(fission sec) 1.26 t^-1.2 (t in seconds)
#params['fis_prod_gamma_energy_rate'] = 1.40 * 1.602e-13 # J/(fission sec) 1.40 t^-1.2 (t in seconds)

params['strict'] = True # apply strict testing to some quantities

# Operations
params['hx_malfunction'] = False
params['hx_malfunction_start_time']  = 0
params['hx_malfunction_down_time']   = 0
params['hx_malfunction_temperature'] = 0

params['hx_breakdown'] = False
params['hx_breakdown_start_time'] = 0
params['hx_breakdown_down_time']  = 0

params['shutdown']      = False
params['shutdown_time'] = 0.0 # s
params['rho_shutdown']  = 0.0 # s
params['hx_relax_time'] = 0 # s

'''Setup function for delayed neutron species concentrations at steady state'''

def setup_initial_conditions(params):

    # setup the steady state for the delayed-neutron precursors

    n_species = len(params['species_decay'])

    assert len(params['species_rel_yield']) == n_species

    import numpy as np
    c_vec_0 = np.zeros(n_species,dtype=np.float64) # initialize conentration vector

    species_decay = params['species_decay'] # retrieve list of decay constants
    lambda_vec    = np.array(species_decay) # create a numpy vector

    species_rel_yield = params['species_rel_yield']
    beta_vec = np.array(species_rel_yield) * beta  # create the beta_i's vector

    gen_time = params['gen_time'] # retrieve neutron generation time

    n_ss = params['n_ss']
    c_vec_ss = beta_vec/lambda_vec/gen_time * n_ss # compute the steady state precursors number density

    params['c_vec_ss'] = c_vec_ss

    # setup initial condition for variables
    params['n_0']     = n_ss
    params['c_vec_0'] = c_vec_ss
    params['rho_0']   = params['reactivity']

    params['temp_f_0'] = params['temp_0'] + 10.0 # helps startup integration
    params['temp_c_0'] = params['temp_0']

    return

'''Reactivity coefficient function'''

def alpha_tn_func(temp, params):
    '''
    Place holder for implementation
    '''
    alpha_tn = params['alpha_tn_fake']

    return alpha_tn

'''Reactivity function'''

def rho_func( time, n_dens, temp, params ):
    '''
    Reactivity function.

    Parameters
    ----------
    t: float, required
        Time.
    temp_f: float, required
        Temperature at time t.
    params: dict, required
        Dictionary of quantities. It must have a `'rho_0'` key/value pair.

    Returns
    -------
    rho_t: float
        Value of reactivity.

    Examples
    --------
    '''

    if params['shutdown'] == False or (params['shutdown'] == True and time < params['shutdown_time']):
        rho_0 = params['rho_0']
        n_dens_ref = params['n_dens_ref']
        temp_ref = params['temp_c_ss_operation']
        alpha_n  = params['alpha_n']
        alpha_tn = alpha_tn_func( temp, params )
    elif params['shutdown'] == True and time >= params['shutdown_time']:
        rho_0 = params['rho_shutdown']
        n_dens_ref = 0.0
        temp_ref = params['temp_o']
        alpha_n  = 0
        alpha_tn = 0
    else:
        assert False

    rho_t = rho_0 + alpha_n * (n_dens - n_dens_ref) + alpha_tn * (temp - temp_ref)

    beta = params['beta']

    if params['strict'] == True:
        assert rho_t/beta < 1,'rho/beta = %r at time = %r; rho_0 = %r; rho_n = %r; rho_tn = %r'%                ( rho_t/beta, time, rho_0/beta, alpha_n*(n_dens - n_dens_ref)/beta,                 alpha_tn*(temp - temp_ref)/beta )

    return rho_t

'''Source function'''

def q_source( t, params ):
    '''
    Neutron source delta function.

    Parameters
    ----------
    t: float, required
        Time.
    params: dict, required
        Dictionary of quantities. It must have a `'q_0'` key/value pair.

    Returns
    -------
    q: float
        Value of source.

    Examples
    --------
    '''

    q = 0.0
    q_0 = params['q_0']

    if t <= 1e-5: # small time value
        q = q_0
    else:
        q = 0.0

    return q

'''Effective microscopic fission cross section'''

def sigma_fis_func( temp, params ):
    '''
    Place holder for implementation
    '''

    sigma_f_fake = params['sigma_f_o']

    return sigma_f_fake

'''Nuclear heating power density function'''

def nuclear_pwr_dens_func( time, temp, n_dens, params ):
    '''
    Place holder for implementation
    '''

    rxn_heat = params['fis_energy'] # get fission reaction energy J per reaction

    sigma_f = sigma_fis_func( temp, params ) # m2

    fis_nuclide_num_dens = params['fis_nuclide_num_dens_fake'] #  #/m3

    Sigma_fis = sigma_f * fis_nuclide_num_dens # macroscopic cross section

    v_o = params['thermal_neutron_velo'] # m/s

    neutron_flux = n_dens * params['n_dens_ss_operation'] * v_o

    # reaction rate density
    rxn_rate_dens = Sigma_fis * neutron_flux

    # nuclear power source
    q3prime = - rxn_heat * rxn_rate_dens # exothermic reaction W/m3

    if params['strict'] == True:
        assert q3prime <= 0.0,"time = %r, q''' = %r, n_dens = %r"%(time,q3prime,n_dens)

    return q3prime

'''Cooling heat rate'''

def heat_sink_rate( time, temp_f, temp_c, params):

    ht_coeff = params['ht_coeff']

    q_f = - ht_coeff * (temp_f - temp_c)

    if params['strict'] == True:
        assert q_f <= 0.0,'q_f = %r at time = %r; temp_f = %r, temp_c = %r'%(q_f,time,temp_f,temp_c)

    return q_f

'''Coolant Inlet Temperature'''

def coolant_inlet_temp_func( time, temp_f, temp_c, params ):

    import math

    if params['shutdown'] == False or (params['shutdown'] == True and time < params['shutdown_time']):
        if temp_c < params['temp_c_ss_operation']:
            temp_in = temp_c
        else:
            temp_in = params['temp_c_ss_operation']
    elif params['shutdown'] == True and time >= params['shutdown_time']:
        temp_in = params['temp_o'] +                   ( params['temp_c_ss_operation'] - params['temp_o'] ) * math.exp(-(time-params['shutdown_time'])/params['hx_relax_time'])
    else:
        assert False

    # protect the fuel
    if params['strict'] == True:
        assert temp_f <= params['temp_f_safe_max'],'Above max. fuel temp. = %r [C], at time = %r [h]'%            (temp_f-273.15,time/3600)

    if params['hx_malfunction'] == True:
        start_time = params['hx_malfunction_start_time']
        end_time   = start_time + params['hx_malfunction_down_time']
        if time >= start_time and time <= end_time:
            temp_in = params['hx_malfunction_temperature'] # external heat exchanger malfunction

    if params['hx_breakdown'] == True:
        start_time = params['hx_breakdown_start_time']
        end_time   = start_time + params['hx_breakdown_down_time']
        if time >= start_time and time <= end_time:
            temp_in = temp_c         # external heat exchanger breakdown

    return temp_in

'''ODE function'''

def f_vec( time, u_vec, params ):  
    
    import numpy as np
    #assert np.all(u_vec >= 0.0),'time = %r; u_vec = %r'%(time,u_vec)

    n_dens = u_vec[0] # get neutron dens

    c_vec = u_vec[1:-2] # get delayed neutron emitter concentration

    temp_f = u_vec[-2] # get temperature of fuel

    temp_c = u_vec[-1] # get temperature of coolant

    # initialize f_vec to zero
    species_decay = params['species_decay']
    lambda_vec = np.array(species_decay)
    n_species  = len(lambda_vec)

    f_tmp = np.zeros(1+n_species+2,dtype=np.float64) # vector for f_vec return

    #----------------
    # neutron balance
    #----------------
    rho_t    = rho_func(time, n_dens, (temp_f+temp_c)/2.0, params)

    beta     = params['beta']
    gen_time = params['gen_time']

    species_rel_yield = params['species_rel_yield']
    beta_vec = np.array(species_rel_yield) * beta

    assert len(lambda_vec)==len(beta_vec)

    q_source_t = q_source(time, params)

    f_tmp[0] = (rho_t - beta)/gen_time * n_dens + lambda_vec @ c_vec + q_source_t

    #-----------------------------------
    # n species balances (implicit loop)
    #-----------------------------------
    f_tmp[1:-2] = beta_vec/gen_time * n_dens - lambda_vec * c_vec

    #--------------------
    # fuel energy balance
    #--------------------
    rho_f    = params['fuel_dens']
    cp_f     = params['cp_fuel']
    vol_fuel = params['fuel_volume']

    pwr_dens = nuclear_pwr_dens_func( time, (temp_f+temp_c)/2, n_dens, params )

    heat_sink = heat_sink_rate( time, temp_f, temp_c, params )

    f_tmp[-2] = - 1/rho_f/cp_f * ( pwr_dens - heat_sink/vol_fuel )

    #-----------------------
    # coolant energy balance
    #-----------------------
    rho_c    = params['coolant_dens']
    cp_c     = params['cp_coolant']
    vol_cool = params['coolant_volume']

    temp_in = coolant_inlet_temp_func(time, temp_f, temp_c, params)

    tau = params['tau_fake']

    heat_source = - heat_sink

    f_tmp[-1] = - 1/tau * (temp_c - temp_in) + 1./rho_c/cp_c/vol_cool * heat_source

    return f_tmp


'''Create the point-reactor run function'''

def run_point_reactor( f_vec, params ):

    from scipy.integrate import odeint # Load ODE solver package

    import numpy as np
    time_final = params['time_final']
    n_time_stamps = params['n_time_stamps']
    time_stamps = np.linspace(0.0, time_final, num=n_time_stamps) # create the time stamps for solution values
    params['time_stamps'] = time_stamps

    max_n_steps_per_time_step = 200 # max number of nonlinear algebraic solver iterations per time step

    n_0     = params['n_0']
    c_vec_0 = params['c_vec_0']

    temp_f_0 = params['temp_f_0']
    temp_c_0 = params['temp_c_0']

    # m-equation point reactor model
    n_species = len(c_vec_0)
    u_vec_0   = np.zeros(1+n_species+2,dtype=np.float64)

    u_vec_0[0]    = n_0
    u_vec_0[1:-2] = c_vec_0
    u_vec_0[-2]   = temp_f_0
    u_vec_0[-1]   = temp_c_0

    #rtol = np.ones(u_vec_0.size)*1e-1
    #atol = np.ones(u_vec_0.size)
    #for i in range(u_vec_0.size-2):
        #print(i)
        #atol[i] = max(u_vec_0[i]*1e-1,1e-4)
        #print(atol)

    (u_vec_history, info_dict) = odeint( f_vec, u_vec_0, time_stamps,
                                         args=( params, ),
                                         rtol=1e-4, atol=1e-8, mxstep=max_n_steps_per_time_step,
                                         #rtol=rtol, atol=atol, mxstep=max_n_steps_per_time_step,
                                         #hmax=2,
                                         full_output=True, tfirst=True )

    assert info_dict['message']=='Integration successful.',                     'Fatal: scipy.integrate.odeint failed %r'%info_dict['message']


    return u_vec_history

'''Plotting function definition'''

def plot_neutron_results( u_vec_history, normalize=False, semi_log=False, markers=False, precursors=True ):

    time_stamps = params['time_stamps']
    n_dens_ss = params['n_dens_ss_operation']
    c_vec_normalize = u_vec_history[-1,1:-2]

    import matplotlib.pyplot as plt

    fig, ax1 = plt.subplots(1, figsize=(14, 6))

    if precursors == True:

        ax2 = ax1.twinx() # duplicate x axes to plot n and c_i's in different y axes

        color_ids = np.linspace(0,1,u_vec_history[:,1:-2].shape[1])

        for (j,color_id) in zip( range(u_vec_history[:,1:-2].shape[1]), color_ids ):
            color=plt.cm.nipy_spectral(color_id)

            if normalize == True:
                ax2.plot( time_stamps/3600,u_vec_history[:,j+1]/c_vec_normalize[j],'-.',color=color,label=r'$c_%i$'%(j+1) )
                ax2.set_ylabel(r'$c_i/c_{i_0}$',fontsize=16,color='black')
            else:
                ax2.plot( time_stamps/3600,u_vec_history[:,j+1],'-.',color=color,label=r'$c_%i$'%(j+1) )
                ax2.set_ylabel(r'$c_i$',fontsize=16,color='black')

        ax2.tick_params(axis='y', labelcolor='black', labelsize=14)
        ax2.legend(loc='lower right',fontsize=12)
        if semi_log == True:
            ax2.set_yscale('log') # uncomment to plot y in log scale
        #ax2.grid(True)

    if markers == True:
        if normalize == True:
            ax1.plot( time_stamps/3600,u_vec_history[:,0]/n_dens_ss,'-',marker='+',color='red',label=r'$n/n_0$' )
            ax1.set_ylabel(r'$n$',fontsize=16,color='black')
        else:
            ax1.plot( time_stamps/3600,u_vec_history[:,0],'-',marker='+',color='red',label=r'$n$' )
            ax1.set_ylabel(r'$n$',fontsize=16,color='black')
    else:
        if normalize == True:
            ax1.plot(time_stamps/3600,u_vec_history[:,0]/n_dens_ss,'-',color='red',label=r'$n/n_0$' )
            ax1.set_ylabel(r'$n/n_{ss}$',fontsize=16,color='black')
        else:
            ax1.plot(time_stamps/3600,u_vec_history[:,0],'-',color='red',label=r'$n$' )
            ax1.set_ylabel(r'$n$',fontsize=16,color='black')

    ax1.set_xlabel(r'Time [h] ($\tau=$%4.3f s)'%tau,fontsize=16)

    ax1.tick_params(axis='y', labelcolor='black', labelsize=14)
    ax1.tick_params(axis='x', labelsize=14)
    ax1.legend(loc='lower left',fontsize=12)
    if semi_log == True:
        ax1.set_yscale('log') # uncomment to plot y in log scale
    ax1.grid(True)

    plt.title(r'Point-Reactor Model: $\rho/\beta=$'
              +str(params['reactivity']/params['beta'])
              +r'; $q_0=$'+str(round(params['q_0'],2)),
              fontsize=18)
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.show()

    print('')

'''Utility function to peak at results table'''

def peek(time,data, head=5, tail=5):  

    import pandas as pd
    
    pd.options.display.float_format = '{:.2e}'.format
    
    layout = {'time':time[:head]}
    
    layout['n'] = data[:head,0]
    
    for j in range(1,data[:,1:-2].shape[1]+1):
        layout['c_%i'%j] = data[:head,j]

    layout['temp_f [K]'] = data[:head,-2]
    layout['temp_c [K]'] = data[:head,-1]

    results = pd.DataFrame(layout)
    print(round(results,2))
    print('')

    layout = {'time':time[-tail:]}

    layout['n'] = data[-tail:,j]

    for j in range(1,data[:,1:-2].shape[1]+1):
        layout['c_%i'%j] = data[-tail:,j]

    layout['temp_f [K]'] = data[-tail:,-2]
    layout['temp_c [K]'] = data[-tail:,-1]

    results = pd.DataFrame(layout)
    print(round(results,2))
    print('')

'''Post-Processing Quantities'''

def get_quantities(u_vec_history,params):

    import pandas as pd
    data = dict()
    tmp1 = list()
    tmp2 = list()
    tmp3 = list()
    tmp4 = list()

    for (time,n_dens,tf,tc) in zip(params['time_stamps'],u_vec_history[:,0],u_vec_history[:,-2],u_vec_history[:,-1]):

        rho = rho_func(time,n_dens,(tf+tc)/2,params)
        tmp1.append( rho )

        temp_in = coolant_inlet_temp_func( time, tf, tc, params )
        tmp2.append(temp_in)

        temp_ave = (tf+tc)/2.0
        q3prime = nuclear_pwr_dens_func( time, temp_ave, n_dens, params )
        tmp4.append(q3prime/1000)

        pwr = params['coolant_volume']/params['tau_fake'] * params['coolant_dens'] * params['cp_coolant'] * (tc - temp_in)
        tmp3.append(pwr/1000)

    data['rho'] = tmp1
    data['T_in [C]'] = np.array(tmp2)-273.15
    data['pwr [kW]'] = tmp3
    data["q''' [kW/m3]"] = tmp4

    df = pd.DataFrame(data)

    return df

'''Plot Tf and Tc temperatures in the reactor'''

def plot_temperature_results( u_vec_history,params, semi_log=False ):

    quant = get_quantities(u_vec_history,params)

    time_stamps = params['time_stamps']

    import matplotlib.pyplot as plt
    fig, ax1 = plt.subplots(1, figsize=(16, 6))
    #ax1.plot(time_stamps/3600,u_vec_history[:,-1]-273.15,'r-',time_stamps/3600,u_vec_history[:,-2]-273.15,'b-',label='$T_f=$')

    ax1.plot(time_stamps/3600,u_vec_history[:,-2]-273.15,'r-.',label='$T_f$')
    ax1.plot(time_stamps/3600,u_vec_history[:,-1]-273.15,'r-',label='$T_c$')
    ax1.plot(time_stamps/3600,quant['T_in [C]'],'b-',label=r'$T_{in}$' )

    ax1.set_xlabel(r'Time [h] ($\tau=$%4.3f s)'%tau,fontsize=16)
    ax1.set_ylabel(r'$T$ [C]',fontsize=16,color='black')
    ax1.tick_params(axis='y', labelcolor='black', labelsize=14)
    ax1.tick_params(axis='x', labelsize=14)
    ax1.legend(loc='upper left',fontsize=12)
    ax1.grid(True)
    if semi_log == True:
        ax1.set_yscale('log')

    plt.title('Single-Point Reactor HTTR Temperatures',fontsize=20)
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.show()
    print('')

'''Reactor Power and Delta T (input/output) at Steady State'''

def get_ss_system_pwr(u_vec_history,params):

    quant = get_quantities(u_vec_history,params)

    temp_in = quant['T_in [C]'].iat[-1]
    delta_T = (u_vec_history[-1,-1]-273.15 - temp_in)

    pwr = quant['pwr [kW]'].iat[-1]

    return (pwr,delta_T)

'''Plot Reactivity'''

def plot_reactivity(u_vec_history,params):

    quant = get_quantities(u_vec_history,params)

    time_stamps = params['time_stamps']
    import matplotlib.pyplot as plt
    fig, ax1 = plt.subplots(1, figsize=(16, 6))
    ax1.plot(time_stamps/3600,quant['rho']/params['beta'],'b-',label=r'$\rho$' )

    ax1.set_xlabel(r'Time [h] ($\tau=$%4.3f s)'%tau,fontsize=16)
    ax1.set_ylabel(r'$\rho(t)/\beta$',fontsize=16,color='black')
    ax1.tick_params(axis='y', labelcolor='black', labelsize=14)
    ax1.tick_params(axis='x', labelsize=14)
    ax1.legend(loc='upper left',fontsize=12)
    ax1.grid(True)

    plt.title('Single-Point Reactor HTTR Reactivity',fontsize=20)
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.show()
    print('')

    return

'''Plot Heating Power'''

def plot_heating_power(u_vec_history,params):

    quant = get_quantities(u_vec_history,params)

    time_stamps = params['time_stamps']
    import matplotlib.pyplot as plt
    fig, ax1 = plt.subplots(1, figsize=(16, 6))

    ax1.plot(time_stamps/3600,quant['pwr [kW]'],'-',color='black',label='$Pwr$' )

    ax1.set_xlabel(r'Time [h] ($\tau=$%4.3f s)'%tau,fontsize=16)
    ax1.set_ylabel(r'Pwr$_{th}$ [kW]',fontsize=16,color='black')
    ax1.tick_params(axis='y', labelcolor='black', labelsize=14)
    ax1.tick_params(axis='x', labelsize=14)
    ax1.legend(loc='upper left',fontsize=12)
    ax1.xaxis.grid(True,linestyle='-',which='major',color='lightgrey',alpha=0.9)
    #ax1.grid(True)

    ax2 = ax1.twinx()

    ax2.plot(time_stamps/3600,-quant["q''' [kW/m3]"]*params['fuel_volume'],'r-.',label=r"$q^{'''}$" )

    ax2.set_ylabel(r"$-q^{'''}\,V_f$ [kW]",fontsize=18,color='red')
    ax2.tick_params(axis='y', labelcolor='red', labelsize=14)
    ax2.legend(loc='lower right',fontsize=12)
    ax2.set_ylim(0,max(ax2.get_ylim()))
    #ax2.grid(True)

    ax1.set_ylim(0,max(ax2.get_ylim()))

    plt.title('Single-Point Reactor HTTR Removed Heat Rate History',fontsize=20)
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.show()
    print('')
    return

'''Decay Heating Power Density'''

def decay_heat_pwr_dens(u_vec_history,params):

    if params['shutdown'] == False:
        print("params['shutdown'] is False; bailing out.")
        return None

    import pandas as pd
    import scipy.integrate as integrate

    time_shutdown = params['shutdown_time']
    time_final    = params['time_final']
    time_cooling  = time_final - time_shutdown

    decay_time = list()
    decay_pwr  = list()

    n_pts = 150
    for x in range(n_pts+1):

        if x <= 2:  # avoid the case with no cooling period because the time singularity
            continue

        time_cooling = x * (time_final-time_shutdown)/n_pts

        tmp1 = list()
        tmp2 = list()

        for (time,n_dens,tf,tc) in zip(params['time_stamps'],u_vec_history[:,0],u_vec_history[:,-2],u_vec_history[:,-1]):

            if time > time_shutdown:
                break

            temp = (tf+tc)/2
            sigma_f = sigma_fis_func( temp, params ) # m2

            fis_nuclide_num_dens = params['fis_nuclide_num_dens_fake'] #  #/m3

            Sigma_fis = sigma_f * fis_nuclide_num_dens # macroscopic cross section

            v_o = params['thermal_neutron_velo'] # m/s

            neutron_flux = n_dens * params['n_dens_ss_operation'] * v_o

            assert time_shutdown - time + time_cooling > 0.0

            integrand = 4.2618e-13 * Sigma_fis * neutron_flux * (time_shutdown - time + time_cooling)**(-1.2)

            tmp1.append(time)
            tmp2.append(integrand)

        integral = integrate.trapz(tmp1,tmp2)
        #print('time [h]             = ',(time_cooling+time_shutdown)/3600)
        #print('decay heat power [W] = ',round(integral*params['fuel_volume'],3))

        decay_time.append(time_cooling+time_shutdown)
        decay_pwr.append(integral*params['fuel_volume'])

    data = dict()
    data['time [s]']  = decay_time
    data['decay [W]'] = decay_pwr

    df = pd.DataFrame(data)

    return df

'''Plot Heating Power'''

def plot_decay_heating_power(u_vec_history,decay_heat,params):

    if params['shutdown'] == False:
        print("params['shutdown'] is False; bailing out.")
        return None

    quant = get_quantities(u_vec_history,params)

    time_stamps = params['time_stamps']

    import matplotlib.pyplot as plt
    fig, ax1 = plt.subplots(1, figsize=(16, 6))

    ax1.plot(decay_heat['time [s]']/3600,decay_heat['decay [W]']/1000,'-',color='red',label='Decay Pwr' )

    ax1.set_xlabel(r'Time [h] ($\tau=$%4.3f s)'%tau,fontsize=16)
    ax1.set_ylabel(r'Decay Heating Power [kW]',fontsize=16,color='red')
    ax1.tick_params(axis='y', labelcolor='red', labelsize=14)
    ax1.tick_params(axis='x', labelsize=14)
    ax1.legend(loc='upper left',fontsize=12)
    ax1.xaxis.grid(True,linestyle='-',which='major',color='lightgrey',alpha=0.9)

    #ax1.grid(True)

    ax2 = ax1.twinx()
    ax2.plot(time_stamps/3600,-quant["q''' [kW/m3]"]*params['fuel_volume'],'k-.',label=r"$-q^{'''}\,V_f$" )
    ax2.set_ylabel(r"$-q^{'''}\,V_f$ [kW]",fontsize=18,color='black')
    ax2.tick_params(axis='y', labelcolor='black', labelsize=14)
    ax2.legend(loc='lower right',fontsize=12)
    ax2.set_ylim(0,max(ax2.get_ylim()))
    #ax2.grid(True)

    ax1.set_ylim(0,max(ax2.get_ylim()))

    plt.title('Single-Point Reactor HTTR Decay Heat History',fontsize=20)
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.show()
    print('')
    return

'''Setup up initial conditions'''

import numpy as np

gen_time = params['gen_time'] # retrieve neutron generation time
params['q_0'] = 1/gen_time # pulse at t = 0

params['n_ss']       = 0.0 # neutronless steady state before start up
params['n_dens_ref'] = 1.0

rho_0_over_beta = 0.5 # $

beta = params['beta'] # retrieve the delayed neutron fraction
params['reactivity'] = rho_0_over_beta * beta # "rho/beta = 10 cents"

params['temp_0'] = params['temp_o']

params['tau_fake'] = .025 # s residence time

# setup remaining initial conditions
setup_initial_conditions( params )

'''Evolve the point-reactor'''

time_final    = 3600 * 25 # s
n_time_stamps = 500 # number of solution values in time

params['time_final']    = time_final
params['n_time_stamps'] = n_time_stamps

# Run the reactor and compute the history of the state variables; tabular form, one row per time stamp
u_vec_history = run_point_reactor( f_vec, params )

peek(params['time_stamps'],u_vec_history)

'''Compute Coolant Flow Rate: DELETE ME'''

tau = params['tau_fake']
flow_rate_c = params['coolant_volume'] * 1000 / (tau*60)
print('coolant vol flow rate [L/min] = ',flow_rate_c)

'''Plot neutron and delayed neutron emitter concentration in the reactor'''

plot_neutron_results(u_vec_history, semi_log=False, normalize=False, precursors=True)

'''Plot Reactivity'''

plot_reactivity(u_vec_history,params)

'''Plot Temperatures'''

plot_temperature_results(u_vec_history,params,semi_log=False)

'''Plot Heating Powers'''

plot_heating_power(u_vec_history,params)

'''Heating Power and Delta T'''

(pwr_kw,delta_T_C) = get_ss_system_pwr(u_vec_history,params)

print('Power = %.2e [kW]'%pwr_kw)
print('Delta T = %.2e [C]'%delta_T_C)

'''Add conditions for HX malfunction'''

params['strict'] = False
params['hx_malfunction'] = True

params['hx_malfunction_start_time']  = 8 * 3600
params['hx_malfunction_down_time']   = 2.5 * 3600
params['hx_malfunction_temperature'] = 873 + 273.15

time_final    = 3600 * 25 # s, longer run to account for the disturbance transient
n_time_stamps = 500 # number of solution values in time

params['time_final']    = time_final
params['n_time_stamps'] = n_time_stamps

# Run the reactor and compute the history of the state variables; tabular form, one row per time stamp
u_vec_history = run_point_reactor( f_vec, params )

'''Plot neutron and delayed neutron emitter concentration in the reactor'''

plot_neutron_results(u_vec_history, semi_log=False, normalize=False, precursors=True)

'''Plot Reactivity'''

plot_reactivity(u_vec_history,params)

'''Plot Temperatures'''

plot_temperature_results(u_vec_history,params,semi_log=False)

'''Plot Heating Powers'''

plot_heating_power(u_vec_history,params)

'''Heating Power and Delta T'''

(pwr_kw,delta_T_C) = get_ss_system_pwr(u_vec_history,params)

print('Power = %.2e [kW]'%pwr_kw)
print('Delta T = %.2e [C]'%delta_T_C)

'''Revert to Default'''

params['hx_malfunction'] = False
params['strict'] = True

'''Add conditions for HX breakdown'''

params['strict'] = False
params['hx_breakdown'] = True

params['hx_breakdown_start_time'] = 11.8 * 3600
params['hx_breakdown_down_time']  = 4.0 * 3600

time_final    = 3600 * 25 # s, longer run to account for the disturbance transient
n_time_stamps = 500 # number of solution values in time

params['time_final']    = time_final
params['n_time_stamps'] = n_time_stamps

# Run the reactor and compute the history of the state variables; tabular form, one row per time stamp
u_vec_history = run_point_reactor( f_vec, params )

'''Plot neutron and delayed neutron emitter concentration in the reactor'''

plot_neutron_results(u_vec_history, semi_log=False, normalize=False, precursors=True)

'''Plot Reactivity'''

plot_reactivity(u_vec_history,params)

'''Plot Temperatures'''

plot_temperature_results(u_vec_history,params,semi_log=False)

'''Plot Heating Powers'''

plot_heating_power(u_vec_history,params)

'''Heating Power and Delta T'''

(pwr_kw,delta_T_C) = get_ss_system_pwr(u_vec_history,params)

print('Power = %.2e [kW]'%pwr_kw)
print('Delta T = %.2e [C]'%delta_T_C)

'''Revert to Default'''

params['hx_breakdown'] = False
params['strict']       = True


# ## Reactor Startup/Shutdown w/ Decay Heat: Reactivity Step<a id="shutdown"></a>
# 
# Apply a shutdown reactivity after steady state operation.

'''Setup up initial conditions'''

import numpy as np

gen_time = params['gen_time'] # retrieve neutron generation time
params['q_0'] = 1/gen_time # pulse at t = 0

params['n_ss'] = 0.0 # neutronless steady state before start up
params['n_dens_ref'] = 1.0

rho_0_over_beta = 0.5 # $

beta = params['beta'] # retrieve the delayed neutron fraction
params['reactivity'] = rho_0_over_beta * beta # "rho/beta = 10 cents"

params['temp_0'] = params['temp_o']

params['tau_fake'] = .025 # s residence time

params['shutdown']      = True
params['rho_shutdown']  = -.1* beta
params['shutdown_time'] = 3600 * 24

params['strict'] = False

params['hx_relax_time'] = 1.5 * 3600 # s

# setup remaining initial conditions
setup_initial_conditions(params)

'''Evolve the point-reactor'''

time_final    = 3600 * 28 # s, longer run to account for the disturbance transient
n_time_stamps = 500 # number of solution values in time

params['time_final']    = time_final
params['n_time_stamps'] = n_time_stamps

# Run the reactor and compute the history of the state variables; tabular form, one row per time stamp
u_vec_history = run_point_reactor( f_vec, params )

'''Compute Coolant Flow Rate: DELETE ME'''

tau = params['tau_fake']
flow_rate_c = params['coolant_volume'] * 1000 / (tau*60)
print('coolant vol flow rate [L/min] = ',flow_rate_c)

'''Plot neutron and delayed neutron emitter concentration in the reactor'''

plot_neutron_results(u_vec_history, semi_log=False, normalize=False, precursors=True)

'''Plot Reactivity'''

plot_reactivity(u_vec_history,params)

'''Plot Temperatures'''

plot_temperature_results(u_vec_history,params,semi_log=False)

'''Plot Heating Powers'''

plot_heating_power(u_vec_history,params)

df = decay_heat_pwr_dens(u_vec_history,params)

plot_decay_heating_power(u_vec_history,df,params)

params['hx_relax_time'] = 0
params['shutdown']      = False
params['rho_shutdown']  = 0
params['shutdown_time'] = 0

df['time [s]'] = df['time [s]']/3600

df.columns = ['time [h]','decay [kW]']

df
