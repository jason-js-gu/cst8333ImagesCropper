import glob
import os
from PIL import Image, ImageTk, ImageChops
import tkinter as tk
from tkinter.filedialog import askopenfile
from tkscrolledframe import ScrolledFrame
from tktooltip import ToolTip
from typing import Tuple


###***********************###
# Component Classes Section #
###***********************###

class RemovableFrame(tk.Frame):
    """
    For the creation of a dynamic frame
    """
    def __init__(self, parent, name, key):
        # initialize the super class 
        tk.Frame.__init__(self, parent)
        # attributes need to be passed into during instantiation
        self.parent = parent
        self.name = name
        self.key = key 
        # attribute with default value
        # container component
        self.frame = tk.Frame(self.parent, name=self.name, pady=5)
        # position and display the container 
        self.frame.pack(side=tk.LEFT)        
        
    # method to remove the attribute with default value
    def delete(self):        
        self.frame.destroy()


class ImageButton(tk.Button):
    """
    For the creation of an image button
    """
    def __init__(self, title, parent, path, callback, tooltip_msg):
        # initialize the super class
        tk.Button.__init__(self, parent)
        self.parent = parent
        self.title = title
        # image path
        self.path = path        
        # call back method
        self.callback = callback
        # tooltip text
        self.tooltip_msg = tooltip_msg
        # local variable
        img = Image.open(self.path).resize((40, 40))
        img = ImageTk.PhotoImage(img) 
        # create a button with image
        self.image_btn = tk.Button(self.parent, image=img, cursor='hand2', name=self.title)
        self.image_btn.image = img
        self.image_btn.pack(side=tk.RIGHT, padx=5)
        # bind call back function to the click event
        self.image_btn.bind('<Button-1>', self.callback)
        # attach tooltip to the button
        ToolTip(self.image_btn, msg=self.tooltip_msg)

###****************###
# Main Class Section #
###****************###

