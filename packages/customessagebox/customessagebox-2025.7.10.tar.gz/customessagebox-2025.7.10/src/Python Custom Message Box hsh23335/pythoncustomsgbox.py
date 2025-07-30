"""
A module for your customized message boxes.

Created by Me! :) This module uses `customtkinter`, which does not include built-in message boxes, 
so I decided to create 5 of them using the Fredoka One font.

I hope you would enjoy it! :)
"""
import customtkinter
import ctypes
import winsound
import os
import sys
from tkinter import messagebox as tkmsg

font_loaded = False
def load_fredoka_one_font():
    """Load Fredoka One font."""
    global font_loaded
    if not font_loaded:
        font_path = r"Fredoka-Bold.ttf"
        if not os.path.exists(font_path):
            tkmsg.showerror("Error!", "Your Fredoka One font is deleted, moved, or lacks your permission. \n Exiting after you click OK...")
            sys.exit()
            return False
        ctypes.windll.gdi32.AddFontResourceExW(font_path, 0x10, 0)
        ctypes.windll.user32.SendMessageTimeoutW(0xFFFF, 0x001D, 0, 0, 0, 1000, None)
        font_loaded = True
    return True

class CustomMessageBox:   
    """Class for the custom message boxes.""" 

    @staticmethod
    def center_msgbox_win(win = customtkinter.CTkToplevel, width = int, height = int):
        """Center the CTkToplevel.
        
        Parameters:
            win (CTkToplevel): The master which is defaulted to CTkToplevel.
            width (int): The width of the CTkToplevel.
            height (int): The height of the CTkToplevel.
        """
        win.update_idletasks()
        screen_width = win.winfo_screenwidth()
        screen_height = win.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        win.geometry(f"{width}x{height}+{x}+{y}")

    @staticmethod
    def customMsgBox(msgboxtitle = str, textmsg = str, bg_color = str, btn_fg_color = str, btn_text_color = str, text_color = str, error = bool):
        """Shows a custom customtkinter messagebox with an OK button.

        Parameters:
            msgboxtitle (str): The title of the messagebox.
            textmsg (str): The text message inside of the messagebox.
            bg_color (str): Background color of the messagebox.
            btn_fg_color (str): The background color of the OK button.
            btn_text_color (str): Color of the text inside of the OK button.
            text_color (str): The text color of the textmsg.
            error (bool): Will initialize an error sound if this evaluates to False.  \n If True, it will be a normal windows messagebox beep.
        """
        load_fredoka_one_font()
        label_font = customtkinter.CTkFont(family="Fredoka", size=20)
        if error is False:
            winsound.MessageBeep()
        elif error is True:
            winsound.MessageBeep(winsound.MB_ICONHAND)
        toplevel = customtkinter.CTkToplevel()
        toplevel.geometry("1000x500")
        width, height = 1000, 500
        CustomMessageBox.center_msgbox_win(toplevel, width, height)
        toplevel.title(msgboxtitle)
        toplevel.configure(fg_color= bg_color)
        toplevel.resizable(False, False)
        spacing_label = customtkinter.CTkLabel(master= toplevel, text= "\n \n")
        spacing_label.pack()
        label = customtkinter.CTkLabel(master= toplevel, text= textmsg, font= label_font, text_color= text_color)
        label.pack()
        spacing_label = customtkinter.CTkLabel(master= toplevel, text= "\n")
        spacing_label.pack()
        button = customtkinter.CTkButton(master= toplevel, text= "OK", corner_radius= 15, fg_color= btn_fg_color, text_color= btn_text_color, hover= False, cursor= "hand2", command= lambda: toplevel.destroy())
        button.pack()
        toplevel.grab_set()
        toplevel.wait_window()

    @staticmethod
    def customMsgBoxWithScrBar(msgboxtitle = str, titlemsg = str, textmsg = str, bg_color = str, btn_fg_color = str, btn_text_color = str, label_text_color = str, text_color = str, error = bool):
        """Shows a custom customtkinter messagebox with an OK button and a horizontal and vertical scrollbar.

        Parameters:
            msgboxtitle (str): The title of the messagebox.
            titlemsg (str): The title text message inside of the messagebox.
            textmsg (str): The text message inside of the messagebox scroll bar.
            bg_color (str): Background color of the messagebox..
            btn_fg_color (str): The background color of the OK button.
            btn_text_color (str): Color of the text inside of the OK button.
            label_text_color (str): Background color of inside the scroll bar area.
            text_color (str): The text color of the textmsg.
            error (bool): Will initialize a windows error sound if this evaluates to True.  \n If False, it will be a normal windows messagebox beep.
        """
        load_fredoka_one_font()
        label_font = customtkinter.CTkFont(family="Fredoka", size=30)
        textbox_font = customtkinter.CTkFont(family="Fredoka", size=20)
        if error is False:
            winsound.MessageBeep()
        elif error is True:
            winsound.MessageBeep(winsound.MB_ICONHAND)
        toplevel = customtkinter.CTkToplevel()
        toplevel.geometry("1000x500")
        width, height = 1000, 500
        CustomMessageBox.center_msgbox_win(toplevel, width, height)
        toplevel.title(msgboxtitle)
        toplevel.configure(fg_color= bg_color)
        toplevel.resizable(False, False)
        spacing_label = customtkinter.CTkLabel(master= toplevel, text= "\n")
        spacing_label.pack()
        label = customtkinter.CTkLabel(master= toplevel, text= titlemsg, font= label_font, text_color= label_text_color)
        label.pack()
        spacing_label1 = customtkinter.CTkLabel(master= toplevel, text= "\n")
        spacing_label1.pack()
        textbox = customtkinter.CTkTextbox(master= toplevel, font= textbox_font, text_color= text_color, wrap= "none")
        textbox.pack(expand= True, fill= "both", pady= 20, padx= 20)
        textbox.insert("1.0", textmsg)
        textbox.configure(state= "disabled")
        spacing_label = customtkinter.CTkLabel(master= toplevel, text= "\n")
        spacing_label.pack()
        button = customtkinter.CTkButton(master= toplevel, text= "OK", corner_radius= 15, fg_color= btn_fg_color, text_color= btn_text_color, hover= False, cursor= "hand2", command= lambda: toplevel.destroy())
        button.pack()
        toplevel.grab_set()
        toplevel.wait_window()

    @staticmethod
    def customYesNoMsg(msgboxtitle = str, textmsgquestion = str, bg_color = str, btn_fg_color = str, btn_text_color = str, text_color = str):
        """Shows a custom customtkinter messagebox with Yes/No buttons.

        Parameters:
            msgboxtitle (str): The title of the messagebox.
            textmsgquestion (str): The text message question inside of the messagebox.
            bg_color (str): Background color of the messagebox.
            btn_fg_color (str): The background color of the Yes/No buttons.
            btn_text_color (str): Color of the text inside of the Yes/No buttons.
            text_color (str): The text color of the textmsgquestion.
        """
        load_fredoka_one_font()
        label_font = customtkinter.CTkFont(family="Fredoka", size=20)
        toplevel = customtkinter.CTkToplevel()
        toplevel.geometry("1000x500")
        width, height = 1000, 500
        CustomMessageBox.center_msgbox_win(toplevel, width, height)
        toplevel.title(msgboxtitle)
        toplevel.configure(fg_color= bg_color)
        toplevel.resizable(False, False)
        spacing_label = customtkinter.CTkLabel(master= toplevel, text= "\n")
        spacing_label.pack()
        label = customtkinter.CTkLabel(master= toplevel, text= textmsgquestion, font= label_font, text_color= text_color)
        label.pack()
        spacing_label1 = customtkinter.CTkLabel(master= toplevel, text= "\n")
        spacing_label1.pack()
        result = {"answer": None}
        def on_yes():
            result["answer"] = True
            toplevel.destroy()
        def on_no():
            result["answer"] = False
            toplevel.destroy()
        buttonyes = customtkinter.CTkButton(master= toplevel, text= "Yes", corner_radius= 15, fg_color= btn_fg_color, text_color= btn_text_color, hover= False, cursor= "hand2", command= on_yes)
        buttonno = customtkinter.CTkButton(master= toplevel, text="No", corner_radius= 15, fg_color= btn_fg_color, text_color= btn_text_color, hover= False, cursor= "hand2", command= on_no)
        buttonyes.pack()
        spacing_label2 = customtkinter.CTkLabel(master= toplevel, text= "\n")
        spacing_label2.pack()
        buttonno.pack()
        toplevel.grab_set()
        toplevel.wait_window()
        return result["answer"]
    
    @staticmethod
    def customYesNoCancelMsg(msgboxtitle, textmsgquestion, bg_color, btn_fg_color, btn_text_color, text_color):
        """Shows a custom customtkinter messagebox with Yes/No/Cancel buttons.

        Parameters:
            msgboxtitle (str): The title of the messagebox.
            textmsg (str): The text message inside of the messagebox.
            bg_color (str): Background color of the messagebox.
            btn_fg_color (str): The background color of the Yes/No/Cancel buttons.
            btn_text_color (str): Color of the text inside of the Yes/No/Cancel buttons.
            text_color (str): The text color of the textmsgquestion.
        """
        load_fredoka_one_font()
        label_font = customtkinter.CTkFont(family="Fredoka", size=20)
        toplevel = customtkinter.CTkToplevel()
        toplevel.geometry("1000x500")
        width, height = 1000, 500
        CustomMessageBox.center_msgbox_win(toplevel, width, height)
        toplevel.title(msgboxtitle)
        toplevel.configure(fg_color= bg_color)
        toplevel.resizable(False, False)
        spacing_label = customtkinter.CTkLabel(master= toplevel, text= "\n")
        spacing_label.pack()
        label = customtkinter.CTkLabel(master= toplevel, text= textmsgquestion, font= label_font, text_color= text_color)
        label.pack()
        spacing_label1 = customtkinter.CTkLabel(master= toplevel, text= "\n")
        spacing_label1.pack()
        result = {"answer": None}
        def on_yes():
            result["answer"] = True
            toplevel.destroy()
        def on_no():
            result["answer"] = False
            toplevel.destroy()
        buttonyes = customtkinter.CTkButton(master= toplevel, text= "Yes", corner_radius= 15, fg_color= btn_fg_color, text_color= btn_text_color, hover= False, cursor= "hand2", command= on_yes)
        buttonno = customtkinter.CTkButton(master= toplevel, text="No", corner_radius= 15, fg_color= btn_fg_color, text_color= btn_text_color, hover= False, cursor= "hand2", command= on_no)
        buttoncancel = customtkinter.CTkButton(master= toplevel, text= "Cancel", corner_radius= 15, fg_color= btn_fg_color, text_color= btn_text_color, hover= False, cursor= "hand2", command= lambda: toplevel.destroy())
        buttonyes.pack()
        spacing_label2 = customtkinter.CTkLabel(master= toplevel, text= "\n")
        spacing_label2.pack()
        buttonno.pack()
        spacing_label3 = customtkinter.CTkLabel(master= toplevel, text= "\n")
        spacing_label3.pack()
        buttoncancel.pack()
        toplevel.grab_set()
        toplevel.wait_window()
        return result["answer"]

    @staticmethod
    def customTextBoxMsg(msgboxtitle, textmsg, bg_color, btn_fg_color, btn_text_color, text_color):
        """Shows a customtkinter textbox with OK/Cancel buttons.

        Parameters:
            msgboxtitle (str): The title of the messagebox.
            textmsg (str): The text message inside of the messagebox.
            bg_color (str): Background color of the messagebox.
            btn_fg_color (str): The background color of the OK/Cancel buttons.
            btn_text_color (str): Color of the text inside of the OK/Cancel button.
            text_color (str): The text color of the textmsg.
        """
        load_fredoka_one_font()
        label_font = customtkinter.CTkFont(family="Fredoka", size=25)
        toplevel = customtkinter.CTkToplevel()
        toplevel.geometry("1000x500")
        width, height = 1000, 500
        CustomMessageBox.center_msgbox_win(toplevel, width, height)
        toplevel.title(msgboxtitle)
        toplevel.configure(fg_color= bg_color)
        toplevel.resizable(False, False)
        spacing_label = customtkinter.CTkLabel(master= toplevel, text= "\n")
        spacing_label.pack()
        label = customtkinter.CTkLabel(master= toplevel, text= textmsg, text_color = text_color, font= label_font)
        label.pack()
        spacing_label1 = customtkinter.CTkLabel(master= toplevel, text= "\n")
        spacing_label1.pack()
        def handle_event(event):
            return "break"
        text_box = customtkinter.CTkTextbox(master= toplevel, height= 20, width= 400, font= label_font)
        text_box.bind("<Return>", handle_event)
        text_box.pack()
        spacing_label2 = customtkinter.CTkLabel(master= toplevel, text= "\n")
        spacing_label2.pack()
        result = {"text": None}
        def get_textbox_val():
            result["text"] = text_box.get("1.0", "end-1c")
            toplevel.destroy()
        submit_btn = customtkinter.CTkButton(master= toplevel, text= "OK", corner_radius= 15, fg_color= btn_fg_color, text_color= btn_text_color, hover= False, cursor= "hand2", command= get_textbox_val)
        submit_btn.pack()
        spacing_label3 = customtkinter.CTkLabel(master= toplevel, text= "\n")
        spacing_label3.pack()
        cancel_btn = customtkinter.CTkButton(master= toplevel, text= "Cancel", corner_radius= 15, fg_color= btn_fg_color, text_color= btn_text_color, hover= False, cursor= "hand2", command= lambda: toplevel.destroy())
        cancel_btn.pack()
        spacing_label4 = customtkinter.CTkLabel(master= toplevel, text= "\n")
        spacing_label4.pack()
        toplevel.grab_set()
        toplevel.wait_window()
        return result["text"]