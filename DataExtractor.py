import os
import re
import traceback
import threading
from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter import messagebox
from tkinter import filedialog as fd

# this is used to calculate the step for progress bar
total_files = 0

# used so multiple files section of code is run and Success message is not repeated for every file
multiple_files = False # use later for selecting multiple input

# used to indicate the last file so success message can be shows
end_of_multiple_file_process = False

# used so files can be passed here and passed to other methods
input_multiple_filenames = []

# obj for threads
global th

# the steps progress bar will take after each file completion
step_length = 0

# increments the progress bar
def pbar_step():
    pbar['value'] += step_length

# calculates each step progress bar will take for completion of one file
def calculate_step_length(total_files):
    global step_length
    step_length = 100/len(total_files)

# this portion handles all the logic for multiple files selected for input
def process_multiple_files(filenames, foldername, start_date, end_date):

    start_date_list = []
    folder = foldername.get()
    global total_files
    total_files = len(filenames)

    i = total_files - 1


    # this section below implements the feature where system reads the last logged date and makes a folder named after date
    # any file with the that date will be filtered and put into that folder
    # implementing output to multiple folders based on date
    if auto_folder_selection_check.get() == 2:
        initializing = Label(text="PLEASE WAIT: Initializing Folders...")
        initializing.grid(row=5, column=3, sticky="E")
        auto_folder_name = []
        temp_list = []
        for i in filenames:
            try:
                temp = read_file(i)
                for x in temp:
                    temp_list.append(x)
            except:
                try:
                    temp = read_file_utf8(i)
                    for x in temp:
                        temp_list.append(x)
                except:
                    print("ERROR")
            # searching the last date from each file
            for x in reversed(temp_list):
                if re.search('^[0-9]{1,2}\\/[0-9]{1,2}\\/[0-9]{4}',x):
                    date = re.search('^[0-9]{1,2}\\/[0-9]{1,2}\\/[0-9]{4}',x)
                    start_date_list.append(date.group())
                    auto_folder_name.append(date.group())
                    break
        multiple_folders = []
        for x in auto_folder_name:
            multiple_folders.append(x.replace("/", "-")) # converts date format of xx/xx/xxxx to xx-xx-xxxx
        initializing.destroy()

    '''
    Exact file names are extracted from input file names i.e. The absolute path is removed,
    and the filename is added to the targeted folder and passed to write to file method. 
    '''
    stripped_down_filename = []
    for x in filenames:
        stripped_down_filename.append(get_filename(x)) # The absolute path is removed by get_filename() method

    output_files = [] # Target Location will be added with filename and saved here

    if auto_folder_selection_check.get() == 2: # adds date folder name to absolute path
        for x in multiple_folders:
            output_files.append(folder + "/" + x)

    if auto_folder_selection_check.get() == 2:
        for x in output_files:
            try:
                os.makedirs(x) # makes folder with folder name of date xx-xx-xxxx
            except:
                pass

    final_output_location = []

    for x in range(len(filenames)):
        if auto_folder_selection_check.get() == 2:
            final_output_location.append(output_files[x] + "/" + stripped_down_filename[x]) # path contains the date folder name
        else:
            final_output_location.append(folder + "/" + stripped_down_filename[x]) # path to a single folder for each file

    for i in range(len(filenames)):
        if i == (len(filenames) -1 ): # finds the last file
            global end_of_multiple_file_process
            end_of_multiple_file_process = True
        if auto_folder_selection_check.get() == 2:
            main(filenames[i], final_output_location[i], start_date_list[i], end_date) # sends file for execution , i.e. Filter and write to file
        else:
            main(filenames[i], final_output_location[i], start_date, end_date)

    global multiple_files
    # multiple_files = False # Re-initializing variables so system can be reused without resetting the program
    end_of_multiple_file_process = False
    pbar['value'] = 0 # resets progress bar to 0


