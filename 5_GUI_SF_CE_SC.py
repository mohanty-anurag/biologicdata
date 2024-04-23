import tkinter as tk
from tkinter import filedialog, messagebox
import os
from galvani import BioLogic
import pandas as pd
import matplotlib.pyplot as plt


def select_single_mpr_file():
    file_path = filedialog.askopenfilename(filetypes=[("MPR files", "*.mpr")])
    if file_path:
        mpr_file_entry.delete(0, tk.END)
        mpr_file_entry.insert(0, file_path)
        process_single_button.config(state=tk.NORMAL)
        folder_option.set(False)


def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folder_path)
        process_folder_button.config(state=tk.NORMAL)
        folder_option.set(True)


def select_single_output_dir():
    output_dir = filedialog.askdirectory()
    single_output_dir_entry.delete(0, tk.END)
    single_output_dir_entry.insert(0, output_dir)


def select_folder_output_dir():
    output_dir = filedialog.askdirectory()
    folder_output_dir_entry.delete(0, tk.END)
    folder_output_dir_entry.insert(0, output_dir)


def process_single_file():
    mpr_file_path = mpr_file_entry.get()
    mass = float(entry_mass.get())
    output_dir = single_output_dir_entry.get()

    if not os.path.isfile(mpr_file_path):
        messagebox.showerror("Error", "Please select a valid MPR file.")
        return
    if not os.path.isdir(output_dir):
        messagebox.showerror("Error", "Please select a valid output directory.")
        return

    file_name = os.path.basename(mpr_file_path)
    output_file_name = f"EZ-Proc_{os.path.splitext(file_name)[0]}"

    mpr_file = BioLogic.MPRfile(mpr_file_path)
    df = pd.DataFrame(mpr_file.data)

    num_rows_with_Ns_0 = len(df[df['Ns'] == 0])
    df_rounded = df.iloc[num_rows_with_Ns_0:]
    df_rounded = df_rounded.round(2)

    df_third = pd.DataFrame(columns=['Ns', 'Q charge/discharge/mA.h', 'half cycle'])

    max_charge = 0
    half_cycle_check = 0
    row_loc = 1

    for index, row in df_rounded.iterrows():
        if row['half cycle'] == half_cycle_check:
            df_third.loc[row_loc, 'Ns'] = row['Ns']
            df_third.loc[row_loc, 'Q charge/discharge/mA.h'] = row['Q charge/discharge/mA.h']
            df_third.loc[row_loc, 'half cycle'] = row['half cycle']
        else:
            row_loc = row_loc + 1
            df_third.loc[row_loc, 'Ns'] = row['Ns']
            df_third.loc[row_loc, 'Q charge/discharge/mA.h'] = row['Q charge/discharge/mA.h']
            df_third.loc[row_loc, 'half cycle'] = row['half cycle']
            half_cycle_check = row['half cycle']
            max_charge = row['Q charge/discharge/mA.h']

    df_fourth = pd.DataFrame(
        columns=['Cycle Number', 'Capa Charge (mA.h)', 'Capa Discharge (mA.h)',
                 'Specific Capacitance (mA.h/gMA)', 'Coulombic Efficiency'])

    cycle_number = 1

    for index in range(1, len(df_third), 2):
        capa_charge = df_third.loc[index, 'Q charge/discharge/mA.h']
        capa_discharge = df_third.loc[index + 1, 'Q charge/discharge/mA.h'] * (-1)
        specific_capacitance = capa_discharge / mass
        coulombic_efficiency = capa_discharge / capa_charge * 100
        specific_capacitance = round(specific_capacitance, 2)
        coulombic_efficiency = round(coulombic_efficiency, 2)

        df_fourth.loc[cycle_number, 'Cycle Number'] = cycle_number
        df_fourth.loc[cycle_number, 'Capa Charge (mA.h)'] = capa_charge
        df_fourth.loc[cycle_number, 'Capa Discharge (mA.h)'] = capa_discharge
        df_fourth.loc[cycle_number, 'Specific Capacitance (mA.h/gMA)'] = specific_capacitance
        df_fourth.loc[cycle_number, 'Coulombic Efficiency'] = coulombic_efficiency
        cycle_number += 1

    df_fourth.to_csv(os.path.join(output_dir, f'{output_file_name}_dataframe.csv'), index=False, sep='\t',
                     encoding='utf-8')

    plt.figure(figsize=(10, 5))

    plt.subplot(1, 2, 1)
    plt.plot(df_fourth['Cycle Number'], df_fourth['Coulombic Efficiency'], 'o', color='green')
    plt.xlabel('Cycle Number')
    plt.ylabel('Coulombic Efficiency')
    plt.title('Coulombic Efficiency vs Cycle Number')
    plt.ylim(0, 110)
    plt.grid(True)

    plt.subplot(1, 2, 2)
    plt.plot(df_fourth['Cycle Number'], df_fourth['Specific Capacitance (mA.h/gMA)'], 'o', color='blue')
    plt.xlabel('Cycle Number')
    plt.ylabel('Specific Capacitance (mA.h/gMA)')
    plt.title('Specific Capacitance (mA.h/gMA) vs Cycle Number')
    plt.grid(True)

    plt.tight_layout()

    output_plot_path = os.path.join(output_dir, f"{output_file_name}_data_analysis_plot.png")
    plt.savefig(output_plot_path)

    messagebox.showinfo("Success", "Single MPR file processed successfully.")
    clear_cache()


