from src.model.behavioral.agent import Agent

def scroll_linux(event, zoom_in, zoom_out, view_port, canvas):
    if event.num == 4:
        on_zoom_in (zoom_in, view_port, canvas)
    elif event.num == 5:
        on_zoom_out (zoom_out, view_port, canvas)

def scroll_mouse_wheel(event, zoom_in, zoom_out, view_port, canvas):
    if event.delta < 0:
        on_zoom_in (zoom_in, view_port, canvas)
    elif event.delta > 0:
        on_zoom_out (zoom_out, view_port, canvas)

def focus_random_agent(rng, view_port, agents, canvas):
    ag: Agent = rng.choice(agents)
    x, y = view_port.apply(*ag.coordinate.get_lon_lat())

    new_x = int(-1*x + canvas.winfo_width()/2)
    new_y = int(-1*y + canvas.winfo_height()/2)

    view_port.change_center(new_x, new_y)
    canvas.scan_dragto(view_port.x, view_port.y, gain=1)

def on_zoom_in (scale, view_port, canvas):
    view_port.update_scale(scale)
    canvas.scale("all", 0, 0, scale, scale)

def on_zoom_out (scale, view_port, canvas):
    view_port.update_scale(scale)
    canvas.scale("all", 0, 0, scale, scale)

def on_mouse_release(view):
    view.mouse_prev_position = None

def on_mouse_hold(event, view):
    x, y  = event.x, event.y
    if view.mouse_prev_position is not None:
        px, py = view.mouse_prev_position
        view.view_port.update_center(px-x, py-y)
        # view.coord_label.configure(text=f"{px-x}, {py-y}")

    view.mouse_prev_position = (x, y)
    view.canvas.scan_dragto (view.view_port.x, view.view_port.y, gain=1)