def main(input_file,output_file,start_date,end_date):
    log_file_name = get_filename(input_file)
    try:
        file = read_file(input_file) # method to read file data
        process_log_file(file,output_file,start_date,end_date,log_file_name) # method that applies filters
    except:
        try:
            file = read_file_utf8(input_file)
            process_log_file(file, output_file, start_date, end_date,log_file_name)  # method that applies filters
        except:
            print("ERROR IN FILE: "+input_file)
            traceback.print_exc()
    if multiple_files and end_of_multiple_file_process: # checks if a set of files are all complete
        messagebox.showinfo("Success","Task Completed Successfully !")
    elif not multiple_files and not end_of_multiple_file_process: # works for single file
        messagebox.showinfo("Success", "Task Completed Successfully !")

def select_file_input():
    filetypes = (('Files','*.log'),('Files','*.txt'))
    filename_selected = fd.askopenfilename(title='Open a file',initialdir='/',filetypes=filetypes)
    input_filename.set(filename_selected)

def select_file_output():
    filetypes = (('Files', '*.log'),('Files','*.txt'))
    filename_selected = fd.askopenfilename(title='Open a file',initialdir='/',filetypes=filetypes)
    output_filename.set(filename_selected)

def select_multiple_input_files():
    filetypes = (('Files', '*.log'),('Files','*.txt'))
    filenames = fd.askopenfilenames(title='Open files',initialdir='/',filetypes=filetypes)
    if filenames:
        global multiple_files
        multiple_files = True
        global text
        text = Label(app, text="*Multiple Files Selected")
        text.grid(row=1, column=3, sticky="SE")
        reset_button = Button(app,text='Reset Multiple Selection',command= lambda : reset_selection())
        reset_button.grid(row=3,column=3,sticky="E")
    global input_multiple_filenames
    input_multiple_filenames = filenames

def select_folder_output():
    foldername = fd.askdirectory(title="Select a folder")
    if foldername:
        global text_2
        text_2 = Label(app, text="*Folder Name Selected")
        text_2.grid(row=2, column=3, sticky="SE")
    output_foldername.set(foldername)

def reset_selection():
    global multiple_files
    multiple_files = False
    text.destroy()
    try:
        text_2.destroy()
    except:
        pass
def sel():
   pass

def validate_dates(start_date,end_date):
    if start_date != "":
        if end_date != "":
            if re.search('^[0-9]{1,2}\\/[0-9]{1,2}\\/[0-9]{4}',start_date) and re.search('^[0-9]{1,2}\\/[0-9]{1,2}\\/[0-9]{4}',end_date):
                return True
            else:
                return False
        else:
            if re.search('^[0-9]{1,2}\\/[0-9]{1,2}\\/[0-9]{4}',start_date):
                return True
            else:
                return False
    elif end_date != "":
        if  re.search('^[0-9]{1,2}\\/[0-9]{1,2}\\/[0-9]{4}',end_date):
            return True
    else:
        return False


def save_info():
    global multiple_files
    global input_multiple_filenames

    is_date_valid = False

    continue_run = True

    start_date_place_holder = ""
    end_date_place_holder = ""

    if filter_by_date_check.get() == 1:
        is_date_valid = validate_dates(start_date.get(), end_date.get())
        if is_date_valid:
            start_date_place_holder = start_date.get()
            end_date_place_holder = end_date.get()
        else:
            messagebox.showerror("ERROR", "Enter a valid date!")
            continue_run = False

    if continue_run:
        if multiple_files:
            if output_foldername.get() != "":
                global th
                th = threading.Thread(target=process_multiple_files, args=(
                input_multiple_filenames, output_foldername,start_date_place_holder,end_date_place_holder))  # creating a seperate thread for processing
                global end_of_multiple_file_process
                end_of_multiple_file_process = False
                th.start()
                calculate_step_length(input_multiple_filenames)
            else:
                messagebox.showerror("ERROR", "Select Output Folder!")
        else:
            if input_filename.get() != '' and output_filename.get() != '' :
                input_filename_info = input_filename.get()
                output_filename_info = output_filename.get()
                # Passes to main function
                global step_length
                step_length = 100
                main(input_filename_info,output_filename_info,start_date_place_holder,end_date_place_holder)
                pbar['value'] = 0
            else:
                messagebox.showerror("ERROR","No Field can be empty!")

