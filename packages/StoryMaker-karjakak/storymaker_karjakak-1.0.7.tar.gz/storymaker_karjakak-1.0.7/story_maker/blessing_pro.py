# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 11:23:58 2018

@author: karja
"""

from tkinter import (
    Menu, StringVar, Frame, Scrollbar, 
    Text, Radiobutton, TOP, BOTTOM, BOTH, 
    RIGHT, LEFT, END, Tk, ttk, 
    filedialog as fil,
    messagebox as mes
)
import webbrowser
from pathlib import Path
from contextlib import chdir
try:
    from .story_archive import StoryFilesLoads, Choices
    from .story_structure import StorySelection
except:
    from story_archive import StoryFilesLoads, Choices
    from story_structure import StorySelection


# Class that generate Windows console and stories from Blessing_Story folder
class Bless:
    
    def __init__(self,root):
        super().__init__()
        self.asw = None
        self.cycle = 0
        self.root = root
        root.title("Blessing Devotion Interactive Story ✟ Story Reader and Maker")
        root.geometry("623x720+257+33")
        root.resizable(False,  False)
        
        # Binding short-cut for keyboard
        self.root.bind('<Control-d>', self.dele)
        self.root.bind('<Control-c>', self.copy)
        self.root.bind('<Control-s>', self.save_as)
        self.root.bind('<Control-x>', self.ex)
        self.root.bind('<Control-D>', self.dele)
        self.root.bind('<Control-C>', self.copy)
        self.root.bind('<Control-S>', self.save_as)
        self.root.bind('<Control-X>', self.ex)
        self.root.bind('<Control-f>', self.refresh)
        self.root.bind('<Control-F>', self.refresh)
        self.root.bind('<Control-P>', self.paste)
        self.root.bind('<Control-p>', self.paste)
        
        # Menu setting
        self.menu_bar = Menu(root)  # menu begins
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label='File', menu=self.file_menu)
        self.edit_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label='Edit', menu=self.edit_menu)
        self.root.config(menu=self.menu_bar)  # menu ends
        
        # Help click to website
        self.about_menu = Menu(self.menu_bar, tearoff = 0)
        self.menu_bar.add_cascade(label = 'About', menu = self.about_menu)
        self.about_menu.add_command(label = 'Help',compound='left', 
                                    command=self.about)
        
        # File menu
        self.file_menu.add_command(label='Save as',  compound='left', 
                                   accelerator='Ctrl+S', command=self.save_as)
        self.file_menu.add_command(label='Refresh File',  compound='left', 
                                   accelerator='Ctrl+F', command=self.refresh)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Exit', compound='left', 
                                   accelerator='Ctrl+X', command=self.ex)
        
        # Edit menu
        self.edit_menu.add_command(label='Copy', accelerator='Ctrl+C',
                                   compound='left', command=self.copy)
        self.edit_menu.add_command(label='Paste', accelerator='Ctrl+P',
                                   compound='left', command=self.paste)
        self.edit_menu.add_command(label='Delete', accelerator='Ctrl+D',
                                   compound='left', command=self.dele)
        
        
        # Variables to connect within widget.
        self.st1 = StringVar()
        
        # Checking the existence of the directory
        self.h_path = Path.home().joinpath("StoryMaker")
                    
        # Create frame, combobox, textbox, scrollbar, and radiobuttons
        self.combo = StorySelection(self.root, self.h_path)
        self.combo.combo_stories.bind("<<ComboboxSelected>>", self.choice, add=True)
        self.frame = Frame(self.root)
        self.frame.pack(side = BOTTOM, fill = BOTH, expand = True)
        self.scr = Scrollbar(self.frame)
        self.scr.pack(side = RIGHT, fill = BOTH, pady = 2, padx = 1)
        self.stbox = Text(self.frame, relief = 'sunken', wrap="word")
        self.stbox.pack(side = LEFT, fill = BOTH, expand = True,
                        padx = 2, pady = 2)
        self.scr.config(command=self.stbox.yview)
        self.stbox.config(
            yscrollcommand=self.scr.set, font=("Avenir", "12", "bold")
        )
        # self.bttr = Button(self.root, text = 'Dictionary', command = self.trans, 
        #                    relief = 'groove')
        # self.bttr.pack(side='left', padx = 3, pady = 2)
        self.rb1 = Radiobutton(self.root, text = 'A', variable=self.st1, 
                            value = 'A', compound='left', 
                            command = self.choice, tristatevalue = 0)
        self.rb1.pack(side='left', expand = True)
        self.rb2 = Radiobutton(self.root, text = 'B', variable=self.st1, 
                            value = 'B', compound=LEFT, 
                            command = self.choice, tristatevalue = 0)
        self.rb2.pack(side='left', expand = True)
        self.rb3 = Radiobutton(self.root, text = 'C', variable=self.st1, 
                            value = 'C', compound=LEFT, 
                            command = self.choice, tristatevalue = 0)
        self.rb3.pack(side='left', expand = True)
        self._set_combo(False)
    
    def _text_conf(self, editable=False):
        if not editable:
            self.stbox.config(state="disabled")
        else:
            self.stbox.config(state="normal")

    def _running(self):
        if self.story_run == self.combo.combo_stories.get() and self.asw:
            return True
        self.refresh()

    # Choices function for choosing A/B/C    
    def choice(self, event = None):
        self._text_conf(True)
        self.asw = (
            Choices(self.st1.get()) if self.st1.get() in ["A", "B", "C"] else ""
        )
        match self.cycle:
            case 0:
                self.story_run = self.combo.combo_stories.get()
                self.clear()
                self.story()
                if self.docr:
                    self.s_story1()
                    self.cycle += 1
            case 1:
                if self._running():
                    self.get_ans(self.asw, self.cycle)
                    self.s_story2()
                    self.cycle += 1
            case 2:
                if self._running():
                    self.get_ans(self.asw, self.cycle)
                    self.s_story3()
                    self.cycle += 1
        if self.cycle == 3:
            self._set_combo(False)
            self.cycle = 0
        self._text_conf()
                    
    def _insert_answer(self, part: int, ans: str, sentences: str):
        double = "\n\n" if part == 2 else "\n"
        self.stbox.insert(END, f"{double}Choose: {ans}\n")
        self.stbox.insert(END, f"\n{sentences}")
        del double, part, ans, sentences

    # Answering function        
    def get_ans(self, ans=None, part=None):
        
        match part:
            case 1:
                self._insert_answer(part, ans, self.docr[0]["stories"]["first"][ans])
            case 2:
                self._insert_answer(part, ans, self.docr[0]["stories"]["second"][ans])
                
    # Filling stories parts into 9 set of class properties    
    def story(self):

        if story := self.combo.combo_stories.get():
            with chdir(self.combo.path):
                self.docr.extend(StoryFilesLoads(self.combo.path).data_extract(story))
        
    def _choices(self, begin: bool = True):
        return [
            f"{k}. {v}" for k, v in self.docr[1]["choices"]["first" if begin else "second"].items()
        ]
   
    # Starting first part of a story
    def s_story1(self):
        self.stbox.insert("1.0", f"{self.docr[0]["stories"]["begin"]}\n\n")
        for i in self._choices():
            self.stbox.insert(END, i+'\n')

    # 2nd part of a story
    def s_story2(self):
        self.stbox.insert(END, '\n')
        for i in self._choices(False):
            self.stbox.insert(END, '\n' + i )
        self.st1.set(1)

    # 3rd of a story           
    def s_story3(self):

        stc = self.docr[2]["scriptures"].get(self.asw)
        if stc:
             self.stbox.insert(END, f"\n\n{stc.upper()}")
        del stc

    def _set_combo(self, normal: bool = True):
        state = "normal" if normal else "disabled"
        self.rb1.config(state=state)
        self.rb2.config(state=state)
        self.rb3.config(state=state)
    
    # Clear function for starting new story afresh    
    def clear(self):
        self._inner_del()
        self.docr = []
        self._set_combo(bool(self.combo.combo_stories.get()))
        self.st1.set(1)

    # Link to lWW Github page
    def about(self):
        webbrowser.open_new(r"https://github.com/kakkarja/Story_Maker")
    
    # Select all text content
    def select_all(self):
        self.stbox.tag_add('sel', '1.0', 'end')
            
    # Generate Copy Function
    def copy(self, event = None):
        self.root.clipboard_clear()
        self.select_all()
        self.stbox.event_generate("<<Copy>>")   
    
    def paste(self, event = None):
        self._text_conf(True)
        self.stbox.event_generate("<<Paste>>")
        self._text_conf()

    def _inner_del(self):
        self.select_all()
        self.stbox.event_generate("<<Clear>>")

    # Generate Delete Function
    def dele(self, event = None):
        self._text_conf(True)
        self._inner_del()
        self._text_conf()
        self._set_combo(False)
    
    # Generate Exit Function
    def ex(self, event = None):
        self.root.destroy()
    
    # Writing to a .txt file (misc) 
    def write_to_file(self, file_name):
        sen = self.combo.combo_stories.get()
        if selection := self.stbox.get('1.0', 'end'):
            content = (
                f"{sen}\n\n{selection}" if sen else selection
            )
            with open(file_name, 'w') as the_file:
                the_file.write(content)
        del sen, selection
    
    # Generate Save as function dialog
    def save_as(self, event = None):
        input_file_name = fil.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Documents", "*.txt")] #("All Files", "*.*")
        )
        if input_file_name:
            self.write_to_file(input_file_name)
    
    # Refresh list of files in BP
    def refresh(self, event = None):
        self.cycle = 0
        self.choice()

    # Dictionary Function
    def trans(self, event = None):
        pass


def transfer_stories(path: Path):
    stories_path = Path(__file__).parent.parent.joinpath("stories")
    if not path.exists():
        path.mkdir()
    if stories_path.joinpath("BlessingPro").exists():
        with chdir(stories_path):
            stories_path.joinpath("BlessingPro").rename(path.joinpath("BlessingPro"))

def main():
    pth = Path.home().joinpath("StoryMaker")
    begin = Tk()
    begin.withdraw()
    try:
        transfer_stories(pth)
    except:
        mes.showinfo(
            "Stories", 
            (
                f"Could not transfer folder of stories, please do it manually from {
                    Path(__file__).parent.parent.joinpath("stories")
                } to {pth}!"
            )
        )
    ans = mes.askyesnocancel("Blessing Project", "Load story or Create story? (yes to load)")
    files = bool(list(pth.iterdir())) if pth.exists() else False
    if pth.exists() and files and ans:
        my_gui = Bless(begin)
        begin.deiconify()
        begin.mainloop()
        main()
    elif ans == False or all([ans == True, not files]) :
        try:
            from .main_frame import story_maker
        except:
            from main_frame import story_maker
        if ans:
            print("No stories yet, please make one!")
            mes.showinfo("No Stories", "No stories exist yet, please make one!")
        begin.destroy()
        story_maker()
        main()
    else:
        begin.destroy()


if __name__ == '__main__':
    main()
   