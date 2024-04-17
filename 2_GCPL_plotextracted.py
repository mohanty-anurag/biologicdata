from galvani import BioLogic
import pandas as pd
import matplotlib.pyplot as plt

# Load the Biologic ECLAB MPR file
mpr_file = BioLogic.MPRfile('C:/Users/user/Desktop/Python_Trials/examples/Batt23-0009-cyclage01_CB3.mpr')  # Replace with the actual file path

# Extract data from the MPR file
data = mpr_file.data

# Extract data from the MPR file and convert to Pandas DataFrame
df = pd.DataFrame(data)
column_list=["flags","Ns","time/s","control/V/mA","Ewe/V","I/mA","dq/mA.h","(Q-Qo)/mA.h","I Range","Q charge/discharge/mA.h","half cycle"]


# Print dataframe to a CSV file with tab space separation and defined encoder
df.to_csv(r'C:/Users/user/Desktop/Python_Trials/examples/pyth_Batt23-0009-t1.csv',  index=False, sep='\t', encoding='utf-8',columns = column_list )

print(df)

#plot the columns
# Plotting
plt.figure(figsize=(10, 6))
plt.plot(df['time/s'], df['Ewe/V'], label='Voltage (Ewe/V)')
plt.plot(df['time/s'], df['I/mA'], label='Current (I/mA)')
plt.xlabel('Time (s)')
plt.ylabel('Value')
plt.title('Voltage and Current vs. Time')
plt.legend()
plt.grid(True)
plt.show()