def process_folder():
    folder_path = folder_entry.get()
    mass = float(entry_mass_folder.get())
    output_dir = folder_output_dir_entry.get()

    if not os.path.isdir(folder_path):
        messagebox.showerror("Error", "Please select a valid folder.")
        return
    if not os.path.isdir(output_dir):
        messagebox.showerror("Error", "Please select a valid output directory.")
        return

    for file_name in os.listdir(folder_path):
        if file_name.endswith('.mpr'):
            mpr_file_path = os.path.join(folder_path, file_name)
            output_file_name = f"EZ-Proc_{os.path.splitext(file_name)[0]}"

            mpr_file = BioLogic.MPRfile(mpr_file_path)
            df = pd.DataFrame(mpr_file.data)

            num_rows_with_Ns_0 = len(df[df['Ns'] == 0])
            df_rounded = df.iloc[num_rows_with_Ns_0:]
            df_rounded = df_rounded.round(2)

            df_third = pd.DataFrame(columns=['Ns', 'Q charge/discharge/mA.h', 'half cycle'])

            max_charge = 0
            half_cycle_check = 0
            row_loc = 1

            for index, row in df_rounded.iterrows():
                if row['half cycle'] == half_cycle_check:
                    df_third.loc[row_loc, 'Ns'] = row['Ns']
                    df_third.loc[row_loc, 'Q charge/discharge/mA.h'] = row['Q charge/discharge/mA.h']
                    df_third.loc[row_loc, 'half cycle'] = row['half cycle']
                else:
                    row_loc = row_loc + 1
                    df_third.loc[row_loc, 'Ns'] = row['Ns']
                    df_third.loc[row_loc, 'Q charge/discharge/mA.h'] = row['Q charge/discharge/mA.h']
                    df_third.loc[row_loc, 'half cycle'] = row['half cycle']
                    half_cycle_check = row['half cycle']
                    max_charge = row['Q charge/discharge/mA.h']

            df_fourth = pd.DataFrame(
                columns=['Cycle Number', 'Capa Charge (mA.h)', 'Capa Discharge (mA.h)',
                         'Specific Capacitance (mA.h/gMA)', 'Coulombic Efficiency'])

            cycle_number = 1

            for index in range(1, len(df_third), 2):
                capa_charge = df_third.loc[index, 'Q charge/discharge/mA.h']
                capa_discharge = df_third.loc[index + 1, 'Q charge/discharge/mA.h'] * (-1)
                specific_capacitance = capa_discharge / mass
                coulombic_efficiency = capa_discharge / capa_charge * 100
                specific_capacitance = round(specific_capacitance, 2)
                coulombic_efficiency = round(coulombic_efficiency, 2)

                df_fourth.loc[cycle_number, 'Cycle Number'] = cycle_number
                df_fourth.loc[cycle_number, 'Capa Charge (mA.h)'] = capa_charge
                df_fourth.loc[cycle_number, 'Capa Discharge (mA.h)'] = capa_discharge
                df_fourth.loc[cycle_number, 'Specific Capacitance (mA.h/gMA)'] = specific_capacitance
                df_fourth.loc[cycle_number, 'Coulombic Efficiency'] = coulombic_efficiency
                cycle_number += 1

            df_fourth.to_csv(os.path.join(output_dir, f'{output_file_name}_dataframe.csv'), index=False, sep='\t',
                             encoding='utf-8')

            plt.figure(figsize=(10, 5))

            plt.subplot(1, 2, 1)
            plt.plot(df_fourth['Cycle Number'], df_fourth['Coulombic Efficiency'], 'o', color='green')
            plt.xlabel('Cycle Number')
            plt.ylabel('Coulombic Efficiency')
            plt.title('Coulombic Efficiency vs Cycle Number')
            plt.ylim(0, 110)
            plt.grid(True)

            plt.subplot(1, 2, 2)
            plt.plot(df_fourth['Cycle Number'], df_fourth['Specific Capacitance (mA.h/gMA)'], 'o', color='blue')
            plt.xlabel('Cycle Number')
            plt.ylabel('Specific Capacitance (mA.h/gMA)')
            plt.title('Specific Capacitance (mA.h/gMA) vs Cycle Number')
            plt.grid(True)

            plt.tight_layout()

            output_plot_path = os.path.join(output_dir, f"{output_file_name}_data_analysis_plot.png")
            plt.savefig(output_plot_path)

    messagebox.showinfo("Success", "All MPR files in the folder processed successfully.")
    clear_cache()


