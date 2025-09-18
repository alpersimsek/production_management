#!/usr/bin/env python3
"""
GDPR Tool CLI - Command Line Interface

This CLI tool provides command-line access to the GDPR compliance tool functionality.
It integrates with the existing backend services and database to provide file upload,
processing, and masking map export capabilities.

Usage:
    python cli.py upload <file_path> --product <product_name>
    python cli.py process <file_id> --product <product_name>
    python cli.py upload-and-process <file_path> --product <product_name>

Features:
- File upload with automatic product detection
- File processing with product-specific rules
- Masking map export alongside processed files
- Output to /var/tmp/cli_masking directory
- Integration with existing database and services
"""

import argparse
import sys
import os
import json
import pathlib
import tempfile
from typing import Optional, Dict, Any
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from database.session import Session, init_db
from database.models import User, File, Product, Preset, MaskingMap, RuleCategory, Role
from services import FileService, MaskingMapService, ProcessingConfig
from storage import FileStorage
import settings
from logger import logger
from charset_normalizer import from_path
import magic
from database.models import ContentType, FileStatus
import time
import tempfile
import pathlib


class CLIManager:
    """CLI Manager for GDPR Tool operations."""
    
    def __init__(self):
        """Initialize CLI manager with database and storage."""
        self.session = Session()
        self.storage = FileStorage(settings.DATA_DIR)
        self.output_dir = pathlib.Path("/var/tmp/cli_masking")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a CLI user if it doesn't exist
        self.cli_user = self._get_or_create_cli_user()
    
    def _get_or_create_cli_user(self) -> User:
        """Get or create a CLI user for operations."""
        user = self.session.query(User).filter(User.username == "cli_user").first()
        if not user:
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            user = User(
                username="cli_user",
                password=pwd_context.hash("cli_password"),
                role=Role.ADMIN
            )
            self.session.add(user)
            self.session.commit()
            logger.info("Created CLI user")
        return user
    
    def upload_file(self, file_path: str, product_name: str) -> str:
        """Upload a file and return the file ID."""
        file_path = pathlib.Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get product
        product = self.session.query(Product).filter(Product.name == product_name).first()
        if not product:
            raise ValueError(f"Product '{product_name}' not found")
        
        # Create file service with product context
        file_service = FileService(self.session, self.cli_user, self.storage, product.id)
        
        # Create a mock UploadFile object
        class MockUploadFile:
            def __init__(self, file_path):
                self.filename = file_path.name
                self.file = open(file_path, 'rb')
            
            def __enter__(self):
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                if hasattr(self, 'file'):
                    self.file.close()
        
        # Upload file
        with MockUploadFile(file_path) as upload_file:
            file_obj = file_service.save_file(upload_file)
        
        logger.info(f"File uploaded successfully: {file_obj.id}")
        return file_obj.id
    
    def process_file(self, file_id: str, product_name: str) -> Dict[str, Any]:
        """Process a file with the given product configuration."""
        # Get product
        product = self.session.query(Product).filter(Product.name == product_name).first()
        if not product:
            raise ValueError(f"Product '{product_name}' not found")
        
        # Get file
        file_obj = self.session.query(File).filter(File.id == file_id).first()
        if not file_obj:
            raise ValueError(f"File with ID '{file_id}' not found")
        
        # Create file service
        file_service = FileService(self.session, self.cli_user, self.storage, product.id)
        
        # Get processing configuration
        tasks_configs = file_service.make_task_config(file_id)
        
        if not tasks_configs:
            raise ValueError(f"No processing configuration found for file {file_id}")
        
        # Process the file using the existing task configuration
        task_config = tasks_configs[0]  # Use first configuration
        
        # Import the processing function
        from tasks import _process_file
        
        # Create processing config
        masking_service = MaskingMapService(self.session)
        config = ProcessingConfig(
            rules_config=task_config['rules_configs'][list(task_config['rules_configs'].keys())[0]],
            maskingMapService=masking_service
        )
        
        # Process the file
        _process_file(config, self.storage, file_id, file_service)
        
        # Get updated file info
        processed_file = file_service.get_by_id(file_id)
        
        # Copy processed file to output directory
        output_file_path = self._copy_to_output(processed_file, product_name)
        
        # Export masking map
        masking_map_path = self._export_masking_map(file_id, product_name)
        
        return {
            "file_id": file_id,
            "original_filename": file_obj.filename,
            "processed_filename": processed_file.filename,
            "output_file": str(output_file_path),
            "masking_map": str(masking_map_path),
            "status": processed_file.status.value
        }
    
    def _copy_to_output(self, file_obj: File, product_name: str) -> pathlib.Path:
        """Copy processed file to output directory."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{product_name}_{timestamp}_{file_obj.filename}"
        output_path = self.output_dir / output_filename
        
        # Copy file from storage to output directory
        src_path = self.storage.get(file_obj.id)
        if src_path.exists():
            import shutil
            shutil.copy2(src_path, output_path)
            logger.info(f"Processed file copied to: {output_path}")
        else:
            raise FileNotFoundError(f"Processed file not found in storage: {src_path}")
        
        return output_path
    
    def _export_masking_map(self, file_id: str, product_name: str) -> pathlib.Path:
        """Export masking map for the processed file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        masking_filename = f"{product_name}_{timestamp}_masking_map.json"
        masking_path = self.output_dir / masking_filename
        
        # Get all masking maps from the session
        masking_maps = self.session.query(MaskingMap).all()
        
        # Convert to JSON-serializable format
        masking_data = {
            "file_id": file_id,
            "product_name": product_name,
            "export_timestamp": datetime.now().isoformat(),
            "total_mappings": len(masking_maps),
            "mappings": []
        }
        
        for mapping in masking_maps:
            masking_data["mappings"].append({
                "id": mapping.id,
                "original_value": mapping.original_value,
                "masked_value": mapping.masked_value,
                "category": mapping.category.value,
                "created_at": mapping.created_at.isoformat()
            })
        
        # Write to file
        with open(masking_path, 'w', encoding='utf-8') as f:
            json.dump(masking_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Masking map exported to: {masking_path}")
        return masking_path
    
    def upload_and_process(self, file_path: str, product_name: str) -> Dict[str, Any]:
        """Upload and process a file in one operation."""
        # Upload file
        file_id = self.upload_file(file_path, product_name)
        
        # Process file
        result = self.process_file(file_id, product_name)
        
        return result
    
    def list_products(self) -> list:
        """List available products."""
        products = self.session.query(Product).all()
        return [{"id": p.id, "name": p.name} for p in products]
    
    def list_files(self) -> list:
        """List files for CLI user."""
        files = self.session.query(File).filter(File.user_id == self.cli_user.id).all()
        return [{
            "id": f.id,
            "filename": f.filename,
            "status": f.status.value,
            "file_size": f.file_size,
            "created_at": f.created_at.isoformat() if f.created_at else None
        } for f in files]
    
    def cleanup(self):
        """Clean up resources."""
        self.session.close()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="GDPR Tool CLI - Command Line Interface for file processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available products
  python cli.py list-products
  
  # List files
  python cli.py list-files
  
  # Mask a file
  python cli.py mask /path/to/file.txt --product "MyProduct"
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Upload command (internal use only)
    upload_parser = subparsers.add_parser('upload', help=argparse.SUPPRESS)
    upload_parser.add_argument('file_path', help='Path to the file to upload')
    upload_parser.add_argument('--product', required=True, help='Product name for processing')
    
    # Process command (internal use only)
    process_parser = subparsers.add_parser('process', help=argparse.SUPPRESS)
    process_parser.add_argument('file_id', help='ID of the file to process')
    process_parser.add_argument('--product', required=True, help='Product name for processing')
    
    # Mask command
    mask_parser = subparsers.add_parser('mask', help='Mask a file')
    mask_parser.add_argument('file_path', help='Path to the file to mask')
    mask_parser.add_argument('--product', required=True, help='Product name for processing')
    
    # List products command
    subparsers.add_parser('list-products', help='List available products')
    
    # List files command
    subparsers.add_parser('list-files', help='List uploaded files')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        # Create CLI manager (database should already be initialized by the app)
        cli = CLIManager()
        
        try:
            if args.command == 'upload':
                file_id = cli.upload_file(args.file_path, args.product)
                print(f"✅ File uploaded successfully!")
                print(f"   File ID: {file_id}")
                print(f"   Product: {args.product}")
                
            elif args.command == 'process':
                result = cli.process_file(args.file_id, args.product)
                print(f"✅ File processed successfully!")
                print(f"   File ID: {result['file_id']}")
                print(f"   Original: {result['original_filename']}")
                print(f"   Processed: {result['processed_filename']}")
                print(f"   Output: {result['output_file']}")
                print(f"   Masking Map: {result['masking_map']}")
                print(f"   Status: {result['status']}")
                
            elif args.command == 'mask':
                result = cli.upload_and_process(args.file_path, args.product)
                print(f"✅ File masked successfully!")
                print(f"   File ID: {result['file_id']}")
                print(f"   Original: {result['original_filename']}")
                print(f"   Masked: {result['processed_filename']}")
                print(f"   Output: {result['output_file']}")
                print(f"   Masking Map: {result['masking_map']}")
                print(f"   Status: {result['status']}")
                
            elif args.command == 'list-products':
                products = cli.list_products()
                print("📋 Available Products:")
                for product in products:
                    print(f"   {product['id']}: {product['name']}")
                    
            elif args.command == 'list-files':
                files = cli.list_files()
                print("📁 Uploaded Files:")
                for file in files:
                    print(f"   {file['id']}: {file['filename']} ({file['status']}) - {file['file_size']} bytes")
                    
        finally:
            cli.cleanup()
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        logger.error(f"CLI error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
