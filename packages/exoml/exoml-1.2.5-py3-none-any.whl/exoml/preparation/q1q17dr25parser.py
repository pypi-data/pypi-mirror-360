import glob
import gzip
import multiprocessing
import os
import pathlib
import re
import shutil
from multiprocessing import Pool
import pandas as pd
import numpy as np

from exoml.preparation.parser_utils import CreateTargetInput, create_target_csv, create_triceratops_prob

def create_targets_df(tces_dir):
    # Merge TCEs DF and cumulative DF ignoring everything not from Kepler or K2
    # Mark TCEs as planet only if they have photometric and rv measurements
    # test_df = pd.read_csv(tces_dir + '/classified_tces.csv', comment='#')
    # test_df = test_df.sort_values(by=["object_id", "period"], ascending=True)
    # test_df = test_df[test_df['type'].isin(['fp', 'planet', 'planet_transit', 'tce'])]
    # test_df.to_csv(tces_dir + '/injected_objects_tces.csv')
    cfps_df = pd.read_csv(tces_dir + '/fpwg_2023.04.25_10.26.55.csv', comment='#')
    kois_df = pd.read_csv(tces_dir + '/cumulative_2023.06.30_13.09.52.csv', comment='#')
                          #usecols=['rowid','kepid','kepoi_name','kepler_name','koi_disposition','koi_vet_stat','koi_vet_date','koi_pdisposition','koi_score','koi_fpflag_nt','koi_fpflag_ss','koi_fpflag_co','koi_fpflag_ec','koi_disp_prov','koi_comment','koi_period','koi_time0bk','koi_time0','koi_eccen','koi_longp','koi_impact','koi_duration','koi_ingress','koi_depth','koi_ror','koi_srho','koi_fittype','koi_prad','koi_sma','koi_incl','koi_teq','koi_insol','koi_dor','koi_limbdark_mod','koi_ldm_coeff4','koi_ldm_coeff3','koi_ldm_coeff2','koi_ldm_coeff1','koi_parm_prov','koi_max_sngle_ev','koi_max_mult_ev','koi_model_snr','koi_count','koi_num_transits','koi_tce_plnt_num','koi_tce_delivname','koi_quarters','koi_bin_oedp_sig','koi_trans_mod','koi_model_dof','koi_model_chisq','koi_datalink_dvr','koi_datalink_dvs','koi_steff','koi_slogg','koi_smet','koi_srad','koi_smass','koi_sage','koi_sparprov','ra','dec','koi_kepmag','koi_gmag','koi_rmag','koi_imag','koi_zmag','koi_jmag','koi_hmag','koi_kmag','koi_fwm_stat_sig','koi_fwm_sra','koi_fwm_sdec','koi_fwm_srao','koi_fwm_sdeco','koi_fwm_prao','koi_fwm_pdeco','koi_dicco_mra','koi_dicco_mdec','koi_dicco_msky','koi_dikco_mra','koi_dikco_mdec','koi_dikco_msky'])
    tces_df = pd.read_csv(tces_dir + '/q1_q17_dr25_tce_2023.07.03_23.17.12.csv', comment='#')
    disc_df = pd.read_csv(tces_dir + '/PSCompPars_2023.06.30_07.30.12.csv', comment='#')
                          #usecols=['pl_name','hostname','tic_id','sy_snum','sy_pnum','discoverymethod','disc_year','disc_facility','rv_flag','tran_flag','pl_controv_flag','pl_orbper','pl_orbsmax','pl_rade','pl_radj','pl_bmasse','pl_bmassj','pl_bmassprov','pl_orbeccen','pl_insol','pl_eqt','ttv_flag','st_spectype','st_teff','st_rad','st_mass','st_met','st_metratio','st_logg','rastr','ra','decstr','dec','sy_dist','sy_vmag','sy_jmag','sy_hmag','sy_kmag','sy_gaiamag','sy_tmag','sy_kepmag','st_nphot','st_nrvc', 'disc_refname'])
    tces_df = tces_df[tces_df['tce_rogue_flag'] == 0]
    kois_df = kois_df[~((kois_df['koi_disposition'] == 'CONFIRMED') & (kois_df['koi_pdisposition'] == 'FALSE POSITIVE'))]
    tces_df['cent_so'] = (tces_df['tce_fwm_srao'] ** 2 + tces_df['tce_fwm_sdeco'] ** 2) ** 0.5
    tces_df['cent_so_err'] = (((tces_df['tce_fwm_srao'] / np.sqrt(tces_df['tce_fwm_srao'] ** 2 + tces_df['tce_fwm_sdeco'] ** 2)) * tces_df['tce_fwm_srao_err']) ** 2 + \
                              ((tces_df['tce_fwm_sdeco'] / np.sqrt(tces_df['tce_fwm_srao'] ** 2 + tces_df['tce_fwm_sdeco'] ** 2)) * tces_df['tce_fwm_sdeco_err']) ** 2) ** 0.5
    tces_df['cent_so_sigma'] = tces_df['cent_so'] / tces_df['cent_so_err']
    tces_df['source_offset_sigma'] = tces_df['tce_dicco_msky'] / tces_df['tce_dicco_msky_err']
    tces_df['kic_offset_sigma'] = tces_df['tce_dikco_msky'] / tces_df['tce_dikco_msky_err']
    # tces_df[~(((tces_df['tce_hap_stat'] / tces_df['tce_cap_stat'] > 1) |
    #            (tces_df['tce_hap_stat'] > 0) & (tces_df['tce_cap_stat'] < 0)) |
    #           (tces_df['tce_maxmes'] > 7.1) |
    #           (tces_df['cent_so_sigma'] > 3) |
    #           (tces_df['source_offset_sigma'] > 3) |
    #           (tces_df['kic_offset_sigma'] > 3)) & (tces_df['tce_model_snr'] > 3.5)]
    kois_df = pd.merge(kois_df, cfps_df, on=['kepoi_name'], how="outer", indicator=True)
    kois_df = kois_df[(kois_df['_merge'] == 'left_only') | (kois_df['_merge'] == 'both')]
    kois_df['kepid'] = kois_df['kepid_x']
    kois_df['pl_name'] = kois_df['kepler_name']
    kois_df['tce_period'] = kois_df['koi_period']
    kois_df['tce_period_round'] = kois_df['tce_period'].round(1)
    tces_df['tce_period_round'] = tces_df['tce_period'].round(1)
    tces_df = pd.merge(tces_df, kois_df, on=['kepid', 'tce_period_round'], how='outer')
    disc_df = disc_df[disc_df['disc_facility'] == 'Kepler']
    disc_df = disc_df[disc_df['discoverymethod'] == 'Transit']
    disc_df = pd.merge(tces_df, disc_df, on='pl_name', how='outer')
    disc_df['close_period'] = 0
    disc_df['type'] = 'tce'
    disc_df.loc[~disc_df['pl_name'].isna(), 'type'] = 'planet'
    disc_df.loc[(disc_df['koi_disposition'] == 'FALSE POSITIVE') & (~disc_df['type'].str.contains('planet')), 'type'] = 'fp_candidate'
    disc_df.loc[(disc_df['koi_disposition'] == 'CONFIRMED'), 'type'] = 'planet_transit'
    disc_df.loc[(disc_df['rv_flag'] > 0) & (disc_df['tran_flag'] > 0) & (disc_df['koi_disposition'] == 'CONFIRMED'), 'type'] = 'planet'
    disc_df.loc[(disc_df['rv_flag'] == 0) & (disc_df['tran_flag'] > 0) & (disc_df['koi_disposition'] == 'CONFIRMED'), 'type'] = 'planet_transit'
    disc_df.loc[(disc_df['koi_disposition'] == 'FALSE POSITIVE') & (~disc_df['type'].str.contains('planet')), 'type'] = 'fp_candidate'
    disc_df.loc[(disc_df['koi_disposition'] == 'CANDIDATE') & (~disc_df['type'].str.contains('planet')), 'type'] = 'candidate'
    disc_df.loc[(disc_df['fpwg_disp_status'] == 'CERTIFIED FP') & (~disc_df['type'].str.contains('planet')), 'type'] = 'fp'
    disc_df.loc[(disc_df['fpwg_disp_status'] == 'CERTIFIED FA') & (~disc_df['type'].str.contains('planet')), 'type'] = 'fa'
    disc_df['object_id'] = 'KIC ' + disc_df['kepid'].astype('Int64').astype('str')
    disc_df['period'] = disc_df['tce_period_x']
    disc_df.loc[disc_df['period'].isna(), 'period'] = disc_df[disc_df['period'].isna()]['tce_period_y']
    disc_df.loc[disc_df['period'].isna(), 'period'] = disc_df[disc_df['period'].isna()]['pl_orbper']
    disc_df['epoch'] = disc_df['tce_time0bk']
    disc_df.loc[disc_df['epoch'].isna(), 'epoch'] = disc_df[disc_df['epoch'].isna()]['koi_time0bk']
    disc_df.loc[disc_df['epoch'].isna(), 'epoch'] = disc_df[disc_df['epoch'].isna()]['pl_tranmid'] - 2454833.0
    disc_df['duration(h)'] = disc_df['pl_trandur']
    disc_df.loc[disc_df['duration(h)'].isna(), 'duration(h)'] = disc_df[disc_df['duration(h)'].isna()]['koi_duration']
    disc_df.loc[disc_df['duration(h)'].isna(), 'duration(h)'] = disc_df[disc_df['duration(h)'].isna()]['tce_duration']
    disc_df['depth_primary'] = disc_df['pl_trandep'] * 10000
    disc_df.loc[disc_df['depth_primary'].isna(), 'depth_primary'] = disc_df[disc_df['depth_primary'].isna()]['koi_depth']
    disc_df.loc[disc_df['depth_primary'].isna(), 'depth_primary'] = disc_df[disc_df['depth_primary'].isna()]['tce_depth']
    disc_df['radius(earth)'] = disc_df['pl_rade']
    disc_df.loc[disc_df['radius(earth)'].isna(), 'radius(earth)'] = disc_df[disc_df['radius(earth)'].isna()]['koi_prad']
    disc_df.loc[disc_df['radius(earth)'].isna(), 'radius(earth)'] = disc_df[disc_df['radius(earth)'].isna()]['tce_prad']
    disc_df = disc_df.sort_values(by=["object_id", "period"], ascending=True)
    disc_df.loc[(disc_df['kepoi_name'].isna()) &
                (disc_df['tce_maxmes'] > 7.1), 'type'] = 'tce_secondary'
    disc_df.loc[(disc_df['kepoi_name'].isna()) &
            (disc_df['cent_so_sigma'] > 3), 'type'] = 'tce_centroids_offset'
    disc_df.loc[(disc_df['kepoi_name'].isna()) &
            ((disc_df['source_offset_sigma'] > 3) |
             (disc_df['kic_offset_sigma'] > 3)), 'type'] = 'tce_source_offset'
    disc_df.loc[(disc_df['kepoi_name'].isna()) &
            (disc_df['tce_bin_oedp_stat'] > 9), 'type'] = 'tce_odd_even'
    disc_df.loc[(disc_df['kepoi_name'].isna()) &
                (disc_df['tce_hap_stat'] > disc_df['tce_cap_stat']), 'type'] = 'tce_og'
    disc_df.loc[(disc_df['kepoi_name'].isna()) &
                      (disc_df['type'] == 'tce') &
                      (disc_df['tce_model_snr'] > 3.5), 'type'] = 'tce_candidate'
    #t[t['boot_fap'] > t['boot_mesmean']]
    last_target = ''
    last_period = 0.5
    last_index = -1
    left_match_index = []
    right_match_index = []
    unpaired_index = disc_df.index.values
    for index, target_row in disc_df.iterrows():
        period_diff = 0.2 / (last_period ** (1/2))
        period_diff = 0.05 if period_diff > 0.05 else period_diff
        current_period = target_row['period']
        if last_target == target_row['object_id'] and np.abs(current_period - last_period) < period_diff * last_period:
            right_match_index = right_match_index + [index]
            if last_index not in left_match_index:
                left_match_index = left_match_index + [last_index]
            if last_index in unpaired_index:
                unpaired_index = unpaired_index[unpaired_index != last_index]
            if index in unpaired_index:
                unpaired_index = unpaired_index[unpaired_index != index]
        else:
            last_period = current_period
            last_index = index
        last_target = target_row['object_id']
    #disc_df = disc_df.loc[left_match_index].combine_first(disc_df.loc[right_match_index])
    result_df = disc_df.loc[unpaired_index]
    for i, index in enumerate(left_match_index):
        result = disc_df.loc[index].combine_first(disc_df.loc[right_match_index[i]])
        result['close_period'] = 1
        result_df = pd.concat([result_df, result.to_frame().T], ignore_index=True)
    result_df.drop(result_df[result_df['duration(h)'].isnull()].index, inplace=True)
    result_df.drop(result_df[result_df['object_id'] == 'KIC <NA>'].index, inplace=True)
    # Remove latest KIC from the catalogue
    result_df.drop(result_df[result_df['object_id'] == 'KIC 100001645'].index, inplace=True)
    result_df['ephemeris_contamination'] = 0
    result_df.loc[(result_df['koi_fpflag_ec'] == 1) & (result_df['koi_fpflag_nt'] == 0) &
                  (result_df['koi_fpflag_ss'] == 0) & (result_df['koi_fpflag_co'] == 0), 'ephemeris_contamination'] = 1
    result_df['koi_without_tce'] = 0
    result_df.loc[(~result_df['kepoi_name'].isna()) & (result_df['tce_plnt_num'].isna()), 'koi_without_tce'] = 1
    #result_df.drop(result_df[(np.isnan(result_df['tce_plnt_num']))].index, inplace=True) # discarding rows without DR25 tce
    result_df.to_csv(tces_dir + '/classified_tces.csv')
    results_df_no_validated = result_df.copy()
    results_df_no_validated.loc[results_df_no_validated['disc_refname'].str.contains('Valizadegan', na=False), ['type']] = 'candidate'
    results_df_no_validated.loc[results_df_no_validated['disc_refname'].str.contains('Armstrong et al. 2021', na=False), ['type']] = 'candidate'
    results_df_no_validated.to_csv(tces_dir + '/classified_tces_no_val.csv')
    #disc_df[disc_df['object_id'] == 'KIC 7377200'].iloc[0]['epoch']
    tce_candidate_df = result_df[result_df['type'].isin(['tce_candidate'])]
    tce_candidate_df.to_csv(tces_dir + '/injected_objects_tce_candidates.csv')
    candidate_df = result_df[result_df['type'].isin(['candidate', 'tce_candidate'])]
    candidate_df.to_csv(tces_dir + '/injected_objects_candidates.csv')
    candidate_df_no_val = results_df_no_validated[results_df_no_validated['type'].isin(['candidate', 'tce_candidate'])]
    candidate_df_no_val.to_csv(tces_dir + '/injected_objects_candidates_no_val.csv')
    result_df = result_df[result_df['type'].isin(['fp', 'fa', 'planet', 'planet_transit', 'tce', 'tce_og',
                                                  'tce_secondary', 'tce_source_offset', 'tce_centroids_offset',
                                                  'tce_odd_even'])]
    result_df = result_df[~result_df['radius(earth)'].isna()]
    result_df.to_csv(tces_dir + '/injected_objects_tces.csv')
    results_df_no_validated = results_df_no_validated[results_df_no_validated['type'].isin(['fp', 'fa', 'planet', 'planet_transit', 'tce', 'tce_og',
                                                  'tce_secondary', 'tce_source_offset', 'tce_centroids_offset',
                                                  'tce_odd_even'])]
    results_df_no_validated = results_df_no_validated[~results_df_no_validated['radius(earth)'].isna()]
    results_df_no_validated.to_csv(tces_dir + '/injected_objects_tces_no_val.csv')