def read_file(file_name):
    try:
        file = open(file_name,"r")
        return file
    except:
        messagebox.showerror("ERROR","Input File not found!")

def read_file_utf8(file_name):
    try:
        file = open(file_name,"r",encoding="utf8")
        return file
    except:
        messagebox.showerror("ERROR","Input File not found!")

def write_to_file(final_data,write_to):
    try:
        # Created new file and writes to it
        new_file = open(write_to, "x")
        for line in final_data:
            new_file.write(line)
    except:
        # Overwrites an existing file
        if var.get() == 2:
            new_file = open(write_to, "w")
            for line in final_data:
                new_file.write(line)
        else:  # Append to end of file, will also work if no radio button is selected. Protecting the old data is case of mistake.
            new_file = open(write_to, "a")
            for line in final_data:
                new_file.write(line)
    pbar_step()

def get_filename(read_from):
    name_length = len(read_from)

    i = name_length
    log_file_name_list = []

    while i != 0:
        if (read_from[i - 1] == '\\') or (read_from[i - 1] == '/'):
            break
        else:
            log_file_name_list.insert(0, read_from[i - 1])
        i = i - 1

    log_file_name = ''

    for characters in log_file_name_list:
        log_file_name += characters

    return log_file_name

def process_log_file(file,write_to,start_date,end_date,log_file_name):

    # file = read_file(read_from)

    date_filter = []

    date_match = False

    if filter_by_date_check.get() == 1 or auto_folder_selection_check.get() == 2:
        if start_date != "" and end_date != "":
            for x in file:
                if re.search('^[0-9]{1,2}\\/[0-9]{1,2}\\/[0-9]{4}',x):
                    if re.search(start_date,x):
                        date_filter.append(x)
                        date_match = True
                        continue
                    if re.search(end_date,x):
                        date_match = False
                    if date_match:
                        date_filter.append(x)
                else:
                    date_filter.append(x)
        elif start_date != "":
            for x in file:
                if re.search('^[0-9]{1,2}\\/[0-9]{1,2}\\/[0-9]{4}',x):
                    if re.search(start_date, x):
                        date_filter.append(x)
                        date_match = True
                        continue
                    if date_match:
                        date_filter.append(x)
                else:
                    date_filter.append(x)
        elif end_date != "":
            date_match = True
            for x in file:
                if re.search('^[0-9]{1,2}\\/[0-9]{1,2}\\/[0-9]{4}', x):
                    if re.search(end_date,x):
                        date_match = False
                    if date_match:
                        date_filter.append(x)
                else:
                    date_filter.append(x)
        file_data = date_filter
    else:
        file_data = file

    date_match = False

    # The first filter i.e. ONLY DB Query data is inserted in this list
    first_clean_run_query_only = []

    first_clean_run_query_only.append(log_file_name + "\n\n")

    db_query = False

    for x in file_data:
        if re.search("\[DB QUERY\]",x):
            if re.search("DELETE", x):
                continue
            db_query = True
            first_clean_run_query_only.append(x)
            continue
        if re.search(r'(\d+/\d+/\d+)',x) and db_query:
            db_query = False
        if db_query:
            first_clean_run_query_only.append(x)

    # For Debugging
    # write_to_file(first_clean_run_query_only, write_to)
    # exit(0)

    # Second filter i.e. DELETE Queries removed
    second_clean_run_delete_removed = []

    for x in first_clean_run_query_only:
        if re.search("DELETE", x):
            continue
        else:
            second_clean_run_delete_removed.append(x)

    # For Debugging
    # write_to_file(second_clean_run_delete_removed, write_to)
    # exit(0)

    # Third filter i.e. Table mp_stg_uni removed
    third_clean_run_mp_stg_removed = []

    for x in second_clean_run_delete_removed:
        if re.search("mp_stg_uni",x):
            if re.search("UMCSYS",x) or re.search("MP_LDVEW_UNI",x) or re.search("MP_BVEW_CMT",x) or re.search("MP_BVEW_UNI",x) or re.search("MP_VEW_UNI",x) or re.search("SB_MPP",x):
                third_clean_run_mp_stg_removed.append(x)
            else:
                continue
        else:
            third_clean_run_mp_stg_removed.append(x)


    # For Debugging
    # write_to_file(third_clean_run_mp_stg_removed, write_to)
    # exit(0)

    # Fourth filter i.e. "successful records removed" statements removed.
    fourth_clean_run_remove_record_statement = []

    for x in third_clean_run_mp_stg_removed:
        if re.search("records removed.",x):
            continue
        else:
            fourth_clean_run_remove_record_statement.append(x)


    # For Debugging
    # write_to_file(fourth_clean_run_remove_record_statement, write_to)
    # exit(0)


    # Fifth filter i.e. UA_SYSTEM_TABLE removed.
    fifth_clean_run_ua_system_table_removed = []
    
    for x in fourth_clean_run_remove_record_statement:
        if re.search("UA_SYSTEM_TABLES",x):
            continue
        else:
            fifth_clean_run_ua_system_table_removed.append(x)


    # For Debugging
    # write_to_file(fifth_clean_run_ua_system_table_removed, write_to)
    # exit(0)


    # Sixth filter i.e. UNICA: sql_on_connect removed
    sixth_clean_run_unica_sql_on_connect_removed = []

    for x in fifth_clean_run_ua_system_table_removed:
        if re.search("UNICA: sql_on_connect",x):
            continue
        else:
            sixth_clean_run_unica_sql_on_connect_removed.append(x)


    # For Debugging
    # write_to_file(sixth_clean_run_unica_sql_on_connect_removed, write_to)
    # exit(0)


    # Seventh filter i.e "UNICA: SCell: calling STMACC init" query removed
    seventh_clean_run_scell_calling_init_removed = []

    for x in sixth_clean_run_unica_sql_on_connect_removed:
        if re.search("SCell:",x):
            continue
        else:
            seventh_clean_run_scell_calling_init_removed.append(x)


    # For Debugging
    # write_to_file(seventh_clean_run_scell_calling_init_removed, write_to)
    # exit(0)

    eight_clean_run_remove_duplicate = []

    allow_duplicate = False

    for x in range(len(seventh_clean_run_scell_calling_init_removed)):
        if re.search(r'(\d+/\d+/\d+)',seventh_clean_run_scell_calling_init_removed[x]):
            if x != (len(seventh_clean_run_scell_calling_init_removed)-1):
                if not re.search(r'(\d+/\d+/\d+)',seventh_clean_run_scell_calling_init_removed[x+1]):
                    allow_duplicate = True
                else:
                    allow_duplicate = False
        if allow_duplicate:
            eight_clean_run_remove_duplicate.append(seventh_clean_run_scell_calling_init_removed[x])
        elif seventh_clean_run_scell_calling_init_removed[x] not in eight_clean_run_remove_duplicate:
            eight_clean_run_remove_duplicate.append(seventh_clean_run_scell_calling_init_removed[x])

    # For Debugging
    # write_to_file(seventh_clean_run_scell_calling_init_removed, write_to)
    # exit(0)


    final_list = eight_clean_run_remove_duplicate

    temp_list = [log_file_name+"\n\n","No Relevant Data Found!\n\n","Reasons for this: \n","   - There was no relevant data in the selected dates.\n","   - A wrong file was read.\n\n","NOTE: If nothing fixes the issue, Please contact system developer.\n","Contact: shehroze0912@gmail.com"]

    if len(final_list) == 1:
        write_to_file(temp_list,write_to)
    else:
        write_to_file(final_list, write_to)


