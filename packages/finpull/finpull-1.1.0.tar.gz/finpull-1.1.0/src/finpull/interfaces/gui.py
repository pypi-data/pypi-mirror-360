"""
Tkinter GUI interface for the financial data scraper
"""

import logging
from typing import Optional

from finpull_core import FinancialDataScraper
from finpull_core.utils.compatibility import HAS_TKINTER
# Check if we have openpyxl (full package feature)
try:
    import openpyxl
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

if HAS_TKINTER:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog

logger = logging.getLogger(__name__)


class FinancialDataGUI:
    """Tkinter GUI for the financial data scraper"""
    
    def __init__(self):
        if not HAS_TKINTER:
            raise ImportError("tkinter is required for GUI functionality")
        
        self.scraper = FinancialDataScraper()
        self.root: Optional[tk.Tk] = None
        self.tree: Optional[ttk.Treeview] = None
        self.ticker_var: Optional[tk.StringVar] = None
        self.status_var: Optional[tk.StringVar] = None
        
        self.setup_gui()
    
    def setup_gui(self):
        """Setup the GUI"""
        self.root = tk.Tk()
        self.root.title("FinPull - Financial Data Scraper")
        self.root.geometry("1400x800")
        self.root.minsize(1000, 600)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Setup menu
        self.setup_menu()
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        
        # Input section
        self.setup_input_section(main_frame)
        
        # Data display
        self.setup_data_display(main_frame)
        
        # Status bar
        self.setup_status_bar(main_frame)
        
        # Load existing data
        self.refresh_display()
        
        # Set up window close handling
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_menu(self):
        """Setup application menu"""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Export JSON", command=lambda: self.export_data("json"))
        file_menu.add_command(label="Export CSV", command=lambda: self.export_data("csv"))
        if HAS_OPENPYXL:
            file_menu.add_command(label="Export Excel", command=lambda: self.export_data("xlsx"))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Refresh All", command=self.refresh_all_data)
        edit_menu.add_command(label="Clear All", command=self.clear_all_data)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cleanup Stale Data", command=self.cleanup_stale_data)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Statistics", command=self.show_statistics)
        tools_menu.add_command(label="Dependencies", command=self.show_dependencies)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def setup_input_section(self, parent):
        """Setup input section"""
        input_frame = ttk.LabelFrame(parent, text="Add Ticker", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        parent.columnconfigure(0, weight=1)
        
        # Input controls
        controls_frame = ttk.Frame(input_frame)
        controls_frame.pack(fill="x")
        
        ttk.Label(controls_frame, text="Ticker Symbol(s):").pack(side="left", padx=(0, 5))
        
        self.ticker_var = tk.StringVar()
        ticker_entry = ttk.Entry(controls_frame, textvariable=self.ticker_var, width=20)
        ticker_entry.pack(side="left", padx=(0, 10))
        ticker_entry.bind("<Return>", lambda e: self.add_ticker())
        ticker_entry.focus()
        
        ttk.Button(controls_frame, text="Add", command=self.add_ticker).pack(side="left", padx=(0, 5))
        ttk.Button(controls_frame, text="Refresh All", command=self.refresh_all_data).pack(side="left", padx=(0, 5))
        
        # Add Remove Selected button
        self.remove_button = ttk.Button(controls_frame, text="Remove Selected", command=self.remove_selected_multiple, state='disabled')
        self.remove_button.pack(side="left", padx=(0, 5))
        
        # Quick add buttons for common tickers
        quick_frame = ttk.Frame(input_frame)
        quick_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Label(quick_frame, text="Quick add:").pack(side="left", padx=(0, 5))
        
        common_tickers = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA"]
        for ticker in common_tickers:
            btn = ttk.Button(quick_frame, text=ticker, width=6,
                           command=lambda t=ticker: self.quick_add_ticker(t))
            btn.pack(side="left", padx=2)
    
    def setup_data_display(self, parent):
        """Setup data display table"""
        # Configure grid weights
        parent.rowconfigure(1, weight=1)
        parent.columnconfigure(0, weight=1)
        
        # Create treeview with scrollbars
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        
        # Columns for display
        columns = [
            "ticker", "company_name", "sector", "price", "change_5y",
            "dividend_yield", "dividend_ttm", "eps_ttm", "eps_next_year", "eps_next_5y",
            "revenue", "revenue_growth_5y", "operating_margin", "profit_margin",
            "roa", "roe", "roi", "pe_ratio", "ps_ratio", "pb_ratio",
            "total_assets", "total_liabilities", "market_cap", "volume", "avg_volume",
            "beta", "timestamp"
        ]
        
        # Enable multiple selection
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20, selectmode="extended")
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        # Setup scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Configure columns
        column_config = {
            "ticker": ("Ticker", 80),
            "company_name": ("Company", 200),
            "sector": ("Sector", 120),
            "price": ("Price", 80),
            "change_5y": ("5Y Change", 80),
            "dividend_yield": ("Div Yield", 80),
            "dividend_ttm": ("Div Yield (TTM)", 80),
            "eps_ttm": ("EPS", 80),
            "eps_next_year": ("EPS Next Year", 80),
            "eps_next_5y": ("EPS Next 5Y", 80),
            "revenue": ("Revenue", 100),
            "revenue_growth_5y": ("Revenue Growth 5Y", 100),
            "operating_margin": ("Operating Margin", 80),
            "profit_margin": ("Profit Margin", 80),
            "roa": ("ROA", 60),
            "roe": ("ROE", 60),
            "roi": ("ROI", 60),
            "pe_ratio": ("P/E", 60),
            "ps_ratio": ("P/S", 60),
            "pb_ratio": ("P/B", 60),
            "total_assets": ("Total Assets", 100),
            "total_liabilities": ("Total Liabilities", 100),
            "market_cap": ("Market Cap", 100),
            "volume": ("Volume", 100),
            "avg_volume": ("Avg Volume", 100),
            "beta": ("Beta", 60),
            "timestamp": ("Updated", 120)
        }
        
        for col in columns:
            name, width = column_config.get(col, (col, 100))
            self.tree.heading(col, text=name, command=lambda c=col: self.sort_treeview(c))
            self.tree.column(col, width=width, minwidth=50)
        
        # Make ticker column fixed (non-scrollable)
        self.tree.column("ticker", anchor="w", stretch=False)
        
        # Initialize sorting state
        self.sort_column = None
        self.sort_reverse = False
        
        # Bind events
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<<TreeviewSelect>>", self.on_selection_changed)
    
    def setup_status_bar(self, parent):
        """Setup status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        status_label = ttk.Label(status_frame, textvariable=self.status_var, relief="sunken", anchor="w")
        status_label.pack(side="left", fill="x", expand=True)
        
        # Add ticker count
        self.ticker_count_var = tk.StringVar()
        ticker_count_label = ttk.Label(status_frame, textvariable=self.ticker_count_var, relief="sunken")
        ticker_count_label.pack(side="right", padx=(5, 0))
        
        self.update_ticker_count()
    
    def show_context_menu(self, event):
        """Show context menu on right-click"""
        selection = self.tree.selection()
        if not selection:
            return
        
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Refresh", command=self.refresh_selected)
        context_menu.add_command(label="Remove", command=self.remove_selected_multiple)
        context_menu.add_separator()
        context_menu.add_command(label="View Details", command=self.view_details)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def on_double_click(self, event):
        """Handle double-click on tree item"""
        self.view_details()
    
    def on_selection_changed(self, event):
        """Handle selection changes in the tree"""
        selection = self.tree.selection()
        if selection:
            self.remove_button.config(state='normal')
        else:
            self.remove_button.config(state='disabled')
    
    def add_ticker(self):
        """Add new ticker(s)"""
        ticker_input = self.ticker_var.get().strip()
        if not ticker_input:
            messagebox.showwarning("Warning", "Please enter one or more ticker symbols")
            return
        
        # Split by spaces or commas to support multiple tickers
        tickers = [t.strip().upper() for t in ticker_input.replace(',', ' ').split() if t.strip()]
        
        if not tickers:
            messagebox.showwarning("Warning", "Please enter valid ticker symbols")
            return
        
        # Validate all tickers first
        invalid_tickers = []
        for ticker in tickers:
            if not self.scraper.validate_ticker(ticker):
                invalid_tickers.append(ticker)
        
        if invalid_tickers:
            messagebox.showwarning("Warning", f"Invalid ticker symbols: {', '.join(invalid_tickers)}")
            return
        
        # Add tickers
        added = []
        already_exists = []
        failed = []
        
        for ticker in tickers:
            self.set_status(f"Adding {ticker}...")
            self.root.update()
            
            # Add temporary entry with loading indicator in ticker column
            temp_values = [f"🔄 {ticker}"] + ["Loading..."] + [""] * 25  # 1 ticker + 1 loading + 25 empty fields
            temp_item = self.tree.insert("", "end", values=temp_values)
            self.root.update()
            
            try:
                if self.scraper.add_ticker(ticker):
                    added.append(ticker)
                    # Remove temporary entry
                    self.tree.delete(temp_item)
                else:
                    already_exists.append(ticker)
                    # Remove temporary entry
                    self.tree.delete(temp_item)
            except Exception as e:
                failed.append(f"{ticker}: {str(e)}")
                # Remove temporary entry
                self.tree.delete(temp_item)
        
        # Clear input
        self.ticker_var.set("")
        
        # Refresh display
        self.refresh_display()
        
        # Show results
        messages = []
        if added:
            messages.append(f"Added: {', '.join(added)}")
            self.set_status(f"Added {', '.join(added)}")
        if already_exists:
            messages.append(f"Already exists: {', '.join(already_exists)}")
        if failed:
            messages.append(f"Failed: {'; '.join(failed)}")
            
        if messages:
            if failed:
                messagebox.showwarning("Results", '\n'.join(messages))
            else:
                messagebox.showinfo("Success", '\n'.join(messages))
    
    def quick_add_ticker(self, ticker: str):
        """Quick add a ticker using button"""
        self.ticker_var.set(ticker)
        self.add_ticker()
    
    def refresh_selected(self):
        """Refresh selected ticker"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        ticker = item['values'][0]
        
        # Show loading indicator
        self.update_ticker_status(ticker, "🔄 Loading...")
        self.set_status(f"Refreshing {ticker}...")
        self.root.update()
        
        try:
            self.scraper.refresh_data(ticker)
            self.update_ticker_status(ticker, "✅ Done")
            self.root.after(2000, lambda: self.update_ticker_status(ticker, ""))  # Clear after 2 seconds
            self.refresh_display()
            self.set_status(f"Refreshed {ticker}")
            messagebox.showinfo("Success", f"Refreshed {ticker}")
        except Exception as e:
            self.update_ticker_status(ticker, "❌ Error")
            self.root.after(2000, lambda: self.update_ticker_status(ticker, ""))  # Clear after 2 seconds
            self.set_status(f"Error refreshing {ticker}")
            messagebox.showerror("Error", f"Failed to refresh {ticker}: {str(e)}")
    
    def update_ticker_status(self, ticker: str, status: str):
        """Update the ticker column to show loading/completion status"""
        for item in self.tree.get_children():
            item_data = self.tree.item(item)
            values = list(item_data['values'])
            if values[0].replace('🔄 ', '').replace('✅ ', '').replace('❌ ', '') == ticker:
                # Update the ticker column (first column) with status symbol
                if status == "🔄 Loading...":
                    values[0] = f"🔄 {ticker}"
                elif status == "✅ Done":
                    values[0] = f"✅ {ticker}"
                elif status == "❌ Error":
                    values[0] = f"❌ {ticker}"
                else:
                    # Clear status - show just ticker
                    values[0] = ticker
                
                self.tree.item(item, values=values)
                break
    
    def remove_selected(self):
        """Remove selected ticker"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        ticker = item['values'][0]
        
        if messagebox.askyesno("Confirm", f"Remove {ticker} from tracking?"):
            self.scraper.remove_ticker(ticker)
            self.refresh_display()
            self.set_status(f"Removed {ticker}")
    
    def remove_selected_multiple(self):
        """Remove multiple selected tickers"""
        selection = self.tree.selection()
        if not selection:
            return
        
        # Get all selected tickers
        tickers = []
        for item_id in selection:
            item = self.tree.item(item_id)
            tickers.append(item['values'][0])
        
        if len(tickers) == 1:
            message = f"Remove {tickers[0]} from tracking?"
        else:
            message = f"Remove {len(tickers)} tickers from tracking?\n\n{', '.join(tickers)}"
        
        if messagebox.askyesno("Confirm", message):
            removed = []
            failed = []
            
            for ticker in tickers:
                try:
                    self.scraper.remove_ticker(ticker)
                    removed.append(ticker)
                except Exception as e:
                    failed.append(f"{ticker}: {str(e)}")
            
            self.refresh_display()
            
            if removed:
                self.set_status(f"Removed {', '.join(removed)}")
            
            if failed:
                messagebox.showerror("Error", f"Failed to remove:\n{chr(10).join(failed)}")
    
    def view_details(self):
        """View details for selected ticker"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        ticker = item['values'][0]
        
        data = self.scraper.get_ticker_data(ticker)
        if not data:
            messagebox.showerror("Error", f"No data found for {ticker}")
            return
        
        # Create details window
        details_window = tk.Toplevel(self.root)
        details_window.title(f"{ticker} - Details")
        details_window.geometry("600x500")
        details_window.transient(self.root)
        details_window.grab_set()
        
        # Create scrollable text widget
        text_frame = ttk.Frame(details_window)
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap="word", font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Format and display data
        details_text = f"=== {data.ticker} - {data.company_name} ===\n\n"
        
        data_dict = data.to_dict()
        for key, value in data_dict.items():
            formatted_key = key.replace('_', ' ').title()
            details_text += f"{formatted_key:<20}: {value}\n"
        
        text_widget.insert("1.0", details_text)
        text_widget.config(state="disabled")
        
        # Close button
        ttk.Button(details_window, text="Close", 
                  command=details_window.destroy).pack(pady=10)
    
    def refresh_all_data(self):
        """Refresh all ticker data asynchronously"""
        import threading
        
        ticker_list = self.scraper.get_ticker_list()
        if len(ticker_list) == 0:
            messagebox.showinfo("Info", "No tickers to refresh")
            return
        
        # Show loading indicators for all tickers
        for ticker in ticker_list:
            self.update_ticker_status(ticker, "🔄 Loading...")
        
        def refresh_worker():
            try:
                # Refresh each ticker individually to show progress
                for ticker in ticker_list:
                    try:
                        self.scraper.refresh_data(ticker)
                        # Update UI in main thread
                        self.root.after(0, lambda t=ticker: self.update_ticker_status(t, "✅ Done"))
                    except Exception as e:
                        # Update UI in main thread
                        self.root.after(0, lambda t=ticker: self.update_ticker_status(t, "❌ Error"))
                
                # Update UI in main thread
                self.root.after(0, lambda: self._refresh_complete(len(ticker_list)))
            except Exception as e:
                # Handle error in main thread
                self.root.after(0, lambda: self._refresh_error(str(e)))
        
        # Disable refresh button and show status
        self._disable_refresh_button()
        self.set_status(f"Refreshing {len(ticker_list)} tickers...")
        
        # Start refresh in background thread
        thread = threading.Thread(target=refresh_worker, daemon=True)
        thread.start()
    
    def _refresh_complete(self, ticker_count):
        """Handle successful refresh completion"""
        self.refresh_display()
        self.set_status("Refreshed all data")
        self._enable_refresh_button()
        
        # Clear all status indicators after 2 seconds
        self.root.after(2000, self._clear_all_status)
        
        messagebox.showinfo("Success", f"Refreshed all {ticker_count} tickers")
    
    def _clear_all_status(self):
        """Clear all status indicators from ticker column"""
        for item in self.tree.get_children():
            item_data = self.tree.item(item)
            values = list(item_data['values'])
            # Remove status symbols from ticker column
            ticker = values[0].replace('🔄 ', '').replace('✅ ', '').replace('❌ ', '')
            values[0] = ticker
            self.tree.item(item, values=values)
    
    def _refresh_error(self, error_msg):
        """Handle refresh error"""
        self.set_status("Error refreshing data")
        self._enable_refresh_button()
        
        # Clear loading indicators and show error for items that were loading
        for item in self.tree.get_children():
            item_data = self.tree.item(item)
            values = list(item_data['values'])
            if values[0].startswith("🔄 "):  # Only update if it was loading
                ticker = values[0].replace('🔄 ', '')
                values[0] = f"❌ {ticker}"
                self.tree.item(item, values=values)
        
        # Clear error indicators after 2 seconds
        self.root.after(2000, self._clear_all_status)
        
        messagebox.showerror("Error", f"Failed to refresh data: {error_msg}")
    
    def _disable_refresh_button(self):
        """Disable refresh button during refresh"""
        # Find and disable the refresh button in the input section
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.LabelFrame) and child.cget('text') == "Add Ticker":
                        for frame in child.winfo_children():
                            if isinstance(frame, ttk.Frame):
                                for btn in frame.winfo_children():
                                    if isinstance(btn, ttk.Button) and btn.cget('text') == "Refresh All":
                                        btn.config(state='disabled', text='Refreshing...')
                                        return
    
    def _enable_refresh_button(self):
        """Enable refresh button after refresh"""
        # Find and enable the refresh button in the input section
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.LabelFrame) and child.cget('text') == "Add Ticker":
                        for frame in child.winfo_children():
                            if isinstance(frame, ttk.Frame):
                                for btn in frame.winfo_children():
                                    if isinstance(btn, ttk.Button) and btn.cget('text') in ['Refreshing...', 'Refresh All']:
                                        btn.config(state='normal', text='Refresh All')
                                        return
    
    def clear_all_data(self):
        """Clear all data"""
        ticker_count = len(self.scraper.get_ticker_list())
        if ticker_count == 0:
            messagebox.showinfo("Info", "No data to clear")
            return
        
        if messagebox.askyesno("Confirm", f"Clear all {ticker_count} tickers and cached data?"):
            self.scraper.clear_all()
            self.refresh_display()
            self.set_status("Cleared all data")
    
    def cleanup_stale_data(self):
        """Clean up stale data"""
        try:
            removed_count = self.scraper.cleanup_stale_data()
            if removed_count > 0:
                self.refresh_display()
                messagebox.showinfo("Success", f"Cleaned up {removed_count} stale records")
            else:
                messagebox.showinfo("Info", "No stale data found")
        except Exception as e:
            messagebox.showerror("Error", f"Cleanup failed: {str(e)}")
    
    def refresh_display(self):
        """Refresh the data display"""
        # Clear existing items
        if self.tree:
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Add current data
            for data in self.scraper.get_all_data():
                # Format timestamp for display
                timestamp_display = "N/A"
                if data.timestamp:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(data.timestamp.replace('Z', '+00:00'))
                        timestamp_display = dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        timestamp_display = data.timestamp[:16] if len(data.timestamp) >= 16 else data.timestamp
                
                values = [
                    data.ticker,
                    data.company_name,
                    data.sector,
                    data.price,
                    data.change_5y,
                    data.dividend_yield,
                    data.dividend_ttm,
                    data.eps_ttm,
                    data.eps_next_year,
                    data.eps_next_5y,
                    data.revenue,
                    data.revenue_growth_5y,
                    data.operating_margin,
                    data.profit_margin,
                    data.roa,
                    data.roe,
                    data.roi,
                    data.pe_ratio,
                    data.ps_ratio,
                    data.pb_ratio,
                    data.total_assets,
                    data.total_liabilities,
                    data.market_cap,
                    data.volume,
                    data.avg_volume,
                    data.beta,
                    timestamp_display
                ]
                self.tree.insert("", "end", values=values)
        
        self.update_ticker_count()
    
    def export_data(self, format_type: str):
        """Export data to file"""
        data_count = len(self.scraper.get_all_data())
        if data_count == 0:
            messagebox.showinfo("Info", "No data to export")
            return
        
        try:
            # Always use file dialog for all formats
            format_extensions = {
                "json": "*.json",
                "csv": "*.csv", 
                "xlsx": "*.xlsx"
            }
            
            format_names = {
                "json": "JSON files",
                "csv": "CSV files",
                "xlsx": "Excel files"
            }
            
            filetypes = [(format_names[format_type], format_extensions[format_type])]
            filename = filedialog.asksaveasfilename(
                title=f"Export as {format_type.upper()}",
                defaultextension=f".{format_type}",
                filetypes=filetypes + [("All files", "*.*")]
            )
            
            if filename:
                self.set_status(f"Exporting to {format_type.upper()}...")
                self.root.update()
                result_filename = self.scraper.export_data(format_type, filename)
                self.set_status(f"Exported to {result_filename}")
                messagebox.showinfo("Success", f"Exported {data_count} records to {result_filename}")
        except Exception as e:
            self.set_status("Export failed")
            messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def show_statistics(self):
        """Show scraper statistics"""
        stats = self.scraper.get_stats()
        
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Statistics")
        stats_window.geometry("500x400")
        stats_window.transient(self.root)
        stats_window.grab_set()
        
        text_widget = tk.Text(stats_window, wrap="word", font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(stats_window, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        stats_text = "=== FinPull Statistics ===\n\n"
        stats_text += f"Total tickers: {stats['total_tickers']}\n"
        stats_text += f"Cached tickers: {stats['cached_tickers']}\n"
        stats_text += f"Missing cache: {stats['missing_cache']}\n"
        stats_text += f"Stale data: {stats['stale_data']}\n"
        stats_text += f"Storage file: {stats['storage_file']}\n"
        stats_text += f"File size: {stats['file_size']} bytes\n\n"
        
        stats_text += "Data sources:\n"
        for i, source in enumerate(stats['data_sources'], 1):
            stats_text += f"  {i}. {source}\n"
        
        text_widget.insert("1.0", stats_text)
        text_widget.config(state="disabled")
        
        ttk.Button(stats_window, text="Close", 
                  command=stats_window.destroy).pack(pady=10)
    
    def show_dependencies(self):
        """Show dependency status"""
        from finpull_core.utils.compatibility import get_missing_dependencies, get_available_features
        
        deps_window = tk.Toplevel(self.root)
        deps_window.title("Dependencies")
        deps_window.geometry("400x300")
        deps_window.transient(self.root)
        deps_window.grab_set()
        
        text_widget = tk.Text(deps_window, wrap="word", font=("Consolas", 10))
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        
        features = get_available_features()
        missing = get_missing_dependencies()
        
        deps_text = "=== Dependency Status ===\n\n"
        
        for feature, available in features.items():
            status = "✓" if available else "✗"
            deps_text += f"{status} {feature.replace('_', ' ').title()}\n"
        
        if missing:
            deps_text += f"\nMissing dependencies:\n"
            for dep in missing:
                deps_text += f"  - {dep}\n"
            deps_text += f"\nInstall with: pip install {' '.join(missing)}\n"
        else:
            deps_text += "\n✓ All dependencies available!"
        
        text_widget.insert("1.0", deps_text)
        text_widget.config(state="disabled")
        
        ttk.Button(deps_window, text="Close", 
                  command=deps_window.destroy).pack(pady=10)
    
    def show_about(self):
        """Show about dialog"""
        from .. import __version__
        about_text = f"""FinPull v{__version__}
        
Comprehensive Financial Data Scraper

Features:
• Multiple data sources with fallback
• Export to JSON, CSV, and Excel
• Real-time data refresh
• Cross-platform compatibility
• Async GUI operations

Built with Python and Tkinter
        """
        messagebox.showinfo("About FinPull", about_text)
    
    def set_status(self, message: str):
        """Set status bar message"""
        if self.status_var:
            self.status_var.set(message)
            self.root.update_idletasks()
    
    def update_ticker_count(self):
        """Update ticker count in status bar"""
        if self.ticker_count_var:
            count = len(self.scraper.get_ticker_list())
            self.ticker_count_var.set(f"Tickers: {count}")
    
    def on_closing(self):
        """Handle window closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit FinPull?"):
            self.root.destroy()
    
    def run(self):
        """Run the GUI application"""
        if self.root:
            self.root.mainloop()

    def sort_treeview(self, column):
        """Sort treeview by column"""
        # Toggle sort direction if same column, otherwise start with ascending
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_reverse = False
        
        self.sort_column = column
        
        # Get all items with their values
        items = []
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            items.append((item, values))
        
        # Sort items based on column
        column_index = list(self.tree['columns']).index(column)
        
        def sort_key(item):
            value = item[1][column_index]
            
            # Handle different data types for proper sorting
            if column == 'ticker':
                # For ticker column, remove status symbols for sorting
                clean_ticker = str(value).replace('🔄 ', '').replace('✅ ', '').replace('❌ ', '')
                return clean_ticker.lower()
            elif column in ['price', 'change_5y', 'dividend_yield', 'dividend_ttm', 'eps_ttm', 
                         'eps_next_year', 'eps_next_5y', 'revenue', 'revenue_growth_5y', 
                         'operating_margin', 'profit_margin', 'roa', 'roe', 'roi', 
                         'pe_ratio', 'ps_ratio', 'pb_ratio', 'total_assets', 'total_liabilities',
                         'market_cap', 'volume', 'avg_volume', 'beta']:
                # Numeric columns - extract numbers
                try:
                    # Remove currency symbols, commas, and percentage signs
                    clean_value = str(value).replace('$', '').replace(',', '').replace('%', '').replace('B', '').replace('M', '').replace('K', '')
                    if clean_value == 'N/A' or clean_value == '':
                        return float('-inf') if not self.sort_reverse else float('inf')
                    return float(clean_value)
                except (ValueError, TypeError):
                    return float('-inf') if not self.sort_reverse else float('inf')
            elif column == 'timestamp':
                # Date/time column
                if value == 'N/A' or value == '':
                    return '0000-00-00 00:00' if not self.sort_reverse else '9999-99-99 99:99'
                return str(value)
            else:
                # String columns
                return str(value).lower()
        
        items.sort(key=sort_key, reverse=self.sort_reverse)
        
        # Reorder items in treeview
        for index, (item, values) in enumerate(items):
            self.tree.move(item, '', index)
        
        # Update column header to show sort direction
        for col in self.tree['columns']:
            if col == column:
                direction = ' ↓' if self.sort_reverse else ' ↑'
                current_text = self.tree.heading(col)['text']
                # Remove existing sort indicators
                clean_text = current_text.replace(' ↑', '').replace(' ↓', '')
                self.tree.heading(col, text=clean_text + direction)
            else:
                # Remove sort indicators from other columns
                current_text = self.tree.heading(col)['text']
                clean_text = current_text.replace(' ↑', '').replace(' ↓', '')
                self.tree.heading(col, text=clean_text) 