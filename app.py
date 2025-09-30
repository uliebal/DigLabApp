import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

import silvio
from silvio.catalog.StrExpSim import DigLabSim
from silvio.experiment import ExperimentSettings
# from silvio.extensions.utils.misc import Download_GSMM
# from silvio.extensions.common import BIGG_dict
# from silvio.utils import coalesce
# get silvio version
from silvio import __version__ as silvio_version

# read variable names from Variables.py
from Variables import SFlask_VarNames, Budget

# # Initialize session state variables
st.session_state['date'] = pd.to_datetime('today').strftime('%y%m%d')
if 'ExpInit' not in st.session_state:
    st.session_state['ExpInit'] = None
# st.session_state['ExpInit'] = False
if 'exp' not in st.session_state:
    st.session_state['exp'] = None
if 'host' not in st.session_state:
    st.session_state['host'] = None
if 'currency' not in st.session_state:
    st.session_state['currency'] = None
if 'LabInvest' not in st.session_state:
    st.session_state['LabInvest'] = None
if 'rand_seed' not in st.session_state:
    st.session_state['rand_seed'] = None
if 'organism' not in st.session_state:
    st.session_state['organism'] = None
if 'GSMM' not in st.session_state:
    st.session_state['GSMM'] = None

# ## File locations
# if 'ModelFile' not in st.session_state:
#     st.session_state['ModelFile'] = None

# st.title('Experiment Details')
st.sidebar.title('Experiment Selection')

st.sidebar.subheader('Experiment Setup')
if st.sidebar.toggle('Experiment Setup'):
    st.title('Setup of Experiment')
    st.markdown('Select the organism for the experiment and the investment into lab equipment.')
    col1, col2 = st.columns(2)
    with col1:
        st.session_state['organism'] = st.selectbox('Select Organism', ['E.coli-core', 'E.coli', 'S.cerevisiae', 'B.subtilis'], index=0)
        # numerical input as number_input, with default value of date with six digits, range 0-100000, step 1
        st.write(f'Default random seed based on date: {st.session_state["date"]}')
        st.session_state['rand_seed'] = st.number_input('Random Seed for Simulation', min_value=0, max_value=999999, value=int(st.session_state['date']), step=1)
        # st.session_state['ModelFile'] = f'Data/{BIGG_dict[st.session_state["organism"]]}.json'
    with col2:
        st.session_state['currency'] = st.selectbox('Currency', ['EURO', 'Dollar', 'Yuan', 'Rupee', 'Yen'], index=0)
        st.session_state['LabInvest'] = st.slider('Investment into Lab Equipment', 0, Budget, 5000, step=100)
    st.markdown(f'You selected {st.session_state["organism"]} as organism and an investment of {st.session_state["LabInvest"]} {st.session_state["currency"]} into lab equipment. The random seed for the simulation is set to {st.session_state["rand_seed"]}.')

    #################################################
    # horizontal line
    st.markdown('---')
    #################################################

    st.subheader('Data management and Analysis')
    st.markdown('Select the data management system and the analysis software.')
    DataExportType = st.selectbox('Data Management System', ['Excel', 'Google Sheets', 'LIMS', 'ELN'], index=0)
    AnalysisSoftware = st.selectbox('Analysis Software', ['Python', 'R', 'Matlab', 'BlueVis'], index=1)

    #################################################
    # horizontal line
    st.markdown('---')
    #################################################

    if st.button('Intialize Experiment'):
        st.session_state['exp'] = DigLabSim(st.session_state['rand_seed'], st.session_state['LabInvest'], Budget)
        st.session_state['host'] = st.session_state['exp'].create_host(st.session_state['organism'])
        # st.session_state['GSMM'] = Download_GSMM(st.session_state['organism'])

        st.success('Experiment initialized. You can now run the experiment.')
        st.session_state['ExpInit'] = True

######################################################
######################################################
# Details on experiment
######################################################
######################################################