class ImagesCropper:    

    def __init__(self, master) -> None:
        # attributes
        self.master = master
        self.master.title('Images Cropper')
        self.master.resizable(False, True)
        # variables can be seen inside the class space
        self.counter = 1
        self.removable_frame_dict = {} 
        self.valid_image_formats = ('JPG', 'JPEG', 'PNG', 'GIF', 'WEBB')
        # initialize all components
        self.create_widgets(self.master)  
        

    ###*****************###
    # Components Creation #
    ###*****************###        
        
    def create_widgets(self, master):
        """
        For the creation of all components
        """  
        # main container    
        mainframe = self.create_main_frame(master)
        # logo
        self.create_logo(mainframe, 'logo_transparent.png')
        # button for browsering the folder that holds all images
        self.create_browser_images_widget(mainframe)
        # second level container for hosting input fields for dimensions
        self.entries_wrapper = tk.Frame(mainframe, name='entries_wrap_frame')
        self.entries_wrapper.pack()
        # input fields for dimensions
        self.create_processing_widgets(self.entries_wrapper)
        # input field for browsering the folder for cropped images
        self.create_save_folder_widgets(mainframe)
        # button for cropping all images
        self.create_crop_images_btn(mainframe)
        
    def create_main_frame(self, master) -> tk.Frame:
        """
        container for all components
        """        
        frame = tk.Frame(master, width=600, height=800)
        frame.pack(side=tk.TOP, expand=1, fill=tk.Y)
        # attach a scroll bar to the main container
        sf = ScrolledFrame(frame, width=580, height=790)
        sf.pack(side=tk.TOP, expand=1, fill='both')        
        sf.bind_arrow_keys(frame)
        sf.bind_scroll_wheel(frame)
        mainframe = sf.display_widget(tk.Frame, fit_width=True) 
        return mainframe
        
    def create_logo(self, parent: tk.Frame, path: str) -> None:
        # container for logo
        logoframe = tk.Frame(parent, width=580)
        logoframe.pack()
        # read and resize logo image
        logo = Image.open(path).resize((200, 200))
        logo = ImageTk.PhotoImage(logo)
        # attach logo image to a label component
        logo_label = tk.Label(logoframe, image=logo)
        logo_label.image = logo
        logo_label.pack()
        
    def create_browser_images_widget(self, parent: tk.Frame)->None:
        # wrap frame
        folder_frame = tk.Frame(parent)
        folder_frame.pack()
        # browser button
        self.btn_select_text = tk.StringVar()
        self.btn_select = tk.Button(folder_frame, bg='#333', 
                               fg='white', height=2, width=50, 
                               textvariable=self.btn_select_text
                               )
        self.btn_select_text.set('Click here to select the folder of your images')                      
        self.btn_select.bind('<Button-1>', self.open_images)                       
        self.btn_select.pack(pady=15, side=tk.TOP)
        # text field to display the folder path
        self.folder_path_var = tk.StringVar()
        self.entry_folder_path = tk.Entry(parent, textvariable=self.folder_path_var, width=59)
        self.entry_folder_path.pack(pady=5) 
        
    def create_processing_widgets(self, parent: tk.Frame) -> None:
        removable_wrap_frame = self.create_removable_wrap_frame(parent, 'removable_frame')
        self.removable_frame_dict['add_entry_btn'] = removable_wrap_frame
        self.create_img_dimension_widgets(removable_wrap_frame.frame, 
                                          'btn_add_entry',
                                          'icons8-add-96.png',
                                          self.add_entry,                                          
                                          'Click to add a new set of entries')
    
    def create_removable_wrap_frame(self, parent: tk.Frame, name) -> tk.Frame:
        wrap_frame = tk.Frame(parent, height=300)
        wrap_frame.pack(pady=5)
        removable_wrap_frame = RemovableFrame(wrap_frame, name, name)        
        return removable_wrap_frame

    def create_img_dimension_widgets(self, parent: tk.Frame, name: str,
                                     icon_path: str, callback, 
                                     tooltip_msg: str) -> None:
        # container                             
        entry_frame = tk.Frame(parent, highlightcolor="#333", 
                               relief=tk.RAISED, bd=1, padx=10, pady=10, name='entry_frame')
        entry_frame.pack(side=tk.LEFT)        
        # image button for adding a set of input fields 
        ImageButton(name, parent, icon_path, callback, tooltip_msg)
        # inner container            
        width_entry_frame = tk.Frame(entry_frame, height=30, name='width_entry_frame')
        width_entry_frame.pack(pady=10)
        height_entry_frame = tk.Frame(entry_frame, height=30, name='height_entry_frame')
        height_entry_frame.pack(pady=5, side=tk.RIGHT)
        # labels and input fields
        width_label = tk.Label(width_entry_frame, text='Enter cropped image width:')
        width_entry = tk.Entry(width_entry_frame, name='wv')        
        width_label.pack(side=tk.LEFT, padx=2)
        width_entry.pack(side=tk.RIGHT)
        height_label = tk.Label(height_entry_frame,text='Enter cropped image height:')
        height_entry = tk.Entry(height_entry_frame, name='hv')        
        height_label.pack(side=tk.LEFT, padx=2)
        height_entry.pack(side=tk.RIGHT)   
            
    def create_save_folder_widgets(self, parent: tk.Frame) -> None:
        save_folder_frame = tk.Frame(parent, highlightcolor="#333", 
                       relief=tk.RAISED, bd=1, padx=10, pady=10)                       
        save_folder_frame.pack(pady=5) 
        save_folder_label = tk.Label(save_folder_frame, text='Enter or select a new folder to save cropped images:')
        save_folder_label.pack(pady=5)

        select_folder_frame = tk.Frame(save_folder_frame)
        select_folder_frame.pack(pady=5)
        self.save_folder_var = tk.StringVar()
        self.save_folder_path_entry = tk.Entry(select_folder_frame, width=43, textvariable=self.save_folder_var)
        self.save_folder_path_entry.pack(side=tk.LEFT)

        btn_select_folder = tk.Button(select_folder_frame, text='Browser',
                                      command=lambda:self.save_folder(), bg='#333',
                                      fg='white')
        btn_select_folder.pack(side=tk.RIGHT, padx=10)
        
    def create_crop_images_btn(self, parent: tk.Frame) -> None:
        self.crop_img_var = tk.StringVar()
        btn_crop = tk.Button(parent, textvariable=self.crop_img_var, 
                             bg='#333', fg='white', height=2, width=50, 
                             command=lambda:self.crop_images())
        self.crop_img_var.set('Crop all chosen images')                     
        btn_crop.pack(pady=10)
 
    
    ###*****************###
    # Components Behavior #
    ###*****************### 
    # method used to open a folder and read all valid images
    def open_images(self, event) -> None:
        self.btn_select_text.set('Reading...')
        folder_name = tk.filedialog.askdirectory()
        # Read all images under the folder path        
        self.valid_images = []        
        # Valid folder path
        if os.path.isdir(folder_name):
            # Display folder path in the text field
            self.folder_path_var.set(folder_name)
            # Change back the button text
            self.btn_select_text.set('Click here to select the folder of your images') 
            # set the folder as the default folder to save cropped images
            self.save_folder_var.set(folder_name)

            for f in os.listdir(folder_name):            
                for e in self.valid_image_formats:                 
                    if f.endswith(e.lower()) or f.endswith(e):
                        self.valid_images.append(folder_name + '/' + f)
        else:
            # Invalid folder path, show the dialog box and display the error message
            tk.messagebox.showerror('OS Error', 'Error: Invalid folder path!')           
        
    # method to add a container with its components
    def add_entry(self, event) -> None: 
        # variable to name components
        btn_name = f'btn_remove_{self.counter}'
        # removable container
        removable_wrap_frame = self.create_removable_wrap_frame(self.entries_wrapper,
                        btn_name) 
        removable_wrap_frame.pack() 
        # save the container into a list
        self.removable_frame_dict[btn_name] = removable_wrap_frame
        # create all components
        self.create_img_dimension_widgets(removable_wrap_frame.frame, 
                                          btn_name,
                                          'icons8-remove-96.png',
                                          self.remove_entry,                                          
                                          'Click to remove a set of entries')    
        # increment the counter    
        self.counter = self.counter + 1

    # method used to delete a container and all its components
    def remove_entry(self, event):
        w=event.widget
        #print(w._name)
        for key in self.removable_frame_dict.keys():
            if w._name == key:
                for w in self.removable_frame_dict[key].frame.winfo_children():
                    w.destroy()
                self.removable_frame_dict[key].frame.destroy()
                del self.removable_frame_dict[key]                
                break
        #print(self.removable_frame_dict)

    # method used to retrieve input values for cropped images dimension
    def get_dimension_values(self):    
        dimensions = []
        for frame in self.removable_frame_dict.values():
            width = frame.frame.children['entry_frame'].children['width_entry_frame'].children['wv'].get()
            height = frame.frame.children['entry_frame'].children['height_entry_frame'].children['hv'].get()
            dimensions.append((width, height))
        return dimensions
        
    # method used to retrieve the path of the folder where would save cropped images
    def save_folder(self):
        folder_path = tk.filedialog.askdirectory()
        self.save_folder_var.set(folder_path)
        
    # method used to validate the input values for cropped images dimension
    def check_dimensions(self, dimensions: list) -> Tuple[bool, str]:
        for dim in dimensions:
            if dim[0] == '' or dim[1] == '':
                return False, 'T1'
            if not dim[0].isdigit() or not dim[1].isdigit():
                return False, 'T2'
            if (dim[0].isdigit() and int(dim[0]) <= 0) or (dim[1].isdigit() and int(dim[1]) <= 0):
                return False, 'T3'
        return True, ''
    
    # method used to crop an image
    def cropping(self, image, dimension: Tuple[str, str]):
        # obtain width and height of cropped image
        cropped_width, cropped_height = int(dimension[0]), int(dimension[1])
        # open image and obtain its dimension
        original_img = Image.open(image)
        img_name = original_img.filename.split('/')[-1]
        original_img.load()        
        original_width, original_height = original_img.size
        # do nothing if cropped dimension is bigger than original dimension
        if cropped_width > original_width or cropped_height > original_height:
            return None, img_name
        
        ratio_cropped = cropped_width / cropped_height
        ratio_original = original_width / original_height
        
        if ratio_cropped == ratio_original:           
           cropped_img = original_img.resize((cropped_width, cropped_height))
        elif ratio_cropped < ratio_original:            
            new_width = cropped_width * (original_height / cropped_height)
            temp_img = original_img.crop((0, 0, new_width, original_height))
            cropped_img = temp_img.resize((cropped_width, cropped_height))
        else:            
            new_height = cropped_height * (original_width / cropped_width)
            temp_img = original_img.crop((0, 0, original_width, new_height))
            cropped_img = temp_img.resize((cropped_width, cropped_height))  
        return cropped_img, img_name
        
    # method used to save a cropped image into a given folder    
    def save_cropped_image(self, image, folder, name):
        from datetime import datetime
        now = datetime.now()
        now_str = ''.join([str(now.year), str(now.month), str(now.day), str(now.hour)])
        w, h = image.size 
        if not folder.endswith('/'):        
            path = os.path.join(folder, now_str + '_' + str(w) + 'X' + str(h))
            if not os.path.exists(path):
                os.mkdir(path)
            image.save(path + '/' + str(w) + 'X' + str(h) + '_' + name)
        else:
            path = os.path.join(folder[:-1], now_str + '_' + str(w) + 'X' + str(h))
            if not os.path.exists(path):
                os.mkdir(path)
            image.save(path + str(w) + 'X' + str(h) + '_' + name)
    # method used to sum up all behaviors
    def crop_images(self):
        #print(self.valid_images)

        # Get images folder path
        images_folder_path = self.entry_folder_path.get()        
        # Get cropped images folder path:
        images_save_folder_path = self.save_folder_path_entry.get()        
        # Get images dimensions info        
        dimensions = self.get_dimension_values()
        res, error_type = self.check_dimensions(dimensions)        
        # blank field 
        if images_folder_path == '' or images_save_folder_path == '' or (not res and error_type == 'T1'):
           tk.messagebox.showerror('OS Error', 'Error: At least one input field is blank!')
           return           
        # Invalid dimension format
        if not res and error_type == 'T2':
            tk.messagebox.showerror('Format Error', 'Error: Dimension must be an integer!')
            return
        # Value 0 or negative value
        if not res and error_type == 'T3':
            tk.messagebox.showerror('Format Error', 'Error: Dimension must be an positive integer!')
            return        
        # No valid images
        if self.valid_images == []: 
           tk.messagebox.showerror('OS Error', 'Error: No valid images!')
           return           
        # change the button text   
        self.crop_img_var.set('Cropping....')
        
        # Process images
        cropped_img = None
        invalid_dim_counter = 0
        for img in self.valid_images:
            for dim in dimensions:
                cropped_img, img_name = self.cropping(img, dim)
                #folder_path = self.save_folder
                if cropped_img:
                    self.save_cropped_image(cropped_img, images_save_folder_path, img_name)
                else:
                    invalid_dim_counter = invalid_dim_counter + 1;
        if invalid_dim_counter == 0:
            self.folder_path_var.set("")
            self.save_folder_var.set("")
            self.valid_images = []    
            # reset button text
            self.crop_img_var.set('Crop all chosen images')            
            tk.messagebox.showinfo('Info', 'All images are cropped')
            return                   
        if len(self.valid_images) == invalid_dim_counter:
            tk.messagebox.showerror('Dimension Error', 'All dimensions are invalid')
            return
        else:
            self.folder_path_var.set("")
            self.save_folder_var.set("")
            self.valid_images = []    
            # reset button text
            self.crop_img_var.set('Crop all chosen images')            
            tk.messagebox.showinfo('Info', 'All images are cropped but ' + str(invalid_dim_counter) + ' of them are not cropped because of invalid crop dimension')
            return
            
        
        
###***************###
# Execution Section #
###***************###

if __name__ == "__main__":
    r = tk.Tk()
   
    app = ImagesCropper(r)

    app.master.mainloop()       
        
        
        
        
        