import pandas as pd


def query_pandas(station_name, var):
    try:
        variant = 'V' + str(var)
        df_settings = pd.read_csv(f'buffer_settings/{station_name}_settings.csv')
        df_settings = df_settings.apply(lambda col: col.str.strip() if col.dtype == "object" else col)
        print(df_settings)
        variant_filter = df_settings['Variant_Code'] == variant
        machine_filter = df_settings['AssetName'] == station_name
        filtered_df = df_settings[machine_filter & variant_filter]
        print(filtered_df)
        variant_name = filtered_df['VariantName'].tolist()[0]
        station_full_name = filtered_df['AssetDescription'].tolist()[0]
        return variant_name, station_full_name
    except Exception as e:
        print(f"Query pandas error {e}")
        return 'XXXX', 'XXXX'


query_pandas('OP10', '0')
