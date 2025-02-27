import sys
import os
import tkinter as tk
from tkinter import messagebox
import json
from pathlib import Path

class ShoutApp:
    # Default color schemes
    COLOR_SCHEMES = {
        "dark": {
            "bg": "#2E2E2E",
            "fg": "#FFFFFF",
            "button": "#444",
            "button_hover": "#777",
            "button_selected": "#00A8E8",
            "entry_bg": "#444",
            "entry_fg": "#FFFFFF",
            "checkbox_select": "#777",
            "text_area_bg": "#333",
            "text_area_fg": "#FFFFFF"
        },
        "light": {
            "bg": "#FFFFFF",
            "fg": "#000000",
            "button": "#DDDDDD",
            "button_hover": "#AAAAAA",
            "button_selected": "#0078D7",
            "entry_bg": "#DDDDDD",
            "entry_fg": "#000000",
            "checkbox_select": "#AAAAAA",
            "text_area_bg": "#F0F0F0",
            "text_area_fg": "#000000"
        }
    }
    
    # Predefined groups
    DEFAULT_GROUPS = [
        "BI Premium_Pipeline_Oncall", "BI_MyT_Mobile", "BI_SCBP_SRT-Oncall", "BI_WebPD",
        "Bond_DT", "Canada_DT", "Claim_DT", "DE_DT", "IAM_DT", "J2EE_DT", "PI_DT",
        "MDM_Legos", "BI-Control Room", "CorpTech_DT", "AIPP", "ED&A_GEO", "PAAS_DT", "UK_DT"
    ]
    
    # Special groups with different display names
    SPECIAL_GROUPS = {
        "PI-ProdServices": "PI-ProdServices.Distributed"
    }
    
    # Config file path
    CONFIG_FILE = Path.home() / ".shout_config.json"
    
    def __init__(self, root):
        self.root = root
        self.root.title("Shout!")
        
        # Set initial window size to match the preferred size
        self.root.geometry("1080x675")
        
        # Set minimum window size to ensure all elements remain visible
        self.root.minsize(1000, 650)
        
        # Initialize variables
        self.group_var = tk.StringVar()
        self.always_on_top_var = tk.BooleanVar()
        self.buttons = {}
        self.labels = []
        self.entries = []
        self.all_frames = []  # Track all frames for theme application
        
        # Load config or use defaults
        self.load_config()
        
        # Set up the UI
        self.setup_ui()
        
        # Apply theme - this needs to happen after UI is completely set up
        self.apply_theme()
        
        # Set up keyboard shortcuts
        self.setup_shortcuts()
        
    def load_config(self):
        """Load configuration from file or use defaults"""
        self.config = {
            "theme": "dark",
            "groups": self.DEFAULT_GROUPS.copy(),  # Create a copy to ensure we don't modify the original
            "always_on_top": False,
            "last_used_group": "",
        }
        
        # Add special groups to the config
        for display_name, full_name in self.SPECIAL_GROUPS.items():
            if full_name not in self.config["groups"]:
                self.config["groups"].append(full_name)
        
        # Try to load from config file
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    loaded_config = json.load(f)
                    
                    # Make sure we're not losing the default groups when loading config
                    if "groups" in loaded_config:
                        # Ensure all default groups and special groups are present
                        for group in self.DEFAULT_GROUPS:
                            if group not in loaded_config["groups"]:
                                loaded_config["groups"].append(group)
                        
                        for _, full_name in self.SPECIAL_GROUPS.items():
                            if full_name not in loaded_config["groups"]:
                                loaded_config["groups"].append(full_name)
                    
                    self.config.update(loaded_config)
            except (json.JSONDecodeError, IOError) as e:
                # Log the error but continue with defaults
                print(f"Error loading config: {e}")
        
        # Apply loaded config to variables
        self.always_on_top_var.set(self.config["always_on_top"])
        
    def save_config(self):
        """Save current configuration to file"""
        try:
            # Update config with current values
            self.config["theme"] = "light" if self.is_light_mode() else "dark"
            self.config["always_on_top"] = self.always_on_top_var.get()
            if self.group_var.get():
                self.config["last_used_group"] = self.group_var.get().replace("@", "")
            
            # Save to file
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(self.config, f)
        except IOError as e:
            messagebox.showwarning("Configuration Save Error", 
                                  f"Could not save configuration: {e}")
    
    def setup_ui(self):
        """Create all UI elements"""
        # Create main frames
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.all_frames.append(self.main_frame)
        
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        self.all_frames.append(self.left_frame)
        
        # Create a right frame that uses grid for better layout control
        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.all_frames.append(self.right_frame)
        
        # Configure the right frame's grid
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(2, weight=1)  # Make the output area expandable
        
        # Create group selection buttons
        self.create_group_buttons()
        
        # Create input fields (row 0)
        self.create_input_fields()
        
        # Create action buttons (row 1)
        self.create_action_buttons()
        
        # Create output area (row 2 - expandable)
        self.create_output_area()
        
        # Create footer controls (row 3 - fixed at bottom)
        self.create_footer_controls()
    
    def create_group_buttons(self):
        """Create buttons for each group"""
        # Group label
        group_label = tk.Label(self.left_frame, text="Select Group:")
        group_label.pack(anchor="w", pady=(0, 5))
        self.labels.append(group_label)
        
        # Create a simple frame for buttons instead of scrollable canvas
        button_frame = tk.Frame(self.left_frame)
        button_frame.pack(fill=tk.BOTH, expand=True)
        self.all_frames.append(button_frame)
        
        # Regular groups from the DEFAULT_GROUPS constant
        for group in self.DEFAULT_GROUPS:
            btn = tk.Button(button_frame, text=group, 
                           command=lambda g=group: self.set_group(g),
                           width=25, relief=tk.FLAT)
            btn.pack(pady=2, padx=1, fill=tk.X)
            self.buttons[group] = btn
        
        # Special groups with different display names
        for display_name, full_name in self.SPECIAL_GROUPS.items():
            btn = tk.Button(button_frame, text=display_name,
                           command=lambda g=full_name: self.set_group(g),
                           width=25, relief=tk.FLAT)
            btn.pack(pady=2, padx=1, fill=tk.X)
            self.buttons[full_name] = btn
            
        # Set last used group if available
        if self.config["last_used_group"]:
            if self.config["last_used_group"] in self.buttons:
                self.set_group(self.config["last_used_group"])
    
    def create_input_fields(self):
        """Create input fields for incident details"""
        fields = [
            ("INC Number:", "inc_entry"),
            ("Short Description:", "desc_entry"),
            ("Problem Ticket #:", "problem_entry"),
            ("Dynatrace URL:", "url_entry")
        ]
        
        # Create a container frame for all input fields
        input_container = tk.Frame(self.right_frame)
        input_container.grid(row=0, column=0, sticky="ew", pady=5)
        self.all_frames.append(input_container)
        
        for i, (label_text, attr_name) in enumerate(fields):
            frame = tk.Frame(input_container)
            frame.pack(fill=tk.X, pady=2)
            self.all_frames.append(frame)
            
            label = tk.Label(frame, text=label_text, width=20, anchor="w")
            label.pack(side=tk.LEFT)
            self.labels.append(label)
            
            entry = tk.Entry(frame, width=50)
            entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
            self.entries.append(entry)
            
            # Store reference as attribute
            setattr(self, attr_name, entry)
    
    def create_action_buttons(self):
        """Create buttons for generating message and copying"""
        # Create frame with explicit background color to fix white bar
        self.button_frame = tk.Frame(self.right_frame)
        self.button_frame.grid(row=1, column=0, sticky="ew", pady=5)
        self.all_frames.append(self.button_frame)
        
        self.generate_button = tk.Button(self.button_frame, text="Generate Message", 
                                        command=self.generate_message, 
                                        relief=tk.FLAT)
        self.generate_button.pack(side=tk.LEFT, padx=5)
        
        self.copy_button = tk.Button(self.button_frame, text="Copy to Clipboard", 
                                    command=self.copy_to_clipboard, 
                                    relief=tk.FLAT)
        self.copy_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = tk.Button(self.button_frame, text="Clear Fields", 
                                     command=self.clear_fields, 
                                     relief=tk.FLAT)
        self.clear_button.pack(side=tk.LEFT, padx=5)
    
    def create_output_area(self):
        """Create output text area"""
        self.output_frame = tk.Frame(self.right_frame)
        self.output_frame.grid(row=2, column=0, sticky="nsew", pady=5)
        self.all_frames.append(self.output_frame)
        
        self.output_label = tk.Label(self.output_frame, text="Generated Message:")
        self.output_label.pack(anchor="w")
        self.labels.append(self.output_label)
        
        self.output_text = tk.Text(self.output_frame, height=5, width=70)
        self.output_text.pack(fill=tk.BOTH, expand=True)
    
    def create_footer_controls(self):
        """Create footer controls like theme toggle and always on top"""
        # Create a dedicated frame for the footer with explicit styling that stays at the bottom
        self.footer_frame = tk.Frame(self.right_frame)
        self.footer_frame.grid(row=3, column=0, sticky="ew", pady=5)
        self.all_frames.append(self.footer_frame)
        
        # Always on top checkbox - explicitly styled
        self.always_on_top_checkbox = tk.Checkbutton(
            self.footer_frame, 
            text="Always on Top", 
            variable=self.always_on_top_var, 
            command=self.toggle_always_on_top
        )
        self.always_on_top_checkbox.pack(side=tk.LEFT, padx=5)
        
        # Create a fixed-width label for shortcuts with explicit styling
        # This replaces the previous status label implementation
        self.shortcuts_label = tk.Label(
            self.footer_frame,
            text="Shortcuts: Ctrl+G (Generate), Ctrl+C (Copy), Ctrl+L (Clear), F1 (Help)",
            anchor="w",
            padx=5
        )
        self.shortcuts_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.labels.append(self.shortcuts_label)
        
        # Theme toggle button - explicit styling
        self.theme_button = tk.Button(
            self.footer_frame, 
            text="Switch to Light Mode" if self.config["theme"] == "dark" else "Switch to Dark Mode",
            command=self.toggle_theme, 
            relief=tk.FLAT
        )
        self.theme_button.pack(side=tk.RIGHT, padx=5)
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.root.bind("<Control-g>", lambda e: self.generate_message())
        self.root.bind("<Control-c>", lambda e: self.copy_to_clipboard())
        self.root.bind("<Control-l>", lambda e: self.clear_fields())
        self.root.bind("<F1>", lambda e: self.show_help())
    
    def show_help(self):
        """Show help information"""
        help_text = """
Keyboard Shortcuts:
- Ctrl+G: Generate Message
- Ctrl+C: Copy to Clipboard
- Ctrl+L: Clear Fields
- F1: Show this Help

Usage:
1. Select a group from the left panel
2. Fill in all the required fields
3. Click 'Generate Message' or press Ctrl+G
4. Copy the message with 'Copy to Clipboard' or Ctrl+C
        """
        messagebox.showinfo("Shout Help", help_text)
    
    def set_group(self, group_name):
        """Set the selected group and update UI"""
        # Clear any previous selection
        for group, btn in self.buttons.items():
            btn.config(bg=self.get_current_colors()["button"],
                      fg=self.get_current_colors()["fg"])
        
        # Set the new group and highlight its button
        self.group_var.set(f"@{group_name}")
        self.buttons[group_name].config(
            bg=self.get_current_colors()["button_selected"],
            fg=self.get_current_colors()["fg"]
        )
    
    def generate_message(self):
        """Generate and display the formatted message"""
        # Get values from fields
        group = self.group_var.get()
        inc_number = self.inc_entry.get().strip()
        description = self.desc_entry.get().strip()
        problem_ticket = self.problem_entry.get().strip()
        url = self.url_entry.get().strip()
        
        # Validate inputs
        if not group or not inc_number or not description or not problem_ticket or not url:
            messagebox.showwarning("Missing Information", 
                                  "Please fill out all fields before generating the message.")
            
            # Highlight empty fields
            self.highlight_empty_fields()
            return
        
        # Format and display message
        output = f"{group} {inc_number} Problem {problem_ticket} {description}\n\n{url}"
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, output)
        
        # Auto-select the text for easy copying
        self.output_text.tag_add(tk.SEL, "1.0", tk.END)
        self.output_text.mark_set(tk.INSERT, "1.0")
        self.output_text.see(tk.INSERT)
        self.output_text.focus_set()
    
    def highlight_empty_fields(self):
        """Highlight empty fields with a red background temporarily"""
        fields = [
            (self.inc_entry, "inc_number"),
            (self.desc_entry, "description"),
            (self.problem_entry, "problem_ticket"),
            (self.url_entry, "url")
        ]
        
        for entry, field_name in fields:
            if not entry.get().strip():
                original_bg = entry.cget("bg")
                entry.config(bg="#FF9999")  # Light red background
                
                # Reset after 1.5 seconds
                self.root.after(1500, lambda e=entry, bg=original_bg: e.config(bg=bg))
    
    def copy_to_clipboard(self):
        """Copy the generated message to clipboard"""
        output_text = self.output_text.get("1.0", tk.END).strip()
        
        if not output_text:
            messagebox.showinfo("No Content", "Please generate a message first.")
            return
        
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(output_text)
            self.root.update()
            
            # Show temporary success message in the shortcuts label
            original_text = self.shortcuts_label.cget("text")
            self.shortcuts_label.config(text="✓ Message copied to clipboard!")
            self.root.after(2000, lambda: self.shortcuts_label.config(text=original_text))
            
        except Exception as e:
            messagebox.showerror("Clipboard Error", f"Could not copy to clipboard: {e}")
    
    def clear_fields(self):
        """Clear all input fields and output"""
        for entry in [self.inc_entry, self.desc_entry, self.problem_entry, self.url_entry]:
            entry.delete(0, tk.END)
        
        self.output_text.delete("1.0", tk.END)
        
        # Set focus to first field
        self.inc_entry.focus_set()
    
    def toggle_always_on_top(self):
        """Toggle the always-on-top window behavior"""
        self.root.attributes("-topmost", self.always_on_top_var.get())
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        if self.is_light_mode():
            self.theme_button.config(text="Switch to Light Mode")
            self.config["theme"] = "dark"
        else:
            self.theme_button.config(text="Switch to Dark Mode")
            self.config["theme"] = "light"
        
        self.apply_theme()
    
    def is_light_mode(self):
        """Check if the app is currently in light mode"""
        return self.root.cget("bg") == self.COLOR_SCHEMES["light"]["bg"]
    
    def get_current_colors(self):
        """Get the current color scheme based on theme"""
        theme = "light" if self.is_light_mode() else "dark"
        return self.COLOR_SCHEMES[theme]
    
    def apply_theme(self):
        """Apply the current theme to all widgets"""
        colors = self.COLOR_SCHEMES[self.config["theme"]]
        
        # First apply to root
        self.root.configure(bg=colors["bg"])
        
        # Apply to ALL frames (crucial for fixing the white bar)
        for frame in self.all_frames:
            frame.configure(bg=colors["bg"])
        
        # Update all labels
        for label in self.labels:
            label.configure(bg=colors["bg"], fg=colors["fg"])
        
        # Update group buttons
        for group, btn in self.buttons.items():
            if self.group_var.get() == f"@{group}":
                btn.configure(bg=colors["button_selected"], fg=colors["fg"])
            else:
                btn.configure(bg=colors["button"], fg=colors["fg"], 
                             activebackground=colors["button_hover"])
        
        # Update action buttons
        for btn in [self.generate_button, self.copy_button, self.clear_button, self.theme_button]:
            btn.configure(bg=colors["button"], fg=colors["fg"], 
                         activebackground=colors["button_hover"])
        
        # Update entry fields
        for entry in self.entries:
            entry.configure(bg=colors["entry_bg"], fg=colors["entry_fg"])
        
        # Update text area
        self.output_text.configure(
            bg=colors["text_area_bg"], 
            fg=colors["text_area_fg"],
            insertbackground=colors["fg"]
        )
        
        # Update checkbox - specifically fix its background
        self.always_on_top_checkbox.configure(
            bg=colors["bg"], 
            fg=colors["fg"],
            selectcolor=colors["checkbox_select"],
            activebackground=colors["bg"],
            highlightbackground=colors["bg"]
        )
        
        # Ensure the shortcuts label has the correct styling
        self.shortcuts_label.configure(
            bg=colors["bg"],
            fg=colors["fg"]
        )
    
    def on_closing(self):
        """Handle application closing"""
        self.save_config()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = ShoutApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()