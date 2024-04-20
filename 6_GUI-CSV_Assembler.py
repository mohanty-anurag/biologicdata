import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def browse_csv_files(var):
    filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    var.set(filename)


def assemble_and_generate_plots(num_csvs, file_vars, start_vars, end_vars, output_folder_var, button, battery_name_entry):
    # Check if all CSV files are added and output folder is selected
    if len([var.get() for var in file_vars if var.get()]) != num_csvs.get() or output_folder_var.get() == "":
        messagebox.showerror("Error", "Please select all CSV files and output folder.")
        return

    # Get the list of selected CSV files and start/end values
    csv_files = [var.get() for var in file_vars if var.get()]
    start_values = [start_var.get() for start_var in start_vars]
    end_values = [end_var.get() for end_var in end_vars]

    # Initialize an empty list to store individual dataframes
    df_list = []

    # Read each CSV file, preprocess it, and append its dataframe to df_list
    for csv_file, start, end in zip(csv_files, start_values, end_values):
        df = pd.read_csv(csv_file, delimiter='\t')  # Specify delimiter as '\t'

        # Convert end to an integer
        end = int(end)

        # Skip specified number of data points from the beginning and end of the dataframe
        df = df.iloc[int(start): -end if end != 0 else None]

        df_list.append(df)

    # Concatenate all dataframes in df_list into a single dataframe
    combined_df = pd.concat(df_list, ignore_index=True)
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Get the battery name from the entry widget
    battery_name = battery_name_entry.get().strip()

    # Construct output file names with battery name and current date
    #combined_output_filename = f"{current_date}_{battery_name}_combined_output.csv"
    replaced_output_filename = f"{current_date}_{battery_name}_replaced_output.csv"

    # Save the combined dataframe to new CSV files with tab space delimiter
    # combined_output_path = os.path.join(output_folder_var.get(), combined_output_filename)
    #combined_df.to_csv(combined_output_path, index=False, sep='\t')  # Use '\t' as the delimiter

    #print("Combined CSVs saved successfully as", combined_output_path)

    # Reset index to generate a new continuous index
    combined_df.reset_index(drop=True, inplace=True)

    # Assign 'Cycle Number' values using a loop and counter
    for index in range(len(combined_df)):
        combined_df.at[index, 'Cycle Number'] = index + 1

    # Save the dataframe with modified 'Cycle Number' column to a new CSV file with tab space delimiter
    replaced_output_path = os.path.join(output_folder_var.get(), replaced_output_filename)
    combined_df.to_csv(replaced_output_path, index=False, sep='\t')  # Use '\t' as the delimiter

    print("CSV with replaced Cycle Numbers saved successfully as", replaced_output_path)

    # Generate dot plots and save them to the output folder
    generate_dot_plots(combined_df, output_folder_var.get(), battery_name, current_date)

    # Show dialog box indicating completion
    messagebox.showinfo("Done", "Processing completed.")

    # Close the windows
    button.quit()


def generate_dot_plots(df, output_folder, battery_name, current_date):
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Generate dot plot for Specific Capacitance vs Cycle Number
    plt.figure(figsize=(10, 5))
    plt.plot(df['Cycle Number'], df['Specific Capacitance (mA.h/gMA)'], 'o', color='blue')
    plt.title('Specific Capacitance vs Cycle Number')
    plt.xlabel('Cycle Number')
    plt.ylabel('Specific Capacitance (mA.h/gMA)')
    plt.grid(True)
    specific_capacitance_plot_filename = f"{current_date}_{battery_name}_Specific_Capacitance.png"
    plt.savefig(os.path.join(output_folder, specific_capacitance_plot_filename))
    plt.close()

    # Generate dot plot for Coulombic Efficiency vs Cycle Number
    plt.figure(figsize=(10, 5))
    plt.plot(df['Cycle Number'], df['Coulombic Efficiency'], 'o', color='green')
    plt.title('Coulombic Efficiency vs Cycle Number')
    plt.xlabel('Cycle Number')
    plt.ylabel('Coulombic Efficiency')
    plt.ylim(0, 110)  # Set Y range for Coulombic Efficiency
    plt.grid(True)
    coulombic_efficiency_plot_filename = f"{current_date}_{battery_name}_Coulombic_Efficiency.png"
    plt.savefig(os.path.join(output_folder, coulombic_efficiency_plot_filename))
    plt.close()