st.sidebar.subheader("Experiment Details")
if st.sidebar.toggle('Show Experiment Details'):
    if st.session_state['exp'] is not None:
        # information box on the main page on the experiment details
        with st.expander('Experiment Details', expanded=True):
            st.markdown(f'Organism: {st.session_state["organism"]}')
            st.markdown(f'Remaining budget: {st.session_state["exp"].budget} {st.session_state["currency"]}')
            # st.sidebar.markdown(f'Model file: {st.session_state["GSMM"].id}')
            st.markdown(f'Model file: {st.session_state["host"].metabolism.model.id}')
            # check whether model is functional
            if st.session_state['host'].metabolism.model.slim_optimize() > 1e-6:
                st.success('Model is functional.')
            else:
                st.error('Model is not functional.')
            st.markdown(f'Optimal Temperature: {st.session_state["host"].opt_growth_temp} °C')
            st.markdown(f'OD2X: {st.session_state["host"].growth.OD2X} gCDW/OD600')
            st.markdown(f'Silvio version: {silvio_version}')
            st.markdown(f'Experiment history: {len(st.session_state["exp"].experiment_history)} experiments recorded.')
            # if there are any experiments in the history, display them
            if st.session_state['exp'].experiment_history:
                st.markdown('### Previous Experiments:')
                st.write({st.session_state['exp'].experiment_history[exp].ExperimentID for exp in st.session_state['exp'].experiment_history})
            st.markdown('---')
            rnd = st.session_state['host'].make_generator()
            st.markdown({rnd.pick_uniform(0,1)})
    else:
        st.warning('Please initialize the experiment first.')

######################################################
######################################################
# Experiment selection
######################################################
######################################################

