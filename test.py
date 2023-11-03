import tkinter
import tkinter.messagebox

def say_helloWorld():
    tkinter.messagebox.showinfo(title="Say",message="Hello, World!")

root = tkinter.Tk()
button = tkinter.Button(root,text="Click me!",command=say_helloWorld)
button.pack()

root.mainloop()