#!/usr/bin/env python3
"""
Production-ready PDF to Q&A Dataset Generator
Automates the creation of Question-Answer datasets from PDF files using Gemini API
Enhanced with multi-machine support, adaptive rate limiting, and robust API key management
"""

import argparse
import io
import json
import logging
import os
import random
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import traceback

import fitz  # PyMuPDF
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
from PIL import Image


class PDFToQAGenerator:
    """Main class for generating Q&A datasets from PDF files."""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the generator with configuration."""
        self.config = self._load_config(config_path)
        self._setup_logging()
        self._setup_output_directory()
        
        # API key management with thread safety
        self._current_api_key_index = 0
        self._api_key_lock = threading.Lock()
        self._api_call_times = []  # Track API call timing for rate limiting
        self._last_api_call_time = 0
        self._current_delay = self.config.get('min_delay_between_calls', 1)
        
        # Multi-machine support
        self.machine_id = self.config.get('machine_id', 0)
        self.total_machines = self.config.get('total_machines', 1)
        
        self._configure_gemini()
        
        # Track processed files for resume functionality
        self.processed_files = self._get_already_processed_files()
        
        self.logger.info(f"Initialized PDF to Q&A Generator")
        self.logger.info(f"Configuration loaded from: {config_path}")
        self.logger.info(f"Machine ID: {self.machine_id}/{self.total_machines}")
        self.logger.info(f"Found {len(self.processed_files)} already processed files")
        self.logger.info(f"API rate limiting: {self.config.get('adaptive_delay', True)} (adaptive)")
        self.logger.info(f"Available API keys: {len(self.config['api_keys'])}")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Validate required keys
            required_keys = [
                'api_keys', 'model_name', 'pdf_folder', 'output_folder',
                'output_filename', 'log_filename', 'max_questions_per_pdf',
                'api_timeout_seconds', 'num_workers'
            ]
            
            for key in required_keys:
                if key not in config:
                    raise ValueError(f"Missing required configuration key: {key}")
            
            # Set default values for optional new parameters
            config.setdefault('api_rate_limit_delay', 2)
            config.setdefault('api_key_rotation_delay', 5)
            config.setdefault('max_retries_per_key', 2)
            config.setdefault('machine_id', 0)
            config.setdefault('total_machines', 1)
            config.setdefault('adaptive_delay', True)
            config.setdefault('min_delay_between_calls', 1)
            config.setdefault('max_delay_between_calls', 10)
            
            return config
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
    
    def _setup_logging(self):
        """Setup logging to both console and file."""
        # Create logger
        self.logger = logging.getLogger('PDFToQAGenerator')
        self.logger.setLevel(logging.INFO)
        
        # Clear any existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Create formatters
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handler
        file_handler = logging.FileHandler(
            self.config['log_filename'], 
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def _setup_output_directory(self):
        """Create output directory if it doesn't exist."""
        output_dir = Path(self.config['output_folder'])
        output_dir.mkdir(exist_ok=True)
        self.logger.info(f"Output directory ready: {output_dir}")
    
    def _configure_gemini(self):
        """Configure Gemini API with the first available key."""
        if not self.config['api_keys']:
            raise ValueError("No API keys provided in configuration")
        
        genai.configure(api_key=self.config['api_keys'][self._current_api_key_index])
        self.logger.info(f"Configured Gemini API with key index: {self._current_api_key_index}")
    
    def _get_already_processed_files(self) -> Set[str]:
        """Get list of already processed PDF files from existing output file."""
        output_path = Path(self.config['output_folder']) / self.config['output_filename']
        processed_files = set()
        
        if not output_path.exists():
            return processed_files
        
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        qa_data = json.loads(line)
                        if 'kaynak' in qa_data:
                            processed_files.add(qa_data['kaynak'])
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"Skipping invalid JSON on line {line_num}: {e}")
                        continue
            
            # Get unique filenames
            unique_files = set()
            for filename in processed_files:
                unique_files.add(filename)
            
            self.logger.info(f"Found {len(unique_files)} unique processed files")
            return unique_files
            
        except Exception as e:
            self.logger.error(f"Error reading existing output file: {e}")
            return set()
    
    def _rotate_api_key(self) -> bool:
        """Rotate to the next API key with thread safety. Returns True if successful, False if no more keys."""
        with self._api_key_lock:
            self._current_api_key_index += 1
            
            if self._current_api_key_index >= len(self.config['api_keys']):
                self.logger.error("All API keys exhausted")
                return False
            
            try:
                genai.configure(api_key=self.config['api_keys'][self._current_api_key_index])
                self.logger.info(f"Rotated to API key index: {self._current_api_key_index}")
                
                # Add delay after key rotation to avoid immediate rate limiting
                delay = self.config.get('api_key_rotation_delay', 5)
                self.logger.info(f"Waiting {delay}s after API key rotation...")
                time.sleep(delay)
                
                return True
            except Exception as e:
                self.logger.error(f"Failed to configure new API key: {e}")
                return False
    
    def _adaptive_rate_limit(self):
        """Implement adaptive rate limiting to avoid API limits."""
        current_time = time.time()
        
        # Clean old call times (keep only last minute)
        self._api_call_times = [t for t in self._api_call_times if current_time - t < 60]
        
        # Check if we're making too many calls
        calls_per_minute = len(self._api_call_times)
        
        if self.config.get('adaptive_delay', True):
            # Adaptive delay based on recent call frequency
            if calls_per_minute > 50:  # High frequency
                self._current_delay = min(self._current_delay * 1.5, self.config['max_delay_between_calls'])
            elif calls_per_minute < 20:  # Low frequency
                self._current_delay = max(self._current_delay * 0.8, self.config['min_delay_between_calls'])
        else:
            # Fixed delay
            self._current_delay = self.config.get('api_rate_limit_delay', 2)
        
        # Ensure minimum time between calls
        time_since_last_call = current_time - self._last_api_call_time
        if time_since_last_call < self._current_delay:
            sleep_time = self._current_delay - time_since_last_call
            if sleep_time > 0.1:  # Only log significant delays
                self.logger.debug(f"Rate limiting: waiting {sleep_time:.1f}s (current delay: {self._current_delay:.1f}s)")
            time.sleep(sleep_time)
        
        # Record this call
        self._api_call_times.append(time.time())
        self._last_api_call_time = time.time()
    
    def _extract_pdf_content(self, pdf_path: Path) -> Tuple[str, List[bytes]]:
        """Extract text and images from PDF using PyMuPDF."""
        try:
            doc = fitz.open(pdf_path)
            all_text = ""
            all_images = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Extract text
                text = page.get_text()
                all_text += f"\n--- Sayfa {page_num + 1} ---\n{text}"
                
                # Extract images
                image_list = page.get_images()
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        
                        if pix.n - pix.alpha < 4:  # Check if it's not CMYK
                            img_data = pix.pil_tobytes(format="PNG")
                            all_images.append(img_data)
                        else:
                            # Convert CMYK to RGB first
                            pix_rgb = fitz.Pixmap(fitz.csRGB, pix)
                            img_data = pix_rgb.pil_tobytes(format="PNG")
                            all_images.append(img_data)
                            pix_rgb = None
                        
                        pix = None
                    except Exception as e:
                        self.logger.warning(f"Failed to extract image {img_index} from page {page_num + 1}: {e}")
                        continue
                
                # Extract tables as images (render page areas with tables)
                # Skip table extraction for pages without proper text layer to reduce noise
                try:
                    # Check if page has text layer (required for table detection)
                    if text.strip():  # Only try table extraction if page has text
                        tables = page.find_tables()
                        if tables:  # Only process if tables are found
                            for table_index, table in enumerate(tables):
                                try:
                                    # Get table bounding box and render as image
                                    bbox = table.bbox
                                    mat = fitz.Matrix(2, 2)  # 2x zoom for better quality
                                    pix = page.get_pixmap(matrix=mat, clip=bbox)
                                    img_data = pix.pil_tobytes(format="PNG")
                                    all_images.append(img_data)
                                    pix = None
                                except Exception as e:
                                    # Only log if it's not a common issue
                                    if "not a textpage" not in str(e).lower() and "weakly-referenced" not in str(e).lower():
                                        self.logger.warning(f"Failed to extract table {table_index} from page {page_num + 1}: {e}")
                                    continue
                except Exception as e:
                    # Only log non-common table extraction issues
                    if "not a textpage" not in str(e).lower() and "weakly-referenced" not in str(e).lower():
                        self.logger.warning(f"Failed to extract tables from page {page_num + 1}: {e}")
            
            doc.close()
            self.logger.info(f"Extracted content from {pdf_path.name}: {len(all_text)} chars, {len(all_images)} images")
            return all_text, all_images
            
        except Exception as e:
            self.logger.error(f"Failed to extract content from {pdf_path}: {e}")
            raise
    
    def _create_prompt(self) -> str:
        """Create the prompt for Gemini API."""
        max_questions = self.config['max_questions_per_pdf']
        
        prompt = f"""
Sen, büyük dil modellerini eğitmek için veri seti hazırlayan uzman bir veri analisti ve eğitim tasarımcısısın.
Görevin, sana sunulan PDF dokümanının içeriğini (metin, tablolar ve görseller dahil) derinlemesine analiz ederek, yüksek kaliteli ve çeşitli Soru-Cevap (S-C) çiftleri oluşturmaktır.

**TEMEL GÖREV:**
Kaliteyi niceliğe tercih et. Bu belgenin içeriğinin desteklediği kadar S-C çifti üret. Eğer bir konu hakkında yeterli bilgi yoksa, o konuda zorla soru üretme. Amacımız, tekrar eden veya düşük değerli sorular olmadan, zengin ve çeşitli bir veri seti oluşturmaktır.

**ÖNEMLİ SINIRLAMA:**
Ne kadar üretken olursan ol, üreteceğin S-C çifti sayısı **KESİNLİKLE {max_questions} sayısını aşmamalıdır.**

**ÇIKTI KURALLARI:**
1.  Çıktın, bir JSON listesi (array of objects) formatında olmalıdır. Başka hiçbir metin veya açıklama ekleme.
2.  Her bir JSON nesnesi şu şemaya sahip olmalıdır: `{{"kategori": "...", "soru": "...", "cevap": "..."}}`
3.  Cevaplar, yalnızca sağlanan PDF içeriğine dayanmalıdır.

**ÜRETİLECEK SORU KATEGORİLERİ:**
Gerçeklere Dayalı, Tablo/Görsel Odaklı, Özetleyici, Karşılaştırmalı, Çıkarımsal/Analitik.
"""
        return prompt.strip()
    
    def _call_gemini_api(self, text_content: str, images: List[bytes], max_retries: int = None) -> Optional[List[Dict]]:
        """Call Gemini API with text and images, with enhanced retry logic and API key rotation."""
        if max_retries is None:
            max_retries = self.config.get('max_retries_per_key', 2) * len(self.config['api_keys'])
        
        prompt = self._create_prompt()
        
        for attempt in range(max_retries):
            try:
                # Apply rate limiting before each API call
                self._adaptive_rate_limit()
                
                # Initialize model
                model = genai.GenerativeModel(self.config['model_name'])
                
                # Prepare content
                content_parts = [prompt, text_content]
                
                # Add images if available (limit to first 10 for performance)
                image_count = 0
                for img_data in images:
                    if image_count >= 10:  # Limit images to avoid timeout
                        break
                    try:
                        # Convert bytes to PIL Image and then to the format Gemini expects
                        pil_img = Image.open(io.BytesIO(img_data))
                        content_parts.append(pil_img)
                        image_count += 1
                    except Exception as e:
                        self.logger.warning(f"Failed to process image: {e}")
                        continue
                
                # Generate content with timeout handling
                response = model.generate_content(
                    content_parts,
                    generation_config=genai.types.GenerationConfig(
                        candidate_count=1,
                        max_output_tokens=8192,
                        temperature=0.1,
                    ),
                    request_options={'timeout': self.config['api_timeout_seconds']}
                )
                
                if not response.text:
                    self.logger.warning("Empty response from Gemini API")
                    time.sleep(1)  # Brief pause before retry
                    continue
                
                # Parse JSON response
                try:
                    # Clean the response text (remove markdown code blocks if present)
                    response_text = response.text.strip()
                    if response_text.startswith('```json'):
                        response_text = response_text[7:]
                    if response_text.endswith('```'):
                        response_text = response_text[:-3]
                    response_text = response_text.strip()
                    
                    qa_pairs = json.loads(response_text)
                    
                    if not isinstance(qa_pairs, list):
                        self.logger.warning("Response is not a JSON array")
                        continue
                    
                    # Validate each Q&A pair
                    valid_pairs = []
                    for qa in qa_pairs:
                        if isinstance(qa, dict) and all(key in qa for key in ['kategori', 'soru', 'cevap']):
                            valid_pairs.append(qa)
                        else:
                            self.logger.warning(f"Invalid Q&A pair format: {qa}")
                    
                    if valid_pairs:
                        self.logger.info(f"Generated {len(valid_pairs)} valid Q&A pairs")
                        return valid_pairs
                    else:
                        self.logger.warning("No valid Q&A pairs found in response")
                        continue
                
                except json.JSONDecodeError as e:
                    self.logger.warning(f"Failed to parse JSON response (attempt {attempt + 1}): {e}")
                    self.logger.debug(f"Response text: {response.text[:500]}...")
                    continue
            
            except Exception as e:
                error_msg = str(e).lower()
                
                # Enhanced error detection and handling
                if any(keyword in error_msg for keyword in [
                    'permission', 'quota', 'exhausted', 'denied', 'invalid api key', 
                    'rate limit', 'too many requests', '429', 'resource_exhausted'
                ]):
                    self.logger.warning(f"API limit/permission issue detected (attempt {attempt + 1}): {e}")
                    
                    # Add extra delay for rate limiting
                    if 'rate limit' in error_msg or '429' in error_msg or 'too many requests' in error_msg:
                        delay = min(self._current_delay * 2, 30)  # Max 30 seconds
                        self.logger.info(f"Rate limit detected, waiting {delay}s before retry...")
                        time.sleep(delay)
                    
                    # Try to rotate API key if we haven't exhausted retries for current key
                    if attempt % self.config.get('max_retries_per_key', 2) == (self.config.get('max_retries_per_key', 2) - 1):
                        if self._rotate_api_key():
                            self.logger.info("Rotated API key due to limits, retrying...")
                            continue
                        else:
                            self.logger.error("All API keys exhausted, cannot continue")
                            return None
                    else:
                        # Wait before retry with same key
                        time.sleep(self.config.get('api_rate_limit_delay', 2))
                        continue
                        
                elif 'timeout' in error_msg or 'deadline' in error_msg:
                    self.logger.warning(f"Timeout error (attempt {attempt + 1}): {e}")
                    # Increase delay for timeout errors
                    timeout_delay = min(5 * (attempt + 1), 30)
                    time.sleep(timeout_delay)
                    continue
                    
                else:
                    self.logger.warning(f"API call failed (attempt {attempt + 1}): {e}")
                    if attempt < max_retries - 1:
                        # Exponential backoff with jitter
                        delay = min(2 ** attempt + random.uniform(0, 1), 15)
                        time.sleep(delay)
                        continue
                    else:
                        self.logger.error(f"All retry attempts failed for API call")
                        return None
        
        return None
    
    def _process_single_pdf(self, pdf_path: Path) -> bool:
        """Process a single PDF file and generate Q&A pairs with chunking and proactive key rotation."""
        try:
            self.logger.info(f"Processing: {pdf_path.name}")
            
            # Extract content from PDF
            text_content, images = self._extract_pdf_content(pdf_path)
            
            if not text_content.strip():
                self.logger.warning(f"No text content extracted from {pdf_path.name}")
                return False
            
            # Split text into chunks to avoid overwhelming single API key
            chunk_size = 50000  # characters per chunk
            text_chunks = []
            for i in range(0, len(text_content), chunk_size):
                chunk = text_content[i:i + chunk_size]
                text_chunks.append(chunk)
            
            # Split images proportionally across chunks
            images_per_chunk = max(1, len(images) // len(text_chunks)) if images else 0
            
            self.logger.info(f"Split {pdf_path.name} into {len(text_chunks)} chunks")
            
            all_qa_pairs = []
            
            # Process each chunk with proactive API key rotation
            for chunk_idx, text_chunk in enumerate(text_chunks):
                self.logger.info(f"Processing chunk {chunk_idx + 1}/{len(text_chunks)} of {pdf_path.name}")
                
                # Rotate API key proactively every 2 chunks to distribute load
                if chunk_idx > 0 and chunk_idx % 2 == 0 and len(self.config['api_keys']) > 1:
                    if self._rotate_api_key():
                        self.logger.info(f"Proactively rotated API key for chunk {chunk_idx + 1}")
                
                # Get images for this chunk
                start_img = chunk_idx * images_per_chunk
                end_img = min((chunk_idx + 1) * images_per_chunk, len(images))
                chunk_images = images[start_img:end_img] if images else []
                
                # Generate Q&A pairs for this chunk
                qa_pairs = self._call_gemini_api(text_chunk, chunk_images)
                
                if qa_pairs:
                    all_qa_pairs.extend(qa_pairs)
                    self.logger.info(f"Chunk {chunk_idx + 1}: Generated {len(qa_pairs)} Q&A pairs")
                else:
                    self.logger.warning(f"Failed to generate Q&A pairs for chunk {chunk_idx + 1}")
                
                # Add delay between chunks to respect rate limits
                if chunk_idx < len(text_chunks) - 1:  # Don't delay after last chunk
                    chunk_delay = max(3, self.config.get('min_delay_between_calls', 5))
                    self.logger.info(f"Waiting {chunk_delay}s before next chunk...")
                    time.sleep(chunk_delay)
            
            if not all_qa_pairs:
                self.logger.error(f"Failed to generate any Q&A pairs for {pdf_path.name}")
                return False
            
            # Add source information and save to output file
            output_path = Path(self.config['output_folder']) / self.config['output_filename']
            
            with open(output_path, 'a', encoding='utf-8') as f:
                for qa in all_qa_pairs:
                    qa['kaynak'] = pdf_path.name
                    f.write(json.dumps(qa, ensure_ascii=False) + '\n')
            
            self.logger.info(f"Successfully processed {pdf_path.name}: {len(all_qa_pairs)} total Q&A pairs generated from {len(text_chunks)} chunks")
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing {pdf_path.name}: {e}")
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
            return False
    
    def _get_pdf_files(self) -> List[Path]:
        """Get list of PDF files to process with multi-machine support."""
        pdf_folder = Path(self.config['pdf_folder'])
        
        if not pdf_folder.exists():
            raise FileNotFoundError(f"PDF folder not found: {pdf_folder}")
        
        pdf_files = list(pdf_folder.glob('*.pdf'))
        
        # Filter out already processed files
        unprocessed_files = [
            pdf for pdf in pdf_files 
            if pdf.name not in self.processed_files
        ]
        
        # Multi-machine support: distribute files across machines
        if self.total_machines > 1:
            # Sort files for consistent distribution
            unprocessed_files.sort(key=lambda x: x.name)
            
            # Calculate files for this machine
            machine_files = []
            for i, pdf_file in enumerate(unprocessed_files):
                if i % self.total_machines == self.machine_id:
                    machine_files.append(pdf_file)
            
            unprocessed_files = machine_files
            self.logger.info(f"Multi-machine mode: Machine {self.machine_id}/{self.total_machines}")
            self.logger.info(f"This machine will process {len(unprocessed_files)} files")
        
        self.logger.info(f"Found {len(pdf_files)} total PDF files")
        self.logger.info(f"Found {len(unprocessed_files)} unprocessed PDF files for this machine")
        
        return unprocessed_files
    
    def run(self):
        """Main execution method."""
        try:
            self.logger.info("Starting PDF to Q&A dataset generation")
            
            # Get PDF files to process
            pdf_files = self._get_pdf_files()
            
            if not pdf_files:
                self.logger.info("No unprocessed PDF files found. Nothing to do.")
                return
            
            # Process files in parallel
            successful_count = 0
            failed_count = 0
            
            with ThreadPoolExecutor(max_workers=self.config['num_workers']) as executor:
                # Submit all tasks
                future_to_pdf = {
                    executor.submit(self._process_single_pdf, pdf_path): pdf_path 
                    for pdf_path in pdf_files
                }
                
                # Process completed tasks
                for future in as_completed(future_to_pdf):
                    pdf_path = future_to_pdf[future]
                    try:
                        success = future.result()
                        if success:
                            successful_count += 1
                        else:
                            failed_count += 1
                    except Exception as e:
                        self.logger.error(f"Unexpected error processing {pdf_path.name}: {e}")
                        failed_count += 1
            
            # Final summary
            total_processed = successful_count + failed_count
            self.logger.info(f"Processing completed!")
            self.logger.info(f"Total files processed: {total_processed}")
            self.logger.info(f"Successful: {successful_count}")
            self.logger.info(f"Failed: {failed_count}")
            
            if successful_count > 0:
                output_path = Path(self.config['output_folder']) / self.config['output_filename']
                self.logger.info(f"Output saved to: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Fatal error in main execution: {e}")
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
            raise


def main():
    """Main entry point with command line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Generate Q&A datasets from PDF files using Gemini API"
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config.json',
        help='Path to configuration file (default: config.json)'
    )
    
    args = parser.parse_args()
    
    try:
        generator = PDFToQAGenerator(config_path=args.config)
        generator.run()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
