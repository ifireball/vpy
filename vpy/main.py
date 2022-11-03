from tkinter import *
from tkinter.ttk import *
from itertools import count
from functools import partial


class WidgetSelector:
    def __init__(self, canvas):
        self.canvas = canvas
        self.ctrl_pt_widgets = [
            Canvas(canvas, background="blue", borderwidth=0, width=7, height=7, relief=FLAT)
            for _ in range(8)
        ]
        self.ctrl_pt_handles = [None] * len(self.ctrl_pt_widgets)
        self.widget = None
        self.canvas_id = None

        for w_cpt in self.ctrl_pt_widgets[2:5]:
            w_cpt.configure(cursor="sb_h_double_arrow")
            w_cpt.bind("<Button-1>", self._begin_drag_width)
            w_cpt.bind("<ButtonRelease-1>", self._end_drag_width)
            
        for v_cpt in self.ctrl_pt_widgets[4:7]:
            v_cpt.configure(cursor="sb_v_double_arrow")
            v_cpt.bind("<Button-1>", self._begin_drag_height, '+')
            v_cpt.bind("<ButtonRelease-1>", self._end_drag_height, '+')

        self.ctrl_pt_widgets[4].configure(cursor="sizing")
        
    def _select_widget(self, canvas_id, event):
        self.widget = event.widget
        self.canvas_id = canvas_id
        self._markers_to_widget(self.widget)
        # print(f"widget selected: {w}")
        self._begin_drag_position(event)

    def _markers_to_widget(self, w):
        x0, x2 = w.winfo_x(), w.winfo_x() + w.winfo_width()
        x1 = (x0 + x2) // 2
        y0, y2 = w.winfo_y(), w.winfo_y() + w.winfo_height()
        y1 = (y0 + y2) // 2
        x_coords = [x0, x1, x2, x2, x2, x1, x0, x0]
        y_coords = [y0, y0, y0, y1, y2, y2, y2, y1]
        for i, widget, handle, x, y in zip(
            count(), self.ctrl_pt_widgets, self.ctrl_pt_handles, x_coords, y_coords
        ):
            # print(f"{i=}, {handle=}, {widget=}, {x=}, {y=}")
            if handle is None:
                self.ctrl_pt_handles[i] = self.canvas.create_window(x, y, window=widget)
            else:
                self.canvas.coords(handle, x, y)
            # Seems there is a bug in widget.lift() and the tk docs!
            self.canvas.tk.call("raise", widget)

    def _begin_drag_position(self, event):
        if not self.canvas_id:
            return
        bind_tag = f"{type(self).__name__}:{self.canvas_id}"
        self.canvas.bind_class(bind_tag, "<Motion>", partial(self._drag_position, event.x, event.y))

    def _end_drag_position(self, event):
        if not self.canvas_id:
            return
        bind_tag = f"{type(self).__name__}:{self.canvas_id}"
        self.canvas.unbind_class(bind_tag, "<Motion>")

    def _drag_position(self, initial_x, initial_y, event):
        if not self.widget:
            return
        p = self.widget.master
        if hasattr(p, "move"):
            p.move(self.canvas_id, event.x - initial_x, event.y - initial_y)
            self.canvas.update_idletasks()
            self._markers_to_widget(self.widget)

    def _begin_drag_width(self, event):
        # print("Begin width drag")
        event.widget.bind("<Motion>", self._drag_width, "+")

    def _end_drag_width(self, event):
        # print("End width drag")
        event.widget.unbind("<Motion>")
        
    def _drag_width(self, event):
        if not self.widget:
            return
        new_width = max(
            event.x_root - self.ctrl_pt_widgets[0].winfo_rootx(),
            self.widget.winfo_reqwidth()
        )
        # print(f"{event.x_root=} {self.ctrl_pt_widgets[0].winfo_rootx()=}")
        p = self.widget.master
        if hasattr(p, "itemconfigure"):
            p.itemconfigure(self.canvas_id, width=new_width)
            self.canvas.update_idletasks()
            self._markers_to_widget(self.widget)

    def _begin_drag_height(self, event):
        # print("Begin height drag")
        event.widget.bind("<Motion>", self._drag_height, "+")

    def _end_drag_height(self, event):
        # print("End height drag")
        event.widget.unbind("<Motion>")
        
    def _drag_height(self, event):
        if not self.widget:
            return
        new_height = max(
            event.y_root - self.ctrl_pt_widgets[0].winfo_rooty(),
            self.widget.winfo_reqheight()
        )
        # print(f"{event.x_root=} {self.ctrl_pt_widgets[0].winfo_rootx()=}")
        p = self.widget.master
        if hasattr(p, "itemconfigure"):
            p.itemconfigure(self.canvas_id, height=new_height)
            self.canvas.update_idletasks()
            self._markers_to_widget(self.widget)

    def manage_widget(self, widget, canvas_id):
        bind_tag = f"{type(self).__name__}:{canvas_id}"
        widget.bindtags(bind_tag)
        self.canvas.bind_class(bind_tag, "<Button-1>", partial(self._select_widget, canvas_id))
        self.canvas.bind_class(bind_tag, "<ButtonRelease-1>", self._end_drag_position)


def main():
    main_window = Tk()
    main_window.columnconfigure(0, weight=1)
    main_window.rowconfigure(0, weight=1)

    canvas = Canvas(main_window, background="white")
    canvas.grid(column=0, row=0, sticky=(N, E, S, W))

    selector = WidgetSelector(canvas)

    b1 = Button(canvas, text="Foo")
    b1_id = canvas.create_window(20, 20, window=b1, anchor=NW)
    selector.manage_widget(b1, b1_id)

    b2 = Button(canvas, text="Bar")
    b2_id = canvas.create_window(20, 60, window=b2, anchor=NW)
    selector.manage_widget(b2, b2_id)
    
    main_window.mainloop()
    

if __name__ == "__main__":
    main()
