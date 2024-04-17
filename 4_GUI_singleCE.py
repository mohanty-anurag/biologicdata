import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os
from galvani import BioLogic
import pandas as pd
import matplotlib.pyplot as plt

def select_mpr_file():
    file_path = filedialog.askopenfilename(filetypes=[("MPR files", "*.mpr")])
    mpr_file_entry.delete(0, tk.END)
    mpr_file_entry.insert(0, file_path)

def select_output_dir():
    output_dir = filedialog.askdirectory()
    output_dir_entry.delete(0, tk.END)
    output_dir_entry.insert(0, output_dir)

def process_data():
    mpr_file_path = mpr_file_entry.get()
    output_dir = output_dir_entry.get()
    if not os.path.isfile(mpr_file_path):
        messagebox.showerror("Error", "Please select a valid MPR file.")
        return
    if not os.path.isdir(output_dir):
        messagebox.showerror("Error", "Please select a valid output directory.")
        return

    # Load the Biologic ECLAB MPR file
    mpr_file = BioLogic.MPRfile(mpr_file_path)

    # Extract data from the MPR file and convert to Pandas DataFrame
    df = pd.DataFrame(mpr_file.data)

    # Identify the number of rows where Ns = 0
    num_rows_with_Ns_0 = len(df[df['Ns'] == 0])

    # Skip the rows with Ns = 0 in the second dataframe
    df_rounded = df.iloc[num_rows_with_Ns_0:]

    # Round the values in the DataFrame to two decimal places
    df_rounded = df_rounded.round(2)

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

    # Save the third DataFrame to CSV
    #df_third.to_csv(os.path.join(output_dir, "third_dataframe.csv"), index=False)

    # Initialize the fourth DataFrame with required columns
    df_fourth = pd.DataFrame(columns=['Cycle Number', 'Capa Charge (mA.h)', 'Capa Discharge (mA.h)', 'Coulombic Efficiency'])

    cycle_number = 1

    # Loop through each row of the fourth DataFrame
    for index in range(1, len(df_third), 2):
        # Calculate Cycle Number and Efficiency based on consecutive rows in the third DataFrame
        capa_charge = df_third.loc[index, 'Q charge/discharge/mA.h']
        capa_discharge = df_third.loc[index + 1, 'Q charge/discharge/mA.h'] * (-1)
        coulombic_efficiency = capa_discharge / capa_charge * 100
        # Add the calculated values to the fourth DataFrame
        df_fourth.loc[cycle_number, 'Cycle Number'] = cycle_number
        df_fourth.loc[cycle_number, 'Capa Charge (mA.h)'] = capa_charge
        df_fourth.loc[cycle_number, 'Capa Discharge (mA.h)'] = capa_discharge
        df_fourth.loc[cycle_number, 'Coulombic Efficiency'] = coulombic_efficiency
        cycle_number += 1

    # Save the fourth DataFrame to CSV
    df_fourth.to_csv(os.path.join(output_dir, "fourth_dataframe.csv"), index=False)

    # Plot Efficiency vs Cycle Number
    plt.plot(df_fourth['Cycle Number'], df_fourth['Coulombic Efficiency'])
    plt.xlabel('Cycle Number')
    plt.ylabel('Efficiency')
    plt.title('Efficiency vs Cycle Number')
    plt.savefig(os.path.join(output_dir, "efficiency_vs_cycle_number.png"))
    plt.show()

# Create UI
root = tk.Tk()
root.title("MPR File Processor")

# MPR file selection
mpr_file_label = tk.Label(root, text="Select MPR File:")
mpr_file_label.grid(row=0, column=0, sticky="w")
mpr_file_entry = tk.Entry(root, width=50)
mpr_file_entry.grid(row=0, column=1, padx=5, pady=5)
mpr_file_button = tk.Button(root, text="Browse", command=select_mpr_file)
mpr_file_button.grid(row=0, column=2, padx=5, pady=5)

# Output directory selection
output_dir_label = tk.Label(root, text="Select Output Directory:")
output_dir_label.grid(row=1, column=0, sticky="w")
output_dir_entry = tk.Entry(root, width=50)
output_dir_entry.grid(row=1, column=1, padx=5, pady=5)
output_dir_button = tk.Button(root, text="Browse", command=select_output_dir)
output_dir_button.grid(row=1, column=2, padx=5, pady=5)

# Process data button
process_button = tk.Button(root, text="Process Data", command=process_data)
process_button.grid(row=2, column=1, pady=10)

root.mainloop()
