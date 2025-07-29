import os
import glob
import pandas as pd

def prep_vle_data(df, rq):
    keys_act = ['code_module', 'code_presentation', 'id_student', 'activity_type']
    keys_assess = ['code_module', 'code_presentation', 'id_student', 'id_assessment', 'activity_type']

    if rq == 1:
        keys = keys_act
        keys_2 = keys_act[0:3]
    else:
        keys = keys_assess
        keys_2 = keys_assess[0:4]

    n_days = df.groupby(keys)['date'].nunique().reset_index().rename(columns={'date': 'n_days'})
    avg_clicks = df.groupby(keys)['sum_click'].mean().reset_index().rename(columns={'sum_click': 'avg_sum_clicks'})
    vle_df = n_days.merge(avg_clicks, on=keys, how='inner')

    if rq == 2:
        vle_df['id_assessment'] = vle_df['id_assessment'].astype(str)

    vle_df = vle_df.set_index(keys).unstack().reset_index()
    vle_df.columns = ['_'.join(c) for c in vle_df.columns]
    vle_df.columns = vle_df.columns.str.rstrip('_')

    if rq == 2:
        vle_df['id_assessment'] = vle_df['id_assessment'].astype(int)

    n_tot_days = df.groupby(keys_2)['date'].nunique().reset_index().rename(columns={'date': 'total_n_days'})
    avg_tot_clicks = df.groupby(keys_2)['sum_click'].mean().reset_index().rename(columns={'sum_click': 'avg_total_sum_clicks'})
    tot_vle = n_tot_days.merge(avg_tot_clicks, on=keys_2, how='inner')

    vle_df = vle_df.merge(tot_vle, on=keys_2, how='inner')

    return vle_df

def basic_clean(df):
    df = df.dropna(axis=1, how='all')
    if 'imd_band' in df.columns:
        df = df.dropna(subset=['imd_band'])
    df = df.fillna(0)
    df = df.drop_duplicates()
    return df

def clean_student_vle(df_vle, df_vle_meta):
    df = df_vle.merge(df_vle_meta, on=['code_module', 'code_presentation', 'id_site'], how='inner')
    df = df.drop(columns=['week_from', 'week_to'], errors='ignore')
    if 'sum_click' in df.columns:
        cap = df['sum_click'].quantile(0.99)
        df['sum_click'] = df['sum_click'].clip(upper=cap)
    return df

def get_master_df_rq1(data_dict):
    df_info = data_dict['studentInfo']
    df_vle = data_dict['studentVle']
    df_assess = data_dict['studentAssessment']
    df_reg = data_dict['studentRegistration']
    df_assessments = data_dict['assessments']
    df_vle_meta = data_dict['vle']

    keys = ['code_module', 'code_presentation', 'id_student', 'id_assessment', 'id_site']

    rq1_df = df_info.merge(df_reg, on=['code_module', 'code_presentation', 'id_student'], how='inner')

    student_vle = clean_student_vle(df_vle, df_vle_meta)
    rq1_vle_final = prep_vle_data(student_vle, rq=1)

    rq1_df = rq1_df.merge(rq1_vle_final, on=['code_module', 'code_presentation', 'id_student'], how='inner')

    return rq1_df

def load_data(data_dir='Data'):
    data_dict = {}
    for file in glob.glob(os.path.join(data_dir, '*.csv')):
        name = os.path.splitext(os.path.basename(file))[0]
        df = pd.read_csv(file)
        data_dict[name] = df
    return data_dict

def run_clean_and_integrate(data_dir='Data', output_path='outputs/dataframes/cleaned_master_df.csv'):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    data_dict = load_data(data_dir)

    for key in ['studentInfo', 'studentAssessment', 'studentRegistration', 'assessments', 'vle', 'studentVle']:
        if key in data_dict:
            data_dict[key] = basic_clean(data_dict[key])

    master_df = get_master_df_rq1(data_dict)

    master_df.to_csv(output_path, index=False)
    print(f"Cleaned and integrated master dataframe saved to: {output_path}")

    return master_df

if __name__ == '__main__':
    run_clean_and_integrate()