def create_targets_multi_df(tces_dir):
    # Merge TCEs DF and cumulative DF ignoring everything not from Kepler or K2
    # Mark TCEs as planet only if they have photometric and rv measurements
    # test_df = pd.read_csv(tces_dir + '/classified_tces.csv', comment='#')
    # test_df = test_df.sort_values(by=["object_id", "period"], ascending=True)
    # test_df = test_df[test_df['type'].isin(['fp', 'planet', 'planet_transit', 'tce'])]
    # test_df.to_csv(tces_dir + '/injected_objects_tces.csv')
    cfps_df = pd.read_csv(tces_dir + '/fpwg_2023.04.25_10.26.55.csv', comment='#')
    kois_df = pd.read_csv(tces_dir + '/cumulative_2023.06.30_13.09.52.csv', comment='#')
    tces_df = pd.read_csv(tces_dir + '/q1_q17_dr25_tce_2023.07.03_23.17.12.csv', comment='#')
    disc_df = pd.read_csv(tces_dir + '/PSCompPars_2023.06.30_07.30.12.csv', comment='#')
    tces_df = tces_df[tces_df['tce_rogue_flag'] == 0]
    kois_df = kois_df[~((kois_df['koi_disposition'] == 'CONFIRMED') & (kois_df['koi_pdisposition'] == 'FALSE POSITIVE'))]
    tces_df['cent_so'] = (tces_df['tce_fwm_srao'] ** 2 + tces_df['tce_fwm_sdeco'] ** 2) ** 0.5
    tces_df['cent_so_err'] = (((tces_df['tce_fwm_srao'] / np.sqrt(tces_df['tce_fwm_srao'] ** 2 + tces_df['tce_fwm_sdeco'] ** 2)) * tces_df['tce_fwm_srao_err']) ** 2 + \
                              ((tces_df['tce_fwm_sdeco'] / np.sqrt(tces_df['tce_fwm_srao'] ** 2 + tces_df['tce_fwm_sdeco'] ** 2)) * tces_df['tce_fwm_sdeco_err']) ** 2) ** 0.5
    tces_df['cent_so_sigma'] = tces_df['cent_so'] / tces_df['cent_so_err']
    tces_df['source_offset_sigma'] = tces_df['tce_dicco_msky'] / tces_df['tce_dicco_msky_err']
    tces_df['kic_offset_sigma'] = tces_df['tce_dikco_msky'] / tces_df['tce_dikco_msky_err']
    # tces_df[~(((tces_df['tce_hap_stat'] / tces_df['tce_cap_stat'] > 1) |
    #            (tces_df['tce_hap_stat'] > 0) & (tces_df['tce_cap_stat'] < 0)) |
    #           (tces_df['tce_maxmes'] > 7.1) |
    #           (tces_df['cent_so_sigma'] > 3) |
    #           (tces_df['source_offset_sigma'] > 3) |
    #           (tces_df['kic_offset_sigma'] > 3)) & (tces_df['tce_model_snr'] > 3.5)]
    kois_df = pd.merge(kois_df, cfps_df, on=['kepoi_name'], how="outer", indicator=True)
    kois_df = kois_df[(kois_df['_merge'] == 'left_only') | (kois_df['_merge'] == 'both')]
    kois_df['kepid'] = kois_df['kepid_x']
    kois_df['pl_name'] = kois_df['kepler_name']
    kois_df['tce_period'] = kois_df['koi_period']
    kois_df['tce_period_round'] = kois_df['tce_period'].round(1)
    tces_df['tce_period_round'] = tces_df['tce_period'].round(1)
    tces_df = pd.merge(tces_df, kois_df, on=['kepid', 'tce_period_round'], how='outer')
    disc_df = disc_df[disc_df['disc_facility'] == 'Kepler']
    disc_df = disc_df[disc_df['discoverymethod'] == 'Transit']
    disc_df = pd.merge(tces_df, disc_df, on='pl_name', how='outer')
    disc_df['multitype'] = ''
    disc_df['close_period'] = 0
    disc_df['type'] = 'tce'
    disc_df.loc[~disc_df['pl_name'].isna(), 'type'] = 'planet'
    disc_df.loc[(disc_df['koi_disposition'] == 'FALSE POSITIVE') & (
        ~disc_df['type'].str.contains('planet')), 'type'] = 'fp_candidate'
    disc_df.loc[(disc_df['koi_disposition'] == 'CONFIRMED'), 'type'] = 'planet_transit'
    disc_df.loc[(disc_df['rv_flag'] > 0) & (disc_df['tran_flag'] > 0) & (
                disc_df['koi_disposition'] == 'CONFIRMED'), 'type'] = 'planet'
    disc_df.loc[(disc_df['rv_flag'] == 0) & (disc_df['tran_flag'] > 0) & (
                disc_df['koi_disposition'] == 'CONFIRMED'), 'type'] = 'planet_transit'
    disc_df.loc[(disc_df['koi_disposition'] == 'FALSE POSITIVE') & (
        ~disc_df['type'].str.contains('planet')), 'type'] = 'fp_candidate'
    disc_df.loc[
        (disc_df['koi_disposition'] == 'CANDIDATE') & (~disc_df['type'].str.contains('planet')), 'type'] = 'candidate'
    disc_df.loc[
        (disc_df['fpwg_disp_status'] == 'CERTIFIED FP') & (~disc_df['type'].str.contains('planet')), 'type'] = 'fp'
    disc_df.loc[
        (disc_df['fpwg_disp_status'] == 'CERTIFIED FA') & (~disc_df['type'].str.contains('planet')), 'type'] = 'fa'
    disc_df['object_id'] = 'KIC ' + disc_df['kepid'].astype('Int64').astype('str')
    disc_df['period'] = disc_df['tce_period_x']
    disc_df.loc[disc_df['period'].isna(), 'period'] = disc_df[disc_df['period'].isna()]['tce_period_y']
    disc_df.loc[disc_df['period'].isna(), 'period'] = disc_df[disc_df['period'].isna()]['pl_orbper']
    disc_df['epoch'] = disc_df['tce_time0bk']
    disc_df.loc[disc_df['epoch'].isna(), 'epoch'] = disc_df[disc_df['epoch'].isna()]['koi_time0bk']
    disc_df.loc[disc_df['epoch'].isna(), 'epoch'] = disc_df[disc_df['epoch'].isna()]['pl_tranmid'] - 2454833.0
    disc_df['duration(h)'] = disc_df['pl_trandur']
    disc_df.loc[disc_df['duration(h)'].isna(), 'duration(h)'] = disc_df[disc_df['duration(h)'].isna()]['koi_duration']
    disc_df.loc[disc_df['duration(h)'].isna(), 'duration(h)'] = disc_df[disc_df['duration(h)'].isna()]['tce_duration']
    disc_df['depth_primary'] = disc_df['pl_trandep'] * 10000
    disc_df.loc[disc_df['depth_primary'].isna(), 'depth_primary'] = disc_df[disc_df['depth_primary'].isna()]['koi_depth']
    disc_df.loc[disc_df['depth_primary'].isna(), 'depth_primary'] = disc_df[disc_df['depth_primary'].isna()]['tce_depth']
    disc_df['radius(earth)'] = disc_df['pl_rade']
    disc_df.loc[disc_df['radius(earth)'].isna(), 'radius(earth)'] = disc_df[disc_df['radius(earth)'].isna()]['koi_prad']
    disc_df.loc[disc_df['radius(earth)'].isna(), 'radius(earth)'] = disc_df[disc_df['radius(earth)'].isna()]['tce_prad']
    disc_df = disc_df.sort_values(by=["object_id", "period"], ascending=True)
    disc_df.loc[(disc_df['kepoi_name'].isna()) & (disc_df['tce_maxmes'] > 7.1), 'type'] = 'tce_secondary'
    disc_df.loc[(disc_df['kepoi_name'].isna()) & (disc_df['tce_maxmes'] > 7.1), 'multitype'] = \
        disc_df.loc[(disc_df['kepoi_name'].isna()) & (disc_df['tce_maxmes'] > 7.1), 'multitype'] + ',tce_secondary'
    disc_df.loc[(disc_df['kepoi_name'].isna()) & (disc_df['cent_so_sigma'] > 3), 'type'] = 'tce_centroids_offset'
    disc_df.loc[(disc_df['kepoi_name'].isna()) & (disc_df['cent_so_sigma'] > 3), 'multitype'] = \
        disc_df.loc[(disc_df['kepoi_name'].isna()) & (disc_df['cent_so_sigma'] > 3), 'multitype'] + ',tce_centroids_offset'
    disc_df.loc[(disc_df['kepoi_name'].isna()) & ((disc_df['source_offset_sigma'] > 3) | (disc_df['kic_offset_sigma'] > 3)), 'type'] = 'tce_source_offset'
    disc_df.loc[(disc_df['kepoi_name'].isna()) & ((disc_df['source_offset_sigma'] > 3) | (disc_df['kic_offset_sigma'] > 3)), 'multitype'] = \
        disc_df.loc[(disc_df['kepoi_name'].isna()) & ((disc_df['source_offset_sigma'] > 3) | (disc_df['kic_offset_sigma'] > 3)), 'multitype'] + \
        ',tce_source_offset'
    disc_df.loc[(disc_df['kepoi_name'].isna()) & (disc_df['tce_bin_oedp_stat'] > 9), 'type'] = 'tce_odd_even'
    disc_df.loc[(disc_df['kepoi_name'].isna()) & (disc_df['tce_bin_oedp_stat'] > 9), 'multitype'] = \
        disc_df.loc[(disc_df['kepoi_name'].isna()) & (disc_df['tce_bin_oedp_stat'] > 9), 'multitype'] + ',tce_odd_even'
    disc_df.loc[(disc_df['kepoi_name'].isna()) & (disc_df['tce_hap_stat'] > disc_df['tce_cap_stat']), 'type'] = 'tce_og'
    disc_df.loc[(disc_df['kepoi_name'].isna()) & (disc_df['tce_hap_stat'] > disc_df['tce_cap_stat']), 'multitype'] = \
        disc_df.loc[(disc_df['kepoi_name'].isna()) & (disc_df['tce_hap_stat'] > disc_df['tce_cap_stat']), 'multitype'] + ',tce_og'
    disc_df.loc[(disc_df['kepoi_name'].isna()) & (disc_df['type'] == 'tce') & (disc_df['tce_model_snr'] > 3.5), 'type'] = 'tce_candidate'
    disc_df.loc[disc_df['disc_refname'].str.contains('Valizadegan', na=False), ['multitype']] = \
        disc_df.loc[disc_df['disc_refname'].str.contains('Valizadegan', na=False), ['multitype']] + ',planet_validated'
    disc_df.loc[disc_df['disc_refname'].str.contains('Armstrong et al. 2021', na=False), ['multitype']] = \
        disc_df.loc[disc_df['disc_refname'].str.contains('Armstrong et al. 2021', na=False), ['multitype']] + ',planet_validated'
    disc_df.loc[((disc_df['multitype'] == '') | (disc_df['multitype'].isna()) | (disc_df['multitype'] == 'nan')), 'multitype'] = disc_df.loc[((disc_df['multitype'] == '') | (disc_df['multitype'].isna()) | (disc_df['multitype'] == 'nan')), 'type']
    last_target = ''
    last_period = 0.5
    last_index = -1
    left_match_index = []
    right_match_index = []
    unpaired_index = disc_df.index.values
    for index, target_row in disc_df.iterrows():
        period_diff = 0.2 / (last_period ** (1/2))
        period_diff = 0.05 if period_diff > 0.05 else period_diff
        current_period = target_row['period']
        if last_target == target_row['object_id'] and np.abs(current_period - last_period) < period_diff * last_period:
            right_match_index = right_match_index + [index]
            if last_index not in left_match_index:
                left_match_index = left_match_index + [last_index]
            if last_index in unpaired_index:
                unpaired_index = unpaired_index[unpaired_index != last_index]
            if index in unpaired_index:
                unpaired_index = unpaired_index[unpaired_index != index]
        else:
            last_period = current_period
            last_index = index
        last_target = target_row['object_id']
    #disc_df = disc_df.loc[left_match_index].combine_first(disc_df.loc[right_match_index])
    result_df = disc_df.loc[unpaired_index]
    for i, index in enumerate(left_match_index):
        result = disc_df.loc[index].combine_first(disc_df.loc[right_match_index[i]])
        result['close_period'] = 1
        result_df = pd.concat([result_df, result.to_frame().T], ignore_index=True)
    result_df.drop(result_df[result_df['duration(h)'].isnull()].index, inplace=True)
    result_df.drop(result_df[result_df['object_id'] == 'KIC <NA>'].index, inplace=True)
    # Remove latest KIC from the catalogue
    result_df.drop(result_df[result_df['object_id'] == 'KIC 100001645'].index, inplace=True)
    result_df['ephemeris_contamination'] = 0
    result_df.loc[(result_df['koi_fpflag_ec'] == 1) & (result_df['koi_fpflag_nt'] == 0) &
                  (result_df['koi_fpflag_ss'] == 0) & (result_df['koi_fpflag_co'] == 0), 'ephemeris_contamination'] = 1
    result_df['koi_without_tce'] = 0
    result_df.loc[(~result_df['kepoi_name'].isna()) & (result_df['tce_plnt_num'].isna()), 'koi_without_tce'] = 1
    #result_df.drop(result_df[(np.isnan(result_df['tce_plnt_num']))].index, inplace=True) # discarding rows without DR25 tce
    result_df.to_csv(tces_dir + '/classified_tces_multi.csv')
    #disc_df[disc_df['object_id'] == 'KIC 7377200'].iloc[0]['epoch']
    result_df = result_df[result_df['type'].isin(['fp', 'fa', 'planet', 'planet_transit', 'tce', 'tce_og',
                                                  'tce_secondary', 'tce_source_offset', 'tce_centroids_offset',
                                                  'tce_odd_even'])]
    result_df = result_df[~result_df['radius(earth)'].isna()]
    #TODO this next statement is to prevent confirmed planets not matching any tce nor koi
    #result_df = result_df[~result_df['object_id'].str.contains('<NA')]
    result_df.to_csv(tces_dir + '/injected_objects_tces_multi.csv')


