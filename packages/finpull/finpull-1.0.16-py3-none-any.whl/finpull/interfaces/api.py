"""
API interface for web/WASM environments and programmatic access
"""

import logging
from typing import Dict, Any, List, Optional

from ..core.scraper import FinancialDataScraper
from ..core.data_models import FinancialData

logger = logging.getLogger(__name__)


class FinancialDataAPI:
    """Simple API interface for web/WASM environments"""
    
    def __init__(self, storage_file: Optional[str] = None):
        """
        Initialize the API
        
        Args:
            storage_file: Custom storage file path
        """
        self.scraper = FinancialDataScraper(storage_file)
        logger.info("FinancialDataAPI initialized")
    
    def add_ticker(self, ticker: str) -> Dict[str, Any]:
        """
        Add ticker and return result
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with success status and message/error
        """
        try:
            success = self.scraper.add_ticker(ticker)
            if success:
                return {
                    "success": True, 
                    "message": f"Added {ticker}",
                    "ticker": ticker.upper()
                }
            else:
                return {
                    "success": False, 
                    "message": f"{ticker} already exists",
                    "ticker": ticker.upper()
                }
        except ValueError as e:
            logger.error(f"API add_ticker validation error for {ticker}: {e}")
            return {
                "success": False, 
                "error": f"Invalid ticker: {str(e)}",
                "ticker": ticker.upper()
            }
        except Exception as e:
            logger.error(f"API add_ticker error for {ticker}: {e}")
            return {
                "success": False, 
                "error": str(e),
                "ticker": ticker.upper()
            }
    
    def get_data(self, ticker: Optional[str] = None) -> Dict[str, Any]:
        """
        Get data for specific ticker or all tickers
        
        Args:
            ticker: Specific ticker symbol (optional)
            
        Returns:
            Dictionary with success status and data
        """
        try:
            if ticker:
                data = self.scraper.get_ticker_data(ticker)
                return {
                    "success": True, 
                    "data": data.to_dict() if data else None,
                    "ticker": ticker.upper()
                }
            else:
                data_list = self.scraper.get_all_data()
                return {
                    "success": True, 
                    "data": [d.to_dict() for d in data_list],
                    "count": len(data_list)
                }
        except Exception as e:
            logger.error(f"API get_data error: {e}")
            return {"success": False, "error": str(e)}
    
    def refresh_data(self, ticker: Optional[str] = None) -> Dict[str, Any]:
        """
        Refresh data for ticker(s)
        
        Args:
            ticker: Specific ticker to refresh (optional, None for all)
            
        Returns:
            Dictionary with success status and message
        """
        try:
            self.scraper.refresh_data(ticker)
            message = f"Refreshed {ticker}" if ticker else "Refreshed all data"
            return {
                "success": True, 
                "message": message,
                "ticker": ticker.upper() if ticker else None
            }
        except Exception as e:
            logger.error(f"API refresh_data error: {e}")
            return {"success": False, "error": str(e)}
    
    def refresh_data_with_progress(self, ticker: Optional[str] = None, progress_callback=None) -> Dict[str, Any]:
        """
        Refresh data for ticker(s) with progress callback
        
        Args:
            ticker: Specific ticker to refresh (optional, None for all)
            progress_callback: Function to call with progress updates (ticker, status)
            
        Returns:
            Dictionary with success status and progress details
        """
        try:
            if ticker:
                # Refresh single ticker
                if progress_callback:
                    progress_callback(ticker, "loading")
                
                self.scraper.refresh_data(ticker)
                
                if progress_callback:
                    progress_callback(ticker, "complete")
                
                return {
                    "success": True, 
                    "message": f"Refreshed {ticker}",
                    "ticker": ticker.upper()
                }
            else:
                # Refresh all tickers
                ticker_list = self.scraper.get_ticker_list()
                results = {
                    "success": True,
                    "total": len(ticker_list),
                    "completed": 0,
                    "failed": 0,
                    "details": []
                }
                
                for tk in ticker_list:
                    try:
                        if progress_callback:
                            progress_callback(tk, "loading")
                        
                        self.scraper.refresh_data(tk)
                        results["completed"] += 1
                        results["details"].append({"ticker": tk, "status": "success"})
                        
                        if progress_callback:
                            progress_callback(tk, "complete")
                    except Exception as e:
                        results["failed"] += 1
                        results["details"].append({"ticker": tk, "status": "error", "error": str(e)})
                        
                        if progress_callback:
                            progress_callback(tk, "error")
                
                return results
                
        except Exception as e:
            logger.error(f"API refresh_data_with_progress error: {e}")
            return {"success": False, "error": str(e)}
    
    def remove_ticker(self, ticker: str) -> Dict[str, Any]:
        """
        Remove ticker from tracking
        
        Args:
            ticker: Ticker symbol to remove
            
        Returns:
            Dictionary with success status and message
        """
        try:
            self.scraper.remove_ticker(ticker)
            return {
                "success": True, 
                "message": f"Removed {ticker}",
                "ticker": ticker.upper()
            }
        except Exception as e:
            logger.error(f"API remove_ticker error for {ticker}: {e}")
            return {"success": False, "error": str(e)}
    
    def export_data(self, format_type: str = "json", filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Export data to file
        
        Args:
            format_type: Export format ("json", "csv", "xlsx")
            filename: Custom filename (optional)
            
        Returns:
            Dictionary with success status and filename/error
        """
        try:
            output_filename = self.scraper.export_data(format_type, filename)
            return {
                "success": True, 
                "filename": output_filename,
                "format": format_type
            }
        except Exception as e:
            logger.error(f"API export_data error: {e}")
            return {"success": False, "error": str(e)}
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get scraper statistics
        
        Returns:
            Dictionary with statistics
        """
        try:
            stats = self.scraper.get_stats()
            return {"success": True, "stats": stats}
        except Exception as e:
            logger.error(f"API get_stats error: {e}")
            return {"success": False, "error": str(e)}
    
    def get_ticker_list(self) -> Dict[str, Any]:
        """
        Get list of tracked tickers
        
        Returns:
            Dictionary with ticker list
        """
        try:
            tickers = self.scraper.get_ticker_list()
            return {
                "success": True, 
                "tickers": tickers,
                "count": len(tickers)
            }
        except Exception as e:
            logger.error(f"API get_ticker_list error: {e}")
            return {"success": False, "error": str(e)}
    
    def validate_ticker(self, ticker: str) -> Dict[str, Any]:
        """
        Validate ticker symbol
        
        Args:
            ticker: Ticker symbol to validate
            
        Returns:
            Dictionary with validation result
        """
        try:
            is_valid = self.scraper.validate_ticker(ticker)
            return {
                "success": True,
                "valid": is_valid,
                "ticker": ticker.upper().strip()
            }
        except Exception as e:
            logger.error(f"API validate_ticker error: {e}")
            return {"success": False, "error": str(e)}
    
    def clear_all(self) -> Dict[str, Any]:
        """
        Clear all tracked tickers and data
        
        Returns:
            Dictionary with success status
        """
        try:
            self.scraper.clear_all()
            return {"success": True, "message": "All data cleared"}
        except Exception as e:
            logger.error(f"API clear_all error: {e}")
            return {"success": False, "error": str(e)}
    
    def cleanup_stale_data(self, max_age_hours: int = 24) -> Dict[str, Any]:
        """
        Clean up stale cached data
        
        Args:
            max_age_hours: Maximum age in hours
            
        Returns:
            Dictionary with cleanup results
        """
        try:
            removed_count = self.scraper.cleanup_stale_data(max_age_hours)
            return {
                "success": True, 
                "removed_count": removed_count,
                "message": f"Cleaned up {removed_count} stale records"
            }
        except Exception as e:
            logger.error(f"API cleanup_stale_data error: {e}")
            return {"success": False, "error": str(e)}
    
    def batch_add_tickers(self, tickers: List[str]) -> Dict[str, Any]:
        """
        Add multiple tickers at once
        
        Args:
            tickers: List of ticker symbols
            
        Returns:
            Dictionary with batch operation results
        """
        results = {
            "success": True,
            "added": [],
            "failed": [],
            "already_exists": []
        }
        
        for ticker in tickers:
            try:
                if self.scraper.has_ticker(ticker):
                    results["already_exists"].append(ticker.upper())
                elif self.scraper.add_ticker(ticker):
                    results["added"].append(ticker.upper())
                else:
                    results["already_exists"].append(ticker.upper())
            except ValueError as e:
                results["failed"].append({
                    "ticker": ticker.upper(),
                    "error": f"Invalid ticker: {str(e)}"
                })
            except Exception as e:
                results["failed"].append({
                    "ticker": ticker.upper(),
                    "error": str(e)
                })
        
        results["summary"] = {
            "total": len(tickers),
            "added_count": len(results["added"]),
            "failed_count": len(results["failed"]),
            "already_exists_count": len(results["already_exists"])
        }
        
        return results 