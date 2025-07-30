# import ttkbootstrap as ttk
# from ttkbootstrap.constants import *

# root = ttk.Window()

# b1 = ttk.Button(root, text="Solid Button", bootstyle=SUCCESS)
# b1.pack(side=LEFT, padx=5, pady=10)

# b2 = ttk.Button(root, text="Outline Button", bootstyle=(SUCCESS, 'outline'))
# b2.pack(side=LEFT, padx=5, pady=10)

# root.mainloop()


import ttkbootstrap as ttk
window = ttk.Window(title='ok')
window.geometry('200x200+100+100')

# ttk.Treeview(master=window).pack()
ttk.ScrolledText(window).pack()

window.mainloop()
