"""
Main entry point for FinPull package
Handles command-line execution and interface selection
"""

import sys
import argparse
import logging
from finpull_core import FinancialDataAPI, get_available_features
from finpull_core.utils.compatibility import HAS_TKINTER

# Full package always has all interfaces
HAS_CLI = True
HAS_GUI = True
IS_CORE_INSTALLATION = False

# Conditional imports
if HAS_CLI:
    from .interfaces.cli import FinancialDataCLI
if HAS_GUI:
    from .interfaces.gui import FinancialDataGUI

# Setup logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_parser():
    """Create command-line argument parser"""
    parser = argparse.ArgumentParser(
        prog='finpull',
        description='FinPull - Professional Financial Data Scraper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  finpull                    Launch GUI (if available)
  finpull --gui              Launch GUI explicitly
  finpull add AAPL GOOGL     Add multiple tickers
  finpull remove AAPL        Remove a ticker
  finpull show AAPL          Show specific ticker details
  finpull show --full        Show all tickers in detail
  finpull refresh            Refresh all tickers
  finpull refresh AAPL       Refresh specific ticker
  finpull export --csv       Export to CSV format
  finpull export data.json   Export to specific file
"""
    )
    
    # Interface mode arguments
    if HAS_GUI or HAS_CLI:
        interface_group = parser.add_mutually_exclusive_group()
        if HAS_GUI:
            interface_group.add_argument('--gui', '-g', action='store_true', help='Launch GUI interface')
        if HAS_CLI:
            interface_group.add_argument('--interactive', '-i', action='store_true', help='Interactive CLI mode')
    
    # Commands - only add if CLI is available
    if HAS_CLI:
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Add command
        add_parser = subparsers.add_parser('add', help='Add one or more tickers')
        add_parser.add_argument('tickers', nargs='+', help='Ticker symbol(s) to add')
        
        # Remove command
        remove_parser = subparsers.add_parser('remove', help='Remove one or more tickers')
        remove_parser.add_argument('tickers', nargs='+', help='Ticker symbol(s) to remove')
        
        # Show command
        show_parser = subparsers.add_parser('show', help='Show ticker data (summary by default)')
        show_parser.add_argument('tickers', nargs='*', help='Ticker symbol(s) to display')
        show_parser.add_argument('--full', '-f', action='store_true', help='Show detailed view')
        
        # Export command
        export_parser = subparsers.add_parser('export', help='Export data to file')
        export_parser.add_argument('path', nargs='?', help='Export file path')
        
        # Format options
        export_parser.add_argument('--json', '-j', action='store_true', help='Export as JSON')
        export_parser.add_argument('--csv', '-c', action='store_true', help='Export as CSV') 
        export_parser.add_argument('--xlsx', '-x', action='store_true', help='Export as Excel')
        
        # Refresh command
        refresh_parser = subparsers.add_parser('refresh', help='Refresh data (all by default)')
        refresh_parser.add_argument('tickers', nargs='*', help='Specific ticker(s) to refresh')
        
        # Stats command
        subparsers.add_parser('stats', help='Show statistics')
        
        # Clear command
        clear_parser = subparsers.add_parser('clear', help='Clear all data')
        clear_parser.add_argument('--force', action='store_true', help='Skip confirmation')
    
    return parser

def handle_command(args):
    """Handle command-line commands"""
    if not HAS_CLI:
        print("❌ CLI commands not available in core installation")
        print("💡 Install full version: pip install finpull")
        return 1
    
    from finpull_core import FinancialDataScraper
    
    scraper = FinancialDataScraper()
    
    try:
        if args.command == 'add':
            print(f"Adding {len(args.tickers)} ticker(s)...")
            added = 0
            for i, tk in enumerate(args.tickers, 1):
                print(f"🔄 [{i}/{len(args.tickers)}] Adding {tk.upper()}...")
                try:
                    if scraper.add_ticker(tk):
                        print(f"✅ [{i}/{len(args.tickers)}] Added {tk.upper()}")
                        added += 1
                    else:
                        print(f"ℹ️  [{i}/{len(args.tickers)}] {tk.upper()} already exists")
                except ValueError as e:
                    print(f"❌ [{i}/{len(args.tickers)}] Invalid ticker {tk.upper()}: {e}")
                except Exception as e:
                    print(f"❌ [{i}/{len(args.tickers)}] Failed to add {tk.upper()}: {e}")
            
            print()
            if added:
                print(f"✅ Added {added} new ticker(s)")
            else:
                print("ℹ️  No new tickers were added")
                
        elif args.command == 'remove':
            print(f"Removing {len(args.tickers)} ticker(s)...")
            removed = 0
            for i, tk in enumerate(args.tickers, 1):
                print(f"🔄 [{i}/{len(args.tickers)}] Removing {tk.upper()}...")
                if scraper.has_ticker(tk):
                    scraper.remove_ticker(tk)
                    print(f"✅ [{i}/{len(args.tickers)}] Removed {tk.upper()}")
                    removed += 1
                else:
                    print(f"❌ [{i}/{len(args.tickers)}] {tk.upper()} not found")
            
            print()
            if removed:
                print(f"✅ Removed {removed} ticker(s)")
            else:
                print("ℹ️  No tickers were removed")
                
        elif args.command == 'show':
            cli = FinancialDataCLI()
            cli.scraper = scraper
            
            if args.tickers:
                # Show specific tickers - automatically add if not present
                for tk in args.tickers:
                    if not scraper.has_ticker(tk):
                        print(f"🔍 {tk.upper()} not found. Fetching data...")
                        try:
                            scraper.add_ticker(tk)
                            print(f"✅ Added {tk.upper()}")
                        except ValueError as e:
                            print(f"❌ Invalid ticker {tk.upper()}: {e}")
                            continue
                        except Exception as e:
                            print(f"❌ Failed to fetch {tk.upper()}: {e}")
                            continue
                    
                    data = scraper.get_ticker_data(tk)
                    if data:
                        cli._display_detailed_table(data)
            elif args.full:
                # Show all tickers in detail
                data_list = scraper.get_all_data()
                if not data_list:
                    print("No tickers found. Use 'finpull add TICKER' to add some.")
                else:
                    for data in data_list:
                        cli._display_detailed_table(data)
            else:
                # Show summary by default
                data_list = scraper.get_all_data()
                if not data_list:
                    print("No tickers found. Use 'finpull add TICKER' to add some.")
                else:
                    cli._show_all_tickers_summary()
                        
        elif args.command == 'export':
            try:
                data_list = scraper.get_all_data()
                if not data_list:
                    print("No data to export")
                    return 0
                
                # Determine formats - support multiple formats
                formats = []
                if args.json:
                    formats.append('json')
                if args.csv:
                    formats.append('csv')
                if args.xlsx:
                    formats.append('xlsx')
                
                import os
                
                # If no format specified, fall back to interactive mode
                if not formats:
                    # No format or path - interactive mode
                    print("\nExport formats:")
                    print("  1. JSON")
                    print("  2. CSV")
                    print("  3. Excel (XLSX)")
                    
                    choice = input("\nSelect format (1-3): ").strip()
                    format_map = {"1": "json", "2": "csv", "3": "xlsx"}
                    if choice not in format_map:
                        print("Invalid choice")
                        return 1
                    formats = [format_map[choice]]
                
                # Export to each format
                exported_files = []
                for i, format_type in enumerate(formats, 1):
                    print(f"🔄 [{i}/{len(formats)}] Exporting to {format_type.upper()}...")
                    
                    if args.path:
                        # Use provided path as base, modify extension for format
                        base_path = os.path.expanduser(args.path)
                        if len(formats) == 1:
                            # Single format, use path as-is or infer extension
                            if not base_path.lower().endswith(f'.{format_type}'):
                                # Remove existing extension and add correct one
                                base_name = os.path.splitext(base_path)[0]
                                output_path = f"{base_name}.{format_type}"
                            else:
                                output_path = base_path
                        else:
                            # Multiple formats, add format suffix
                            base_name = os.path.splitext(base_path)[0]
                            output_path = f"{base_name}_{format_type}.{format_type}"
                    else:
                        # No path provided, use default naming
                        output_path = None
                    
                    try:
                        if output_path:
                            filename = scraper.export_data(format_type, output_path)
                        else:
                            filename = scraper.export_data(format_type)
                        
                        exported_files.append(filename)
                        print(f"✅ [{i}/{len(formats)}] Exported to {filename}")
                    except Exception as e:
                        print(f"❌ [{i}/{len(formats)}] Failed to export {format_type.upper()}: {e}")
                
                print()
                if exported_files:
                    print(f"✅ Successfully exported {len(data_list)} records to {len(exported_files)} file(s):")
                    for filename in exported_files:
                        print(f"   📄 {filename}")
                else:
                    print("❌ No files were exported")
                    
            except Exception as e:
                print(f"❌ Export error: {e}")
                
        elif args.command == 'refresh':
            try:
                if args.tickers:
                    # Refresh specific tickers
                    print(f"Refreshing {len(args.tickers)} ticker(s)...")
                    for tk in args.tickers:
                        if not scraper.has_ticker(tk):
                            print(f"❌ {tk.upper()} not tracked")
                            continue
                        print(f"🔄 Refreshing {tk.upper()}...")
                        try:
                            scraper.refresh_data(tk)
                            print(f"✅ Refreshed {tk.upper()}")
                        except Exception as e:
                            print(f"❌ Error refreshing {tk.upper()}: {e}")
                else:
                    # Refresh all
                    ticker_list = scraper.get_ticker_list()
                    if not ticker_list:
                        print("No tickers to refresh")
                    else:
                        print(f"Refreshing {len(ticker_list)} tickers...")
                        print()
                        
                        # Show progress for each ticker
                        for i, tk in enumerate(ticker_list, 1):
                            print(f"🔄 [{i}/{len(ticker_list)}] Refreshing {tk}...")
                            try:
                                scraper.refresh_data(tk)
                                print(f"✅ [{i}/{len(ticker_list)}] Refreshed {tk}")
                            except Exception as e:
                                print(f"❌ [{i}/{len(ticker_list)}] Error refreshing {tk}: {e}")
                        
                        print()
                        print("✅ Refresh complete")
            except Exception as e:
                print(f"❌ Refresh error: {e}")
                
        elif args.command == 'stats':
            stats = scraper.get_stats()
            print("\n📊 FinPull Statistics")
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
                
        elif args.command == 'clear':
            ticker_count = len(scraper.get_ticker_list())
            if ticker_count == 0:
                print("No data to clear")
                return
                
            if args.force:
                scraper.clear_all()
                print("✅ All data cleared")
            else:
                confirm = input(f"Clear all {ticker_count} tickers? (y/N): ").strip().lower()
                if confirm == 'y':
                    scraper.clear_all()
                    print("✅ All data cleared")
                else:
                    print("Cancelled")
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

def main():
    """Main function to run appropriate interface"""
    parser = create_parser()
    
    # If no arguments, show available interfaces
    if len(sys.argv) == 1:
        if IS_CORE_INSTALLATION:
            print("🔧 FinPull Core Installation")
            print("💡 API-only version. For full features: pip install finpull")
            print()
            print("Available interfaces:")
            print("  • API (programmatic access)")
            print()
            print("Usage:")
            print("  python -c \"from finpull import FinancialDataAPI; api = FinancialDataAPI(); print(api.add_ticker('AAPL'))\"")
            print()
            print("For CLI and GUI: pip install finpull")
            return 0
        elif HAS_GUI:
            try:
                gui = FinancialDataGUI()
                gui.run()
                return 0
            except Exception as e:
                print(f"❌ GUI failed: {e}")
        parser.print_help()
        return 0
    
    args = parser.parse_args()
    
    # Handle interface modes
    if args.gui:
        if not HAS_GUI:
            print("❌ GUI not available in core installation")
            print("💡 Install full version: pip install finpull")
            return 1
        try:
            gui = FinancialDataGUI()
            gui.run()
            return 0
        except Exception as e:
            print(f"❌ GUI failed: {e}")
            return 1
            
    elif args.interactive:
        if not HAS_CLI:
            print("❌ Interactive CLI not available in core installation")
            print("💡 Install full version: pip install finpull")
            return 1
        cli = FinancialDataCLI()
        cli.run()
        return 0
        
    # Handle specific commands
    elif args.command:
        return handle_command(args)
        
    else:
        parser.print_help()
        return 0

# For WASM/web environments - expose key functions globally
def setup_web_environment():
    """Setup for web/WASM environments"""
    try:
        # This will fail in normal Python but might work in Pyodide/WASM
        import js
        # Web environment detected
        print("Web environment detected")
        global_api = FinancialDataAPI()
        
        # Expose functions to JavaScript
        js.pyodide_financial_scraper = {
            'add_ticker': global_api.add_ticker,
            'get_data': global_api.get_data,
            'refresh_data': global_api.refresh_data,
            'remove_ticker': global_api.remove_ticker,
            'export_data': global_api.export_data,
            'get_features': lambda: get_available_features()
        }
        print("Financial scraper API exposed to JavaScript")
        return True
        
    except ImportError:
        return False

if __name__ == "__main__":
    if not setup_web_environment():
        sys.exit(main()) 