app = Tk()

# Default resolution for window
app.geometry("720x580")


# Init rows and columns for grid
Grid.rowconfigure(app,0,weight=1)
Grid.columnconfigure(app,0,weight=1)
Grid.rowconfigure(app,1,weight=1)
Grid.columnconfigure(app,1,weight=1)
Grid.rowconfigure(app,2,weight=1)
Grid.columnconfigure(app,2,weight=1)
Grid.rowconfigure(app,3,weight=1)
Grid.columnconfigure(app,3,weight=1)
Grid.rowconfigure(app,4,weight=1)
Grid.columnconfigure(app,4,weight=1)
Grid.rowconfigure(app,5,weight=1)
Grid.rowconfigure(app,6,weight=1)
Grid.rowconfigure(app,7,weight=1)
app.title("LOG FILE DATA EXTRACTOR [Made by Shehroze Ehsan(Intern CVM Operations)]")

heading = Label(app,text="Log File Data Extractor",font="25")

heading.grid(row=0,column=2,columnspan=2,sticky="")

var = IntVar()
input_filename = StringVar()
output_filename = StringVar()
input_multiple_filenames = []
output_foldername = StringVar()
filter_by_date_check = IntVar()
start_date = StringVar()
end_date = StringVar()
auto_folder_selection_check = IntVar()