def create_synth_targets_df(tces_dir):
    inj1_df = pd.read_csv(tces_dir + '/kplr_dr25_inj1_tces.csv', comment='#')
    inj1_df['type'] = 'inj1'
    inj2_df = pd.read_csv(tces_dir + '/kplr_dr25_inj2_tces.csv', comment='#')
    inj2_df['type'] = 'inj2'
    inj3_df = pd.read_csv(tces_dir + '/kplr_dr25_inj3_tces.csv', comment='#')
    inj3_df['type'] = 'inj3'
    inv_df = pd.read_csv(tces_dir + '/kplr_dr25_inv_tces.csv', comment='#')
    inv_df['type'] = 'inv'
    scr1_df = pd.read_csv(tces_dir + '/kplr_dr25_scr1_tces.csv', comment='#')
    scr1_df['type'] = 'scr1'
    scr2_df = pd.read_csv(tces_dir + '/kplr_dr25_scr2_tces.csv', comment='#')
    scr2_df['type'] = 'scr2'
    scr3_df = pd.read_csv(tces_dir + '/kplr_dr25_scr3_tces.csv', comment='#')
    scr3_df['type'] = 'scr3'
    synth_df = pd.concat([inj1_df, inj2_df, inj3_df, inv_df, scr1_df, scr2_df, scr3_df], ignore_index=True)
    synth_df['duration(h)'] = synth_df['duration']
    synth_df['depth_primary'] = synth_df['depth']
    synth_df['radius(earth)'] = synth_df['Rp']
    synth_df.rename(columns={'KIC': 'kepid'}, inplace=True)
    synth_df['object_id'] = 'KIC ' + synth_df.loc[:, 'kepid'].astype(str)
    synth_df.to_csv(tces_dir + '/classified_tces_synthetic.csv')

