import json
import logging
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RoomMapApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Room Map Maker")
        
        # Initialize ttk.Style
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#ccc")
        self.style.configure("TLabel", background="#f0f0f0", font=("Helvetica", 12))
        self.style.configure("TEntry", padding=6)
        self.style.configure("Treeview", background="#f0f0f0", fieldbackground="#f0f0f0", font=("Helvetica", 10))
        
        # Prompt user for grid size
        self.grid_width = simpledialog.askinteger("Grid Width", "Enter the grid width (X):", minvalue=1, maxvalue=50)
        self.grid_height = simpledialog.askinteger("Grid Height", "Enter the grid height (Y):", minvalue=1, maxvalue=50)
        
        self.map_data = {"width": self.grid_width, "height": self.grid_height, "rooms": [[{
            "name": "",
            "description": "",
            "ingresses": [],
            "egresses": [],
            "inventory": [],
            "has_weather": False,
            "is_list": False
        } for _ in range(self.grid_height)] for _ in range(self.grid_width)]}
        
        self.canvas = tk.Canvas(self.root, width=self.grid_width * 50, height=self.grid_height * 50)
        self.canvas.pack(padx=10, pady=10)
        
        self.create_menu()
        self.draw_map()
        
        self.start_room = None
        self.end_room = None

    def save_room_edit(self, x, y, name, description, ingresses, egresses, inventory, has_weather, is_list):
        """
        Save room edits.

        Parameters:
        x (int): The x-coordinate of the room.
        y (int): The y-coordinate of the room.
        name (str): The name of the room.
        description (str): The description of the room.
        ingresses (list): The ingresses of the room.
        egresses (list): The egresses of the room.
        inventory (list): The inventory of the room.
        has_weather (bool): Whether the room has weather.
        is_list (bool): Whether the room is a list.
        """
        try:
            self.map_data["rooms"][x][y]["name"] = name
            self.map_data["rooms"][x][y]["description"] = description
            self.map_data["rooms"][x][y]["ingresses"] = ingresses
            self.map_data["rooms"][x][y]["egresses"] = egresses
            self.map_data["rooms"][x][y]["inventory"] = inventory
            self.map_data["rooms"][x][y]["has_weather"] = has_weather
            self.map_data["rooms"][x][y]["is_list"] = is_list
            self.draw_map()  # Redraw the map to update the tile names
        except Exception as e:
            logger.error(f"Error saving room edit at ({x}, {y}): {e}")

    def new_map(self):
        """
        Create a new map.
        """
        self.map_data = {"width": self.grid_width, "height": self.grid_height, "rooms": [[{
            "name": "",
            "description": "",
            "ingresses": [],
            "egresses": [],
            "inventory": [],
            "has_weather": False,
            "is_list": False
        } for _ in range(self.grid_height)] for _ in range(self.grid_width)]}
        self.draw_map()

    def on_stop(self):
        """
        Save the map data and cleanly shut down the application.
        """
        try:
            with open("map1.json", "w") as f:
                json.dump(self.map_data, f)
            logger.info("Map data saved successfully.")
        except Exception as e:
            logger.error(f"Error saving map data: {e}")
        finally:
            self.root.destroy()

    def create_menu(self):
        """
        Create the menu for the application.
        """
        menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New Map", command=self.new_map)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_stop)
        menu_bar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menu_bar)

    def draw_map(self):
        """
        Draw the map grid.
        """
        self.canvas.delete("all")
        self.room_rects = {}
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                rect = self.canvas.create_rectangle(x * 50, y * 50, x * 50 + 50, y * 50 + 50, fill="white", outline="black")
                self.room_rects[(x, y)] = rect
                self.canvas.tag_bind(rect, "<Button-1>", lambda event, x=x, y=y: self.on_canvas_click(event, x, y))
                self.canvas.tag_bind(rect, "<B1-Motion>", self.on_canvas_drag)
                self.canvas.tag_bind(rect, "<ButtonRelease-1>", self.on_canvas_release)
                # Display the name of the tile inside the tile
                room_name = self.map_data["rooms"][x][y]["name"]
                if room_name:
                    self.canvas.create_text(x * 50 + 25, y * 50 + 25, text=room_name, tags="room_name")

    def edit_room(self, x, y):
        """
        Open a dialog to edit room details.

        Parameters:
        x (int): The x-coordinate of the room.
        y (int): The y-coordinate of the room.
        """
        room = self.map_data["rooms"][x][y]
        
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Edit Room ({x}, {y})")

        frame = ttk.Frame(edit_window, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(frame, text="Name:").grid(row=0, column=0, sticky=tk.W)
        name_entry = ttk.Entry(frame, width=50)
        name_entry.grid(row=0, column=1, padx=10, pady=5)
        name_entry.insert(0, room["name"])

        ttk.Label(frame, text="Description:").grid(row=1, column=0, sticky=tk.W)
        description_entry = ttk.Entry(frame, width=50)
        description_entry.grid(row=1, column=1, padx=10, pady=5)
        description_entry.insert(0, room["description"])

        ttk.Label(frame, text="Ingresses:").grid(row=2, column=0, sticky=tk.W)
        ingresses_tree = ttk.Treeview(frame, columns=("Direction", "Target"), show="headings")
        ingresses_tree.heading("Direction", text="Direction")
        ingresses_tree.heading("Target", text="Target")
        ingresses_tree.grid(row=2, column=1, padx=10, pady=5)
        for ingress in room["ingresses"]:
            ingresses_tree.insert("", "end", values=(ingress["direction"], ingress["target"]))

        ttk.Label(frame, text="Egresses:").grid(row=3, column=0, sticky=tk.W)
        egresses_tree = ttk.Treeview(frame, columns=("Direction", "Target"), show="headings")
        egresses_tree.heading("Direction", text="Direction")
        egresses_tree.heading("Target", text="Target")
        egresses_tree.grid(row=3, column=1, padx=10, pady=5)
        for egress in room["egresses"]:
            egresses_tree.insert("", "end", values=(egress["direction"], egress["target"]))

        ttk.Label(frame, text="Inventory:").grid(row=4, column=0, sticky=tk.W)
        inventory_tree = ttk.Treeview(frame, columns=("Item"), show="headings")
        inventory_tree.heading("Item", text="Item")
        inventory_tree.grid(row=4, column=1, padx=10, pady=5)
        for item in room["inventory"]:
            inventory_tree.insert("", "end", values=(item,))

        def add_inventory_item():
            inventory_tree.insert("", "end", values=("New Item",))

        def delete_inventory_item():
            selected_item = inventory_tree.selection()
            if selected_item:
                inventory_tree.delete(selected_item)

        add_button = ttk.Button(frame, text="Add Item", command=add_inventory_item)
        add_button.grid(row=5, column=0, padx=10, pady=5)

        delete_button = ttk.Button(frame, text="Delete Item", command=delete_inventory_item)
        delete_button.grid(row=5, column=1, padx=10, pady=5)

        ttk.Label(frame, text="Has Weather:").grid(row=6, column=0, sticky=tk.W)
        has_weather_var = tk.BooleanVar(value=room["has_weather"])
        has_weather_dropdown = ttk.Combobox(frame, textvariable=has_weather_var, values=[True, False])
        has_weather_dropdown.grid(row=6, column=1, padx=10, pady=5)

        ttk.Label(frame, text="Is List:").grid(row=7, column=0, sticky=tk.W)
        is_list_var = tk.BooleanVar(value=room["is_list"])
        is_list_dropdown = ttk.Combobox(frame, textvariable=is_list_var, values=[True, False])
        is_list_dropdown.grid(row=7, column=1, padx=10, pady=5)

        def save_changes():
            name = name_entry.get()
            description = description_entry.get()
            ingresses = [{"direction": ingresses_tree.item(item)["values"][0], "target": ingresses_tree.item(item)["values"][1]} for item in ingresses_tree.get_children()]
            egresses = [{"direction": egresses_tree.item(item)["values"][0], "target": egresses_tree.item(item)["values"][1]} for item in egresses_tree.get_children()]
            inventory = [inventory_tree.item(item)["values"][0] for item in inventory_tree.get_children()]
            has_weather = has_weather_var.get()
            is_list = is_list_var.get()
            self.save_room_edit(x, y, name, description, ingresses, egresses, inventory, has_weather, is_list)
            edit_window.destroy()

        save_button = ttk.Button(frame, text="Save", command=save_changes)
        save_button.grid(row=8, column=0, columnspan=2, pady=10)

    def on_canvas_click(self, event, x, y):
        """
        Handle canvas click event to start drawing an arrow.
        """
        self.start_room = (x, y)
        self.end_room = None

    def on_canvas_drag(self, event):
        """
        Handle canvas drag event to draw an arrow.
        """
        if self.start_room:
            self.canvas.delete("arrow")
            start_x, start_y = self.get_nearest_point(self.start_room, event.x, event.y)
            self.canvas.create_line(start_x, start_y, event.x, event.y, arrow=tk.LAST, tags="arrow")

    def on_canvas_release(self, event):
        """
        Handle canvas release event to finalize the arrow.
        """
        x, y = event.x // 50, event.y // 50
        if self.start_room == (x, y):
            self.edit_room(x, y)
        else:
            if self.start_room:
                if (x, y) in self.room_rects:
                    self.end_room = (x, y)
                    self.canvas.delete("arrow")
                    start_x, start_y = self.get_nearest_point(self.start_room, event.x, event.y)
                    end_x, end_y = self.get_nearest_point(self.end_room, start_x, start_y)
                    self.ask_connection_type(start_x, start_y, end_x, end_y)
                self.start_room = None
                self.end_room = None

    def get_nearest_point(self, room, target_x, target_y):
        """
        Get the nearest point (corner or side) of the room to the target coordinates.

        Parameters:
        room (tuple): The (x, y) coordinates of the room.
        target_x (int): The x-coordinate of the target point.
        target_y (int): The y-coordinate of the target point.

        Returns:
        tuple: The (x, y) coordinates of the nearest point.
        """
        x, y = room
        offset = 10
        corners = [
            (x * 50 + offset, y * 50 + offset), (x * 50 + 50 - offset, y * 50 + offset),
            (x * 50 + offset, y * 50 + 50 - offset), (x * 50 + 50 - offset, y * 50 + 50 - offset)
        ]
        sides = [
            (x * 50 + 25, y * 50 + offset), (x * 50 + 25, y * 50 + 50 - offset),
            (x * 50 + offset, y * 50 + 25), (x * 50 + 50 - offset, y * 50 + 25)
        ]
        points = corners + sides
        nearest_point = min(points, key=lambda point: (point[0] - target_x) ** 2 + (point[1] - target_y) ** 2)
        return nearest_point

    def ask_connection_type(self, start_x, start_y, end_x, end_y):
        """
        Ask the user if the connection is one-way or two-way.
        """
        connection_window = tk.Toplevel(self.root)
        connection_window.title("Connection Type")

        one_way_var = tk.BooleanVar(value=False)
        two_way_var = tk.BooleanVar(value=False)

        def on_one_way_checked():
            if one_way_var.get():
                two_way_var.set(False)

        def on_two_way_checked():
            if two_way_var.get():
                one_way_var.set(False)

        one_way_check = ttk.Checkbutton(connection_window, text="One-way", variable=one_way_var, command=on_one_way_checked)
        one_way_check.grid(row=0, column=0, padx=10, pady=5)

        two_way_check = ttk.Checkbutton(connection_window, text="Two-way", variable=two_way_var, command=on_two_way_checked)
        two_way_check.grid(row=0, column=1, padx=10, pady=5)

        def save_connection():
            direction = self.get_direction(start_x, start_y, end_x, end_y)
            if one_way_var.get():
                self.canvas.create_line(start_x, start_y, end_x, end_y, arrow=tk.LAST)
                self.map_data["rooms"][self.start_room[0]][self.start_room[1]]["egresses"].append({"direction": direction, "target": self.end_room})
                self.map_data["rooms"][self.end_room[0]][self.end_room[1]]["ingresses"].append({"direction": direction, "target": self.start_room})
            elif two_way_var.get():
                self.canvas.create_line(start_x, start_y, end_x, end_y, arrow=tk.BOTH)
                self.map_data["rooms"][self.start_room[0]][self.start_room[1]]["egresses"].append({"direction": direction, "target": self.end_room})
                self.map_data["rooms"][self.end_room[0]][self.end_room[1]]["ingresses"].append({"direction": direction, "target": self.start_room})
                self.map_data["rooms"][self.end_room[0]][self.end_room[1]]["egresses"].append({"direction": direction, "target": self.start_room})
                self.map_data["rooms"][self.start_room[0]][self.start_room[1]]["ingresses"].append({"direction": direction, "target": self.end_room})
            else:
                messagebox.showwarning("Invalid Input", "Please select a connection type.")
                return
            connection_window.destroy()

        save_button = ttk.Button(connection_window, text="Save", command=save_connection)
        save_button.grid(row=1, column=0, columnspan=2, pady=10)

    def get_direction(self, start_x, start_y, end_x, end_y):
        """
        Determine the direction of the connection based on the start and end coordinates.

        Parameters:
        start_x (int): The x-coordinate of the start point.
        start_y (int): The y-coordinate of the start point.
        end_x (int): The x-coordinate of the end point.
        end_y (int): The y-coordinate of the end point.

        Returns:
        str: The direction of the connection.
        """
        if start_x < end_x and start_y < end_y:
            return "SE"
        elif start_x < end_x and start_y > end_y:
            return "NE"
        elif start_x > end_x and start_y < end_y:
            return "SW"
        elif start_x > end_x and start_y > end_y:
            return "NW"
        elif start_x < end_x:
            return "E"
        elif start_x > end_x:
            return "W"
        elif start_y < end_y:
            return "S"
        elif start_y > end_y:
            return "N"
        return ""

if __name__ == "__main__":
    root = tk.Tk()
    app = RoomMapApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_stop)
    root.mainloop()