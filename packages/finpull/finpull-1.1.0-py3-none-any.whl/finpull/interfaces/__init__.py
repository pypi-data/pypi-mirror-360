from .cli import FinancialDataCLI

try:
    from .gui import FinancialDataGUI
    __all__ = ["FinancialDataCLI", "FinancialDataGUI"]
except ImportError:
    __all__ = ["FinancialDataCLI"] 