st.sidebar.subheader("Experiment Section")
Experiment_select = st.sidebar.selectbox('Fermentation Type', ['Select', 'Batch', 'Continuous'], key='1')
if Experiment_select == 'Batch' and st.session_state['exp'] is not None:
    myExp = ExperimentSettings()
    myExp.ExperimentType = 'Batch'
    myExp.HostName = st.session_state['organism']
    st.title('Batch Experiment in Shake Flask')
    st.markdown('For the shake flask experiment, you can set the temperature, shaking speed (rpm), initial optical density (OD600), and glucose concentration in g/L. After setting the parameters, click on "Run Simulation" to start the experiment.')
    # Display image
    st.image('Figures/Icons/ShakeFlaskFermentation_SBI.jpg', caption='Shake Flask Experiment', width='stretch')
    # Input parameters
    st.subheader('Input parameters for batch shake flask experiment')
    col1, col2 = st.columns(2)
    with col1:
        # User input for multiple temperatures (integers)
        temp_str = st.text_input('Enter temperatures (comma-separated, e.g. 25,30,37)', value='30')
        try:
            myExp.Temperature = [int(x.strip()) for x in temp_str.split(',') if x.strip()]
        except ValueError:
            st.error("Please enter only integer values separated by commas.")
        # rpm_val = st.number_input(SFlask_VarNames['rpm'], min_value=100, max_value=300, value=200)
        myExp.InitBiomass = round(st.number_input(SFlask_VarNames['od0'], min_value=0.0, max_value=0.3, value=0.1), 3)        
        myExp.MediumVolume = st.slider('Culture Volume (mL) of 500 ml max', min_value=10, max_value=500, value=100, step=10)
        # total cultivation time in hours
        myExp.CultivationTime = st.slider('Total Cultivation Time (h)', min_value =1, max_value=48, value=24, step=1)
        # sampling interval in hours
        myExp.SamplingInterval = st.slider('Sampling Interval (h)', min_value=.5, max_value=12.0, value=1.0, step=0.5)
        myExp.set_SamplingVector()

    with col2:
        # text input to narrow down to specific carbon source
        Substrate_Filter = st.text_input('Filter Carbon Source (e.g. glc, lac, ace, glucose, Glucose etc)', value='glc')
        model = st.session_state['host'].metabolism.model
        if Substrate_Filter:
            Fil1 = set(model.metabolites.query(Substrate_Filter, attribute='name'))
            Fil2 = set(model.metabolites.query(Substrate_Filter, attribute='id'))
            Fil2_unique = Fil2 - Fil1
            Carbon_Substrates =  list(Fil1) + list(Fil2_unique)
            # coalesce(st.session_state['GSMM'].metabolites.query(Substrate_Filter[1:], attribute='name') + st.session_state['GSMM'].metabolites.query(Substrate_Filter[1:], attribute='id'))
            sub_sel = st.selectbox('Select Carbon Source', Carbon_Substrates, index=0)
            # find sustrate in exchange reactions
            Exch_Reactions = [r for r in model.exchanges if sub_sel.id in r.reaction]
            if not Exch_Reactions:
                st.warning(f'No exchange reaction found for "{sub_sel}". Please select another substrate.')
            else:
                myExp.CarbonID = Exch_Reactions[0].id
                myExp.CarbonName = sub_sel.name
                st.markdown(f'Found exchange reaction "{myExp.CarbonID}"')
        # selectbox for concentration unit, default g/L, options: g/L, mM, M
        # the number input for concentration is only shown if the concentration unit is selected
        Conc_Unit = st.selectbox('Select Concentration Unit', ['g/L', 'mM', 'M'], index=0)
        if Conc_Unit == 'g/L':
            conc_unit_factor = 1/(sub_sel.formula_weight/1000)  # convert g/L to mmol/L
        elif Conc_Unit == 'mM':
            conc_unit_factor = 1 
        elif Conc_Unit == 'M':
            conc_unit_factor = 1/1000  # convert M to mmol/L
        else:
            conc_unit_factor = 1  # default to g/L if something goes wrong
        sub_val = round(st.number_input(f'Concentration ({Conc_Unit})', min_value=0., max_value=50., value=1., step=.1),2)
        myExp.CarbonConc = round(abs(sub_val * conc_unit_factor),2)
        st.markdown(f'You selected {myExp.CarbonName} with {myExp.CarbonConc} mM.')

        # if st.button('Run FBA'):
        #     # set uptake rate of selected substrate
        #     st.session_state['host'].metabolism.set_resetCarbonExchanges({myExp.CarbonID: myExp.CarbonConc})
        #     GrowthRate = st.session_state['host'].metabolism.slim_optimize()
        #     ExchangeRates = st.session_state['host'].metabolism.optimize_ReportExchanges()
        #     UpRate = -ExchangeRates[myExp.CarbonID]
        #     Yield = round(GrowthRate/UpRate,2) if UpRate != 0 else 0 # gCDW/mmol
        #     # calculate biomass capacity in gCDW/L
        #     BioWeightConc = Yield * myExp.CarbonConc  # gCDW/L
        #     CapacityWeight = BioWeightConc * (myExp.MediumVolume/1000)  # gCDW in the flask
        #     CapacityOD = CapacityWeight / st.session_state['host'].growth.OD2X  # convert gCDW to OD600
        #     Vmax = st.session_state["host"].metabolism.model_tmp.reactions.get_by_id(Exch_Reactions[0].id).Vmax
        #     Km = st.session_state["host"].metabolism.model_tmp.reactions.get_by_id(Exch_Reactions[0].id).Km
        #     st.success(f'FBA with {Exch_Reactions[0].id} and uptake rate of {UpRate} mmol/gCDW/h. Kinetics: {Vmax} mmol/gDW/h and {Km} mM. Growth rate {GrowthRate}/h.\n\n Yield: {Yield} gCDW/mmol ({round(Yield*1000/sub_sel.formula_weight,2)} gCDW/gSubstrate) substrate.\n\n Biomass capacity in flask: {round(CapacityOD,2)} OD600).')
        #     st.write(st.session_state['host'].metabolism.model_tmp.summary())

    # text input for experiment id
    myExp.ExperimentID = st.text_input('Experiment ID', value=f'Batch_v1')

    if st.button('Run Simulation'):
        # set uptake rate of selected substrate
        st.session_state['host'].metabolism.set_resetCarbonExchanges({myExp.CarbonID: myExp.CarbonConc})
        GrowthRate, ExchangeRates = st.session_state['host'].metabolism.optimize_ReportExchanges()
        UpRate = -ExchangeRates[myExp.CarbonID]
        Yield = round(GrowthRate/UpRate,2) if UpRate != 0 else 0 # gCDW/mmol
        # calculate biomass capacity in gCDW/L
        BioWeightConc = Yield * myExp.CarbonConc  # gCDW/L
        CapacityWeight = BioWeightConc * (myExp.MediumVolume/1000)  # gCDW in the flask
        CapacityOD = CapacityWeight / st.session_state['host'].growth.OD2X  # convert gCDW to OD600

        # format Data as xlsx for download
        myExp.Results = f'Data/{pd.to_datetime("today").strftime("%y%m%d")}_{st.session_state["organism"].replace(".","")}_ODInit{str(myExp.InitBiomass).replace(".","-")}_ShakeFlask.xlsx'
        # run simulation
        Data = st.session_state['exp'].measure_TemperatureGrowth(myExp, Test=True)
        with pd.ExcelWriter(myExp.Results, engine='openpyxl') as writer:
            Data.value.to_excel(writer, sheet_name='TemperatureGrowth', index=False)
        st.markdown(f'Data saved to {myExp.Results}')
        st.download_button(
            label="Download data as Excel",
            data=open(myExp.Results, 'rb').read(),
            file_name=os.path.split(myExp.Results)[-1],
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.session_state['exp'].record_experiment(myExp)
        st.success('Data simulation completed and file is ready for download.')
else:
    if st.session_state['exp'] is None:
        st.warning('Please initialize the experiment first.')
    else:
        st.info('Select "Shake Flask" from the dropdown to set parameters and run the simulation.')

st.sidebar.subheader("Reset Experiment")
if st.sidebar.button('Reset Experiment'):
    st.session_state['ExpInit'] = None
    st.session_state['exp'] = None
    st.sidebar.success('Experiment reset. You can set up a new experiment now.')