def create_tess_cps_df(df_dir):
    tois_df = pd.read_csv('/home/martin/.sherlockpipe/tois.csv')
    tois_df = tois_df.loc[(tois_df["Disposition"] == "KP") | (tois_df["Disposition"] == "CP")]
    tois_df['object_id'] = tois_df['Object Id']
    tois_df['kepid'] = tois_df['Object Id'].str[4:]
    tois_df['period'] = tois_df['Period (days)']
    tois_df['epoch'] = tois_df['Epoch (BJD)']
    tois_df['duration(h)'] = tois_df['Duration (hours)']
    tois_df['depth_primary'] = tois_df['Depth (ppm)']
    tois_df['radius(earth)'] = tois_df['Planet Radius (R_Earth)']
    tois_df = tois_df.loc[(~tois_df['period'].isna()) & (tois_df['period'] > 0.0)]
    tois_df.to_csv(f"{df_dir}/tess_cps.csv", index=False)

def create_tess_fps_df(df_dir):
    tois_df = pd.read_csv('/home/martin/.sherlockpipe/tois.csv')
    tois_df = tois_df.loc[(tois_df["Disposition"] == "FP") | (tois_df["Disposition"] == "FA")]
    tois_df['object_id'] = tois_df['Object Id']
    tois_df['kepid'] = tois_df['Object Id'].str[4:]
    tois_df['period'] = tois_df['Period (days)']
    tois_df['epoch'] = tois_df['Epoch (BJD)']
    tois_df['duration(h)'] = tois_df['Duration (hours)']
    tois_df['depth_primary'] = tois_df['Depth (ppm)']
    tois_df['radius(earth)'] = tois_df['Planet Radius (R_Earth)']
    tois_df = tois_df.loc[(~tois_df['period'].isna()) & (tois_df['period'] > 0.0)]
    tois_df.to_csv(f"{df_dir}/tess_cps.csv", index=False)

