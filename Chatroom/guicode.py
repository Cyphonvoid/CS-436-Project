import customtkinter



customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")
    
class MyFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # add widgets onto the frame...
        self.frame = customtkinter.CTkFrame(self,width=200, height=200, corner_radius=5, bg_color="grey")
        self.frame.grid(row=0, column=0, padx=20)

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()


        self.title("Chat Room")
        self.geometry("1280x720")

       
        #Textbox
        self.textbox = customtkinter.CTkTextbox(master=self, width=1000, height=500, font = ("Arial", 20), text_color="white",wrap = "word", state = "disabled")
        self.textbox.place(relx = 0.1, rely = 0.1, anchor = "nw")
        
        
        #Send Button
        self.message_frame = customtkinter.CTkFrame(self,width=1280, height=70, corner_radius=1, bg_color="grey")
        self.message_frame.pack(side = "bottom", padx=20, pady=10)
        self.button = customtkinter.CTkButton(master=self.message_frame, text="Send", command=self.button_callback, width = 200, height = 50, font = ("Arial", 20), text_color="white", fg_color="grey")
        self.button.place(relx = 0.825, rely = 0.89, anchor = "sw")

        #Exit Button
        self.button = customtkinter.CTkButton(master=self, text="EXIT", command=self.exit_button, width = 100, height = 50, font = ("Arial", 20), text_color="white", fg_color="grey")
        self.button.place(relx = 0.975, rely = 0.025, anchor = "ne")

        #User Input
        self.text_entry = customtkinter.CTkEntry(master=self.message_frame, placeholder_text= "Input Message Here", width = 1000, height = 50, font = ("Arial", 20), text_color="white", fg_color="grey")
        self.text_entry_frame = customtkinter.CTkFrame(self)
        self.text_entry.place(relx = 0.01, rely = 0.89, anchor = "sw")
        
    def button_callback(self):
        #send message to server here
        self.text_entry.delete(0,(len(self.text_entry.get())))
    
    def display_text(self,message):
        self.textbox.configure(state="normal")
        self.textbox.insert('end',message)
        self.textbox.configure(state="disabled")

    def exit_button(self):
        self.destroy()
        exit()

    

app = App()

#USE IN CODE
#USE INSTEAD OF PRINT
app.display_text()

#USE IN MAIN TO START GUI
app.update_idletasks()
app.update()

