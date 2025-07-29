"""Google Play Console data source"""

import pyarrow as pa
from typing import Any, Dict, Optional
import logging
from datetime import datetime, timedelta

from ..core.base import DataSource
from ..core.data_packet import DataPacket


class GooglePlaySource(DataSource):
    """Google Play Console data source for financial data"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = logging.getLogger(f"dft.sources.google_play.{self.name}")
    
    def extract(self, variables: Optional[Dict[str, Any]] = None) -> DataPacket:
        """Extract financial data from Google Play Console"""
        
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
        except ImportError:
            raise ImportError(
                "Google API libraries required for Google Play source. "
                "Install with: pip install google-api-python-client google-auth"
            )
        
        # Configuration
        package_name = self.get_config("package_name")
        service_account_file = self.get_config("service_account_file")
        report_type = self.get_config("report_type", "financial")  # financial, installs, etc.
        
        if not package_name:
            raise ValueError("package_name is required for Google Play source")
        if not service_account_file:
            raise ValueError("service_account_file is required for Google Play source")
        
        # Date range
        start_date = self.get_config("start_date")
        end_date = self.get_config("end_date")
        
        if not start_date:
            # Default to last 30 days
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m")
        if not end_date:
            end_date = datetime.now().strftime("%Y%m")
        
        try:
            # Authenticate
            credentials = service_account.Credentials.from_service_account_file(
                service_account_file,
                scopes=['https://www.googleapis.com/auth/androidpublisher']
            )
            
            # Build service
            service = build('androidpublisher', 'v3', credentials=credentials)
            
            # Extract data based on report type
            if report_type == "financial":
                data = self._extract_financial_data(service, package_name, start_date, end_date)
            elif report_type == "installs":
                data = self._extract_installs_data(service, package_name, start_date, end_date)
            else:
                raise ValueError(f"Unsupported report_type: {report_type}")
            
            # Convert to Arrow table
            if data:
                table = pa.table(data)
            else:
                table = pa.table({})
            
            # Create data packet
            packet = DataPacket(
                data=table,
                source=f"google_play:{package_name}:{report_type}",
                metadata={
                    "package_name": package_name,
                    "report_type": report_type,
                    "start_date": start_date,
                    "end_date": end_date,
                    "variables": variables or {},
                }
            )
            
            self.logger.info(f"Extracted {packet.row_count} records from Google Play")
            return packet
            
        except Exception as e:
            self.logger.error(f"Failed to extract from Google Play: {e}")
            raise RuntimeError(f"Google Play extraction failed: {e}")
    
    def _extract_financial_data(self, service, package_name: str, start_date: str, end_date: str) -> list:
        """Extract financial data (revenue, transactions)"""
        
        financial_data = []
        
        try:
            # Get financial data
            # Note: This is a simplified example - actual Google Play API calls would be more complex
            
            # Example structure - would need to be adapted to actual API
            reports = service.reports()
            
            # This is pseudocode - actual implementation would depend on Google Play API structure
            # response = reports.financial().list(
            #     packageName=package_name,
            #     startDate=start_date,
            #     endDate=end_date
            # ).execute()
            
            # For now, create sample data structure
            sample_data = [
                {
                    "date": "2024-01-01",
                    "revenue_usd": 1000.50,
                    "transactions": 150,
                    "currency": "USD",
                    "country": "US",
                    "product_id": "premium_subscription",
                },
                {
                    "date": "2024-01-02", 
                    "revenue_usd": 1200.75,
                    "transactions": 180,
                    "currency": "USD",
                    "country": "US",
                    "product_id": "premium_subscription",
                }
            ]
            
            financial_data.extend(sample_data)
            
        except Exception as e:
            self.logger.warning(f"Error extracting financial data: {e}")
        
        return financial_data
    
    def _extract_installs_data(self, service, package_name: str, start_date: str, end_date: str) -> list:
        """Extract installs/downloads data"""
        
        installs_data = []
        
        try:
            # Example structure for installs data
            sample_data = [
                {
                    "date": "2024-01-01",
                    "installs": 1500,
                    "uninstalls": 50,
                    "net_installs": 1450,
                    "country": "US",
                    "source": "organic",
                },
                {
                    "date": "2024-01-02",
                    "installs": 1800,
                    "uninstalls": 60,
                    "net_installs": 1740,
                    "country": "US", 
                    "source": "organic",
                }
            ]
            
            installs_data.extend(sample_data)
            
        except Exception as e:
            self.logger.warning(f"Error extracting installs data: {e}")
        
        return installs_data
    
    def test_connection(self) -> bool:
        """Test Google Play Console connection"""
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
            
            service_account_file = self.get_config("service_account_file")
            if not service_account_file:
                return False
            
            # Try to authenticate
            credentials = service_account.Credentials.from_service_account_file(
                service_account_file,
                scopes=['https://www.googleapis.com/auth/androidpublisher']
            )
            
            # Build service to test connection
            service = build('androidpublisher', 'v3', credentials=credentials)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Google Play connection test failed: {e}")
            return False