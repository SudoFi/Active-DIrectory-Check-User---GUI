# -*- coding: utf-8 -*-
"""
Active Directory User Search Tool

A simple Python GUI application for checking if one or more users exist
in Active Directory.

Author: [Your Name]
Date: 2024-05-20
Dependencies: ldap3
"""

import os
import socket
import tkinter as tk
from tkinter import ttk
from ldap3 import Server, Connection, ALL

def add_user():
    """Gets the first and last name from the input fields,
    adds the user to the list, and clears the fields."""
    first_name = entry_first_name.get()
    last_name = entry_last_name.get()
    if first_name and last_name:
        user_list.append((first_name.strip(), last_name.strip()))
        user_listbox.insert("end", f"{first_name.strip()} {last_name.strip()}")
        entry_first_name.delete(0, "end")  # Clear entry fields after adding user
        entry_last_name.delete(0, "end")

def search_users():
    """Connects to AD and searches for each user in the user_list.
    Updates the results table and progress bar accordingly."""
    if not user_list:
        return  # No users in the list, so do nothing

    progress_bar["value"] = 0
    progress_bar["maximum"] = len(user_list)
    result_tree.delete(*result_tree.get_children())  # Clear previous search results

    # --- Get AD connection details dynamically ---
    domain = os.environ.get('USERDOMAIN')
    # Strip the "\\" from the start of the server name
    domain_controller = os.environ.get('LOGONSERVER')[2:]
    fqdn = socket.getfqdn(domain_controller)
    server = Server(fqdn, get_info=ALL)

    try:
        with Connection(server, auto_bind=True) as conn:
            for first_name, last_name in user_list:
                try:
                    # Construct the search filter for an exact match on first and last name
                    search_filter = f'(&(givenName={first_name.strip()})(sn={last_name.strip()}))'
                    conn.search(f'{domain}', search_filter, attributes=['cn'])
                    
                    if conn.entries:
                        result_tree.insert("", "end", values=(f"{first_name.strip()} {last_name.strip()}", "Found"), tags=("found",))
                    else:
                        result_tree.insert("", "end", values=(f"{first_name.strip()} {last_name.strip()}", "Not Found"), tags=("not_found",))
                except Exception as e:
                    print("Search Error:", e)
                    result_tree.insert("", "end", values=(f"{first_name.strip()} {last_name.strip()}", "Error"), tags=("error",))
                
                progress_bar["value"] += 1
    except Exception as e:
        print("Connection Error:", e)
        result_tree.insert("", "end", values=("Connection Error", "Check logs"), tags=("error",))
    
    progress_bar["value"] = 0  # Reset progress bar after search is done

# --- UI Setup ---
root = tk.Tk()
root.title("Active Directory User Search")

# Get domain and server info to display it in the UI
domain = os.environ.get('USERDOMAIN')
domain_controller = os.environ.get('LOGONSERVER')[2:]
fqdn = socket.getfqdn(domain_controller)

# Domain and Server display (read-only)
tk.Label(root, text="Domain:").grid(row=0, column=0, padx=5, pady=5)
entry_domain = tk.Entry(root)
entry_domain.insert(tk.END, domain)
entry_domain.config(state='readonly')
entry_domain.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="AD/LDAP Server:").grid(row=1, column=0, padx=5, pady=5)
entry_server = tk.Entry(root)
entry_server.insert(tk.END, fqdn)
entry_server.config(state='readonly')
entry_server.grid(row=1, column=1, padx=5, pady=5)

# User input fields
tk.Label(root, text="First Name:").grid(row=2, column=0, padx=5, pady=5)
entry_first_name = tk.Entry(root)
entry_first_name.grid(row=2, column=1, padx=5, pady=5)

tk.Label(root, text="Last Name:").grid(row=3, column=0, padx=5, pady=5)
entry_last_name = tk.Entry(root)
entry_last_name.grid(row=3, column=1, padx=5, pady=5)

# Buttons and display widgets
tk.Button(root, text="Add User", command=add_user).grid(row=4, column=0, columnspan=2, padx=5, pady=5)
user_listbox = tk.Listbox(root)
user_listbox.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
tk.Button(root, text="Search", command=search_users).grid(row=6, column=0, columnspan=2, padx=5, pady=5)

# Progress bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=200, mode="determinate")
progress_bar.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky='ew')

# Results table
result_tree = ttk.Treeview(root, columns=("Name", "Status"), show="headings")
result_tree.heading("Name", text="Name")
result_tree.heading("Status", text="Status")
result_tree.grid(row=8, column=0, columnspan=2, padx=5, pady=5)

# Color-coding for results
result_tree.tag_configure("found", background="#90EE90") # LightGreen
result_tree.tag_configure("not_found", background="#F08080") # LightCoral
result_tree.tag_configure("error", background="#FFD700") # Gold

# Initialize user list to store names to be checked
