"""
Enterprise-grade PDF processing for CBUAE regulations.
Handles Arabic/English mixed content, poor scan quality, and text cleaning.
"""

import re
import os
import json
import hashlib
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CBUAEPDFProcessor:
    """
    Enterprise-grade PDF processor for CBUAE regulatory documents.
    Handles mixed Arabic/English content, OCR, and text cleaning.
    """
    
    def __init__(self):
        self.arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]+')
        self.english_pattern = re.compile(r'[A-Za-z0-9\s\.,;:!?\-\'\"()]+')
        
        # Common Arabic/English headers that appear in CBUAE documents
        self.section_markers = {
            'english': [
                'CHAPTER', 'SECTION', 'ARTICLE', 'REGULATION', 'STANDARD',
                'CIRCULAR', 'NOTICE', 'GUIDELINE', 'PROCEDURE', 'REQUIREMENT',
                'DEFINITION', 'SCOPE', 'APPLICATION', 'COMPLIANCE', 'SUPERVISION'
            ],
            'arabic': [
                'الفصل', 'المادة', 'البند', 'التعريف', 'النطاق', 'التطبيق',
                'الامتثال', 'الإشراف', 'المتطلبات', 'الإجراءات'
            ]
        }
    
    def detect_language(self, text: str) -> str:
        """Detect if text is primarily Arabic or English."""
        if not text.strip():
            return 'unknown'
        
        arabic_chars = len(self.arabic_pattern.findall(text))
        english_chars = len(self.english_pattern.findall(text))
        
        if arabic_chars > english_chars:
            return 'arabic'
        elif english_chars > arabic_chars:
            return 'english'
        else:
            return 'mixed'
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text from PDF extraction."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers/footers
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^Page \d+ of \d+\s*$', '', text, flags=re.MULTILINE)
        
        # Remove common PDF artifacts
        text = re.sub(r'[^\w\s\u0600-\u06FF\u0750-\u077F.,;:!?\-\'\"()/%\n]', ' ', text)
        
        # Fix common OCR errors for Arabic
        text = text.replace('٠', '0').replace('١', '1').replace('٢', '2')
        text = text.replace('٣', '3').replace('٤', '4').replace('٥', '5')
        text = text.replace('٦', '6').replace('٧', '7').replace('٨', '8').replace('٩', '9')
        
        # Fix common OCR errors for English
        text = text.replace('|', 'I').replace('0', 'O', 1) if text.count('0') < 3 else text
        
        # Remove duplicate lines
        lines = text.split('\n')
        cleaned_lines = []
        prev_line = ""
        for line in lines:
            line = line.strip()
            if line and line != prev_line:
                cleaned_lines.append(line)
                prev_line = line
        
        return '\n'.join(cleaned_lines).strip()
    
    def separate_languages(self, text: str) -> Dict[str, str]:
        """Separate Arabic and English content from mixed text."""
        lines = text.split('\n')
        english_lines = []
        arabic_lines = []
        mixed_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            lang = self.detect_language(line)
            if lang == 'english':
                english_lines.append(line)
            elif lang == 'arabic':
                arabic_lines.append(line)
            else:
                mixed_lines.append(line)
        
        return {
            'english': '\n'.join(english_lines),
            'arabic': '\n'.join(arabic_lines),
            'mixed': '\n'.join(mixed_lines),
            'combined': text
        }
    
    def extract_metadata(self, text: str, filename: str) -> Dict[str, Any]:
        """Extract structured metadata from policy document."""
        metadata = {
            'filename': filename,
            'extracted_date': datetime.now().isoformat(),
            'file_hash': hashlib.md5(text.encode()).hexdigest(),
            'document_type': 'regulation',
            'language_distribution': {},
            'sections': [],
            'key_terms': []
        }
        
        # Analyze language distribution
        lang_content = self.separate_languages(text)
        for lang, content in lang_content.items():
            if content:
                metadata['language_distribution'][lang] = len(content)
        
        # Extract document type and number
        doc_patterns = [
            r'CIRCULAR\s+NO\.\s*(\d+/\d+)',
            r'REGULATION\s+NO\.\s*(\d+/\d+)',
            r'STANDARD\s+NO\.\s*(\d+/\d+)',
            r'NOTICE\s+NO\.\s*(\d+/\d+)'
        ]
        
        for pattern in doc_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metadata['document_number'] = match.group(1)
                metadata['document_type'] = pattern.split('\\s+')[0].lower()
                break
        
        # Extract sections
        sections = self._extract_sections(text)
        metadata['sections'] = sections
        
        # Extract key compliance terms
        key_terms = self._extract_key_terms(text)
        metadata['key_terms'] = key_terms
        
        return metadata
    
    def _extract_sections(self, text: str) -> List[Dict[str, str]]:
        """Extract document sections and their content."""
        sections = []
        
        # Look for numbered sections
        section_pattern = r'^(\d+(?:\.\d+)*)\s+(.+?)(?=^\d+(?:\.\d+)*\s+|\Z)'
        matches = re.finditer(section_pattern, text, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            section_num = match.group(1)
            section_content = match.group(2).strip()
            
            # Extract section title (first line)
            lines = section_content.split('\n')
            title = lines[0] if lines else ""
            content = '\n'.join(lines[1:]) if len(lines) > 1 else ""
            
            sections.append({
                'number': section_num,
                'title': title,
                'content': content,
                'language': self.detect_language(content)
            })
        
        return sections
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key compliance and regulatory terms."""
        key_terms = set()
        
        # English compliance terms
        english_terms = [
            'capital adequacy', 'liquidity ratio', 'customer due diligence',
            'anti-money laundering', 'know your customer', 'suspicious transaction',
            'risk management', 'internal controls', 'compliance monitoring',
            'regulatory reporting', 'operational risk', 'credit risk',
            'market risk', 'stress testing', 'governance', 'audit',
            'fintech', 'digital banking', 'cybersecurity', 'data protection'
        ]
        
        # Arabic compliance terms (transliterated)
        arabic_terms = [
            'كفاية رأس المال', 'نسبة السيولة', 'العناية الواجبة بالعملاء',
            'مكافحة غسل الأموال', 'اعرف عميلك', 'معاملة مشبوهة',
            'إدارة المخاطر', 'الضوابط الداخلية', 'مراقبة الامتثال',
            'التقارير التنظيمية', 'المخاطر التشغيلية', 'مخاطر الائتمان'
        ]
        
        all_terms = english_terms + arabic_terms
        
        for term in all_terms:
            if term.lower() in text.lower():
                key_terms.add(term)
        
        return list(key_terms)
    
    def process_pdf_text(self, text: str, filename: str) -> Dict[str, Any]:
        """
        Main processing function for PDF text.
        Returns cleaned, separated, and analyzed content.
        """
        try:
            # Clean the raw text
            cleaned_text = self.clean_text(text)
            
            # Separate languages
            language_content = self.separate_languages(cleaned_text)
            
            # Extract metadata
            metadata = self.extract_metadata(cleaned_text, filename)
            
            # Prepare final result
            result = {
                'status': 'success',
                'filename': filename,
                'processed_date': datetime.now().isoformat(),
                'raw_text': text,
                'cleaned_text': cleaned_text,
                'language_content': language_content,
                'metadata': metadata,
                'quality_score': self._calculate_quality_score(cleaned_text),
                'processing_notes': []
            }
            
            # Add processing notes
            if len(language_content['mixed']) > 0:
                result['processing_notes'].append('Document contains mixed Arabic/English content')
            
            if result['quality_score'] < 0.7:
                result['processing_notes'].append('Low quality scan detected - manual review recommended')
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing PDF text for {filename}: {e}")
            return {
                'status': 'error',
                'filename': filename,
                'error': str(e),
                'processed_date': datetime.now().isoformat()
            }
    
    def _calculate_quality_score(self, text: str) -> float:
        """Calculate a quality score for the extracted text (0-1)."""
        if not text:
            return 0.0
        
        score = 1.0
        
        # Penalize for excessive special characters (indicates OCR issues)
        special_char_ratio = len(re.findall(r'[^\w\s\u0600-\u06FF]', text)) / len(text)
        if special_char_ratio > 0.1:
            score -= 0.2
        
        # Penalize for very short lines (indicates poor extraction)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            avg_line_length = sum(len(line) for line in lines) / len(lines)
            if avg_line_length < 10:
                score -= 0.3
        
        # Penalize for excessive repetition
        unique_lines = set(lines)
        if len(lines) > 0:
            repetition_ratio = 1 - (len(unique_lines) / len(lines))
            if repetition_ratio > 0.3:
                score -= 0.2
        
        return max(0.0, score)
    
    def batch_process_pdfs(self, pdf_directory: str, output_file: str) -> Dict[str, Any]:
        """
        Process multiple PDFs and create a comprehensive policy database.
        """
        results = {
            'processed_files': [],
            'failed_files': [],
            'total_policies': 0,
            'processing_summary': {},
            'created_date': datetime.now().isoformat()
        }
        
        # This would integrate with actual PDF extraction library
        # For now, showing the structure
        logger.info(f"Batch processing PDFs from {pdf_directory}")
        
        return results