def create_tess_tces_df(df_dir, single_sector_only=True):
    df = None
    if not single_sector_only:
        for file in sorted(glob.glob(f'{df_dir}/multi_sector/tess*tcestats.csv')):
            if df is None:
                df = pd.read_csv(file, comment='#')
            else:
                df = pd.concat([df, pd.read_csv(file, comment='#')], ignore_index=True)
    df.loc[:, 'sectors'] = 'all'
    for file in sorted(glob.glob(f'{df_dir}/single_sector/tess*tcestats.csv')):
        if df is None:
            df = pd.read_csv(file, comment='#')
        else:
            df = pd.concat([df, pd.read_csv(file, comment='#')], ignore_index=True)
    df.sort_values(by=['tceid', 'sectors'], ascending=[True, True], inplace=True)
    df.drop_duplicates(subset=['tceid'], keep='first', inplace=True)
    tois_df = pd.read_csv(pathlib.Path.home() / '.sherlockpipe' / 'tois.csv')
    removed_tces = 0
    df.sort_values(by=['ticid', 'tce_period'], inplace=True)
    df['type'] = 'tce_candidate'
    last_tic_id = df.iloc[0]['ticid']
    last_period = df.iloc[0]['tce_period']
    row_to_write = None
    clean_df = pd.DataFrame(columns=df.columns)
    for index, row in df.copy().iterrows():
        if row['ticid'] != last_tic_id or np.abs(1 - (last_period / row['tce_period'])) >= 0.01:
            clean_df = pd.concat([clean_df, pd.DataFrame([row_to_write])])
            row_to_write = None
        if row_to_write is None or \
                (row_to_write['ticid'] == row['ticid'] and np.abs(1 - (row_to_write['tce_period'] / row['tce_period'])) < 0.01 \
                and len(row['sectors']) > len(row_to_write['sectors'])) or last_tic_id != row['ticid'] or \
                np.abs(1 - (last_period / row['tce_period'])) >= 0.01:
            row_to_write = row
        last_period = row['tce_period']
        last_tic_id = row['ticid']
    clean_df = clean_df.loc[(~clean_df['tce_period'].isna()) & (clean_df['tce_period'] > 0.0)]
    clean_df.to_csv(df_dir + '/tces.csv')
    clean_df = pd.read_csv(df_dir + '/tces.csv')
    for index, row in tois_df.copy().iterrows():
        if len(clean_df.loc[(np.abs(row['Period (days)'] - clean_df['tce_period']) < 0.05) &
                           (int(row['Object Id'][4:]) == clean_df['ticid']) &
                           ((row["Disposition"] == "KP") | (row["Disposition"] == "CP"))]) > 0:
            clean_df.loc[(np.abs(row['Period (days)'] - clean_df['tce_period']) < 0.05) &
                           (int(row['Object Id'][4:]) == clean_df['ticid']) &
                           ((row["Disposition"] == "KP") | (row["Disposition"] == "CP")), 'type'] = 'planet_transit'
        elif len(clean_df.loc[(np.abs(row['Period (days)'] - clean_df['tce_period']) < 0.05) &
                           (int(row['Object Id'][4:]) == clean_df['ticid']) &
                           ((row["Disposition"] == "FP") | (row["Disposition"] == "FA"))]) > 0:
            clean_df.loc[(np.abs(row['Period (days)'] - clean_df['tce_period']) < 0.05) &
                           (int(row['Object Id'][4:]) == clean_df['ticid']) &
                           ((row["Disposition"] == "FP") | (row["Disposition"] == "FA")), 'type'] = 'fp'
        elif len(clean_df.loc[(np.abs(row['Period (days)'] - clean_df['tce_period']) < 0.05) &
                           (int(row['Object Id'][4:]) == clean_df['ticid'])]) > 0:
            clean_df.loc[(np.abs(row['Period (days)'] - clean_df['tce_period']) < 0.05) &
                         (int(row['Object Id'][4:]) == clean_df['ticid']), 'type'] = 'candidate'
    clean_df['object_id'] = "TIC " + clean_df['ticid'].apply(lambda x: str(x))
    clean_df['kepid'] = clean_df['ticid']
    clean_df['period'] = clean_df['tce_period']
    clean_df['epoch'] = clean_df['tce_time0bt']
    clean_df['duration(h)'] = clean_df['tce_duration']
    clean_df['depth_primary'] = clean_df['tce_depth']
    clean_df['radius(earth)'] = clean_df['tce_prad']
    clean_df.to_csv(df_dir + '/tces.csv')

