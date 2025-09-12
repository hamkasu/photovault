#!/usr/bin/env python3
"""
CSRF Token Verification Script for PhotoVault
Verifies that CSRF tokens have been properly added to all POST forms

Usage:
    python verify_csrf_tokens.py
    python verify_csrf_tokens.py --templates-dir "path/to/templates"

Author: Calmic Sdn Bhd
Date: September 2025
"""

import os
import re
import sys
import argparse
from pathlib import Path
import logging
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('csrf_verification.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class CSRFTokenVerifier:
    def __init__(self, templates_dir="photovault/templates"):
        self.templates_dir = Path(templates_dir)
        self.results = {
            'total_files': 0,
            'files_with_forms': 0,
            'files_with_csrf': 0,
            'files_without_csrf': 0,
            'forms_total': 0,
            'forms_with_csrf': 0,
            'forms_without_csrf': 0
        }
        self.detailed_results = []
        
        # Regular expressions for analysis
        self.form_patterns = [
            re.compile(r'<form[^>]*method\s*=\s*["\']?POST["\']?[^>]*>', re.IGNORECASE | re.MULTILINE),
            re.compile(r'<form[^>]*>.*?method\s*=\s*["\']?POST["\']?.*?>', re.IGNORECASE | re.MULTILINE | re.DOTALL),
        ]
        
        self.csrf_patterns = [
            re.compile(r'\{\{\s*csrf_token\(\)\s*\}\}', re.IGNORECASE),
            re.compile(r'name\s*=\s*["\']csrf_token["\']', re.IGNORECASE),
            re.compile(r'name\s*=\s*["\']_token["\']', re.IGNORECASE),
        ]

    def find_post_forms(self, content):
        """Find all POST forms in content"""
        forms = []
        for pattern in self.form_patterns:
            forms.extend(pattern.findall(content))
        return forms

    def has_csrf_token_in_form(self, form_content):
        """Check if a form section has CSRF token"""
        for pattern in self.csrf_patterns:
            if pattern.search(form_content):
                return True
        return False

    def analyze_file(self, file_path):
        """Analyze a single HTML file for CSRF compliance"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all POST forms
            post_forms = self.find_post_forms(content)
            
            file_result = {
                'file_path': str(file_path.relative_to(self.templates_dir)),
                'post_forms_count': len(post_forms),
                'forms_with_csrf': 0,
                'forms_without_csrf': 0,
                'has_csrf_token': False,
                'status': 'OK',
                'issues': []
            }
            
            if not post_forms:
                file_result['status'] = 'NO_FORMS'
                return file_result
            
            # Check each form for CSRF tokens
            forms_with_csrf = 0
            forms_without_csrf = 0
            
            # Split content into form sections and check each
            form_sections = re.split(r'<form[^>]*>', content, flags=re.IGNORECASE)
            
            for i, form in enumerate(post_forms):
                # Check if this POST form has CSRF token nearby
                if i + 1 < len(form_sections):
                    form_section = form_sections[i + 1].split('</form>')[0] if '</form>' in form_sections[i + 1] else form_sections[i + 1]
                    
                    if self.has_csrf_token_in_form(form + form_section):
                        forms_with_csrf += 1
                    else:
                        forms_without_csrf += 1
                        file_result['issues'].append(f"POST form #{i+1} missing CSRF token")
            
            # Check for any CSRF token in the file
            file_has_csrf = any(pattern.search(content) for pattern in self.csrf_patterns)
            
            file_result.update({
                'forms_with_csrf': forms_with_csrf,
                'forms_without_csrf': forms_without_csrf,
                'has_csrf_token': file_has_csrf
            })
            
            # Determine overall file status
            if forms_without_csrf > 0:
                file_result['status'] = 'MISSING_CSRF'
            elif forms_with_csrf > 0:
                file_result['status'] = 'PROTECTED'
            
            return file_result
            
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return {
                'file_path': str(file_path),
                'error': str(e),
                'status': 'ERROR'
            }

    def find_html_files(self):
        """Find all HTML files in templates directory"""
        if not self.templates_dir.exists():
            logger.error(f"Templates directory not found: {self.templates_dir}")
            return []
        
        return list(self.templates_dir.rglob("*.html"))

    def run_verification(self):
        """Run complete CSRF verification"""
        logger.info("="*60)
        logger.info("CSRF Token Verification for PhotoVault")
        logger.info("="*60)
        logger.info(f"Templates directory: {self.templates_dir.absolute()}")
        logger.info("="*60)
        
        html_files = self.find_html_files()
        
        if not html_files:
            logger.error("No HTML files found!")
            return False
        
        self.results['total_files'] = len(html_files)
        
        # Analyze each file
        for file_path in html_files:
            result = self.analyze_file(file_path)
            self.detailed_results.append(result)
            
            # Update statistics
            if result.get('post_forms_count', 0) > 0:
                self.results['files_with_forms'] += 1
                self.results['forms_total'] += result.get('post_forms_count', 0)
                self.results['forms_with_csrf'] += result.get('forms_with_csrf', 0)
                self.results['forms_without_csrf'] += result.get('forms_without_csrf', 0)
                
                if result.get('has_csrf_token', False):
                    self.results['files_with_csrf'] += 1
                else:
                    self.results['files_without_csrf'] += 1
        
        self.print_detailed_report()
        return self.results['forms_without_csrf'] == 0

    def print_detailed_report(self):
        """Print detailed verification report"""
        logger.info("\n" + "="*60)
        logger.info("VERIFICATION RESULTS")
        logger.info("="*60)
        
        # Overall statistics
        logger.info(f"📊 SUMMARY STATISTICS:")
        logger.info(f"  Total HTML files: {self.results['total_files']}")
        logger.info(f"  Files with POST forms: {self.results['files_with_forms']}")
        logger.info(f"  Files with CSRF tokens: {self.results['files_with_csrf']}")
        logger.info(f"  Files missing CSRF tokens: {self.results['files_without_csrf']}")
        logger.info(f"  Total POST forms found: {self.results['forms_total']}")
        logger.info(f"  Forms with CSRF protection: {self.results['forms_with_csrf']}")
        logger.info(f"  Forms without CSRF protection: {self.results['forms_without_csrf']}")
        
        # Security status
        if self.results['forms_without_csrf'] == 0 and self.results['forms_total'] > 0:
            logger.info("\n🟢 SECURITY STATUS: ✅ FULLY PROTECTED")
            logger.info("All POST forms have CSRF protection!")
        elif self.results['forms_without_csrf'] > 0:
            logger.error("\n🔴 SECURITY STATUS: ❌ VULNERABLE")
            logger.error(f"{self.results['forms_without_csrf']} forms lack CSRF protection!")
        else:
            logger.info("\n🟡 SECURITY STATUS: ℹ️ NO POST FORMS")
            logger.info("No POST forms found (no CSRF protection needed)")
        
        # Detailed file analysis
        logger.info("\n📋 DETAILED FILE ANALYSIS:")
        logger.info("-" * 60)
        
        # Group results by status
        status_groups = defaultdict(list)
        for result in self.detailed_results:
            status_groups[result['status']].append(result)
        
        # Protected files
        if status_groups['PROTECTED']:
            logger.info("✅ PROPERLY PROTECTED FILES:")
            for result in status_groups['PROTECTED']:
                logger.info(f"  ✅ {result['file_path']} ({result['forms_with_csrf']} forms protected)")
        
        # Vulnerable files
        if status_groups['MISSING_CSRF']:
            logger.error("❌ VULNERABLE FILES (NEED CSRF TOKENS):")
            for result in status_groups['MISSING_CSRF']:
                logger.error(f"  ❌ {result['file_path']} ({result['forms_without_csrf']} unprotected forms)")
                for issue in result.get('issues', []):
                    logger.error(f"      - {issue}")
        
        # Files without forms
        if status_groups['NO_FORMS']:
            logger.info("ℹ️ FILES WITHOUT POST FORMS:")
            for result in status_groups['NO_FORMS']:
                logger.info(f"  ℹ️ {result['file_path']} (no POST forms)")
        
        # Error files
        if status_groups['ERROR']:
            logger.error("🔥 FILES WITH ERRORS:")
            for result in status_groups['ERROR']:
                logger.error(f"  🔥 {result['file_path']} - {result.get('error', 'Unknown error')}")
        
        # Recommendations
        logger.info("\n🎯 RECOMMENDATIONS:")
        if self.results['forms_without_csrf'] > 0:
            logger.warning("  ⚠️ Run the CSRF token injector to fix vulnerable forms:")
            logger.warning("     python add_csrf_tokens.py --dry-run")
            logger.warning("     python add_csrf_tokens.py")
        else:
            logger.info("  ✅ No action needed - all forms are properly protected!")
        
        logger.info("\n" + "="*60)

def main():
    """Main function with command line arguments"""
    parser = argparse.ArgumentParser(
        description="Verify CSRF token implementation in PhotoVault templates",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--templates-dir',
        default='photovault/templates',
        help='Path to templates directory (default: photovault/templates)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        verifier = CSRFTokenVerifier(templates_dir=args.templates_dir)
        success = verifier.run_verification()
        
        if success:
            logger.info("🎉 CSRF verification completed - All forms are protected!")
            sys.exit(0)
        else:
            logger.error("❌ CSRF verification found security issues!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.warning("\n⚠️ Verification cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
