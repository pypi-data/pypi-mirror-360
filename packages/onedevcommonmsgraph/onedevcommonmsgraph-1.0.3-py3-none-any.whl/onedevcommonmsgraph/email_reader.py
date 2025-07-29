import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class EmailReader:
    """
    Core email reader class for Microsoft Graph API
    """

    def __init__(self, tenant_id: str, client_id: str, client_secret: str, email_box: str):
        """
        Initialize the email reader
        
        Args:
            tenant_id: Tenant ID
            client_id: Client ID
            client_secret: Client secret
            email_box: Email address of the mailbox to be read
        """
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.email_box = email_box
        self.token = self._get_token()

    def list_emails(self, limit: int = 50, filter_query: Optional[str] = None) -> List[Dict]:
        """
        List emails from the mailbox
        
        Args:
            limit: Maximum number of emails to return
            filter_query: Optional OData filter (e.g., "isRead eq false")
        
        Returns:
            List of emails
        """
        url = f'https://graph.microsoft.com/v1.0/users/{self.email_box}/messages'
        
        params = {
            '$top': limit,
            '$orderby': 'receivedDateTime desc',
            '$select': 'id,subject,from,receivedDateTime,isRead,bodyPreview,hasAttachments'
        }
        
        if filter_query:
            params['$filter'] = filter_query
            
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json().get('value', [])
            
        except requests.exceptions.RequestException:
            return []

    def read_detailed_email(self, email_id: str) -> Optional[Dict]:
        """
        Read a specific email with all details
        
        Args:
            email_id: Email ID
            
        Returns:
            Complete email data or None if error
        """
        url = f'https://graph.microsoft.com/v1.0/users/{self.email_box}/messages/{email_id}'
        
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException:
            return None

    def list_unread_emails(self) -> List[Dict]:
        """
        List only unread emails
        
        Returns:
            List of unread emails
        """
        return self.list_emails(filter_query="isRead eq false")

    def list_emails_period(self, days: int = 7) -> List[Dict]:
        """
        List emails from a specific period
        
        Args:
            days: Number of days to search emails (default: 7)
            
        Returns:
            List of emails from the period
        """
        date_limit = (datetime.now() - timedelta(days=days)).isoformat() + 'Z'
        filter_query = f"receivedDateTime ge {date_limit}"
        
        return self.list_emails(filter_query=filter_query)

    def mark_as_read(self, email_id: str) -> bool:
        """
        Mark an email as read
        
        Args:
            email_id: Email ID
            
        Returns:
            True if successful, False otherwise
        """
        url = f'https://graph.microsoft.com/v1.0/users/{self.email_box}/messages/{email_id}'
        
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        data = {"isRead": True}
        
        try:
            response = requests.patch(url, headers=headers, json=data)
            response.raise_for_status()
            return True
            
        except requests.exceptions.RequestException:
            return False

    def _get_token(self) -> str:
        """
        Get access token from Microsoft Graph
        
        Returns:
            Access token string
        """
        url = f'https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'client_id': self.client_id,
            'scope': 'https://graph.microsoft.com/.default',
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()['access_token']


if __name__ == "__main__":
    # Simple usage example
    tenant_id = 'X'
    client_id = 'X' 
    client_secret = 'X'
    email_box = 'X'
    
    try:
        # Create email reader
        reader = EmailReader(tenant_id, client_id, client_secret, email_box)
        
        # List latest 5 emails
        print("📧 Listing latest 5 emails...")
        emails = reader.list_emails(limit=5)
        
        if emails:
            print(f"✅ Found {len(emails)} emails")
            for email in emails:
                subject = email.get('subject', 'No subject')
                sender = email.get('from', {}).get('emailAddress', {}).get('address', 'Unknown')
                date = email.get('receivedDateTime', '')
                read_status = "Read" if email.get('isRead', False) else "Unread"
                print(f"  • {subject[:50]}... | From: {sender} | {read_status}")
        else:
            print("❌ No emails found")
            
        # Check unread emails
        unread_emails = reader.list_unread_emails()
        print(f"\n📬 Unread emails: {len(unread_emails)}")
        
    except Exception as e:
        print(f"❌ Error: {e}") 