def label_triage_tces_df(df_dir):
    df = None
    for file in sorted(glob.glob(f'{df_dir}/triage/spoc*fluxtriage*.txt')):
        new_df = pd.read_table(file, delim_whitespace=True, header=None)
        match = re.search(r'sector(\d+)(?:-(\d+))?', file)
        sector_start = int(match.group(1))
        sector_end = int(match.group(2)) if match.group(2) else sector_start
        sectors = f"s{sector_start:04d}"
        if sector_start != sector_end:
            sectors = 'all'
        new_df['sectors'] = sectors
        if df is None:
            df = new_df.copy()
        else:
            df = pd.concat([df, new_df], ignore_index=True)
    df.sort_values(by=['tceid', 'sectors'], ascending=[True, True], inplace=True)
    df.drop_duplicates(subset=['tceid'], keep='first', inplace=True)
    df.to_csv(f'{df_dir}/triage_tces.csv')

def label_tces_df(df_dir):
    tces_df = pd.read_csv(df_dir + '/tces.csv')
    labels_df = pd.read_csv(df_dir + '/hlsp_tess-ebs_tess_lcf-ffi_s0001-s0026_tess_v1.0_cat.csv')
    for index, row in labels_df.iterrows():
        tces_df.loc[(row['tess_id'] == tces_df['ticid']) & (np.abs(1 - row['period'] / tces_df['tce_period']) < 0.001), 'type'] = 'EB'
    labels_df = pd.read_csv(df_dir + '/triage_tces.csv')
    labels_df = labels_df.loc[labels_df['2'] == 0]
    for index, row in labels_df.iterrows():
        tces_df.loc[((tces_df['type'] == 'tce_candidate') | (tces_df['type'] == 'tce')) &
                    (row['0'] == tces_df['ticid']) & (row['1'] == tces_df['tce_plnt_num']) & (row['2'] == 0) &
                    (row['sectors'] == tces_df['sectors']), 'type'] = 'FA'
    def process_sector(sector_value):
        if sector_value == 'all':
            return 'all'
        elif sector_value.startswith("s"):
            return int(sector_value[1:])
        else:
            return int(sector_value)
    # Apply the function to the 'sectors' column
    tces_df['sectors_original'] = tces_df['sectors']
    tces_df['sectors'] = tces_df['sectors'].apply(process_sector)
    tces_df.to_csv(f'{df_dir}/tces.csv')


