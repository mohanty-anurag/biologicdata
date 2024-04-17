from galvani import BioLogic
import pandas as pd
import matplotlib.pyplot as plt

# Load the Biologic ECLAB MPR file
mpr_file = BioLogic.MPRfile('C:/Users/user/Desktop/Python_Trials/examples/ex2/Batt23-100_Cyclage1_CH6.mpr')  # Replace with the actual file path

# Extract data from the MPR file and convert to Pandas DataFrame
df = pd.DataFrame(mpr_file.data)

# Print dataframe to a CSV file with tab space separation and defined encoder
#df.to_csv(r'C:/Users/user/Desktop/Python_Trials/examples/ex2/pyth_Batt23-100_Cyclage1_CH6-t1.csv', sep='\t', encoding='utf-8' )
#print(df)

# Identify the number of rows where Ns = 0
num_rows_with_Ns_0 = len(df[df['Ns'] == 0])

# Skip the rows with Ns = 0 in the second dataframe
df_rounded = df.iloc[num_rows_with_Ns_0:]

# Round the values in the DataFrame to two decimal places
df_rounded = df_rounded.round(2)

# Print dataframe to a CSV file with tab space separation and defined encoder
#df_rounded.to_csv(r'C:/Users/user/Desktop/Python_Trials/examples/ex2/pyth_Batt23-100_Cyclage1_CH6-t2.csv', sep='\t', encoding='utf-8' )
#print(df_rounded)

# Initialize the third DataFrame with required columns
df_third = pd.DataFrame(columns=['Ns', 'Q charge/discharge/mA.h', 'half cycle'])

# Initialize variables
max_charge = 0
half_cycle_check = 0
row_loc = 1

# Loop through each row of the second DataFrame
for index, row in df_rounded.iterrows():
    # Check if half cycle matches with half_cycle_check
    if row['half cycle'] == half_cycle_check:
        # Replace (Q-Qo)/mA.h value in the current row of the third DataFrame
        df_third.loc[row_loc, 'Ns'] = row['Ns']
        df_third.loc[row_loc, 'Q charge/discharge/mA.h'] = row['Q charge/discharge/mA.h']
        df_third.loc[row_loc, 'half cycle'] = row['half cycle']
    else:
        # Move to the next row in the third DataFrame
        row_loc = row_loc + 1
        df_third.loc[row_loc, 'Ns'] = row['Ns']
        df_third.loc[row_loc, 'Q charge/discharge/mA.h'] = row['Q charge/discharge/mA.h']
        df_third.loc[row_loc, 'half cycle'] = row['half cycle']
        # Update half_cycle_check and max_charge
        half_cycle_check = row['half cycle']
        max_charge = row['Q charge/discharge/mA.h']

# Print the third DataFrame
print("Third DataFrame (df_third):")
print(df_third)

# Initialize the fourth DataFrame with required columns
df_fourth = pd.DataFrame(columns=['Cycle Number', 'Capa Charge (mA.h)', 'Capa Discharge (mA.h)', 'Couloumbic Efficiency'])

cycle_number = 1

# Loop through each row of the fourth DataFrame
for index in range(1, len(df_third), 2):
    print (df_third.loc[index, 'Q charge/discharge/mA.h'])
    # Calculate Cycle Number and Efficiency based on consecutive rows in the third DataFrame
    capa_charge= df_third.loc[index, 'Q charge/discharge/mA.h']
    capa_discharge =  df_third.loc[index + 1, 'Q charge/discharge/mA.h'] * (-1)
    couloumbic_efficiency= capa_discharge/ capa_charge *100
    # Add the calculated values to the fourth DataFrame
    df_fourth.loc[cycle_number, 'Cycle Number'] = cycle_number
    df_fourth.loc[cycle_number, 'Capa Charge (mA.h)'] = capa_charge
    df_fourth.loc[cycle_number, 'Capa Discharge (mA.h)'] = capa_discharge
    df_fourth.loc[cycle_number, 'Couloumbic Efficiency'] = couloumbic_efficiency
    cycle_number = cycle_number + 1


# Print the fourth DataFrame
print("Fourth DataFrame (df_fourth):")
print(df_fourth)

# Plot Efficiency vs Cycle Number
plt.plot(df_fourth['Cycle Number'], df_fourth['Couloumbic Efficiency'])
plt.xlabel('Cycle Number')
plt.ylabel('Efficiency')
plt.title('Efficiency vs Cycle Number')
plt.grid(True)
plt.show()
