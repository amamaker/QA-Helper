from datetime import datetime
from bs4 import BeautifulSoup
import requests
from requests.auth import HTTPBasicAuth
import json
import pyperclip
from tkinter import *
import customtkinter
import os
from PIL import Image, ImageTk
from cryptography.fernet import Fernet
import re
import webbrowser
import paramiko
import numpy as np
import matplotlib.pyplot as plt
import stat
import shutil
import threading
import schedule
import time

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

def only_latin_password(event):
    input_widget = event.widget
    input_text = input_widget.get()
    cursor_position = input_widget.index("insert")

    latin_text = re.sub(r'[А-Яа-я]', '', input_text)
    input_widget.delete(0, "end")
    input_widget.insert(0, latin_text)

    input_widget.icursor(cursor_position)

def only_latin_username(event):
    input_widget = event.widget
    input_text = input_widget.get()
    cursor_position = input_widget.index("insert")

    latin_text = re.sub(r'[^a-zA-Z0-9\.\-\s_]', '', input_text)
    input_widget.delete(0, "end")
    input_widget.insert(0, latin_text)

    input_widget.icursor(cursor_position)

def only_numberspoint_ip(event):
    input_widget = event.widget
    input_text = input_widget.get()
    cursor_position = input_widget.index("insert")

    latin_text = re.sub(r'[^0-9.]+', '', input_text)
    input_widget.delete(0, "end")
    input_widget.insert(0, latin_text)

    input_widget.icursor(cursor_position)

def open_folder(path):
    app.check_folders()
    app.check_ip_data()
    os.startfile(path)

def  delete_files_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f'Ошибка при удалении файла {file_path}. {e}')

def delete_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Error while deleting {file_path}. {e}')

def open_ip_map():
    second_window = customtkinter.CTkToplevel()
    second_window.title("IP map")
    current_path = os.path.dirname(os.path.realpath(__file__))
    ip_map_image = customtkinter.CTkImage(Image.open(current_path + "/assets/IPmap.png"),
                                                  size=(760, 572))
    ip_map = customtkinter.CTkLabel(second_window, text="", image=ip_map_image)
    ip_map.grid(row=0, column=0, padx=(10, 10), pady=(10, 10))


