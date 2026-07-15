import os
import hashlib
import json
import urllib.request
import urllib.parse
import urllib.error
import time
from datetime import datetime


class VirusTotalAPI:
    def __init__(self, api_key=None):
        """
        Initialize VirusTotal API
        
        Args:
            api_key: Your VirusTotal API key (get from virustotal.com)
        """
        self.api_key = api_key or os.environ.get('VIRUSTOTAL_API_KEY', '')
        self.base_url = "https://www.virustotal.com/api/v3"
        self.quota_remaining = 500  # Free tier: 500 requests/day
        self.last_request_time = 0
        
    def set_api_key(self, api_key):
        """Set API key"""
        self.api_key = api_key
    
    def has_api_key(self):
        """Check if API key is set"""
        return bool(self.api_key)
    
    def _make_request(self, endpoint, method='GET', data=None, files=None):
        """Make API request using urllib"""
        if not self.api_key:
            return {'error': 'API key not set'}
        
        # Rate limiting (4 requests per minute)
        current_time = time.time()
        if current_time - self.last_request_time < 15:
            time.sleep(15 - (current_time - self.last_request_time))
        
        url = f"{self.base_url}/{endpoint}"
        headers = {
            'x-apikey': self.api_key,
            'User-Agent': 'NexusAntivirus/2.0'
        }
        
        try:
            if method == 'GET':
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=30) as response:
                    result = json.loads(response.read().decode('utf-8'))
                    self.last_request_time = time.time()
                    return result
            
            elif method == 'POST':
                if files:
                    # Multipart form data for file upload
                    boundary = '---------------------------' + str(hash(time.time()))
                    headers['Content-Type'] = f'multipart/form-data; boundary={boundary}'
                    
                    # Build multipart data
                    body_parts = []
                    for key, value in files.items():
                        if hasattr(value, 'read'):
                            # File
                            filename = os.path.basename(value.name)
                            body_parts.append(f'--{boundary}')
                            body_parts.append(f'Content-Disposition: form-data; name="{key}"; filename="{filename}"')
                            body_parts.append('Content-Type: application/octet-stream')
                            body_parts.append('')
                            body_parts.append(value.read().decode('latin1'))
                            value.close()
                        else:
                            body_parts.append(f'--{boundary}')
                            body_parts.append(f'Content-Disposition: form-data; name="{key}"')
                            body_parts.append('')
                            body_parts.append(str(value))
                    
                    body_parts.append(f'--{boundary}--')
                    body = '\r\n'.join(body_parts).encode('utf-8')
                    
                    req = urllib.request.Request(url, data=body, headers=headers)
                    with urllib.request.urlopen(req, timeout=60) as response:
                        result = json.loads(response.read().decode('utf-8'))
                        self.last_request_time = time.time()
                        return result
                else:
                    # JSON post
                    headers['Content-Type'] = 'application/json'
                    if data:
                        body = json.dumps(data).encode('utf-8')
                        req = urllib.request.Request(url, data=body, headers=headers)
                    else:
                        req = urllib.request.Request(url, headers=headers)
                    
                    with urllib.request.urlopen(req, timeout=30) as response:
                        result = json.loads(response.read().decode('utf-8'))
                        self.last_request_time = time.time()
                        return result
                        
        except urllib.error.HTTPError as e:
            error_msg = e.read().decode('utf-8') if hasattr(e, 'read') else str(e)
            return {'error': f'HTTP Error {e.code}: {error_msg}'}
        except urllib.error.URLError as e:
            return {'error': f'Network Error: {str(e)}'}
        except Exception as e:
            return {'error': f'Error: {str(e)}'}
    
    def scan_file(self, filepath, callback=None):
        """
        Upload file to VirusTotal for scanning
        
        Args:
            filepath: Path to file
            callback: Callback for progress updates
        
        Returns:
            Scan result dictionary
        """
        if not os.path.exists(filepath):
            return {'error': 'File not found'}
        
        if not self.api_key:
            return {'error': 'API key not set'}
        
        if callback:
            callback('Uploading file to VirusTotal...', 30)
        
        try:
            # Calculate file hash
            sha256_hash = hashlib.sha256()
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256_hash.update(chunk)
            file_hash = sha256_hash.hexdigest()
            
            # Check if file already scanned
            if callback:
                callback('Checking existing reports...', 50)
            
            report = self.get_file_report(file_hash)
            if report and not report.get('error'):
                if callback:
                    callback('Report retrieved from cache!', 100)
                return report
            
            # Upload file
            with open(filepath, 'rb') as f:
                result = self._make_request(
                    'files',
                    method='POST',
                    files={'file': f}
                )
            
            if callback:
                callback('File uploaded, waiting for analysis...', 70)
            
            # Wait for analysis
            analysis_id = result.get('data', {}).get('id')
            if analysis_id:
                # Wait and get results
                for i in range(10):  # Max 10 attempts
                    time.sleep(5)  # Wait 5 seconds between checks
                    status = self.get_analysis_status(analysis_id)
                    if status and status.get('data', {}).get('attributes', {}).get('status') == 'completed':
                        if callback:
                            callback('Analysis complete!', 100)
                        return self.get_file_report(file_hash)
            
            if callback:
                callback('Analysis in progress...', 90)
            
            return result
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_file_report(self, file_hash):
        """
        Get scan report for a file by hash
        
        Args:
            file_hash: SHA-256 hash of file
        
        Returns:
            Report dictionary
        """
        if not self.api_key:
            return {'error': 'API key not set'}
        
        result = self._make_request(f'files/{file_hash}', method='GET')
        
        if result and not result.get('error'):
            # Parse the report
            data = result.get('data', {})
            attributes = data.get('attributes', {})
            
            # Extract relevant info
            stats = attributes.get('last_analysis_stats', {})
            results = attributes.get('last_analysis_results', {})
            
            # Count detections
            total_detections = stats.get('malicious', 0)
            total_engines = len(results)
            
            # Get detection details
            detections = []
            for engine, result_data in results.items():
                if result_data.get('category') == 'malicious':
                    detections.append({
                        'engine': engine,
                        'result': result_data.get('result', 'Malicious'),
                        'category': result_data.get('category', 'malicious')
                    })
            
            return {
                'file_hash': file_hash,
                'file_name': attributes.get('meaningful_name', os.path.basename(file_hash)),
                'detections': total_detections,
                'total_engines': total_engines,
                'detection_ratio': f"{total_detections}/{total_engines}",
                'detections_detail': detections,
                'status': 'malicious' if total_detections > 0 else 'clean',
                'timestamp': datetime.now().isoformat()
            }
        
        return result
    
    def get_analysis_status(self, analysis_id):
        """Get status of file analysis"""
        return self._make_request(f'analyses/{analysis_id}', method='GET')
    
    def scan_url(self, url):
        """
        Scan URL for threats
        
        Args:
            url: URL to scan
        
        Returns:
            Scan result
        """
        if not self.api_key:
            return {'error': 'API key not set'}
        
        return self._make_request(
            'urls',
            method='POST',
            data={'url': url}
        )
    
    def get_url_report(self, url_hash):
        """Get report for URL"""
        return self._make_request(f'urls/{url_hash}', method='GET')
    
    def get_ip_report(self, ip_address):
        """Get report for IP address"""
        return self._make_request(f'ip_addresses/{ip_address}', method='GET')
    
    def get_domain_report(self, domain):
        """Get report for domain"""
        return self._make_request(f'domains/{domain}', method='GET')