def generate_gui():
    root = tk.Tk()
    root.title("AM CSV Assembler")

    main_frame = ttk.Frame(root, padding="20")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    ttk.Label(main_frame, text="Battery Name:").grid(row=0, column=0, sticky=tk.W)
    battery_name_var = tk.StringVar()
    battery_name_entry = ttk.Entry(main_frame, textvariable=battery_name_var, width=50)
    battery_name_entry.grid(row=0, column=1, sticky=tk.W)

    ttk.Label(main_frame, text="Select number of CSV files:").grid(row=1, column=0, sticky=tk.W)
    num_csvs = tk.IntVar(value=1)
    num_csvs_dropdown = ttk.Combobox(main_frame, textvariable=num_csvs, values=[i for i in range(1, 11)],
                                     state="readonly")
    num_csvs_dropdown.grid(row=1, column=1, sticky=tk.W, padx=10)

    file_vars = []
    start_vars = []
    end_vars = []

    def add_csv_lines():
        num = num_csvs.get()
        for i in range(num):
            ttk.Label(main_frame, text=f"CSV File {i + 1}:").grid(row=i + 2, column=0, sticky=tk.W)
            file_var = tk.StringVar()
            file_vars.append(file_var)
            file_entry = ttk.Entry(main_frame, textvariable=file_var, width=50)
            file_entry.grid(row=i + 2, column=1, sticky=tk.W)
            browse_button = tk.Button(main_frame, text="Browse", command=lambda v=file_var: browse_csv_files(v))
            browse_button.grid(row=i + 2, column=2, sticky=tk.W)

            ttk.Label(main_frame, text="Start:").grid(row=i + 2, column=3, sticky=tk.W)
            start_var = tk.StringVar(value="0")
            start_vars.append(start_var)
            start_dropdown = ttk.Combobox(main_frame, textvariable=start_var, values=[i for i in range(6)],
                                          state="readonly")
            start_dropdown.grid(row=i + 2, column=4, sticky=tk.W)

            ttk.Label(main_frame, text="End:").grid(row=i + 2, column=5, sticky=tk.W)
            end_var = tk.StringVar(value="0")
            end_vars.append(end_var)
            end_dropdown = ttk.Combobox(main_frame, textvariable=end_var, values=[i for i in range(6)],
                                        state="readonly")
            end_dropdown.grid(row=i + 2, column=6, sticky=tk.W)

        root.update()
        assemble_button.config(state=tk.NORMAL)

    ttk.Button(main_frame, text="Add CSV Files", command=add_csv_lines).grid(row=1, column=2, sticky=tk.W, padx=10)

    ttk.Label(main_frame, text="Output Folder:").grid(row=12, column=0, sticky=tk.W)
    output_folder_var = tk.StringVar()
    output_folder_entry = ttk.Entry(main_frame, textvariable=output_folder_var, width=50)
    output_folder_entry.grid(row=12, column=1, sticky=tk.W)
    output_folder_button = tk.Button(main_frame, text="Browse",
                                     command=lambda: browse_output_folder(output_folder_var))
    output_folder_button.grid(row=12, column=2, sticky=tk.W)

    assemble_button = ttk.Button(main_frame, text="Assemble and Generate Plots", state=tk.DISABLED,
                                  command=lambda: assemble_and_generate_plots(num_csvs, file_vars, start_vars,
                                                                               end_vars, output_folder_var, root, battery_name_entry))
    assemble_button.grid(row=13, column=0, columnspan=3, pady=10)

    # Copyright Label
    copyright_label = tk.Label(root, text="Copyright Anurag Mohanty - 2024", fg="grey")
    copyright_label.grid(row=14, column=0, sticky="w", padx=5)

    root.mainloop()


def browse_output_folder(output_folder_var):
    folder_selected = filedialog.askdirectory()
    output_folder_var.set(folder_selected)


if __name__ == "__main__":
    generate_gui()