def clear_cache():
    mpr_file_entry.delete(0, tk.END)
    single_output_dir_entry.delete(0, tk.END)
    folder_entry.delete(0, tk.END)
    entry_mass.delete(0, tk.END)
    entry_mass_folder.delete(0, tk.END)
    folder_output_dir_entry.delete(0, tk.END)
    process_single_button.config(state=tk.DISABLED)
    process_folder_button.config(state=tk.DISABLED)
    folder_option.set(False)


def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()


# Create UI
root = tk.Tk()
root.title("AM MPR File Processor")

folder_option = tk.BooleanVar(root, value=False)

single_frame = tk.LabelFrame(root, text="Single File")
single_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

folder_frame = tk.LabelFrame(root, text="Folder")
folder_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

single_button = tk.Radiobutton(root, text="Single File", variable=folder_option, value=False, command=lambda: select_single_mpr_file())
single_button.grid(row=2, column=0, padx=5, pady=5, sticky="w")

folder_button = tk.Radiobutton(root, text="Folder", variable=folder_option, value=True, command=lambda: select_folder())
folder_button.grid(row=2, column=0, padx=5, pady=5, sticky="e")

# Single File Section
mpr_file_label = tk.Label(single_frame, text="Select MPR File:")
mpr_file_label.grid(row=0, column=0, sticky="w")
mpr_file_entry = tk.Entry(single_frame, width=50)
mpr_file_entry.grid(row=0, column=1, padx=5, pady=5)
mpr_file_button = tk.Button(single_frame, text="Browse", command=select_single_mpr_file)
mpr_file_button.grid(row=0, column=2, padx=5, pady=5)

mass_label = tk.Label(single_frame, text="Mass of Active Material (g):")
mass_label.grid(row=1, column=0, sticky="w")
entry_mass = tk.Entry(single_frame, width=20)
entry_mass.grid(row=1, column=1, padx=5, sticky="w")

output_dir_label = tk.Label(single_frame, text="Select Output Directory:")
output_dir_label.grid(row=2, column=0, sticky="w")
single_output_dir_entry = tk.Entry(single_frame, width=50)
single_output_dir_entry.grid(row=2, column=1, padx=5, pady=5)
output_dir_button = tk.Button(single_frame, text="Browse", command=select_single_output_dir)
output_dir_button.grid(row=2, column=2, padx=5, pady=5)

process_single_button = tk.Button(single_frame, text="Process Data", command=process_single_file, state=tk.DISABLED)
process_single_button.grid(row=3, column=1, pady=10)

# Folder Section
folder_label = tk.Label(folder_frame, text="Select Folder:")
folder_label.grid(row=0, column=0, sticky="w")
folder_entry = tk.Entry(folder_frame, width=50)
folder_entry.grid(row=0, column=1, padx=5, pady=5)
folder_button = tk.Button(folder_frame, text="Browse", command=select_folder)
folder_button.grid(row=0, column=2, padx=5, pady=5)

mass_label_folder = tk.Label(folder_frame, text="Mass of Active Material (g):")
mass_label_folder.grid(row=1, column=0, sticky="w")
entry_mass_folder = tk.Entry(folder_frame, width=20)
entry_mass_folder.grid(row=1, column=1, padx=5, sticky="w")

output_dir_label_folder = tk.Label(folder_frame, text="Select Output Directory:")
output_dir_label_folder.grid(row=2, column=0, sticky="w")
folder_output_dir_entry = tk.Entry(folder_frame, width=50)
folder_output_dir_entry.grid(row=2, column=1, padx=5, pady=5)
output_dir_button_folder = tk.Button(folder_frame, text="Browse", command=select_folder_output_dir)
output_dir_button_folder.grid(row=2, column=2, padx=5, pady=5)

process_folder_button = tk.Button(folder_frame, text="Process Data", command=process_folder, state=tk.DISABLED)
process_folder_button.grid(row=3, column=1, pady=10)

# Close Button
close_button = tk.Button(root, text="Close", command=on_closing)
close_button.grid(row=3, column=0, pady=10)

# Copyright Label
copyright_label = tk.Label(root, text="Copyright Anurag Mohanty - 2024", fg="grey")
copyright_label.grid(row=5, column=0, sticky="w", padx=5)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