class App(customtkinter.CTk):
    width = 1000
    height = 550

    def __init__(self):
        super().__init__()

        # configure window
        self.title("QA Helper")
        self.geometry(f"{self.width}x{self.height}")
        self.resizable(width=False, height=False)

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # read credentials
        self.Read_credentials()
        self.Set_credentials()

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")

        # create logo label
        current_path = os.path.dirname(os.path.realpath(__file__))
        self.main_logo_image = customtkinter.CTkImage(Image.open(current_path + "/assets/boy.png"),
                                               size=(100, 100))
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="", image=self.main_logo_image)
        self.logo_label.grid(row=0, column=0, padx=(0, 0), pady=(10, 0))
        self.main_label = customtkinter.CTkLabel(self.sidebar_frame, text="QA Helper", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.main_label.grid(row=1, column=0, padx=(0, 0), pady=(0, 10))

        # BUTTONS
        self.plan_button = customtkinter.CTkButton(master=self.sidebar_frame, text="Daily plan", command=self.plan)
        self.plan_button.grid(row=2, column=0, padx=(20, 20), pady=(10, 10), sticky="nsew")
        self.report_button = customtkinter.CTkButton(master=self.sidebar_frame, text="Daily report", command=self.report)
        self.report_button.grid(row=3, column=0, padx=(20, 20), pady=(0, 10), sticky="nsew")
        self.copy_button = customtkinter.CTkButton(master=self.sidebar_frame, command=self.copy_textbox, text="Copy to clipboard", fg_color="transparent", border_width=1, text_color=("gray10", "#DCE4EE"))
        self.copy_button.grid(row=4, column=0, padx=(20, 20), pady=(0, 10), sticky="nsew")
        self.login_button = customtkinter.CTkButton(master=self.sidebar_frame, text=self.username, command=self.open_toplevel)
        self.login_button.grid(row=9, column=0, padx=(20, 20), pady=(230, 10), sticky="nsew")
        self.toplevel_window = None

        # main frame
        self.main_frame = customtkinter.CTkFrame(self, width=140, height=500, corner_radius=0)
        self.main_frame.grid(row=0, column=1, rowspan=4, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.tabview = customtkinter.CTkTabview(master=self.main_frame, width=250, height=540)
        self.tabview.grid(row=0, column=0, padx=(0, 5), pady=(0, 0), sticky="nsew")
        self.tabview.add(" Reports ")
        self.tabview.add(" Game logs ")
        self.tabview.add("Memory logs")
        self.tabview.add("Specifications")
        self.tabview.add("USB Authorization")
        self.tabview.add(" Settings ")
        self.tabview.tab(" Reports ").grid_columnconfigure(0, weight=1)
        self.tabview.tab(" Game logs ").grid_columnconfigure((0,1), weight=1)
        self.tabview.tab("Memory logs").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Specifications").grid_columnconfigure(0, weight=1)
        self.tabview.tab("USB Authorization").grid_columnconfigure((0,1), weight=1)
        self.tabview.tab(" Settings ").grid_columnconfigure((0,1), weight=1)

        # Settings
        self.appearance_mode_label = customtkinter.CTkLabel(self.tabview.tab(" Settings "), text="Theme:", font=customtkinter.CTkFont(size=15, weight="bold"), anchor="w")
        self.appearance_mode_label.grid(row=0, column=0, padx=(20, 150), pady=(50, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.tabview.tab(" Settings "),
                                                                       values=["System", "Light", "Dark"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=1, column=0, padx=(20, 150), pady=(0, 0))
        self.scaling_label = customtkinter.CTkLabel(self.tabview.tab(" Settings "), text="UI Scaling:", font=customtkinter.CTkFont(size=15, weight="bold"), anchor="w")
        self.scaling_label.grid(row=0, column=1, padx=(0,0), pady=(50, 0))
        self.scaling_optionmenu = customtkinter.CTkOptionMenu(self.tabview.tab(" Settings "),
                                                               values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionmenu.set("100%")
        self.scaling_optionmenu.grid(row=1, column=1, padx=(0,0), pady=(0, 0))
        self.cache_label = customtkinter.CTkLabel(self.tabview.tab(" Settings "), text="Cache:", font=customtkinter.CTkFont(size=15, weight="bold"), anchor="w")
        self.cache_label.grid(row=2, column=0, padx=(20, 150), pady=(10, 0))
        self.clear_cache = customtkinter.CTkButton(self.tabview.tab(" Settings "),
                                                       text="Clear cache",
                                                       fg_color="transparent",
                                                       border_width=2,
                                                       text_color=("gray10", "#DCE4EE"),
                                                       command=lambda: self.del_cache())
        self.clear_cache.grid(row=3, column=0, padx=(20, 150), pady=(5, 0), sticky="ew")

        # create switches
        self.appearance_mode_label = customtkinter.CTkLabel(self.tabview.tab(" Settings "), text="Daily report settings:", font=customtkinter.CTkFont(size=15, weight="bold"), anchor="w")
        self.appearance_mode_label.grid(row=0, column=2, padx=(150,50), pady=(50, 0))
        self.switch1 = customtkinter.CTkSwitch(self.tabview.tab(" Settings "), text=f"Opened")
        self.switch1.grid(row=1, column=2, padx=(0,0), pady=(5, 10))
        self.switch1.select(1)
        self.switch2 = customtkinter.CTkSwitch(self.tabview.tab(" Settings "), text=f"Closed")
        self.switch2.grid(row=2, column=2, padx=(0,0), pady=(0, 10))
        self.switch2.select(1)
        self.switch3 = customtkinter.CTkSwitch(self.tabview.tab(" Settings "), text=f"Reopened")
        self.switch3.grid(row=3, column=2, padx=(0,0), pady=(0, 10))
        self.switch3.select(1)
        self.switch4 = customtkinter.CTkSwitch(self.tabview.tab(" Settings "), text=f"Tasks")
        self.switch4.grid(row=4, column=2, padx=(0,0), pady=(0, 10))
        self.switch4.select(1)

        # schedule
        self.schedule_label = customtkinter.CTkLabel(self.tabview.tab(" Settings "), text="Schedule", font=customtkinter.CTkFont(size=15, weight="bold"), anchor="w")
        self.schedule_label.grid(row=6, column=2, padx=(0,0), pady=(10, 10))
        self.report_schedule_switch = customtkinter.CTkSwitch(self.tabview.tab(" Settings "), text=f"Report")
        self.report_schedule_switch.grid(row=7, column=2, padx=(0,0), pady=(0, 10))
        # self.report_schedule_switch.select(0)
        self.plan_schedule_switch = customtkinter.CTkSwitch(self.tabview.tab(" Settings "), text=f"Plan")
        self.plan_schedule_switch.grid(row=8, column=2, padx=(0,0), pady=(0, 10))
        # self.plan_schedule_switch.select(0)


        # create textbox
        self.textbox = customtkinter.CTkTextbox(self.tabview.tab(" Reports "), width=240, height=490)
        self.textbox.grid(row=0, column=0, padx=(0, 0), pady=(0, 0), sticky="nsew")

        # create login frame
        self.login_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.login_frame.grid(padx=(15, 15), pady=(15, 15), row=0, column=0, sticky="ns")
        self.login_label = customtkinter.CTkLabel(self.login_frame, text="Sign in\n to your account", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.login_label.grid(row=0, column=0, padx=30, pady=(165, 20))
        self.username_entry = customtkinter.CTkEntry(self.login_frame, width=200, placeholder_text="Username")
        self.username_entry.grid(row=1, column=0, padx=30, pady=(15, 15))
        self.username_entry.bind("<KeyRelease>", only_latin_username)
        self.password_entry = customtkinter.CTkEntry(self.login_frame, width=200, show="*", placeholder_text="Password")
        self.password_entry.grid(row=2, column=0, padx=30, pady=(0, 0))
        self.password_entry.bind("<KeyRelease>", only_latin_password)
        self.error_label = customtkinter.CTkLabel(self.login_frame, text="Test", text_color="red")
        self.error_label.grid(row=3, column=0, padx=30, pady=(10, 0))
        self.auth_button = customtkinter.CTkButton(self.login_frame, text="Sign in", command=self.back_event, width=200)
        self.auth_button.grid(row=4, column=0, padx=30, pady=(150, 0))
        self.back_button = customtkinter.CTkButton(self.login_frame, fg_color="transparent", width=180, border_width=1, text_color=("gray10", "#DCE4EE"), text="Back", command=self.back_login_frame)
        self.back_button.grid(row=5, column=0, padx=30, pady=(10, 30), sticky="nsew")
        self.password_entry.bind("<Return>", self.back_event)
        self.username_entry.bind("<Return>", self.back_event)
        self.login_frame.grid_forget()


        # create SSH page
        # New frame with scroll - create SSH page
        # column 1 - all IP
        self.scroll_frame = customtkinter.CTkScrollableFrame(self.tabview.tab(" Game logs "), width=300, height=475)
        self.scroll_frame.grid(row=0, column=0, padx=(5, 5), pady=(5, 5), rowspan=100, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        self.scr_switch = customtkinter.CTkSwitch(self.tabview.tab(" Game logs "), text="DG log", command=self.switch_text)
        self.scr_switch.grid(row=1, column=1, padx=(5, 5), pady=(10, 10), columnspan=100, sticky="ew")
        self.ip_entry = customtkinter.CTkEntry(self.tabview.tab(" Game logs "), placeholder_text="IP")
        self.ip_entry.grid(row=1, column=2, padx=(40, 5), pady=(10, 10), sticky="ew")
        self.ip_entry.bind("<KeyRelease>", only_numberspoint_ip)
        self.add_button_ip = customtkinter.CTkButton(self.tabview.tab(" Game logs "), fg_color="transparent",
                                                     text="Add", border_width=2,
                                                     text_color=("gray10", "#DCE4EE"), command=self.save_ip, width=50)
        self.add_button_ip.grid(row=1, column=3, padx=(5, 5), pady=(10, 10), columnspan=100)
        self.automat_button01 = customtkinter.CTkButton(self.tabview.tab(" Game logs "), text="Open DG.log folder",
                                                        command=lambda: open_folder('logs'))
        self.automat_button01.grid(row=2, column=1, padx=(5, 5), pady=(0, 0), columnspan=100, sticky="ew")
        self.automat_button02 = customtkinter.CTkButton(self.tabview.tab(" Game logs "), text="Open screenshots folder",
                                                        command=lambda: open_folder('screenshots'))
        self.automat_button02.grid(row=3, column=1, padx=(5, 5), pady=(5, 0), columnspan=100, sticky="ew")
        self.ssh_status_label = customtkinter.CTkLabel(self.tabview.tab(" Game logs "), text="")
        self.ssh_status_label.grid(row=4, column=1, padx=(5, 5), pady=(5, 10), columnspan=100, sticky="ew")
        self.ip_map_btn = customtkinter.CTkButton(self.tabview.tab(" Game logs "), fg_color="transparent",
                                                       border_width=2,
                                                       text_color=("gray10", "#DCE4EE"),
                                                       text="Open IP map",
                                                       command=open_ip_map)
        self.ip_map_btn.grid(row=96, column=1, padx=(5, 5), pady=(5, 0), columnspan=100, sticky="ew")
        self.delete_button01 = customtkinter.CTkButton(self.tabview.tab(" Game logs "), fg_color="transparent",
                                                       border_width=2,
                                                       text_color=("gray10", "#DCE4EE"),
                                                       text="Delete all DG.log",
                                                       command=lambda: self.del_dglog())
        self.delete_button01.grid(row=97, column=1, padx=(5, 5), pady=(5, 0), columnspan=100, sticky="ew")
        self.delete_button02 = customtkinter.CTkButton(self.tabview.tab(" Game logs "), fg_color="transparent",
                                                       border_width=2,
                                                       text_color=("gray10", "#DCE4EE"),
                                                       text="Delete all screenshots",
                                                       command=lambda: self.del_screenshots())
        self.delete_button02.grid(row=98, column=1, padx=(5, 5), pady=(5, 5), columnspan=100, sticky="ew")

        # mem log page
        self.ip_dropbox = customtkinter.CTkOptionMenu(self.tabview.tab("Memory logs"),
                                                      values=self.update_option_menu())
        self.ip_dropbox.grid(row=0, column=1, padx=(5, 5), pady=(5, 0), sticky="ew")
        self.mem_button = customtkinter.CTkButton(self.tabview.tab("Memory logs"), text="Get log", command=lambda: self.create_graph())
        self.mem_button.grid(row=1, column=1, padx=(5, 5), pady=(5, 0), sticky="ew")
        self.canvas_frame = customtkinter.CTkFrame(self.tabview.tab("Memory logs"), width=640, height=480)
        self.canvas_frame.grid(row=0, column=0, padx=(5, 5), pady=(5, 0), sticky="ew", rowspan=100)
        self.img_label = customtkinter.CTkLabel(self.canvas_frame, image=None, text='', width=640, height=480)
        self.automat_button02 = customtkinter.CTkButton(self.tabview.tab("Memory logs"), text="Open mem.log folder", command=lambda: open_folder('memory'))
        self.automat_button02.grid(row=2, column=1, padx=(5, 5), pady=(5, 0), sticky="ew")
        self.ip_map_btn_mem = customtkinter.CTkButton(self.tabview.tab("Memory logs"), fg_color="transparent",
                                                  border_width=2,
                                                  text_color=("gray10", "#DCE4EE"),
                                                  text="Open IP map",
                                                  command=open_ip_map)
        self.ip_map_btn_mem.grid(row=96, column=1, padx=(5, 5), pady=(5, 0), columnspan=100, sticky="ew")
        self.delete_button03 = customtkinter.CTkButton(self.tabview.tab("Memory logs"), fg_color="transparent", border_width=2,
                                                       text_color=("gray10", "#DCE4EE"), text="Delete all mem.log",
                                                       command=lambda: self.del_mem())
        self.delete_button03.grid(row=97, column=1, padx=(5, 5), pady=(5, 0), sticky="ew")
        self.automat_button03 = customtkinter.CTkButton(self.tabview.tab("Memory logs"), text="Open graphics folder", command=lambda: open_folder('graphs'))
        self.automat_button03.grid(row=3, column=1, padx=(5, 5), pady=(5, 0), sticky="ew")
        self.delete_button04 = customtkinter.CTkButton(self.tabview.tab("Memory logs"), fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"),
                                                       text="Delete all graphics",
                                                       command=lambda: self.del_graphs())
        self.delete_button04.grid(row=98, column=1, padx=(5, 5), pady=(5, 0), sticky="ew")
        self.img_label.pack()

        #specification page
        self.spec_textbox = customtkinter.CTkTextbox(self.tabview.tab("Specifications"), width=640, height=490)
        self.spec_textbox.grid(row=0, column=0, padx=(5, 5), pady=(5, 0), sticky="nsew", rowspan=100)
        self.spec_switch = customtkinter.CTkSwitch(self.tabview.tab("Specifications"), text="Short view", command=self.switch_spec)
        self.spec_switch.grid(row=1, column=1, padx=(5, 5), pady=(10, 10), sticky="ew")
        self.spec_dropbox = customtkinter.CTkOptionMenu(self.tabview.tab("Specifications"), values=self.update_option_menu())
        self.spec_dropbox.grid(row=0, column=1, padx=(5, 5), pady=(5, 0), sticky="ew")
        self.info_button = customtkinter.CTkButton(self.tabview.tab("Specifications"), text="Get info", command=lambda: self.specification())
        self.info_button.grid(row=2, column=1, padx=(5, 5), pady=(5, 0), sticky="ew")
        self.open_jenkins = customtkinter.CTkButton(self.tabview.tab("Specifications"),
                                                 text="Open in Jenkins", command=self.open_jenkins)
        self.open_jenkins.grid(row=4, column=1, padx=(5, 5), pady=(0, 0), sticky="ew")
        self.open_spec = customtkinter.CTkButton(self.tabview.tab("Specifications"), text="Open specification folder",
                                                        command=lambda: open_folder('specification'))
        self.open_spec.grid(row=5, column=1, padx=(5, 5), pady=(5, 0), sticky="ew")
        self.ip_map_btn_spec = customtkinter.CTkButton(self.tabview.tab("Specifications"), fg_color="transparent",
                                                      border_width=2,
                                                      text_color=("gray10", "#DCE4EE"),
                                                      text="Open IP map",
                                                      command=open_ip_map)
        self.ip_map_btn_spec.grid(row=97, column=1, padx=(5, 5), pady=(5, 0), columnspan=100, sticky="ew")
        self.delete_button05 = customtkinter.CTkButton(self.tabview.tab("Specifications"), fg_color="transparent",
                                                       border_width=2, text_color=("gray10", "#DCE4EE"),
                                                       text="Delete all specification",
                                                       command=lambda: self.del_spec())
        self.delete_button05.grid(row=98, column=1, padx=(5, 5), pady=(5, 0), sticky="ew")

        #USB Auth page
        self.usb_dropbox = customtkinter.CTkOptionMenu(self.tabview.tab("USB Authorization"), values=self.update_option_menu())
        self.usb_dropbox.grid(row=0, column=0, padx=(20, 150), pady=(50, 0), sticky="w")
        self.usb_checkbox = customtkinter.CTkCheckBox(self.tabview.tab("USB Authorization"), text="Reboot", fg_color="red", command=self.chg_usb_label)
        self.usb_checkbox.grid(row=1, column=0, padx=(20, 150), pady=(10, 0), sticky="w")
        self.usb_start_button = customtkinter.CTkButton(self.tabview.tab("USB Authorization"), text="Authorize", fg_color="transparent",
                                                       border_width=2, text_color=("gray10", "#DCE4EE"), command=lambda: self.start_usb_authorization())
        self.usb_start_button.grid(row=2, column=0, padx=(20, 150), pady=(10, 0), sticky="w")
        self.usb_label = customtkinter.CTkLabel(self.tabview.tab("USB Authorization"), text="", font=customtkinter.CTkFont(size=12, weight="bold"), text_color="red")
        self.usb_label.grid(row=3, column=0, padx=(20, 150), pady=(0, 0), sticky="w")


        # get response status code
        # self.loading_screen()
        self.init_request()
        self.create_ip_buttons()
        self.switch_text()

        schedule.every().day.at("17:55").do(self.run_report_schedule)
        schedule.every().day.at("09:30").do(self.run_plan_schedule)
        first = threading.Thread(target=self.report_schedule)
        first.start()

    def start_usb_authorization(self):
        self.check_folders()
        try:
            self.usb_authorization(self.usb_dropbox.get())
        except Exception as e:
            print(f"Произошла ошибка: {e}")
    def usb_authorization(self, hostname):
        username = 'username'
        password = 'topsecret'
        local_script_path = 'usb_auth.sh'
        private_key_path = 'automat'
        remote_script_path = '/usb_auth.sh'
        checkbox_sts = self.usb_checkbox.get()
        if checkbox_sts == 0:
            try:
                self.usb_btn_state()
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname, username=username, password=password, key_filename=private_key_path)
                sftp = ssh_client.open_sftp()
                sftp.put(local_script_path, remote_script_path)
                sftp.close()

                cd_command = f'cd /dgt/distr/'
                chmod_command = f'chmod +x /usb_auth.sh'
                remount_command = f'remount.sh'
                run_script_command = f'/dgt/distr/usb_auth.sh'
                clear_command = f'rm /dgt/distr/usb_auth.sh'

                stdin, stdout, stderr = ssh_client.exec_command(cd_command)
                print(stdout.read().decode())

                stdin, stdout, stderr = ssh_client.exec_command(chmod_command)
                print(stdout.read().decode())

                stdin, stdout, stderr = ssh_client.exec_command(remount_command)
                print(stdout.read().decode())

                stdin, stdout, stderr = ssh_client.exec_command(run_script_command)
                print(stdout.read().decode())

                stdin, stdout, stderr = ssh_client.exec_command(clear_command)
                print(stdout.read().decode())

            finally:
                ssh_client.close()
        else:
            try:
                self.usb_btn_state()
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname, username=username, password=password, key_filename=private_key_path)
                sftp = ssh_client.open_sftp()
                sftp.put(local_script_path, remote_script_path)
                sftp.close()

                cd_command = f'cd /dgt/distr/'
                chmod_command = f'chmod +x /usb_auth.sh'
                remount_command = f'remount.sh'
                run_script_command = f'/usb_auth.sh'
                clear_command = f'rm /usb_auth.sh'
                reboot_command = f'reboot'

                stdin, stdout, stderr = ssh_client.exec_command(cd_command)
                print(stdout.read().decode())

                stdin, stdout, stderr = ssh_client.exec_command(chmod_command)
                print(stdout.read().decode())

                stdin, stdout, stderr = ssh_client.exec_command(remount_command)
                print(stdout.read().decode())

                stdin, stdout, stderr = ssh_client.exec_command(run_script_command)
                print(stdout.read().decode())

                stdin, stdout, stderr = ssh_client.exec_command(clear_command)
                print(stdout.read().decode())

                stdin, stdout, stderr = ssh_client.exec_command(reboot_command)
                print(stdout.read().decode())

            finally:
                ssh_client.close()
    def chg_usb_label(self):
        check_box_status = self.usb_checkbox.get()
        if check_box_status == 0:
            self.usb_label.configure(text='')
        else:
            self.usb_label.configure(text='!!! MACHINE WILL BE REBOOTED !!!', font=customtkinter.CTkFont(size=12, weight="bold"), text_color="red")

    def usb_btn_state(self):
        second = threading.Thread(target=self.state_update)
        second.start()

    def state_update(self):
        self.usb_start_button.configure(fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), text="Processing..")
        time.sleep(2)
        self.usb_start_button.configure(fg_color='#00FF7F', border_width=0, text_color='black', text='Complete!')
        self.after(1000, self.update_usb_btn)

    def update_usb_btn(self):
        self.usb_start_button.configure(fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), text="Authorize")

    def report_schedule(self):
        while True:
            current_time = datetime.now()
            schedule.run_pending()
            time.sleep(1)
            print(current_time)


    def run_report_schedule(self):
        sch_switch_status = self.report_schedule_switch.get()
        if sch_switch_status == 1:
            self.report()

    def run_plan_schedule(self):
            sch_switch_status = self.plan_schedule_switch.get()
            if sch_switch_status == 1:
                self.plan()

#функции состояния кнопок удаления
    def del_cache(self):
        if len(os.listdir('specification')) == 0 and len(os.listdir('memory')) == 0 and len(os.listdir('logs')) == 0 and len(os.listdir('screenshots')) == 0 and len(os.listdir('graphs')) == 0:
            self.clear_cache.configure(fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), text="Clear cache")
        else:
            def delete_files_and_update_button():
                delete_files_in_folder('specification')
                delete_files_in_folder('graphs')
                delete_files_in_folder('memory')
                delete_folder('screenshots')
                delete_files_in_folder('logs')
                self.after(1000, self.update_delbutton06)

            self.clear_cache.configure(fg_color='#00FF7F', border_width=0, text_color='black', text='Deleting...')
            threading.Thread(target=delete_files_and_update_button).start()
    def update_delbutton06(self):
        self.clear_cache.configure(fg_color="transparent", border_width=2, text_color=("gray10","#DCE4EE"), text="Clear cache")

    def del_spec(self):

        if len(os.listdir('specification')) == 0:
            self.delete_button05.configure(fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"),
                                           text="Delete all specification")
        else:
            def delete_files_and_update_button():
                delete_files_in_folder('specification')
                self.after(1000, self.update_delbutton05)
            self.delete_button05.configure(fg_color='#00FF7F', border_width=0, text_color='black', text='Deleting...')
            threading.Thread(target=delete_files_and_update_button).start()
    def update_delbutton05(self):
        self.delete_button05.configure(fg_color="transparent", border_width=2, text_color=("gray10","#DCE4EE"), text="Delete all specification")

    def del_graphs(self):

        if len(os.listdir('graphs')) == 0:
            self.delete_button04.configure(fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"),
                                           text="Delete all graphics")
        else:
            def delete_files_and_update_button():
                delete_files_in_folder('graphs')
                self.after(1000, self.update_delbutton04)

            self.delete_button04.configure(fg_color='#00FF7F', border_width=0, text_color='black', text='Deleting...')
            threading.Thread(target=delete_files_and_update_button).start()
    def update_delbutton04(self):
        self.delete_button04.configure(fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), text="Delete all graphics")

    def del_mem(self):
        if len(os.listdir('memory')) == 0:
            self.delete_button03.configure(fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"),
                                           text="Delete all mem.log")
        else:
            def delete_files_and_update_button():
                delete_files_in_folder('memory')
                self.after(1000, self.update_delbutton03)

            self.delete_button03.configure(fg_color='#00FF7F', border_width=0, text_color='black', text='Deleting...')
            threading.Thread(target=delete_files_and_update_button).start()
    def update_delbutton03(self):
        self.delete_button03.configure(fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), text="Delete all mem.log")

    def del_screenshots(self):
        if len(os.listdir('screenshots')) == 0:
            self.delete_button02.configure(fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"),
                                           text="Delete all screenshots")
        else:
            def delete_files_and_update_button():
                delete_folder('screenshots')
                self.after(1000, self.update_delbutton02)

            self.delete_button02.configure(fg_color='#00FF7F', border_width=0, text_color='black', text='Deleting...')
            threading.Thread(target=delete_files_and_update_button).start()
    def update_delbutton02(self):
        self.delete_button02.configure(fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), text="Delete all screenshots")

    def del_dglog(self):
        if len(os.listdir('screenshots')) == 0:
            self.delete_button01.configure(fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"),
                                           text="Delete all DG.log")
        else:
            def delete_files_and_update_button():
                delete_files_in_folder('logs')
                self.after(1000, self.update_delbutton01)

            self.delete_button01.configure(fg_color='#00FF7F', border_width=0, text_color='black', text='Deleting...')
            threading.Thread(target=delete_files_and_update_button).start()
    def update_delbutton01(self):
        self.delete_button01.configure(fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), text="Delete all DG.log")

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)
    def switch_text(self):
        scr_sw_status = self.scr_switch.get()
        if scr_sw_status == 0:
            self.scr_switch.configure(text="DG log")
        else:
            self.scr_switch.configure(text="Screenshots")

    def switch_spec(self):
        specification_sw_status = self.spec_switch.get()
        if specification_sw_status == 0:
            self.spec_switch.configure(text="Short view")
        else:
            self.spec_switch.configure(text="Extended view")

    def save_ip(self):
        self.check_folders()
        self.check_ip_data()
        ip = self.ip_entry.get()
        if not ip == "":
            if not os.path.exists('ip_data.json'):
                with open('ip_data.json', 'w') as file:
                    json.dump({'ip_list': [ip]}, file)
            else:
                with open('ip_data.json', 'r') as file:
                    data = json.load(file)
                ip_list = data.get('ip_list', [])
                ip_list.append(ip)
                with open('ip_data.json', 'w') as file:
                    json.dump({'ip_list': ip_list}, file)
            self.ip_entry.delete(0, END)
            self.create_ip_buttons()
            self.ip_dropbox.configure(values=self.update_option_menu())
            self.ssh_status_label.configure(text=f'IP address successfully added', text_color='lime')
            self.spec_dropbox.configure(values=self.update_option_menu())
            self.ssh_status_label.configure(text=f'IP адрес успешно добавлен.', text_color='lime')
        else:
            self.ssh_status_label.configure(text=f'Enter the IP address', text_color='red')


    def update_option_menu(self):
        self.check_ip_data()
        with open('ip_data.json', 'r') as file:
            data = json.load(file)
        ip_list = data.get('ip_list', [])
        self.check_ip_data()
        return ip_list

    def create_ip_buttons(self):
        self.check_ip_data()
        with open('ip_data.json', 'r') as file:
            data = json.load(file)
        ip_list = data.get('ip_list', [])

        for i, ip in enumerate(ip_list):
            button = customtkinter.CTkButton(master=self.scroll_frame, text=ip, command=lambda ip=ip: self.ssh_log_keeper(ip))
            button.grid(row=i, column=0, padx=(10, 10), pady=(10, 0), sticky="ew")

    def check_ip_data(self):
        try:
            with open('ip_data.json', 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {"ip_list": []}
            with open('ip_data.json', 'w') as file:
                json.dump(data, file, indent=4)
    def check_folders(self):
        required_folders = ['logs', 'memory', 'graphs', 'screenshots', 'specification']
        for folder in required_folders:
            if not os.path.exists(folder):
                os.makedirs(folder)

    def background(self):
        current_path = os.path.dirname(os.path.realpath(__file__))
        self.bg_image = customtkinter.CTkImage(Image.open(current_path + "/assets/bg_gradient.jpg"), size=(self.width, self.height))
        self.bg_image_label = customtkinter.CTkLabel(self, image=self.bg_image, text='')
        self.bg_image_label.grid(row=0, column=1, sticky="ns")

    def reset_fields(self):
        self.username_entry.delete(0, 'end')
        self.password_entry.delete(0, 'end')
        self.username_entry.configure(placeholder_text="Username")
        self.password_entry.configure(placeholder_text="Password", show="*")

    def configure_border(self):
        self.username_entry.configure(border_color="gray")
        self.password_entry.configure(border_color="gray")
    def back_login_frame(self):
        self.login_frame.grid_forget()
        self.bg_image_label.grid_forget()
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.main_frame.grid(row=0, column=1, rowspan=4, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.reset_fields()
        self.copy_clipboard_button_reset()

    def hide_back_button(self):
        self.back_button.grid_forget()
        self.auth_button.grid(row=4, column=0, padx=30, pady=(180, 30))

    def show_back_button(self):
        self.auth_button.grid(row=4, column=0, padx=30, pady=(150, 0))
        self.back_button.grid(row=5, column=0, padx=30, pady=(10, 30), sticky="nsew")

    def login_event(self):
        self.sidebar_frame.grid_forget()
        self.main_frame.grid_forget()
        self.login_frame.grid()
        self.error_label.grid_forget()

    def back_event(self, event=NONE):
        self.login()
        self.test_request()
        self.reset_fields()

    def open_toplevel(self):
        self.Read_credentials()
        self.reset_fields()
        self.username_entry.focus_set()
        self.login_event()
        self.configure_border()
        self.background()

    def btn_update(self):
        self.login_button.configure(text=self.username)

    def login(self):
        self.save_credentials()
        self.Read_credentials()
        self.Set_credentials()
        self.btn_update()

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def buttons_disabled(self):
        self.copy_button.configure(state='disabled')
        self.report_button.configure(state='disabled')
        self.plan_button.configure(state='disabled')

    def buttons_enabled(self):
        self.copy_button.configure(state='normal')
        self.report_button.configure(state='normal')
        self.plan_button.configure(state='normal')

    def copy_clipboard_button(self):
        self.copy_button.configure(fg_color='#00FF7F', border_width=0, text_color='black', text='Copied!')

    def copy_clipboard_button_reset(self):
        self.copy_button.configure(fg_color="transparent", border_width=1, text_color=("gray10", "#DCE4EE"), text='Copy to clipboard')

    def copy_textbox(self):
        pyperclip.copy(self.textbox.get('1.0', END))
        self.copy_clipboard_button()

    def mem_log_reader(self, log_name):
        data = np.loadtxt(f'memory/{log_name}', usecols=(2, 3), unpack=True)
        x = data[0]
        y = data[1]

        plt.figure(figsize=(6, 4.75))
        plt.plot(x, y//1000)
        plt.xlabel('Spins amount')
        plt.ylabel('Memory Mb')
        plt.title(f'{log_name}')
        plt.grid(True)
        plt.savefig(f'graphs/Graph_({log_name}).png')
        graph_path = f'graphs/Graph_({log_name}).png'
        tk_image = ImageTk.PhotoImage(Image.open(graph_path))
        plt.close()
        return tk_image

    def canvas_update(self, img):
        self.img_label.configure(image=img)

    def specification(self):
        self.check_folders()
        try:
            self.specification_keeper(self.spec_dropbox.get())
        except Exception as e:
            print(f"Произошла ошибка: {e}")

    def create_graph(self):
        self.check_folders()
        try:
            self.canvas_update(self.mem_log_reader(self.mem_log_keeper(self.ip_dropbox.get())))
        except Exception as e:
            print(f"Error: {e}")

    def mem_log_keeper(self, hostname):
        username = 'root'
        password = '654321'
        private_key_path = 'automat'
        date = datetime.today().strftime('%d.%m.%Y_%H.%M.%S')

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh_client.connect(hostname, username=username, password=password, key_filename=private_key_path)
            remote_file_path = '/mem.log'
            local_file_path = f'Memory_log_{date} (ip {hostname}).log'
            sftp = ssh_client.open_sftp()
            sftp.get(remote_file_path, local_file_path)
            sftp.close()
            mem_log_path = os.path.basename(local_file_path)
            print(f"{remote_file_path} downloaded to {local_file_path}")

        except paramiko.AuthenticationException:
            print("Ошибка аутентификации")
        except paramiko.SSHException as e:
            print("Ошибка SSH:", str(e))
        except Exception as e:
            print("Ошибка:", str(e))
        finally:
            ssh_client.close()
        return mem_log_path

    def specification_keeper(self, hostname):
        username = 'root'
        password = '654321'
        private_key_path = 'automat'
        date = datetime.today().strftime('%d.%m.%Y_%H.%M.%S')

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh_client.connect(hostname, username=username, password=password, key_filename=private_key_path)
        remote_file_path = 'specification.txt'
        local_file_path = f'specification_{date} (ip {hostname}).txt'
        sftp = ssh_client.open_sftp()
        sftp.get(remote_file_path, local_file_path)
        sftp.close()
        spec_path = os.path.basename(local_file_path)
        print(f"Файл {remote_file_path} успешно загружен как {spec_path}")
        file_path = local_file_path

        if file_path:
            with open(file_path, "r") as file:
                file_contents = file.readlines()

        sw_status = self.spec_switch.get()
        try:
            if sw_status == 0:
                lines_to_print = [1, 3, 4, 8, 9, -1, -4, -5, -0]
                lines_to_print = [line - 1 for line in lines_to_print]
                output_lines = [file_contents[line] for line in lines_to_print]
                output_text = "".join(output_lines)
                self.spec_textbox.delete(1.0, 'end')
                self.spec_textbox.insert('end', output_text)
            else:
                self.spec_textbox.delete(1.0, END)
                self.spec_textbox.insert(END, "".join(file_contents))
        except paramiko.AuthenticationException:
            print("Ошибка аутентификации")
        except paramiko.SSHException as e:
            print("Ошибка SSH:", str(e))
        except Exception as e:
            print("Ошибка:", str(e))
        finally:
            ssh_client.close()
        return local_file_path


    def download_directory(self, remote_dir, local_dir, hostname, username, password):
        self.check_folders()
        if not os.path.exists(local_dir):
            os.mkdir(local_dir)
        private_key_path = 'automat'
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password, key_filename=private_key_path)

        sftp = ssh.open_sftp()
        file_counter = 0

        for item in sftp.listdir_attr(remote_dir):
            remote_path = os.path.join(remote_dir, item.filename)
            local_path = os.path.join(local_dir, item.filename)

            if stat.S_ISDIR(item.st_mode):
                self.download_directory(sftp, remote_path, local_path)
            else:
                sftp.get(remote_path, local_path)
                file_counter += 1

        sftp.close()
        ssh.close()
        print(f"Downloaded {file_counter} files.")
        return file_counter

    def ssh_log_keeper(self, hostname):
        username = 'username'
        password = 'topsecret'
        private_key_path = 'automat'
        date = datetime.today().strftime('%d.%m.%Y_%H.%M.%S')

        sw_status = self.scr_switch.get()
        if sw_status == 0:
            try:
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.check_folders()
                ssh_client.connect(hostname, username=username, password=password, key_filename=private_key_path)
                remote_file_path = '/tmp/DG.log'
                local_file_path = f'logs/DG_{date} (ip {hostname}).log'
                sftp = ssh_client.open_sftp()
                sftp.get(remote_file_path, local_file_path)
                sftp.close()
                print(f"Файл {remote_file_path} успешно загружен как {local_file_path}")
                self.ssh_status_label.configure(text=f'DG log downloaded\nfrom {hostname}', text_color='lime')

            except paramiko.AuthenticationException:
                print("Ошибка аутентификации")
                self.ssh_status_label.configure(text=f'Authentification error', text_color='red')
            except paramiko.SSHException as e:
                print("Ошибка SSH:", str(e))
                self.ssh_status_label.configure(text=f'SSH error', text_color='red')
            except Exception as e:
                print("Ошибка:", str(e))
                self.ssh_status_label.configure(text=f'Error', text_color='red')

        else:
            try:
                remote_file_path = 'screenshots/'
                local_file_path = f'screenshots/Screenshots_{date} (ip {hostname})/'
                file_counter = self.download_directory(remote_file_path, local_file_path, hostname, username, password)
                self.ssh_status_label.configure(text=f'Downloaded {file_counter} files\nfrom {hostname}', text_color='lime')
                print(f'Скриншоты успешно загружены с\n {hostname}')
            except paramiko.AuthenticationException:
                print("Ошибка аутентификации")
                self.ssh_status_label.configure(text=f'Authentification error', text_color='red')
            except paramiko.SSHException as e:
                print("Ошибка SSH:", str(e))
                self.ssh_status_label.configure(text=f'SSH error', text_color='red')
            except Exception as e:
                print("Ошибка:", str(e))
                self.ssh_status_label.configure(text=f'Error', text_color='red')


    def init_request(self):
        username = self.username
        password = self.password
        test_url = 'https://jira.ru'
        response = requests.get(test_url, auth=HTTPBasicAuth(username.encode("utf-8"), password.encode("utf-8")), verify=False)
        if response.status_code != 200:
                self.open_toplevel()
                self.hide_back_button()

    def test_request(self):
        username = self.username
        password = self.password
        test_url = 'https://jira.ru'
        response = requests.get(test_url, auth=HTTPBasicAuth(username.encode("utf-8"), password.encode("utf-8")), verify=False)

        if response.status_code != 200:
            self.back_login_frame()
            self.open_toplevel()
            self.hide_back_button()
            self.username_entry.configure(border_color="red")
            self.password_entry.configure(border_color="red", show="*")
            self.error_label.grid(row=3, column=0, padx=30, pady=(10, 0))
            self.error_label.configure(text=f"Incorrect login or password.\nError code: {response.status_code}")
            self.error_label.bind("<Button-1>", lambda event: self.open_link())
            self.auth_button.grid(row=4, column=0, padx=30, pady=(145, 35))
        else:
            self.back_login_frame()
            self.show_back_button()

    def open_jenkins(self):
        self.get_value_and_last_line(self.specification_keeper(self.spec_dropbox.get()))
        self.spec_path = self.specification_keeper(self.spec_dropbox.get())
        value, last_line = self.get_value_and_last_line(self.spec_path)
        value_length = len(value)
        if value_length == 5:
            webbrowser.open(f'http://jenkins/{value}/parameters/')
        elif value_length == 4:
            webbrowser.open(f'http://jenkins/{value}/parameters/')
        else:
            print("Invalid value length")
    def get_value_and_last_line(self, filename):
        with open(filename, 'r') as file:
            lines = file.readlines()
            for line in lines:
                match = re.search(r'(BuildNumber: .....\s)(\d+)', line)
                if match is not None:
                    value = match.group(2)
            last_line = lines[-1]
        return value, last_line.strip()


    def generate_key(self):
        return Fernet.generate_key()

    def open_link(self):
        webbrowser.open("https://jira.ru")

    def decrypt_password(self, encrypted_password, key):
        cipher_suite = Fernet(key)
        decrypted_password = cipher_suite.decrypt(encrypted_password.encode('utf-8'))
        return decrypted_password.decode('utf-8')

    def save_credentials(self):
        usr = self.username_entry.get()
        pwd = self.password_entry.get()
        key = self.generate_key()
        with open('not_key.key', 'wb') as key_file:
            key_file.write(key)

        cipher_suite = Fernet(key)
        encrypted_password = cipher_suite.encrypt(pwd.encode('utf-8'))

        with open('data.json', 'w', encoding='utf-8') as file:
            user_data = {
                'username': usr,
                'password': encrypted_password.decode('utf-8'),
            }
            json.dump(user_data, file, ensure_ascii=False, indent=4)

    def Read_credentials(self):
        filename = 'data.json'
        json_data = {
            'username': "",
            'password': "",
        }

        if os.path.exists(filename):
            with open(filename, 'r') as user_file:
                try:
                    json_data = json.load(user_file)
                    if 'password' in json_data:
                        with open('not_key.key', 'rb') as key_file:
                            key = key_file.read()
                        json_data['password'] = self.decrypt_password(json_data['password'], key)
                except:
                    pass
        else:
            with open(filename, 'w', encoding='utf-8') as user_file:
                json.dump(json_data, user_file, ensure_ascii=False, indent=4)

        return json_data

    def Current_date(self, title):
        date = datetime.today().strftime('%d.%m.%Y')
        self.textbox.insert("0.0", f"{title}{date}:")

    username = ''
    password = ''

    createdToday = 'https://jira.ru/created'
    closedToday = 'https://jira.ru/closed'
    tasks = 'https://jira.ru/tasks'
    reopenedToday = 'https://jira.ru/reopened'
    currentBugs = 'https://jira.ru/currentBugs'

    open_today = 'Opened:'
    closed_today = 'Closed:'
    current_tasks = 'Tasks:'
    reopened_today = 'Reopened:'
    current_bugs = 'Bugs:'

    title_plan = f'План на '
    title_report = f'Отчёт за '

    report_flags = {
        "CurrentTasks": 1,
        "OpenToday": 1,
        "ClosedToday": 1,
        "ReopenedToday": 1
    }

    def Switch_parameters(self):
        self.report_flags.update({"CurrentTasks": self.switch4.get()})
        self.report_flags.update({"OpenToday": self.switch1.get()})
        self.report_flags.update({"ClosedToday": self.switch2.get()})
        self.report_flags.update({"ReopenedToday": self.switch3.get()})

    def Report_parameters(self):
        if self.report_flags["ReopenedToday"] == 1:
            try:
                self.request(self.reopenedToday, self.reopened_today)
            except:
                return
        if self.report_flags["ClosedToday"] == 1:
            try:
                self.request(self.closedToday, self.closed_today)
            except:
                return
        if self.report_flags["OpenToday"] == 1:
            try:
                self.request(self.createdToday, self.open_today)
            except:
                return
        if self.report_flags["CurrentTasks"] == 1:
            try:
                self.request(self.tasks, self.current_tasks)
            except:
                return

    def Set_credentials(self):
        credentials = self.Read_credentials()
        if credentials:
            self.username = credentials['username']
            self.password = credentials['password']

    def request(self, url, header):
        username = self.username
        password = self.password

        response = requests.get(url, auth=HTTPBasicAuth(username, password), verify=False)


        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            summary_elements = soup.find_all(class_='summary')
            key_elements = soup.find_all(class_='issuekey')

            parent_issue_elements = soup.find_all(class_='issue-link parentIssue')
            for element in parent_issue_elements:
                element.decompose()

            elements_exist = False
            if summary_elements and key_elements:
                max_elements = max(len(summary_elements), len(key_elements))
                for i in range(max_elements, 0, -1):
                    summary = (summary_elements[i - 1].text.strip()) if i <= len(summary_elements) else ''
                    key = (key_elements[i - 1].text.strip()) if i <= len(key_elements) else ''
                    self.textbox.insert("1.0", f"{i}. {summary} ({key})\n")
                    elements_exist = True
            if not elements_exist:
                self.textbox.insert("0.0", f"Нет тикетов.\n")
            self.textbox.insert("0.0", f"{header}\n")
            self.textbox.insert("0.0", f"\n")
        else:
            self.textbox.insert("0.0", f"\n"
                                       f"-----------------------------------------------------------------------------\n"
                                       f"Ошибка при получении страницы. Код ответа: {response.status_code}\n"
                                       f"-----------------------------------------------------------------------------")

    def report(self):
        self.copy_clipboard_button_reset()
        self.textbox.delete("1.0", END)
        self.buttons_disabled()
        self.Set_credentials()
        self.Switch_parameters()
        self.Report_parameters()
        self.Current_date(self.title_report)
        self.buttons_enabled()

    def plan(self):
        self.copy_clipboard_button_reset()
        self.textbox.delete("1.0", END)
        self.buttons_disabled()
        self.Set_credentials()
        self.request(self.currentBugs, self.current_bugs)
        self.request(self.tasks, self.current_tasks)
        self.Current_date(self.title_plan)
        self.buttons_enabled()

if __name__ == "__main__":
    app = App()
    center_window(app, App.width, App.height)
    app.mainloop()