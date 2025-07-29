#!/usr/bin/env python3
"""
CeWLio (Custom Word List Generator) - Python Version (CeWLio just like Coolio!)
Extracts words, emails, and metadata from HTML content after JavaScript execution.

Based on the original Ruby CeWL by Robin Wood (robin@digi.ninja)
"""

import re
from pathlib import Path
from urllib.parse import urlparse, urljoin
from collections import Counter
import asyncio
from .extractors import extract_html


class CeWLio:
    def __init__(self, min_word_length=3, max_word_length=None, lowercase=False, 
                 with_numbers=False, convert_umlauts=False, show_count=False):
        self.min_word_length = min_word_length
        self.max_word_length = max_word_length
        self.lowercase = lowercase
        self.with_numbers = with_numbers
        self.convert_umlauts = convert_umlauts
        self.show_count = show_count
        
        # Data storage
        self.words = Counter()
        self.emails = set()
        self.metadata = set()
        self.word_groups = Counter()
        
        # Compile regex patterns
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.mailto_pattern = re.compile(r'mailto:([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})', re.IGNORECASE)
        self.html_tag_pattern = re.compile(r'<[^>]+>')
        self.html_entity_pattern = re.compile(r'&[a-zA-Z]+;')
        self.comment_pattern = re.compile(r'<!--.*?-->', re.DOTALL)
                
        # Umlaut conversion mapping
        self.umlaut_map = {
            'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss',
            'Ä': 'Ae', 'Ö': 'Oe', 'Ü': 'Ue'
        }

    def clean_html(self, html_content):
        """Clean HTML content by removing tags, comments, and entities."""
        # Remove HTML comments
        html_content = self.comment_pattern.sub('', html_content)
        
        # Remove script tags and their content
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove style tags and their content
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags
        html_content = self.html_tag_pattern.sub(' ', html_content)
        
        # Remove HTML entities
        html_content = self.html_entity_pattern.sub('', html_content)
        
        # Extract text from common attributes
        attribute_patterns = [
            r'alt="([^"]*)"',
            r'title="([^"]*)"',
            r'placeholder="([^"]*)"',
            r'aria-label="([^"]*)"'
        ]
        
        for pattern in attribute_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                html_content += f" {match}"
        
        return html_content

    def extract_emails(self, text):
        """Extract email addresses from text."""
        # First, extract emails using the standard pattern
        emails = self.email_pattern.findall(text)
        
        # Also extract emails from mailto: links
        mailto_emails = self.mailto_pattern.findall(text)
        
        # Combine both results
        all_emails = emails + mailto_emails
        
        for email in all_emails:
            self.emails.add(email.lower())
        return all_emails

    def extract_metadata(self, html_content):
        """Extract metadata from HTML meta tags."""
        # Extract meta description
        desc_pattern = r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']'
        desc_matches = re.findall(desc_pattern, html_content, re.IGNORECASE)
        
        # Extract meta keywords
        keywords_pattern = r'<meta[^>]*name=["\']keywords["\'][^>]*content=["\']([^"\']*)["\']'
        keywords_matches = re.findall(keywords_pattern, html_content, re.IGNORECASE)
        
        # Extract author information
        author_pattern = r'<meta[^>]*name=["\']author["\'][^>]*content=["\']([^"\']*)["\']'
        author_matches = re.findall(author_pattern, html_content, re.IGNORECASE)
        
        # Add to metadata set
        for match in desc_matches + keywords_matches + author_matches:
            if match.strip():
                self.metadata.add(match.strip())

    def process_words(self, text, group_size=None):
        """Process text and extract words."""
        # Convert to lowercase if requested
        if self.lowercase:
            text = text.lower()
        
        # Convert umlauts if requested
        if self.convert_umlauts:
            for umlaut, replacement in self.umlaut_map.items():
                text = text.replace(umlaut, replacement)
        
        # Split into words
        if self.with_numbers:
            # Allow alphanumeric characters
            words = re.findall(r'\b[a-zA-Z0-9]+\b', text)
        else:
            # Only alphabetic characters
            words = re.findall(r'\b[a-zA-Z]+\b', text)
        
        # Filter words by length for individual word counting
        filtered_words = []
        for word in words:
            if len(word) >= self.min_word_length:
                if self.max_word_length is None or len(word) <= self.max_word_length:
                    filtered_words.append(word)
        
        # Count words (only filtered words)
        for word in filtered_words:
            self.words[word] += 1
        
        # Generate word groups if requested (use original words, not filtered)
        if group_size and group_size > 1:
            for i in range(len(words) - group_size + 1):
                group = ' '.join(words[i:i + group_size])
                self.word_groups[group] += 1

    def process_html(self, html_content, group_size=None):
        """Process HTML content to extract words, emails, and metadata."""
        # Extract metadata first
        self.extract_metadata(html_content)
        
        # Extract emails from original HTML (before cleaning)
        self.extract_emails(html_content)
        
        # Clean HTML
        clean_text = self.clean_html(html_content)
        
        # Process words
        self.process_words(clean_text, group_size)

    def save_results(self, output_file=None, email_file=None, metadata_file=None):
        """Save results to files or print to console."""
        output = output_file if output_file else sys.stdout
        
        # Save words
        if self.words:
            sorted_words = sorted(self.words.items(), key=lambda x: (-x[1], x[0]))
            for word, count in sorted_words:
                if self.show_count:
                    print(f"{word}, {count}", file=output)
                else:
                    print(word, file=output)
        
        # Save word groups
        if self.word_groups:
            sorted_groups = sorted(self.word_groups.items(), key=lambda x: (-x[1], x[0]))
            for group, count in sorted_groups:
                if self.show_count:
                    print(f"{group}, {count}", file=output)
                else:
                    print(group, file=output)
        
        # Save emails
        if self.emails:
            email_output = email_file if email_file else output
            sorted_emails = sorted(self.emails)
            for email in sorted_emails:
                print(email, file=email_output)
        
        # Save metadata
        if self.metadata:
            metadata_output = metadata_file if metadata_file else output
            sorted_metadata = sorted(self.metadata)
            for meta in sorted_metadata:
                print(meta, file=metadata_output)
        


async def process_url_with_cewlio(url, cewlio_instance, group_size=None, output_file=None, 
                               email_file=None, metadata_file=None, wait_time=0, 
                               headless=True, timeout=30000):
    """Extract HTML from URL and process it with CeWLio."""
    print(f"Processing URL: {url}")
    
    # Extract HTML
    html_content = await extract_html(
        url=url,
        output_file=None,  # We don't want to save the HTML file
        wait_time=wait_time,
        headless=headless,
        timeout=timeout
    )
    
    if html_content is None:
        print(f"Failed to extract HTML from {url}")
        return False
    
    # Process with CeWLio
    cewlio_instance.process_html(html_content, group_size)
    
    # Save results
    cewlio_instance.save_results(output_file, email_file, metadata_file)
    
    return True

