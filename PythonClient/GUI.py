# coding: utf-8
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import asksaveasfilename
from tkinter.messagebox import showerror

from matplotlib.figure import Figure
import matplotlib.backends.tkagg as tkagg
from matplotlib.backends.backend_agg import FigureCanvasAgg

import re
import numpy as np
import os


class App(ttk.Frame):
    """
    There are three public method in this class.

    get_ip(): return IP addresses for host, ZJUVision, NatNet and multicast which are configured in the window
    display(x, y, mtx): display the result in the window. x and y are positions for points, and mtx is the matrix
    write_info(buf): display information in the bottom of window to help user

    An App instance has already been created in this module. You should use it with the following format:
        from GUI import app
        ... # other thread or process
        app.mainloop()  # this is a blocking method. You should only call it after your own process or thread starts.

    An example is given in Coordinate.py.
    """
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.__ip_area()
        self.__fitting_area()
        self.__info_area()

        self.start_stop_callback = None
        self.clear_callback = None

    def __ip_area(self):
        self.IPArea = ttk.Labelframe(master=self, text="IP configure")
        self.IPArea.pack(padx=5, pady=5, ipadx=2, ipady=2, fill="x")

        # validation
        vcmd = self.master.register(self.__ip_is_okay)
        ivcmd = self.master.register(self.__ip_isnt_okay)

        # get IP from configuration file
        if os.path.exists("configure/IP_address.npz"):
            with np.load("configure/IP_address.npz") as X:
                hostIP, ZJUVisionIP, NatNetIP, multicastIP = [X[i] for i in
                                                              ("hostIP", "ZJUVisionIP", "NatNetIP", "multicastIP")]
        else:
            hostIP, ZJUVisionIP, NatNetIP, multicastIP = "192.168.1.1", "192.168.1.2", "192.168.1.3", "192.168.1.4"
            if not os.path.isdir("configure"):
                os.mkdir("configure")
            np.savez("configure/IP_address.npz",
                     hostIP=hostIP,
                     ZJUVisionIP=ZJUVisionIP,
                     NatNetIP=NatNetIP,
                     multicastIP=multicastIP)

        # IP for host
        self.hostIP = tk.StringVar(master=self.IPArea, value=hostIP)
        self.label_host = ttk.Label(master=self.IPArea, text="Host IP", justify=tk.RIGHT)
        self.label_host.grid(row=0, column=0, padx=2)
        self.entry_hostIP = ttk.Entry(master=self.IPArea, justify=tk.CENTER,
                                      state=tk.DISABLED, textvariable=self.hostIP,
                                      validatecommand=(vcmd, "%P"),
                                      validate="focusout",
                                      invalidcommand=(ivcmd, "%W"))
        self.entry_hostIP.grid(row=0, column=1, padx=2)

        # IP for ZJUVision
        self.ZJUVisionIP = tk.StringVar(master=self.IPArea, value=ZJUVisionIP)
        self.label_ZJUVision = ttk.Label(master=self.IPArea, text="ZJUVision IP", justify=tk.RIGHT)
        self.label_ZJUVision.grid(row=1, column=0, padx=2)
        self.entry_ZJUVisionIP = ttk.Entry(master=self.IPArea, justify=tk.CENTER,
                                           state=tk.DISABLED, textvariable=self.ZJUVisionIP,
                                           validatecommand=(vcmd, "%P"),
                                           validate="focusout",
                                           invalidcommand=(ivcmd, "%W"))
        self.entry_ZJUVisionIP.grid(row=1, column=1, padx=2)

        # IP for Motion capture
        self.NatNetIP = tk.StringVar(master=self.IPArea, value=NatNetIP)
        self.label_NatNet = ttk.Label(master=self.IPArea, text="Motion Capture IP", justify=tk.RIGHT)
        self.label_NatNet.grid(row=0, column=2, padx=2)
        self.entry_NatNetIP = ttk.Entry(master=self.IPArea, justify=tk.CENTER,
                                        state=tk.DISABLED, textvariable=self.NatNetIP,
                                        validatecommand=(vcmd, "%P"),
                                        validate="focusout",
                                        invalidcommand=(ivcmd, "%W"))
        self.entry_NatNetIP.grid(row=0, column=3, padx=2)

        # IP for multicast
        self.multicastIP = tk.StringVar(master=self.IPArea, value=multicastIP)
        self.label_multi = ttk.Label(master=self.IPArea, text="multicast IP", justify=tk.RIGHT)
        self.label_multi.grid(row=1, column=2, padx=2)
        self.entry_multicastIP = ttk.Entry(master=self.IPArea, justify=tk.CENTER,
                                           state=tk.DISABLED, textvariable=self.multicastIP,
                                           validatecommand=(vcmd, "%P"),
                                           validate="focusout",
                                           invalidcommand=(ivcmd, "%W"))
        self.entry_multicastIP.grid(row=1, column=3, padx=2)

        # disable the entries when the checkbox is selected
        self.isLocked = tk.IntVar(master=self.IPArea, value=0)
        self.edit_button = ttk.Checkbutton(master=self.IPArea, text="Edit Enable",
                                           command=self.__edit_ip, variable=self.isLocked)
        self.edit_button.grid(row=0, column=4, rowspan=2, columnspan=1, padx=10)

    def __edit_ip(self):
        if self.isLocked.get() == 1:
            self.entry_hostIP["state"] = tk.NORMAL
            self.entry_multicastIP["state"] = tk.NORMAL
            self.entry_NatNetIP["state"] = tk.NORMAL
            self.entry_ZJUVisionIP["state"] = tk.NORMAL
        else:
            self.entry_hostIP["state"] = tk.DISABLED
            self.entry_multicastIP["state"] = tk.DISABLED
            self.entry_NatNetIP["state"] = tk.DISABLED
            self.entry_ZJUVisionIP["state"] = tk.DISABLED

    def __ip_is_okay(self, ip_str):
        pattern = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)" \
                  r"\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)" \
                  r"\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)" \
                  r"\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
        if re.match(pattern, ip_str):
            if not os.path.isdir("configure"):
                os.mkdir("configure")
            np.savez("configure/IP_address.npz",
                     hostIP=self.hostIP.get(),
                     ZJUVisionIP=self.ZJUVisionIP.get(),
                     NatNetIP=self.NatNetIP.get(),
                     multicastIP=self.multicastIP.get())
            return True
        else:
            return False

    def __ip_isnt_okay(self, widget_name):
        widget = self.nametowidget(widget_name)
        widget.delete(0, tk.END)
        widget.focus_set()
        widget.bell()

    def get_ip(self):
        return self.hostIP.get(), self.ZJUVisionIP.get(), self.NatNetIP.get(), self.multicastIP.get()

    def __fitting_area(self):
        self.fittingArea = ttk.Labelframe(master=self, text="workspace")
        self.fittingArea.pack(padx=5, pady=5, ipadx=2, ipady=2, fill="x")
        self.fittingArea.rowconfigure(0, weight=1)
        self.fittingArea.rowconfigure(1, weight=1)
        self.fittingArea.rowconfigure(2, weight=5)

        # canvas for displaying the curve
        self.canvas = tk.Canvas(master=self.fittingArea, width=400, height=400)
        self.photo_curve = tk.PhotoImage(master=self.canvas, width=400, height=400)
        self.canvas.create_image(200, 200, anchor=tk.CENTER, image=self.photo_curve)
        self.canvas.grid(row=0, rowspan=4, column=0, padx=5, pady=5)

        # start and stop fitting
        self.button_fit = ttk.Button(master=self.fittingArea, text="start fitting", command=self.__start_stop_fitting)
        self.button_fit.grid(row=0, column=1, padx=5)

        # clear all the history data
        self.button_clear = ttk.Button(master=self.fittingArea, text="clear", command=self.__clear)
        self.button_clear.grid(row=0, column=2, padx=5)

        # export result
        self.button_export = ttk.Button(master=self.fittingArea, text="export", command=self.__export)
        self.button_export.grid(row=1, column=2, padx=5)

        # way of export
        self.export_type = tk.StringVar(master=self.fittingArea, value="┈┈ type ┈┈")
        self.combo_export = ttk.Combobox(master=self.fittingArea, justify=tk.LEFT, width=9,
                                         textvariable=self.export_type, height=4)
        self.combo_export["values"] = ["Clipboard", "File"]
        self.combo_export.grid(row=1, column=1, padx=5)

        # print result out
        self.frame_result = ttk.Frame(master=self.fittingArea)
        self.frame_result.grid(row=2, column=1, columnspan=2, padx=5)
        self.label_tag = ttk.Label(master=self.frame_result, justify=tk.LEFT, text="Result: ")
        self.label_tag.grid(row=0, column=0, padx=5)
        self.matrix = [[tk.StringVar(master=self.fittingArea,value="0.000") for _ in range(4)] for _ in range(4)]
        self.label_result = [[None]*4]*4
        for i in range(4):
            for j in range(4):
                self.label_result[i][j] = ttk.Label(master=self.frame_result,
                                                    borderwidth=1, relief="groove", width=6, anchor=tk.CENTER,
                                                    textvariable=self.matrix[i][j])
                self.label_result[i][j].grid(row=1+i, column=0+j, padx=3)

    def __start_stop_fitting(self):
        self.start_stop_callback()

    def __clear(self):
        self.clear_callback()

    def __export(self):
        # prepare the string that will be exported
        str_temp = ""
        for i in range(4):
            for j in range(4):
                str_temp = str_temp + self.matrix[i][j].get() + r' '
            str_temp = str_temp + '\n'

        method = self.export_type.get()
        if method == "Clipboard":
            self.clipboard_clear()
            self.clipboard_append(str_temp)
        elif method == "File":
            if not os.path.isdir("output"):
                os.mkdir("output")
            filename = asksaveasfilename(filetypes=[("TXT", "*.txt")], defaultextension=".txt",
                                         initialdir=os.path.join(os.curdir, "output"))
            if filename != "":
                with open(filename, 'w') as f:
                    f.write(str_temp)
        else:
            showerror(title="Error", message="Invalid type of export")

    def display(self, x, y, mtx):
        # display the curve
        fig = Figure(figsize=(4, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(x, y)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

        figure_canvas_agg = FigureCanvasAgg(fig)
        figure_canvas_agg.draw()

        tkagg.blit(self.photo_curve, figure_canvas_agg.get_renderer()._renderer, colormode=2)

        # display the result matrix
        mtx = np.array(mtx)
        for i in range(4):
            for j in range(4):
                self.matrix[i][j].set("%1.3f" % mtx[i][j])

    def __info_area(self):
        # some information
        self.info = tk.StringVar(master=self, value="Welcome")
        self.label_info = ttk.Label(master=self,
                                    anchor=tk.CENTER,
                                    textvariable=self.info)
        self.label_info.pack(fill='x', padx=5, pady=3)

    def write_info(self, buf):
        self.info.set(buf)


root = tk.Tk()
root.iconbitmap("configure/DF.ico")
root.title("Synchronized Calibration")
app = App(master=root)


if __name__ == '__main__':
    app.mainloop()
