from email_reader import EmailReader
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union

class EmailAnalyzer:
    """
    Class for flexible email analysis with configurable options
    """
    
    # Types of emails that can be read
    EMAIL_TYPES = {
        'all': 'All emails',
        'latest': 'Latest N emails',
        'unread': 'Only unread emails',
        'period': 'Emails from a specific period',
        'by_sender': 'Emails from specific sender',
        'by_subject': 'Emails with term in subject'
    }
    
    # Types of information that can be extracted
    INFORMATION_TYPES = {
        'all': 'All available information',
        'basic': 'Basic information (ID, subject, sender, date)',
        'status': 'Email status (read/unread, attachments)',
        'senders': 'Only sender information',
        'content': 'Email content',
        'attachments': 'Attachment information',
        'summary': 'Executive summary'
    }

    def __init__(self, tenant_id: str, client_id: str, client_secret: str, email_box: str):
        """
        Initializes the email analyzer
        
        Args:
            tenant_id: Tenant ID
            client_id: Client ID
            client_secret: Client secret
            email_box: Email address of the mailbox to be analyzed
        """
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.email_box = email_box
        self.reader = EmailReader(tenant_id, client_id, client_secret, email_box)

    def analyze_emails(self, 
                       email_type: str = 'latest',
                       information_to_extract: Union[str, List[str]] = 'all',
                       parameters: Optional[Dict] = None,
                       save_file: bool = True) -> Dict:
        """
        Analyzes emails according to specified configuration
        
        Args:
            email_type: Type of emails to read ('all', 'latest', 'unread', 'period', 'by_sender', 'by_subject')
            information_to_extract: Which information to extract ('all', 'basic', 'status', 'senders', 'content', 'attachments', 'summary') or list of fields
            parameters: Additional parameters ('limit', 'days', 'sender', 'search_term', etc.)
            save_file: If True, automatically saves to JSON file
            
        Returns:
            Dictionary with analysis results in JSON format
        """
        if parameters is None:
            parameters = {}
            
        try:
            print(f"🔍 Starting email analysis ({email_type})...")
            
            # 1. Search emails according to criteria
            email_summaries = self._search_emails(email_type, parameters)
            
            if not email_summaries:
                error_result = {
                    "success": False,
                    "error": "No emails found with the specified criteria",
                    "total_emails": 0,
                    "emails": []
                }
                if save_file:
                    self._save_file_automatically(error_result, email_type, information_to_extract)
                return error_result
            
            # 2. Get complete details for each email
            detailed_emails = []
            total_emails = len(email_summaries)
            print(f"📧 Processing {total_emails} emails...")
            
            for i, email_summary in enumerate(email_summaries, 1):
                email_id = email_summary.get('id')
                complete_email = self.reader.read_detailed_email(email_id)
                if complete_email:
                    detailed_emails.append(complete_email)
                
                # Show progress
                if i % 10 == 0 or i == total_emails:
                    print(f"   ⏳ Processed {i}/{total_emails} emails...")
            
            # 3. Extract information as requested
            processed_emails = []
            for email in detailed_emails:
                email_info = self._extract_information(email, information_to_extract)
                processed_emails.append(email_info)
            
            # 4. Generate final result
            result = {
                "success": True,
                "configuration": {
                    "email_type": email_type,
                    "information_extracted": information_to_extract,
                    "parameters": parameters
                },
                "total_emails": len(processed_emails),
                "emails": processed_emails,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            # 5. Add statistics if requested
            if information_to_extract == 'all' or 'summary' in information_to_extract:
                result["statistics"] = self._generate_statistics(processed_emails)
            
            # 6. Save file automatically if requested
            if save_file:
                filename = self._save_file_automatically(result, email_type, information_to_extract)
                result["saved_file"] = filename
                
                # Show summary
                print(f"✅ Analysis completed!")
                print(f"📊 Total emails analyzed: {result['total_emails']}")
                print(f"💾 Result saved to: {filename}")
                
                # Show statistics if available
                if 'statistics' in result:
                    stats = result['statistics']
                    print(f"\n📈 STATISTICS:")
                    print(f"   • Read emails: {stats.get('read_emails', 0)}")
                    print(f"   • Unread emails: {stats.get('unread_emails', 0)}")
                    print(f"   • Read rate: {stats.get('read_rate', 0)}%")
                    print(f"   • Emails with attachments: {stats.get('emails_with_attachments', 0)}")
            
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": f"Error during analysis: {str(e)}",
                "total_emails": 0,
                "emails": []
            }
            if save_file:
                self._save_file_automatically(error_result, email_type, information_to_extract)
            return error_result

    def _search_emails(self, email_type: str, parameters: Dict) -> List[Dict]:
        """Search emails according to specified type"""
        
        if email_type == 'all':
            limit = parameters.get('limit', 1000)
            return self.reader.list_emails(limit=limit)
            
        elif email_type == 'latest':
            limit = parameters.get('limit', 10)
            return self.reader.list_emails(limit=limit)
            
        elif email_type == 'unread':
            return self.reader.list_unread_emails()
            
        elif email_type == 'period':
            days = parameters.get('days', 7)
            return self.reader.list_emails_period(days=days)
            
        elif email_type == 'by_sender':
            sender = parameters.get('sender', '')
            if not sender:
                raise ValueError("Parameter 'sender' is required for type 'by_sender'")
            filter_query = f"from/emailAddress/address eq '{sender}'"
            limit = parameters.get('limit', 100)
            return self.reader.list_emails(limit=limit, filter_query=filter_query)
            
        elif email_type == 'by_subject':
            term = parameters.get('subject_term', '')
            if not term:
                raise ValueError("Parameter 'subject_term' is required for type 'by_subject'")
            filter_query = f"contains(subject,'{term}')"
            limit = parameters.get('limit', 100)
            return self.reader.list_emails(limit=limit, filter_query=filter_query)
            
        else:
            raise ValueError(f"Email type '{email_type}' not supported. Use: {list(self.EMAIL_TYPES.keys())}")

    def _extract_information(self, email: Dict, information_to_extract: Union[str, List[str]]) -> Dict:
        """Extract specific information from email"""
        
        if isinstance(information_to_extract, str):
            if information_to_extract == 'all':
                return self._extract_all_information(email)
            elif information_to_extract == 'basic':
                return self._extract_basic_information(email)
            elif information_to_extract == 'status':
                return self._extract_status(email)
            elif information_to_extract == 'senders':
                return self._extract_senders(email)
            elif information_to_extract == 'content':
                return self._extract_content(email)
            elif information_to_extract == 'attachments':
                return self._extract_attachments(email)
            elif information_to_extract == 'summary':
                return self._extract_summary(email)
        
        elif isinstance(information_to_extract, list):
            # Custom list of fields
            return self._extract_custom_fields(email, information_to_extract)
        
        # Fallback to basic information
        return self._extract_basic_information(email)

    def _extract_all_information(self, email: Dict) -> Dict:
        """Extract all available information"""
        return {
            "id": email.get('id'),
            "subject": email.get('subject'),
            "sender": self._format_email_address(email.get('from', {})),
            "recipients": [self._format_email_address(dest) for dest in email.get('toRecipients', [])],
            "cc": [self._format_email_address(cc) for cc in email.get('ccRecipients', [])],
            "received_date": self._format_date(email.get('receivedDateTime')),
            "sent_date": self._format_date(email.get('sentDateTime')),
            "is_read": email.get('isRead', False),
            "has_attachments": email.get('hasAttachments', False),
            "importance": email.get('importance', 'normal'),
            "content": {
                "type": email.get('body', {}).get('contentType'),
                "size": len(email.get('body', {}).get('content', '')),
                "preview": email.get('bodyPreview', ''),
                "full_content": email.get('body', {}).get('content', '')
            },
            "attachments": self._process_attachments(email.get('attachments', [])),
            "web_link": email.get('webLink')
        }

    def _extract_basic_information(self, email: Dict) -> Dict:
        """Extract only basic information"""
        return {
            "id": email.get('id'),
            "subject": email.get('subject'),
            "sender": self._format_email_address(email.get('from', {})),
            "received_date": self._format_date(email.get('receivedDateTime'))
        }

    def _extract_status(self, email: Dict) -> Dict:
        """Extract only status information"""
        return {
            "id": email.get('id'),
            "is_read": email.get('isRead', False),
            "has_attachments": email.get('hasAttachments', False),
            "importance": email.get('importance', 'normal')
        }

    def _extract_senders(self, email: Dict) -> Dict:
        """Extract only sender information"""
        return {
            "id": email.get('id'),
            "sender": self._format_email_address(email.get('from', {})),
            "recipients": [self._format_email_address(dest) for dest in email.get('toRecipients', [])],
            "cc": [self._format_email_address(cc) for cc in email.get('ccRecipients', [])]
        }

    def _extract_content(self, email: Dict) -> Dict:
        """Extract only email content"""
        body = email.get('body', {})
        return {
            "id": email.get('id'),
            "subject": email.get('subject'),
            "content": {
                "type": body.get('contentType'),
                "size": len(body.get('content', '')),
                "preview": email.get('bodyPreview', ''),
                "full_content": body.get('content', '')
            }
        }

    def _extract_attachments(self, email: Dict) -> Dict:
        """Extract attachment information"""
        return {
            "id": email.get('id'),
            "has_attachments": email.get('hasAttachments', False),
            "attachments": self._process_attachments(email.get('attachments', []))
        }

    def _extract_summary(self, email: Dict) -> Dict:
        """Extract email summary"""
        return {
            "id": email.get('id'),
            "subject": email.get('subject'),
            "sender_email": email.get('from', {}).get('emailAddress', {}).get('address'),
            "date": self._format_date(email.get('receivedDateTime')),
            "read": email.get('isRead', False),
            "has_attachments": email.get('hasAttachments', False),
            "preview": email.get('bodyPreview', '')[:100] + '...' if email.get('bodyPreview', '') else ''
        }

    def _extract_custom_fields(self, email: Dict, fields: List[str]) -> Dict:
        """Extract specific fields requested by user"""
        result = {"id": email.get('id')}
        
        for field in fields:
            if field == 'subject':
                result['subject'] = email.get('subject')
            elif field == 'sender':
                result['sender'] = self._format_email_address(email.get('from', {}))
            elif field == 'date':
                result['received_date'] = self._format_date(email.get('receivedDateTime'))
            elif field == 'content':
                result['content'] = email.get('body', {}).get('content', '')
            elif field == 'preview':
                result['preview'] = email.get('bodyPreview', '')
            elif field == 'attachments':
                result['attachments'] = self._process_attachments(email.get('attachments', []))
            elif field == 'status':
                result['is_read'] = email.get('isRead', False)
            # Add more fields as needed
        
        return result

    def _format_email_address(self, address_info: Dict) -> Dict:
        """Format email address information"""
        if not address_info:
            return {}
        
        email_address = address_info.get('emailAddress', {})
        return {
            "name": email_address.get('name', ''),
            "email": email_address.get('address', '')
        }

    def _format_date(self, iso_date: str) -> str:
        """Convert ISO date to Brazilian format"""
        if not iso_date:
            return ''
        try:
            dt = datetime.fromisoformat(iso_date.replace('Z', '+00:00'))
            return dt.strftime('%d/%m/%Y %H:%M:%S')
        except:
            return iso_date

    def _process_attachments(self, attachments: List[Dict]) -> List[Dict]:
        """Process attachment list"""
        return [
            {
                "name": attachment.get('name', 'Unnamed attachment'),
                "size": attachment.get('size', 0),
                "type": attachment.get('contentType', 'Unknown')
            }
            for attachment in attachments
        ]

    def _generate_statistics(self, emails: List[Dict]) -> Dict:
        """Generate statistics from analyzed emails"""
        total = len(emails)
        if total == 0:
            return {}
        
        # Count read/unread emails
        read = sum(1 for email in emails if email.get('is_read', False))
        unread = total - read
        
        # Count emails with attachments
        with_attachments = sum(1 for email in emails if email.get('has_attachments', False))
        
        # Top senders
        senders = {}
        for email in emails:
            sender_email = email.get('sender', {}).get('email', 'Unknown')
            senders[sender_email] = senders.get(sender_email, 0) + 1
        
        top_senders = sorted(senders.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_emails": total,
            "read_emails": read,
            "unread_emails": unread,
            "read_rate": round((read / total) * 100, 1),
            "emails_with_attachments": with_attachments,
            "attachment_percentage": round((with_attachments / total) * 100, 1),
            "top_senders": [{"email": email, "count": count} for email, count in top_senders]
        }

    def save_result(self, result: Dict, filename: str = None) -> str:
        """Save result to JSON file"""
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"email_analysis_{timestamp}.json"
        
        # Ensure filename is in logs directory
        if not os.path.dirname(filename):
            filename = os.path.join(logs_dir, filename)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return filename

    def _save_file_automatically(self, result: Dict, email_type: str, information_to_extract: Union[str, List[str]]) -> str:
        """Automatically save result with formatted name and unique datetime"""
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # Generate unique timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create descriptive name based on parameters
        if isinstance(information_to_extract, list):
            info_str = "_".join(information_to_extract[:2])  # Use only first 2 to avoid too long names
            if len(information_to_extract) > 2:
                info_str += "_etc"
        else:
            info_str = information_to_extract
        
        # Generate filename in logs directory
        filename = os.path.join(logs_dir, f"email_analysis_{timestamp}.json")
        
        # Save file with pretty formatting
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return filename

    @classmethod
    def list_options(cls):
        """List all available options"""
        print("🎯 AVAILABLE EMAIL TYPES:")
        for key, desc in cls.EMAIL_TYPES.items():
            print(f"  '{key}' - {desc}")
        
        print("\n📊 AVAILABLE INFORMATION TYPES:")
        for key, desc in cls.INFORMATION_TYPES.items():
            print(f"  '{key}' - {desc}")


# Usage example
if __name__ == "__main__":
    # Configuration
    tenantId = 'X'
    clientId = 'X' 
    clientSecret = 'X'
    emailBox = 'X'
    
    # Create analyzer
    analyzer = EmailAnalyzer(tenantId, clientId, clientSecret, emailBox)
    
    # Example 1: Latest 5 emails with basic information
    result1 = analyzer.analyze_emails(
        email_type='latest',
        information_to_extract='basic',
        parameters={'limit': 5}
    )
    
    print("📧 EXAMPLE 1 - Latest 5 emails (basic):")
    print(json.dumps(result1, ensure_ascii=False, indent=2))
    
    # Example 2: Unread emails with all information
    result2 = analyzer.analyze_emails(
        email_type='unread',
        information_to_extract='all'
    )
    
    print("\n📬 EXAMPLE 2 - Unread emails (complete):")
    print(json.dumps(result2, ensure_ascii=False, indent=2))
    
    # Save result
    file = analyzer.save_result(result2)
    print(f"\n💾 Result saved to: {file}") 