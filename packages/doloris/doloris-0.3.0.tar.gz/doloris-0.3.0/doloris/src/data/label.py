def define_label_binary(df):
    df = df.copy()
    df['label_binary'] = df['final_result'].map(lambda x: 1 if x in ['Pass', 'Distinction'] else 0)
    return df


def define_label_multiclass(df):
    label_map = {
        'Distinction': 2,
        'Pass': 1,
        'Withdrawn': 0,
        'Fail': -1
    }
    df = df.copy()
    df['label_multiclass'] = df['final_result'].map(label_map)
    return df

def LabelEncoder(df):
    age_map = {
        '0-35': 0,
        '35-55': 1,
        '55<=': 2
    }
    highest_education_map = {
        'Lower Than A Level': 0,
        'A Level or Equivalent': 1,
        'HE Qualification': 2
    }
    imd_band_map = {
        '0-10%': 0,
        '10-20': 1,
        '20-30%': 2,
        '30-40%': 3,
        '40-50%': 4,
        '50-60%': 5,
        '60-70%': 6,
        '70-80%': 7,
        '80-90%': 8,
        '90-100%': 9
    }
    df = df.copy()
    df['age_band'] = df['age_band'].map(age_map)
    df['highest_education'] = df['highest_education'].map(highest_education_map)
    df['imd_band'] = df['imd_band'].map(imd_band_map)
    return df