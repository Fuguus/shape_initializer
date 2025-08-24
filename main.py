import tkinter as tk

def main():
    # Setup
    root = tk.Tk()
    window_width = int(root.winfo_screenwidth()/1.5)
    window_height = int(root.winfo_screenheight()/1.5)
    root.geometry(f"{window_width}x{window_height}")
    root.title('Canvas')
    root.resizable(width=False, height=False)

    #Menu Container
    menu_height = 40
    menu_frame = tk.Frame(root, height=menu_height, bg="#121212")
    menu_frame.pack(side="top", fill="x")

    #Canvas
    canvas = tk.Canvas(root, bg = "#121212", bd=0, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    #ID Handling
    next_id = 0
    
    def generate_id():
        nonlocal next_id
        next_id += 1
        return next_id - 1

    #History
    history = []

    def undo(event=None):
        if not history:
            return
        eid = history.pop()
        for cid in entities[eid]["canvas_id"]:
            canvas.delete(cid)
        del entities[eid]

    root.bind("<Control-z>", undo)

    #Grid
    cell_size = 20
    row = int(window_width/cell_size)
    col = int(window_height/cell_size)

    for i in range(row+1):
        x_loc = i * cell_size
        canvas.create_line(x_loc, 0, x_loc, window_height-menu_height, fill="#2A2A2A", width=1)

    for j in range(col+1):
        y_loc = j * cell_size
        canvas.create_line(0, y_loc, window_width, y_loc, fill="#2A2A2A", width=1)

    #Entity Container
    entities = {}

    #Trim Function
    trim_mode = {"active": False}

    def enable_trim_mode():
        disable_all_modes()
        trim_mode["active"] = True
        root.bind("<Escape>", disable_all_modes)
        canvas.bind("<Button-1>", on_click_trim)

    def on_click_trim(e):
        if not trim_mode["active"]:
            return
        half = cell_size // 2
        item = canvas.find_overlapping(e.x - half, e.y - half, e.x + half, e.y + half)
        if not item:
            return
        print(item[-1])


    # --- Point Mode ---
    r = 2
    preview_point = canvas.create_oval(-10, -10, -10, -10, fill="red", outline="")  # hidden preview
    point_mode = {"active": False}

    def enable_point_mode():
        disable_all_modes()
        point_mode["active"] = True
        canvas.tag_raise(preview_point)
        root.bind("<Escape>", disable_all_modes)
        canvas.bind("<Button-1>", on_click_point)
        canvas.bind("<Motion>", on_motion_point)

    def on_motion_point(e):
        if not point_mode["active"]:
            return
        grid_x = round(e.x / cell_size) * cell_size
        grid_y = round(e.y / cell_size) * cell_size
        canvas.coords(preview_point, grid_x - r, grid_y - r, grid_x + r, grid_y + r)

    def on_click_point(e):
        if not point_mode["active"]:
            return
        grid_x = round(e.x / cell_size) * cell_size
        grid_y = round(e.y / cell_size) * cell_size
        point_id = canvas.create_oval(grid_x - r, grid_y - r, grid_x + r, grid_y + r, fill="red", outline="")
        eid = generate_id()
        entity = {
            "entity_id": eid,
            "type": "point",
            "coords": (grid_x, grid_y),
            "canvas_id": [point_id]
        }
        entities[eid] = entity
        history.append(eid)

    # --- Line Mode ---
    preview_line = canvas.create_line(-10, -10, -10, -10, fill="cyan", dash=(3,2))
    preview_line_point = canvas.create_oval(-10, -10, -10, -10, fill="red", outline="")
    line_mode = {"active": False, "first_point": None, "first_point_id": None}
    
    def enable_line_mode():
        disable_all_modes()
        line_mode["active"] = True
        line_mode["first_point"] = None
        canvas.tag_raise(preview_line)
        canvas.tag_raise(preview_line_point)
        root.bind("<Escape>", disable_all_modes)
        canvas.bind("<Button-1>", on_click_line)
        canvas.bind("<Motion>", on_motion_line)
        
    def on_click_line(e):
        if not line_mode["active"]:
            return
        grid_x = round(e.x / cell_size) * cell_size
        grid_y = round(e.y / cell_size) * cell_size
        if line_mode["first_point"] is None:
            line_mode["first_point"] = (grid_x, grid_y)
            line_mode["first_point_id"] = canvas.create_oval(grid_x - r, grid_y - r, grid_x + r, grid_y + r, fill="red", outline="")
            canvas.coords(preview_line_point, grid_x - r, grid_y - r, grid_x + r, grid_y + r)
        else:
            # Second click → finalize line
            x0, y0 = line_mode["first_point"]
            if x0 != grid_x or y0 != grid_y:
                line_id = canvas.create_line(x0, y0, grid_x, grid_y, fill="red", width=2)
                point2_id = canvas.create_oval(grid_x - r, grid_y - r, grid_x + r, grid_y + r, fill="red", outline="")
                eid = generate_id()
                entity = {
                    "entity_id": eid,
                    "type": "line",
                    "coords": (x0, y0, grid_x, grid_y),
                    "canvas_id": [line_mode["first_point_id"], line_id, point2_id]
                }
                entities[eid] = entity
                history.append(eid)
            else:
                canvas.delete(line_mode["first_point_id"])
            line_mode["first_point"] = None
            line_mode["first_point_id"] = None
            # hide preview
            canvas.coords(preview_line, -10, -10, -10, -10)
            canvas.coords(preview_line_point, -10, -10, -10, -10)

    def on_motion_line(e):
        if not line_mode["active"]:
            return
        grid_x = round(e.x / cell_size) * cell_size
        grid_y = round(e.y / cell_size) * cell_size
        canvas.coords(preview_line_point, grid_x - r, grid_y - r, grid_x + r, grid_y + r)
        if line_mode["first_point"]:
            x0, y0 = line_mode["first_point"]
            canvas.coords(preview_line, x0, y0, grid_x, grid_y)

    # --- Circle Mode ---
    preview_circle = canvas.create_oval(-10, -10, -10, -10, outline="cyan", dash=(3,2))
    preview_circle_point = canvas.create_oval(-10, -10, -10, -10, fill="red", outline="")
    circle_mode = {"active" : False, "center": None, "center_id": None}

    def enable_circle_mode():
        disable_all_modes()
        circle_mode["active"] = True
        circle_mode["first_point"] = None
        canvas.tag_raise(preview_circle)
        canvas.tag_raise(preview_circle_point)
        root.bind("<Escape>", disable_all_modes)
        canvas.bind("<Button-1>", on_click_circle)
        canvas.bind("<Motion>", on_motion_circle)

    def on_click_circle(e):
        if not circle_mode["active"]:
            return
        grid_x = round(e.x / cell_size) * cell_size
        grid_y = round(e.y / cell_size) * cell_size
        if circle_mode["center"] is None:
            circle_mode["center"] = (grid_x, grid_y)
            circle_mode["center_id"] = canvas.create_oval(grid_x - r, grid_y - r, grid_x + r, grid_y + r, fill="red", outline="")
            canvas.coords(preview_circle_point, grid_x - r, grid_y - r, grid_x + r, grid_y + r)
        else:
            x0, y0 = circle_mode[("center")]
            dx = grid_x - x0
            dy = grid_y - y0
            radius = round(((dx**2 + dy**2)**0.5) / cell_size) * cell_size
            if radius > 0:
                id = canvas.create_oval(x0 - radius, y0 - radius, x0 + radius, y0 + radius, outline="red", width=2)
                eid = generate_id()
                entity = {
                    "entity_id": eid,
                    "type": "circle",
                    "center": (x0, y0),
                    "radius": radius,
                    "canvas_id": [id]
                }
                entities[eid] = entity
                history.append(eid)
            canvas.delete(circle_mode["center_id"])
            circle_mode["center_id"] = None
            circle_mode["center"] = None
            canvas.coords(preview_circle, -10, -10, -10, -10)
            canvas.coords(preview_circle_point, -10, -10, -10, -10)

    def on_motion_circle(e):
        if not circle_mode["active"]:
            return
        grid_x = round(e.x / cell_size) * cell_size
        grid_y = round(e.y / cell_size) * cell_size
        if circle_mode["center"] is None:
            canvas.coords(preview_line_point, grid_x - r, grid_y - r, grid_x + r, grid_y + r)
        else:
            x0, y0 = circle_mode["center"]
            dx = grid_x - x0
            dy = grid_y - y0
            radius = round(((dx ** 2 + dy ** 2) ** 0.5) / cell_size) * cell_size
            canvas.coords(preview_circle, x0 - radius, y0 - radius, x0 + radius, y0 + radius)

    # --- Disable All Modes ---
    def disable_all_modes(event=None):
        point_mode["active"] = False
        line_mode["active"] = False
        circle_mode["active"] = False
        trim_mode["active"] = False

        if line_mode.get("first_point_id"):
            canvas.delete(line_mode["first_point_id"])
            line_mode["first_point_id"] = None

        if circle_mode.get("center_id"):
            canvas.delete(circle_mode["center_id"])
            circle_mode["center_id"] = None

        line_mode["first_point"] = None
        circle_mode["center"] = None

        canvas.coords(preview_point, -10, -10, -10, -10)
        canvas.coords(preview_line, -10, -10, -10, -10)
        canvas.coords(preview_line_point, -10, -10, -10, -10)
        canvas.coords(preview_circle, -10, -10, -10, -10)
        canvas.coords(preview_circle_point, -10, -10, -10, -10)

        root.unbind("<Escape>")
        canvas.unbind("<Button-1>")
        canvas.unbind("<Motion>")

    #Buttons
    tk.Button(menu_frame, text="Point", command=enable_point_mode).pack(side="left")
    tk.Button(menu_frame, text="Line", command=enable_line_mode).pack(side="left")
    tk.Button(menu_frame, text="Circle", command=enable_circle_mode).pack(side="left")
    tk.Button(menu_frame, text="Trim", command=enable_trim_mode).pack(side="left")

    root.mainloop()

if __name__ == "__main__":
    main()