input_filename_text = Label(text="Input Filename :")
open_button_input = Button(app,text='Select an Input File',command= lambda : select_file_input())
output_filename_text = Label(text="Output Filename :")
open_button_output = Button(app,text='Select an Output File',command= lambda : select_file_output())
open_button_multiple_input = Button(app,text='Select Multiple Input Files',command=lambda : select_multiple_input_files())
open_button_output_folder_multiple_files = Button(app,text='Select a Folder for multiple files',command=lambda : select_folder_output())
radio_one = Radiobutton(app,text="Add To End of File",variable=var,value=1,command=sel())
radio_two = Radiobutton(app,text="Overwrite the File",variable=var,value=2,command=sel())
radio_three = Radiobutton(app, text="Apply Date Filter", variable=filter_by_date_check, value=1, command=sel())
radio_four = Radiobutton(app, text="Remove Date Filter", variable=filter_by_date_check, value=2, command=sel())
radio_five = Radiobutton(app, text="Manual Single Folder ", variable=auto_folder_selection_check, value=1, command=sel())
radio_six = Radiobutton(app, text="Auto Multiple Folders", variable=auto_folder_selection_check, value=2, command=sel())
pbar = ttk.Progressbar(app,orient=HORIZONTAL,length=300,mode="determinate")
input_filename_entry = Entry(textvariable=input_filename, width="80")
output_filename_entry = Entry(textvariable=output_filename, width="80")
start_date_text = Label(app,text="Start Date : ")
start_date_entry = Entry(textvariable=start_date,width="35")
end_date_text = Label(app,text="End Date : ")
end_date_entry = Entry(textvariable=end_date,width="35")
date_help = Label(text="NOTE: Date should be in MM/DD/YYYY Format!")
button = Button(app, text="Submit", command=save_info, width="20")

input_filename_text.grid(row=1,column=2,sticky="")
open_button_input.grid(row=1,column=3,columnspan=2,sticky="SW")
open_button_multiple_input.grid(row=1,column=3,sticky="S")
output_filename_text.grid(row=2,column=2,sticky="")
open_button_output.grid(row=2,column=3,columnspan=2,sticky="SW")
open_button_output_folder_multiple_files.grid(row=2,column=3,sticky="S")
radio_one.grid(row=6,column=2,sticky="")
radio_two.grid(row=6,column=3,sticky="W")
radio_three.grid(row=3,column=2,sticky="")
radio_four.grid(row=4,column=2,sticky="")
radio_five.grid(row=4,column=3,sticky="E")
radio_six.grid(row=3,column=3,sticky="SE")
pbar.grid(row=6,column=3,sticky="E")
start_date_text.grid(row=3,column=3,sticky="W")
input_filename_entry.grid(row=1,column=3,sticky="W")
output_filename_entry.grid(row=2,column=3,sticky="W")
start_date_entry.grid(row=3,column=2,columnspan=2,sticky="")
end_date_entry.grid(row=4,column=2,columnspan=2,sticky="")
end_date_text.grid(row=4,column=3,sticky="W")
date_help.grid(row=5,column=2,columnspan=2,sticky="")
button.grid(row=7,column=2,columnspan=2,sticky="")

mainloop()