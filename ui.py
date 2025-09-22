import tkinter as tk
import json
import os
import time
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class OrderDisplayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Customer Order Display")
        self.root.geometry("800x600")
        self.root.configure(bg="#000000")  # Black background
        
        # Set to fullscreen for actual deployment
        # self.root.attributes('-fullscreen', True)
        
        # Create main frames
        self.create_widgets()
        
        # Set up the file watcher to monitor orders directory
        self.setup_order_watcher()
        
        # Current order being displayed
        self.current_order_id = None
        self.current_items = []
        
        # Check for new orders periodically
        self.check_for_new_orders()
    
    def create_widgets(self):
        # Header frame
        self.header_frame = tk.Frame(self.root, bg="#222222", height=80)
        self.header_frame.pack(fill=tk.X)
        
        # Restaurant logo and name
        self.logo_label = tk.Label(self.header_frame, text="FAST FOOD", font=("Arial", 28, "bold"), 
                                 fg="#FFD700", bg="#222222")  # Gold text on dark background
        self.logo_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Current time
        self.time_label = tk.Label(self.header_frame, font=("Arial", 18), fg="white", bg="#222222")
        self.time_label.pack(side=tk.RIGHT, padx=20, pady=15)
        self.update_time()
        
        # Order content frame
        self.content_frame = tk.Frame(self.root, bg="#000000")
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Order details - left side
        self.order_frame = tk.Frame(self.content_frame, bg="#000000")
        self.order_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.order_title = tk.Label(self.order_frame, text="YOUR ORDER", font=("Arial", 24, "bold"), 
                                  fg="#FFD700", bg="#000000")
        self.order_title.pack(pady=15)
        
        # Scrollable order items frame
        self.order_canvas = tk.Canvas(self.order_frame, bg="#000000", highlightthickness=0)
        self.order_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar for order items
        self.scrollbar = tk.Scrollbar(self.order_frame, orient=tk.VERTICAL, command=self.order_canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.order_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Frame inside canvas for order items
        self.items_frame = tk.Frame(self.order_canvas, bg="#000000")
        self.order_canvas.create_window((0, 0), window=self.items_frame, anchor=tk.NW)
        self.items_frame.bind("<Configure>", lambda e: self.order_canvas.configure(scrollregion=self.order_canvas.bbox("all")))
        
        # Order summary - right side
        self.summary_frame = tk.Frame(self.content_frame, bg="#333333", width=300)
        self.summary_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5)
        
        # Order summary title
        tk.Label(self.summary_frame, text="ORDER SUMMARY", font=("Arial", 20, "bold"), 
                fg="#FFD700", bg="#333333").pack(pady=15)
        
        # Order number
        self.order_number_frame = tk.Frame(self.summary_frame, bg="#333333")
        self.order_number_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(self.order_number_frame, text="Order #:", font=("Arial", 16), 
                fg="white", bg="#333333").pack(side=tk.LEFT, padx=20)
        
        self.order_number_label = tk.Label(self.order_number_frame, text="----", font=("Arial", 16, "bold"), 
                                        fg="white", bg="#333333")
        self.order_number_label.pack(side=tk.LEFT)
        
        # Subtotal
        self.subtotal_frame = tk.Frame(self.summary_frame, bg="#333333")
        self.subtotal_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(self.subtotal_frame, text="Subtotal:", font=("Arial", 16), 
                fg="white", bg="#333333").pack(side=tk.LEFT, padx=20)
        
        self.subtotal_label = tk.Label(self.subtotal_frame, text="$0.00", font=("Arial", 16), 
                                     fg="white", bg="#333333")
        self.subtotal_label.pack(side=tk.RIGHT, padx=20)
        
        # Tax
        self.tax_frame = tk.Frame(self.summary_frame, bg="#333333")
        self.tax_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(self.tax_frame, text="Tax:", font=("Arial", 16), 
                fg="white", bg="#333333").pack(side=tk.LEFT, padx=20)
        
        self.tax_label = tk.Label(self.tax_frame, text="$0.00", font=("Arial", 16), 
                                fg="white", bg="#333333")
        self.tax_label.pack(side=tk.RIGHT, padx=20)
        
        # Separator
        self.separator = tk.Frame(self.summary_frame, bg="white", height=2)
        self.separator.pack(fill=tk.X, padx=20, pady=10)
        
        # Total
        self.total_frame = tk.Frame(self.summary_frame, bg="#333333")
        self.total_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(self.total_frame, text="TOTAL:", font=("Arial", 20, "bold"), 
                fg="#FFD700", bg="#333333").pack(side=tk.LEFT, padx=20)
        
        self.total_label = tk.Label(self.total_frame, text="$0.00", font=("Arial", 20, "bold"), 
                                  fg="#FFD700", bg="#333333")
        self.total_label.pack(side=tk.RIGHT, padx=20)
        
        # Payment method
        self.payment_frame = tk.Frame(self.summary_frame, bg="#333333")
        self.payment_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(self.payment_frame, text="Payment:", font=("Arial", 16), 
                fg="white", bg="#333333").pack(side=tk.LEFT, padx=20)
        
        self.payment_label = tk.Label(self.payment_frame, text="----", font=("Arial", 16), 
                                    fg="white", bg="#333333")
        self.payment_label.pack(side=tk.RIGHT, padx=20)
        
        # Promotional message at the bottom
        self.promo_frame = tk.Frame(self.root, bg="#222222", height=60)
        self.promo_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.promo_label = tk.Label(self.promo_frame, 
                                  text="Thank you for choosing us! Please drive to the next window.", 
                                  font=("Arial", 14), fg="white", bg="#222222")
        self.promo_label.pack(pady=15)
    
    def update_time(self):
        current_time = datetime.now().strftime("%I:%M:%S %p")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
    
    def clear_items_frame(self):
        for widget in self.items_frame.winfo_children():
            widget.destroy()
    
    def display_order(self, order_data):
        # Clear previous items
        self.clear_items_frame()
        
        # Update order number
        self.order_number_label.config(text=str(order_data.get("order_id", "--")))
        
        # Update order items
        for i, item in enumerate(order_data.get("items", [])):
            # Item frame
            item_frame = tk.Frame(self.items_frame, bg="#111111", padx=10, pady=10)
            item_frame.pack(fill=tk.X, pady=5)
            
            # Item name and price
            header_frame = tk.Frame(item_frame, bg="#111111")
            header_frame.pack(fill=tk.X)
            
            tk.Label(header_frame, text=item.get("item", ""), font=("Arial", 14, "bold"), 
                    fg="white", bg="#111111", anchor="w").pack(side=tk.LEFT)
            
            tk.Label(header_frame, text=f"${item.get('total', 0):.2f}", font=("Arial", 14), 
                    fg="#FFD700", bg="#111111").pack(side=tk.RIGHT)
            
            # Customizations if any
            customizations = item.get("customizations", {})
            for section, selections in customizations.items():
                if isinstance(selections, list) and selections:  # Multiple selections
                    custom_text = f"{section}: {', '.join(selections)}"
                    tk.Label(item_frame, text=custom_text, font=("Arial", 12), fg="#BBBBBB", 
                           bg="#111111", anchor="w").pack(fill=tk.X, pady=2)
                elif isinstance(selections, str) and selections != self.get_default_option(section, item.get("category", "")):
                    custom_text = f"{section}: {selections}"
                    tk.Label(item_frame, text=custom_text, font=("Arial", 12), fg="#BBBBBB", 
                           bg="#111111", anchor="w").pack(fill=tk.X, pady=2)
        
        # Update summary
        self.subtotal_label.config(text=f"${order_data.get('subtotal', 0):.2f}")
        self.tax_label.config(text=f"${order_data.get('tax', 0):.2f}")
        self.total_label.config(text=f"${order_data.get('total', 0):.2f}")
        self.payment_label.config(text=order_data.get('payment_method', '----'))
        
        # Force update of items_frame size
        self.items_frame.update_idletasks()
        self.order_canvas.configure(scrollregion=self.order_canvas.bbox("all"))
    
    def get_default_option(self, section, category):
        # This would need to match the default options in your menu system
        default_options = {
            "Size": "Regular",
            "Ice": "Regular Ice",
            "Extras": "No Extras",
            "Seasoning": "Regular Salt",
            "Dips": "No Dip",
            "Sauce": "No Sauce",
            "Cheese": "No Cheese",
            "Protein": "Beef Patty"
        }
        return default_options.get(section, "")
    
    def setup_order_watcher(self):
        # Create orders directory if it doesn't exist
        if not os.path.exists("temp"):
            os.makedirs("temp")
        
        # Set up watchdog handler
        class OrderHandler(FileSystemEventHandler):
            def __init__(self, app):
                self.app = app
            
            def on_created(self, event):
                if event.is_directory:
                    return
                if event.src_path.endswith(".json"):
                    self.app.process_order_file(event.src_path)
            
            def on_modified(self, event):
                if event.is_directory:
                    return
                if event.src_path.endswith(".json"):
                    self.app.process_order_file(event.src_path)
        
        # Set up watchdog observer
        self.event_handler = OrderHandler(self)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, path="temp", recursive=False)
        self.observer.start()
    
    def process_order_file(self, filepath):
        try:
            with open(filepath, 'r') as f:
                order_data = json.load(f)
                self.display_order(order_data)
                self.current_order_id = order_data.get("order_id")
        except Exception as e:
            print(f"Error processing order file: {e}")
    
    def check_for_new_orders(self):
        # Check for the most recent order file
        try:
            order_files = [f for f in os.listdir("temp") if f.startswith("order_") and f.endswith(".json")]
            if order_files:
                # Sort by order ID
                order_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
                latest_order = order_files[-1]
                
                # If this is a new order, process it
                order_id = int(latest_order.split('_')[1].split('.')[0])
                if self.current_order_id is None or order_id > self.current_order_id:
                    self.process_order_file(os.path.join("temp", latest_order))
        except Exception as e:
            print(f"Error checking for new orders: {e}")
        
        # Check again after 500ms
        self.root.after(500, self.check_for_new_orders)
    
    def on_closing(self):
        self.observer.stop()
        self.observer.join()
        self.root.destroy()

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = OrderDisplayApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()