def download_synth_targets(download_dir, wget_files, df_file):
    df = pd.read_csv(df_file, comment='#')
    os.chdir(download_dir)
    pattern = r'kplr(\d+).*'
    pattern_date = r'(\d+)\_INJECTED.*'
    for wget_file in wget_files:
        with open(wget_file, 'r') as file:
            for line in file:
                match = re.search(pattern, line)
                if match is not None:
                    kepid = int(match.group(1))
                    rows = df[df['KIC'] == kepid]
                    for index, row in rows.iterrows():
                        if 'inj' in row['type']:
                            match_date = re.search(pattern_date, line)
                            lc_file = f'{download_dir}/kplr{kepid:09}-{match_date.group(1)}_INJECTED-' + row['type'] + '_llc.fits'
                            if not os.path.exists(lc_file):
                                print(f"Downloading: {line}")
                                os.system(line)
                                compressed_file = f'{lc_file}.gz'
                                if os.path.exists(compressed_file):
                                    with gzip.open(compressed_file, 'rb') as f_in:
                                        with open(lc_file, 'wb') as f_out:
                                            shutil.copyfileobj(f_in, f_out)
                                            os.remove(compressed_file)


def create_target_csvs(csv, target_dir, cache_dir, cores=multiprocessing.cpu_count() - 1, force=False, ids=None,
                       mode='all', mission_prefix='KIC', limit=0):
    tces_df = pd.read_csv(csv, comment='#')
    if limit > 0:
        tces_df = tces_df.iloc[0:limit]
    tces_df = tces_df.sort_values(by=["object_id"], ascending=True)
    #tces_df = tces_df.drop_duplicates(subset=["kepid"], keep='last')
    tces_df = tces_df.sort_values(by=["period"], ascending=True)
    #tces_df = tces_df.sample(frac=1).reset_index(drop=True)
    inputs = []
    if ids is not None:
        tces_df = tces_df[tces_df['object_id'].isin(ids)]
    tces_df = tces_df.reset_index(drop=True)
    ranges = range(0, len(tces_df))
    print("Total number of targets is " + str(len(tces_df)))
    for index in ranges:
        tce_row = tces_df.iloc[index]
        inputs = inputs + [CreateTargetInput(mission_prefix, tce_row['object_id'], None, target_dir, None, tce_row, cache_dir, index, force=force, mode=mode)]
    with Pool(processes=cores, maxtasksperchild=1) as pool:
        pool.map(create_target_csv, inputs, chunksize=1)


