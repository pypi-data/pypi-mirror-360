import logging
from typing import List, Optional

from finpull_core import FinancialDataScraper, get_available_features

logger = logging.getLogger(__name__)


class FinancialDataCLI:
    """Command-line interface for the financial data scraper"""
    
    def __init__(self):
        self.scraper = FinancialDataScraper()
        print("FinPull - Financial Data Scraper")
        print("Type 'help' for available commands")
        print()
    
    def run(self):
        """Run the CLI interface"""
        while True:
            try:
                line = input("finpull> ").strip()
                if not line:
                    continue
                tokens = line.split()
                if not tokens:
                    continue
                cmd = tokens[0].lower()
                args = tokens[1:]
                
                if cmd in ["quit", "exit", "q"]:
                    print("Goodbye!")
                    break
                elif cmd == "add":
                    self._command_add(args)
                elif cmd == "remove":
                    self._command_remove(args)
                elif cmd == "show":
                    self._command_show(args)
                elif cmd == "refresh":
                    self._command_refresh(args)
                elif cmd == "export":
                    self._command_export(args)
                elif cmd == "stats":
                    self._handle_stats()
                elif cmd == "clear":
                    self._handle_clear()
                elif cmd == "help":
                    self._handle_help()
                else:
                    print(f"Unknown command: '{cmd}'. Type 'help' for available commands.")
                
                print()
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except EOFError:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
                logger.error(f"CLI error: {e}")
    
    def _get_file_dialog_path(self, format_type: str) -> Optional[str]:
        """Get file path using GUI dialog if available"""
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            
            # Set file types based on format
            if format_type == 'csv':
                filetypes = [("CSV files", "*.csv"), ("All files", "*.*")]
                defaultextension = ".csv"
            elif format_type == 'xlsx':
                filetypes = [("Excel files", "*.xlsx"), ("All files", "*.*")]
                defaultextension = ".xlsx"
            else:
                filetypes = [("JSON files", "*.json"), ("All files", "*.*")]
                defaultextension = ".json"
            
            file_path = filedialog.asksaveasfilename(
                title=f"Save {format_type.upper()} file",
                filetypes=filetypes,
                defaultextension=defaultextension
            )
            root.destroy()
            
            return file_path if file_path else None
            
        except ImportError:
            print("GUI file dialog not available (tkinter not found)")
            return None
        except Exception as e:
            print(f"Could not open file dialog: {e}")
            return None
    
    def _command_add(self, tickers: List[str]):
        """Add tickers via command args or fallback to interactive"""
        if not tickers:
            self._handle_add()
            return
        
        print(f"Adding {len(tickers)} ticker(s)...")
        added = 0
        for i, tk in enumerate(tickers, 1):
            print(f"🔄 [{i}/{len(tickers)}] Adding {tk.upper()}...")
            if not self.scraper.validate_ticker(tk):
                print(f"❌ [{i}/{len(tickers)}] '{tk}' is not a valid ticker symbol")
                continue
            try:
                if self.scraper.add_ticker(tk):
                    print(f"✅ [{i}/{len(tickers)}] Added {tk.upper()}")
                    added += 1
                else:
                    print(f"ℹ️  [{i}/{len(tickers)}] {tk.upper()} already exists")
            except ValueError as e:
                print(f"❌ [{i}/{len(tickers)}] Invalid ticker: {e}")
            except Exception as e:
                print(f"❌ [{i}/{len(tickers)}] Error adding {tk.upper()}: {e}")
        
        print()
        if added:
            print(f"✅ Added {added} new ticker(s)")
        else:
            print("ℹ️  No new tickers were added")

    def _command_remove(self, tickers: List[str]):
        """Remove tickers via command args or interactive"""
        if not tickers:
            self._handle_remove()
            return
        
        print(f"Removing {len(tickers)} ticker(s)...")
        removed = 0
        for i, tk in enumerate(tickers, 1):
            print(f"🔄 [{i}/{len(tickers)}] Removing {tk.upper()}...")
            if not self.scraper.has_ticker(tk):
                print(f"❌ [{i}/{len(tickers)}] {tk.upper()} not tracked")
                continue
            self.scraper.remove_ticker(tk)
            print(f"✅ [{i}/{len(tickers)}] Removed {tk.upper()}")
            removed += 1
        
        print()
        if removed:
            print(f"✅ Removed {removed} ticker(s)")
        else:
            print("ℹ️  No tickers were removed")

    def _command_show(self, args: List[str]):
        """Show tickers; no args = summary, with args = detailed view"""
        show_full = False
        ticker_args = []
        for arg in args:
            if arg in ['--full', '-f']:
                show_full = True
            else:
                ticker_args.append(arg)
        
        if not ticker_args and not show_full:
            # No specific tickers, show summary
            self._show_all_tickers_summary()
            return
        
        if not ticker_args and show_full:
            # --full flag without tickers, show all in detail
            for data in self.scraper.get_all_data():
                self._display_detailed_table(data)
            return
            
        # Specific tickers requested
        for tk in ticker_args:
            if not self.scraper.has_ticker(tk):
                print(f"🔍 {tk.upper()} not tracked. Fetching...")
                try:
                    self.scraper.add_ticker(tk)
                    print(f"✅ Added {tk.upper()}")
                except Exception as e:
                    print(f"❌ Failed to fetch {tk.upper()}: {e}")
                    continue
            data = self.scraper.get_ticker_data(tk)
            if data:
                self._display_detailed_table(data)

    def _command_export(self, args: List[str]):
        """Export with optional path and format flags"""
        import os
        
        data_list = self.scraper.get_all_data()
        if not data_list:
            print("No data to export")
            return
        
        # Parse export arguments
        export_path = None
        format_type = None
        
        i = 0
        while i < len(args):
            arg = args[i]
            if arg in ['-j', '--json']:
                format_type = 'json'
            elif arg in ['-c', '--csv']:
                format_type = 'csv'
            elif arg in ['-x', '--xlsx']:
                format_type = 'xlsx'
            elif not export_path and not arg.startswith('-'):
                # First non-flag argument is the path
                export_path = os.path.expanduser(arg)
            i += 1
        
        # If format specified but no path, ask for path
        if format_type and not export_path:
            current_dir = os.getcwd()
            custom_path = input(f"Enter file path (press Enter for current directory: {current_dir}, or # for file dialog): ").strip()
            if custom_path == "#":
                export_path = self._get_file_dialog_path(format_type)
                if not export_path:
                    print("Export cancelled")
                    return
            elif custom_path:
                export_path = os.path.expanduser(custom_path)
        
        # If path provided, use it directly
        if export_path:
            if not format_type:
                # Try to infer format from extension
                if export_path.lower().endswith('.csv'):
                    format_type = 'csv'
                elif export_path.lower().endswith('.xlsx'):
                    format_type = 'xlsx'
                else:
                    format_type = 'json'
            
            try:
                filename = self.scraper.export_data(format_type, export_path)
                print(f"✅ Exported {len(data_list)} records to {filename}")
            except Exception as e:
                print(f"❌ Export error: {e}")
            return
        
        # No path provided, fall back to interactive mode
        self._handle_export()
    
    def _handle_add(self):
        """Handle add ticker command"""
        ticker = input("Enter ticker symbol: ").strip()
        if not ticker:
            print("Please enter a ticker symbol")
            return
        
        if not self.scraper.validate_ticker(ticker):
            print(f"'{ticker}' doesn't appear to be a valid ticker symbol")
            return
        
        try:
            if self.scraper.add_ticker(ticker):
                print(f"✅ Added {ticker.upper()}")
            else:
                print(f"! {ticker.upper()} already exists")
        except ValueError as e:
            print(f"❌ Invalid ticker: {e}")
        except Exception as e:
            print(f"❌ Error adding {ticker.upper()}: {e}")
    
    def _handle_remove(self):
        """Handle remove ticker command"""
        self._show_ticker_list()
        if not self.scraper.get_ticker_list():
            return
        
        ticker = input("Enter ticker to remove: ").strip()
        if not ticker:
            print("Please enter a ticker symbol")
            return
        
        if not self.scraper.has_ticker(ticker):
            print(f"'{ticker.upper()}' is not being tracked")
            return
        
        confirm = input(f"Remove {ticker.upper()}? (y/N): ").strip().lower()
        if confirm == 'y':
            self.scraper.remove_ticker(ticker)
            print(f"✅ Removed {ticker.upper()}")
        else:
            print("Cancelled")
    
    def _command_refresh(self, args: List[str]):
        """Refresh ticker data - all by default, or specific tickers if provided"""
        if args:
            # Refresh specific tickers
            print(f"Refreshing {len(args)} ticker(s)...")
            for tk in args:
                if not self.scraper.has_ticker(tk):
                    print(f"❌ {tk.upper()} not tracked")
                    continue
                print(f"🔄 Refreshing {tk.upper()}...")
                try:
                    self.scraper.refresh_data(tk)
                    print(f"✅ Refreshed {tk.upper()}")
                except Exception as e:
                    print(f"❌ Error refreshing {tk.upper()}: {e}")
        else:
            # Refresh all
            ticker_list = self.scraper.get_ticker_list()
            if not ticker_list:
                print("No tickers to refresh")
                return
            
            print(f"Refreshing {len(ticker_list)} tickers...")
            print()
            
            # Show progress for each ticker
            for i, tk in enumerate(ticker_list, 1):
                print(f"🔄 [{i}/{len(ticker_list)}] Refreshing {tk}...")
                try:
                    self.scraper.refresh_data(tk)
                    print(f"✅ [{i}/{len(ticker_list)}] Refreshed {tk}")
                except Exception as e:
                    print(f"❌ [{i}/{len(ticker_list)}] Error refreshing {tk}: {e}")
            
            print()
            print("✅ Refresh complete")

    def _show_all_tickers_summary(self):
        """Show summary table for all tickers"""
        data_list = self.scraper.get_all_data()
        if not data_list:
            print("No tickers found")
            return
        
        # Enhanced summary table with ASCII formatting
        box_width = 100
        print("+" + "=" * (box_width - 2) + "+")
        print(f"| {'PORTFOLIO SUMMARY':<{box_width - 4}} |")
        print("+" + "=" * (box_width - 2) + "+")
        
        # Header
        print(f"| {'Ticker':<8} | {'Company':<25} | {'Price':<10} | {'P/E':<8} | {'Market Cap':<12} | {'5Y Change':<10} |")
        print("+" + "-" * (box_width - 2) + "+")
        
        # Data rows
        for data in data_list:
            company = data.company_name[:24] if len(data.company_name) > 24 else data.company_name
            price = f"${data.price}" if data.price != "N/A" else "N/A"
            pe_ratio = data.pe_ratio if data.pe_ratio != "N/A" else "N/A"
            market_cap = data.market_cap if data.market_cap != "N/A" else "N/A"
            change_5y = data.change_5y if data.change_5y != "N/A" else "N/A"
            
            print(f"| {data.ticker:<8} | {company:<25} | {price:<10} | {pe_ratio:<8} | {market_cap:<12} | {change_5y:<10} |")
        
        print("+" + "=" * (box_width - 2) + "+")
        print(f"| {'Total Tickers: ' + str(len(data_list)):<{box_width - 4}} |")
        print("+" + "=" * (box_width - 2) + "+")
    
    def _display_detailed_table(self, data):
        """Display financial data in a beautiful ASCII table"""
        ticker = data.ticker
        company = data.company_name
        
        # Calculate box width based on content
        max_width = max(
            len(f"{ticker} - {company}"),
            60  # Minimum width
        )
        box_width = min(max_width + 4, 80)  # Max 80 chars wide
        
        # Header
        print()
        print("+" + "=" * (box_width - 2) + "+")
        title = f"{ticker} - {company}"
        if len(title) > box_width - 4:
            title = title[:box_width - 7] + "..."
        print(f"| {title:<{box_width - 4}} |")
        print("+" + "=" * (box_width - 2) + "+")
        
        # Basic Information Section
        self._print_section_header("BASIC INFORMATION", box_width)
        self._print_table_row("Sector", data.sector, box_width)
        self._print_table_row("Price", f"${data.price}" if data.price != "N/A" else "N/A", box_width)
        self._print_table_row("Market Cap", data.market_cap, box_width)
        
        # Valuation Ratios Section
        self._print_section_header("VALUATION RATIOS", box_width)
        self._print_table_row("P/E Ratio", data.pe_ratio, box_width)
        self._print_table_row("P/S Ratio", data.ps_ratio, box_width)
        self._print_table_row("P/B Ratio", data.pb_ratio, box_width)
        
        # Earnings & Growth Section
        self._print_section_header("EARNINGS & GROWTH", box_width)
        self._print_table_row("EPS (TTM)", data.eps_ttm, box_width)
        self._print_table_row("EPS Next Year", data.eps_next_year, box_width)
        self._print_table_row("EPS Next 5Y", data.eps_next_5y, box_width)
        self._print_table_row("5-Year Change", data.change_5y, box_width)
        
        # Dividend Information Section
        self._print_section_header("DIVIDEND INFORMATION", box_width)
        self._print_table_row("Dividend TTM", data.dividend_ttm, box_width)
        self._print_table_row("Dividend Yield", data.dividend_yield, box_width)
        
        # Performance Metrics Section
        self._print_section_header("PERFORMANCE METRICS", box_width)
        self._print_table_row("ROA", data.roa, box_width)
        self._print_table_row("ROE", data.roe, box_width)
        self._print_table_row("ROI (ROIC)", data.roi, box_width)
        self._print_table_row("Profit Margin", data.profit_margin, box_width)
        self._print_table_row("Operating Margin", data.operating_margin, box_width)
        
        # Financial Position Section
        self._print_section_header("FINANCIAL POSITION", box_width)
        self._print_table_row("Revenue", data.revenue, box_width)
        self._print_table_row("Total Assets", self._format_large_number(data.total_assets), box_width)
        self._print_table_row("Total Liabilities", self._format_large_number(data.total_liabilities), box_width)
        
        # Market Data Section
        self._print_section_header("MARKET DATA", box_width)
        self._print_table_row("Beta", data.beta, box_width)
        self._print_table_row("Volume", self._format_volume(data.volume), box_width)
        self._print_table_row("Avg Volume", data.avg_volume, box_width)
        
        # Footer
        print("+" + "-" * (box_width - 2) + "+")
        timestamp = "N/A"
        if data.timestamp:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(data.timestamp.replace('Z', '+00:00'))
                timestamp = dt.strftime('%Y-%m-%d %H:%M:%S UTC')
            except:
                timestamp = data.timestamp
        
        footer = f"Last Updated: {timestamp}"
        if len(footer) > box_width - 4:
            footer = footer[:box_width - 7] + "..."
        print(f"| {footer:<{box_width - 4}} |")
        print("+" + "=" * (box_width - 2) + "+")
        print()
    
    def _print_section_header(self, title, box_width):
        """Print a section header in the table"""
        print("+" + "-" * (box_width - 2) + "+")
        print(f"| {title:<{box_width - 4}} |")
        print("+" + "-" * (box_width - 2) + "+")
    
    def _print_table_row(self, label, value, box_width):
        """Print a data row in the table"""
        if value == "N/A" or value is None:
            value = "N/A"
        else:
            value = str(value)
        
        # Calculate spacing
        available_space = box_width - 6  # "| ", " |" and ": "
        label_space = min(len(label), available_space // 2)
        value_space = available_space - label_space - 2  # -2 for ": "
        
        # Truncate if necessary
        if len(label) > label_space:
            label = label[:label_space - 3] + "..."
        if len(value) > value_space:
            value = value[:value_space - 3] + "..."
        
        print(f"| {label:<{label_space}}: {value:<{value_space}} |")
    
    def _format_large_number(self, value):
        """Format large numbers for display"""
        if value == "N/A" or value is None:
            return "N/A"
        
        try:
            num = float(value)
            if num >= 1e9:
                return f"${num/1e9:.1f}B"
            elif num >= 1e6:
                return f"${num/1e6:.1f}M"
            else:
                return f"${num:,.0f}"
        except:
            return str(value)
    
    def _format_volume(self, value):
        """Format volume numbers for display"""
        if value == "N/A" or value is None:
            return "N/A"
        
        try:
            # Remove commas and convert
            clean_value = str(value).replace(',', '')
            num = float(clean_value)
            if num >= 1e9:
                return f"{num/1e9:.1f}B"
            elif num >= 1e6:
                return f"{num/1e6:.1f}M"
            elif num >= 1e3:
                return f"{num/1e3:.1f}K"
            else:
                return f"{num:,.0f}"
        except:
            return str(value)
    
    def _handle_export(self):
        """Handle export data command"""
        data_list = self.scraper.get_all_data()
        if not data_list:
            print("No data to export")
            return
        
        print("\nExport formats:")
        print("  1. JSON")
        print("  2. CSV")
        print("  3. Excel (XLSX)")
        
        choice = input("\nSelect format (1-3): ").strip()
        
        format_map = {"1": "json", "2": "csv", "3": "xlsx"}
        if choice not in format_map:
            print("Invalid choice")
            return
        
        format_type = format_map[choice]
        
        # Ask for file path
        import os
        current_dir = os.getcwd()
        custom_path = input(f"Enter file path (press Enter for current directory: {current_dir}, or # for file dialog): ").strip()
        
        if custom_path == "#":
            custom_filename = self._get_file_dialog_path(format_type)
            if not custom_filename:
                print("Export cancelled")
                return
        elif custom_path:
            custom_filename = os.path.expanduser(custom_path)
        else:
            custom_filename = None
        
        try:
            if custom_filename:
                filename = self.scraper.export_data(format_type, custom_filename)
            else:
                filename = self.scraper.export_data(format_type)
            print(f"\n✅ Exported {len(data_list)} records to {filename}")
        except Exception as e:
            print(f"\n❌ Export error: {e}")
    
    def _handle_stats(self):
        """Handle stats command"""
        stats = self.scraper.get_stats()
        
        print("=== FinPull Statistics ===")
        print(f"Total tickers: {stats['total_tickers']}")
        print(f"Cached tickers: {stats['cached_tickers']}")
        print(f"Missing cache: {stats['missing_cache']}")
        print(f"Stale data: {stats['stale_data']}")
        print(f"Storage file: {stats['storage_file']}")
        print(f"File size: {stats['file_size']} bytes")
        print()
        
        print("Data sources:")
        for i, source in enumerate(stats['data_sources'], 1):
            print(f"  {i}. {source}")
        
        # Show feature availability
        features = get_available_features()
        print("\nFeatures:")
        for feature, available in features.items():
            status = "✅" if available else "❌"
            print(f"  {status} {feature.replace('_', ' ').title()}")
    
    def _handle_clear(self):
        """Handle clear all data command"""
        ticker_count = len(self.scraper.get_ticker_list())
        if ticker_count == 0:
            print("No data to clear")
            return
        
        print(f"This will remove all {ticker_count} tickers and cached data.")
        confirm = input("Are you sure? (y/N): ").strip().lower()
        
        if confirm == 'y':
            self.scraper.clear_all()
            print("✅ All data cleared")
        else:
            print("Cancelled")
    
    def _handle_help(self):
        """Handle help command"""
        print("\nCommands:")
        print("  add [TICKER...]      Add one or more tickers")
        print("  remove [TICKER...]   Remove one or more tickers")
        print("  show [TICKER...]     Show ticker data (summary by default)")
        print("    --full, -f         Show detailed view")
        print("  refresh [TICKER...]  Refresh data (all by default)")
        print("  export [PATH]        Export data to file")
        print("    --json, -j         Export as JSON")
        print("    --csv, -c          Export as CSV")
        print("    --xlsx, -x         Export as Excel")
        print("  stats                Show statistics")
        print("  clear                Clear all data")
        print("  help                 Show this help")
        print("  quit                 Exit the program")
        print()
        print("Examples:")
        print("  add AAPL GOOGL MSFT")
        print("  show AAPL")
        print("  show --full")
        print("  refresh AAPL GOOGL")
        print("  export ~/data.json --json")
        print("  export --csv")
    
    def _show_ticker_list(self):
        """Show current ticker list"""
        tickers = self.scraper.get_ticker_list()
        if not tickers:
            print("No tickers currently tracked")
        else:
            print(f"Currently tracking: {', '.join(tickers)}") 