def create_synth_csvs(csv, lcs_dir, target_dir, cache_dir, cores=multiprocessing.cpu_count() - 1, force=False, ids=None, mode='all'):
    synth_df = pd.read_csv(csv, comment='#')
    synth_df = synth_df.sort_values(by=["kepid"], ascending=True)
    inputs = []
    if ids is not None:
        synth_df = synth_df[synth_df['kepid'].isin(int(id) for id in ids)]
    synth_df = synth_df.reset_index(drop=True)
    ranges = range(0, len(synth_df))
    print("Total number of targets is " + str(len(synth_df)))
    for index in ranges:
        tce_row = synth_df.iloc[index]
        kepid = int(tce_row['kepid'])
        matching_files = None
        if 'inj' in tce_row['type']:
            path_pattern = f"{lcs_dir}/kplr{kepid:09}-*.fits"
            matching_files = sorted(glob.glob(path_pattern))
        inputs = inputs + [CreateTargetInput('KIC', 'KIC ' + str(kepid), matching_files, target_dir, None, tce_row, cache_dir, index, force=force, mode=mode)]
    with Pool(processes=cores, maxtasksperchild=1) as pool:
        pool.map(create_target_csv, inputs, chunksize=1)

def create_triceratops_probs(csv, target_dir, cache_dir, cores=multiprocessing.cpu_count() - 1, force=False, ids=None):
    tces_df = pd.read_csv(csv, comment='#')
    tces_df = tces_df.sort_values(by=["kepid"], ascending=True)
    # tces_df = tces_df.drop_duplicates(subset=["kepid"], keep='last')
    #tces_df = tces_df.sample(frac=1).reset_index(drop=True)
    if not force and 'tric_tp_total' in tces_df.columns:
        tces_df = tces_df.loc[tces_df['tric_tp_total'].isna()]
    print("Total number of targets is " + str(len(tces_df)))
    inputs = []
    if ids is not None:
        tces_df = tces_df[tces_df['object_id'].isin(ids)]
    for index, tce_row in tces_df.iterrows():
        inputs = inputs + [
            CreateTargetInput('KIC', tce_row['object_id'], None, target_dir, None, tce_row, cache_dir, force=force)]
    with Pool(processes=cores, maxtasksperchild=1) as pool:
        pool.map(create_triceratops_prob, inputs, chunksize=1)
