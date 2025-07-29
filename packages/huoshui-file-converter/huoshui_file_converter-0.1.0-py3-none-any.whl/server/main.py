import os
import pypandoc
import time
import platform
import re
import argparse
from typing import Dict, List, Annotated
from pathlib import Path
from pydantic import BaseModel, Field
from fastmcp import FastMCP, Context
from fastmcp.exceptions import ToolError

# Initialize server
mcp = FastMCP("huoshui-structured-converter")


# =============================================================================
# DATA MODELS
# =============================================================================

class FileResource(BaseModel):
    """File resource representation"""
    path: str = Field(description="File path (absolute or relative to home directory)")
    size_bytes: int = Field(description="File size in bytes")
    format: str = Field(description="Detected file format")

class ConversionCapability(BaseModel):
    """Conversion capability resource"""
    id: str = Field(description="Unique identifier for conversion rule")
    from_format: str = Field(description="Source format")
    to_format: str = Field(description="Target format")

# Supported conversion capabilities
CONVERSION_CAPABILITIES = [
    ConversionCapability(id="markdown-to-docx", from_format="markdown", to_format="docx"),
    ConversionCapability(id="markdown-to-html", from_format="markdown", to_format="html"),
    ConversionCapability(id="docx-to-markdown", from_format="docx", to_format="markdown"),
    ConversionCapability(id="docx-to-html", from_format="docx", to_format="html"),
    ConversionCapability(id="html-to-markdown", from_format="html", to_format="markdown"),
    ConversionCapability(id="html-to-docx", from_format="html", to_format="docx"),
    ConversionCapability(id="txt-to-markdown", from_format="txt", to_format="markdown"),
    ConversionCapability(id="txt-to-docx", from_format="txt", to_format="docx"),
    ConversionCapability(id="txt-to-html", from_format="txt", to_format="html"),
]

# Custom error codes for better UX
ERROR_CODES = {
    'PATH_SECURITY': -40001,
    'FORMAT_UNSUPPORTED': -40002, 
    'FILE_SIZE_LIMIT': -40003,
    'ENCODING_ERROR': -40004,
    'EMPTY_FILE': -40005,
    'BINARY_FILE': -40006,
    'PATH_INVALID': -40007
}

def _validate_path(file_path: str) -> Path:
    """
    Validate and resolve file path with comprehensive security checks and user-friendly errors
    """
    # Input validation
    if not file_path or not file_path.strip():
        raise ToolError(
            "Please specify a file path like 'Desktop/myfile.txt' or 'Documents/report.docx'", 
            ERROR_CODES['PATH_INVALID']
        )
    
    file_path = file_path.strip()
    
    # Check for suspicious patterns before resolution
    suspicious_patterns = ['..'  , '~/', '%2e', '%2f', '\x00']
    for pattern in suspicious_patterns:
        if pattern in file_path.lower():
            if pattern == '..':
                raise ToolError(
                    "Path traversal not allowed. Use direct paths like 'Documents/file.txt'",
                    ERROR_CODES['PATH_SECURITY']
                )
            elif pattern == '~/':
                # Handle tilde expansion properly
                file_path = os.path.expanduser(file_path)
            else:
                raise ToolError(
                    "Invalid characters in file path. Use simple paths like 'Desktop/file.txt'",
                    ERROR_CODES['PATH_INVALID']
                )
    
    # Test encoding
    try:
        file_path.encode('utf-8').decode('utf-8')
    except UnicodeError:
        raise ToolError(
            "File path contains invalid characters. Try renaming your file with simpler characters.",
            ERROR_CODES['PATH_INVALID']
        )
    
    # Convert to Path object with proper resolution
    try:
        if os.path.isabs(file_path):
            resolved_path = Path(file_path).resolve()
        else:
            # Relative path - resolve relative to user's home directory  
            resolved_path = (Path.home() / file_path).resolve()
    except (OSError, ValueError) as e:
        raise ToolError(
            f"Invalid file path format. Try: 'Desktop/filename.txt' or copy the full path from your file manager.",
            ERROR_CODES['PATH_INVALID']
        )
    
    # Enhanced security: comprehensive restricted directories
    restricted_dirs = {
        # Unix/Linux/macOS system directories
        '/etc', '/sys', '/proc', '/dev', '/boot', '/root', '/var/log',
        '/System', '/Library/System', '/private/etc', '/usr/bin', '/usr/sbin',
        # Windows system directories  
        'C:\\Windows', 'C:\\Program Files', 'C:\\Program Files (x86)',
        'C:\\System32', 'C:\\Windows\\System32', 'C:\\Windows\\SysWOW64'
    }
    
    resolved_str = str(resolved_path)
    for restricted in restricted_dirs:
        if resolved_str.startswith(restricted):
            raise ToolError(
                f"For security, I cannot access system folders. Please use files from your Documents, Desktop, or Downloads folder instead.",
                ERROR_CODES['PATH_SECURITY']
            )
    
    # Check path depth (prevent extremely deep nesting issues)
    if len(resolved_path.parts) > 50:
        raise ToolError(
            "File path is too deeply nested. Try moving your file to a simpler location like Desktop or Documents.",
            ERROR_CODES['PATH_INVALID']
        )
    
    # Check for very long filenames that might cause filesystem issues
    if len(resolved_path.name) > 250:
        raise ToolError(
            "Filename is too long. Please rename your file to something shorter.",
            ERROR_CODES['PATH_INVALID']
        )
    
    return resolved_path

def _detect_format_by_extension(file_path: Path) -> str:
    """Fast format detection by file extension only"""
    ext = file_path.suffix.lower()
    format_map = {
        '.md': 'markdown',
        '.markdown': 'markdown',
        '.txt': 'txt',
        '.docx': 'docx',
        '.html': 'html',
        '.htm': 'html'
    }
    
    return format_map.get(ext, 'unknown')

def _is_binary_file(file_path: Path) -> bool:
    """Check if file is binary by examining first few bytes"""
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            return b'\x00' in chunk  # Null bytes indicate binary
    except Exception:
        return False

def _is_likely_markdown(content: str) -> bool:
    """More sophisticated markdown detection"""
    lines = content.split('\n')[:50]  # Check first 50 lines
    markdown_score = 0
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Headers
        if line.startswith('#') and len(line) > 1 and line[1] == ' ':
            markdown_score += 3
        # Lists
        elif line.startswith(('- ', '* ', '+ ')) or any(line.startswith(f'{i}. ') for i in range(1, 10)):
            markdown_score += 2
        # Code blocks
        elif line.startswith('```'):
            markdown_score += 2
        # Links
        elif '[' in line and '](' in line:
            markdown_score += 1
        # Bold/italic
        elif '**' in line or '__' in line or '*' in line:
            markdown_score += 1
    
    return markdown_score >= 3

def _detect_format_by_extension(file_path: Path) -> str:
    """Fast format detection by file extension with enhanced patterns"""
    # Handle files with no extension
    if not file_path.suffix:
        name = file_path.name.lower()
        if name in ['readme', 'changelog', 'license', 'authors']:
            return 'markdown'
        return 'txt'
    
    # Handle multiple extensions
    name = file_path.name.lower()
    if any(name.endswith(ext) for ext in ['.backup.md', '.old.txt', '.orig.html']):
        parts = name.split('.')
        if len(parts) >= 3:
            format_ext = '.' + parts[-2]
            ext = format_ext
        else:
            ext = file_path.suffix.lower()
    else:
        ext = file_path.suffix.lower()
    
    format_map = {
        '.md': 'markdown',
        '.markdown': 'markdown',
        '.mdown': 'markdown',
        '.txt': 'txt',
        '.text': 'txt',
        '.docx': 'docx',
        '.html': 'html',
        '.htm': 'html'
    }
    
    return format_map.get(ext, 'unknown')

def _detect_format_by_content(file_path: Path) -> str:
    """Detailed format detection by content analysis with enhanced error handling"""
    if not file_path.exists():
        raise ToolError(
            f"File not found: {file_path}. Please check the path and try again.",
            ERROR_CODES['PATH_INVALID']
        )
    
    # Check for binary files first
    if _is_binary_file(file_path):
        raise ToolError(
            f"This appears to be a binary file. I can only convert text files like .txt, .md, .docx, .html",
            ERROR_CODES['BINARY_FILE']
        )
    
    # First try by extension
    detected_format = _detect_format_by_extension(file_path)
    
    # For txt files or unknown formats, check content (with size limit)
    if detected_format in ['txt', 'unknown']:
        try:
            # Only read small files for content analysis (< 1MB)
            file_size = file_path.stat().st_size
            if file_size > 1024 * 1024:
                return detected_format if detected_format != 'unknown' else 'txt'
            
            # Check if file is empty
            if file_size == 0:
                raise ToolError(
                    "File is empty - please add some content first.",
                    ERROR_CODES['EMPTY_FILE']
                )
                
            content = file_path.read_text(encoding='utf-8', errors='ignore')[:1000]
            
            # Check for whitespace-only content
            if not content.strip():
                raise ToolError(
                    "File contains only whitespace - please add some meaningful content.",
                    ERROR_CODES['EMPTY_FILE']
                )
            
            # Enhanced markdown detection
            if _is_likely_markdown(content):
                detected_format = 'markdown'
            # Check for HTML content
            elif '<html>' in content.lower() or '<DOCTYPE' in content or '<body>' in content.lower():
                detected_format = 'html'
                
        except UnicodeDecodeError:
            raise ToolError(
                "Unable to read file - it may have encoding issues. Try saving it as UTF-8 text.",
                ERROR_CODES['ENCODING_ERROR']
            )
        except Exception as e:
            if isinstance(e, ToolError):
                raise
            raise ToolError(
                f"Error reading file: {str(e)}",
                ERROR_CODES['PATH_INVALID']
            )
    
    if detected_format == 'unknown':
        supported_formats = ", ".join([".md", ".txt", ".docx", ".html"])
        raise ToolError(
            f"File format '{file_path.suffix}' is not supported. I can work with: {supported_formats}",
            ERROR_CODES['FORMAT_UNSUPPORTED']
        )
    
    return detected_format

# =============================================================================
# PROMPTS
# =============================================================================

@mcp.prompt
def role_and_rules() -> str:
    """
    Core identity and operational rules for the AI assistant
    """
    return """
# Your Identity and Core Mission
I'm your File Conversion Assistant. I help you convert documents between formats safely and easily.

# What I Need From You
Just tell me:
1. **Your file location** (like 'Desktop/myfile.txt' or 'Documents/report.docx')
2. **What format you want** (DOCX, HTML, Markdown, or TXT)

# What I Can Do
- Convert between **Markdown**, **DOCX**, **HTML**, and **TXT** formats
- Handle files anywhere on your system safely
- Give you the new file in the same folder as your original
- Provide clear guidance when something goes wrong

# Quick Start Examples
- "Convert Desktop/report.md to DOCX"
- "Change Documents/presentation.html to Markdown"
- "Turn Downloads/notes.txt into HTML"

**That's it!** I'll handle all the technical details and tell you exactly where your new file is saved.
"""

@mcp.prompt
def explain_file_paths(user_os: str = "mac") -> str:
    """Help users understand how to specify file paths correctly"""
    if user_os.lower() in ["mac", "macos", "darwin"]:
        return """
# The Easiest Way to Tell Me Where Your File Is 📂

## Start Here (Recommended):
Just tell me: `Desktop/filename.docx` or `Documents/report.txt`

## If That Doesn't Work:
1. **Find your file** in Finder
2. **Right-click** → "Copy as Pathname"
3. **Paste it** in our conversation

## Common Locations:
- `Desktop/filename.docx` - Files on your Desktop
- `Documents/filename.docx` - Files in Documents
- `Downloads/filename.txt` - Files in Downloads

**That's it!** Most people only need the first method.
"""
    else:  # Windows
        return """
# The Easiest Way to Tell Me Where Your File Is 📂

## Start Here (Recommended):
Just tell me: `Desktop/filename.docx` or `Documents/report.txt`

## If That Doesn't Work:
1. **Find your file** in File Explorer
2. **Right-click** → "Copy as path"
3. **Paste it** in our conversation

## Common Locations:
- `Desktop/filename.docx` - Files on your Desktop
- `Documents/filename.docx` - Files in Documents
- `Downloads/filename.txt` - Files in Downloads

**That's it!** Most people only need the first method.
"""

@mcp.prompt
def suggest_conversion_format(source_format: str, user_intent: str = "") -> str:
    """Suggest the best target format based on source format and intended use"""
    
    return f"""
# What Do You Want to Do With Your Converted File?

## Most Popular Choices:
- **📝 Edit and format** → Convert to **DOCX**
- **🌐 Share online** → Convert to **HTML** 
- **✍️ Simple notes** → Convert to **Markdown**

## Not Sure?
**DOCX** is usually the best choice - it opens in Word, Google Docs, and most apps.

**Tell me your goal and I'll recommend the perfect format!**
"""

@mcp.prompt
def troubleshoot_error(error_type: str, file_path: str = "", details: str = "") -> str:
    """Provide helpful guidance for common conversion errors"""
    
    if error_type == "file_not_found":
        return f"""
# 🔍 File Not Found

**Most Common Fix**: Check your spelling and try: `Desktop/filename.txt`

## Still Having Trouble?
1. **Copy the exact path**: Right-click your file → "Copy as Pathname"
2. **Check the folder**: Make sure it's where you think it is
3. **Try a different approach**: Tell me what folder it's in and I'll help

**Need more help?** Just describe where you think the file is located.
"""
    
    elif error_type == "unsupported_format":
        return f"""
# ⚠️ Unsupported File Format

**I can work with**: .md, .docx, .html, .txt files

## Quick Solutions:
1. **Save as text**: Open your file and "Save As" → .txt
2. **Check file extension**: Make sure it ends with .md, .docx, .html, or .txt
3. **Try a different file**: Pick a file I can convert first

**Still stuck?** Tell me what type of file you have and I'll suggest the best approach.
"""
    
    elif error_type == "file_too_large":
        return f"""
# 📏 File Too Large (20MB limit)

**Quick fixes**:
1. **Compress images** in your document
2. **Split into smaller files**  
3. **Save as text only** first, then convert

**Most text documents are tiny** - large files usually have high-resolution images.
"""
    
    else:
        return f"""
# 🤔 Something Went Wrong

**Let's fix this together:**
1. **What file type** are you converting?
2. **What format** do you want?
3. **Can you open** the original file normally?

**Quick try**: Use a different output format or simplify your document.
"""

@mcp.prompt
def explain_conversion_result(original_file: str, new_file: str, format: str, file_size_mb: float = 0) -> str:
    """Explain conversion results clearly and provide next steps"""
    
    return f"""
# ✅ Conversion Complete!

**Your new {format.upper()} file is ready**: `{new_file}`

## What's Next:
- **Open it**: Double-click the file to open
- **Find it**: It's in the same folder as your original
- **Convert more?** Just ask!

Your original file is safe and unchanged. 🎉
"""

# =============================================================================
# RESOURCES
# =============================================================================



@mcp.tool
def file_get(
    path: Annotated[str, Field(description="File path (absolute or relative to home directory)")]
) -> FileResource:
    """
    Retrieves detailed information about a single file.
    
    Args:
        path: File path (absolute or relative to home directory)
        
    Returns:
        File resource with detailed information
    """
    try:
        file_path = _validate_path(path)
        
        if not file_path.exists():
            raise ToolError(
                f"File not found: {path}\n✅ Quick fix: Try 'Desktop/filename.txt'\n🔍 Still stuck? Right-click your file → 'Copy as Pathname'",
                ERROR_CODES['PATH_INVALID']
            )
        
        if not file_path.is_file():
            raise ToolError(
                f"'{path}' is a folder, not a file. Please specify a file like 'Documents/myfile.txt'",
                ERROR_CODES['PATH_INVALID']
            )
        
        file_format = _detect_format_by_content(file_path)
        
        return FileResource(
            path=str(file_path).replace('\\', '/'),
            size_bytes=file_path.stat().st_size,
            format=file_format
        )
        
    except Exception as e:
        if isinstance(e, ToolError):
            raise
        raise ToolError(f"Error getting file info: {e}", ERROR_CODES['PATH_INVALID'])

@mcp.resource(uri="resource://conversion_capability_list")
def conversion_capability_list() -> List[ConversionCapability]:
    """
    Provides a complete list of all file format conversions this server supports.
    
    Returns:
        List of supported conversion capabilities
    """
    return CONVERSION_CAPABILITIES

# =============================================================================
# TOOLS
# =============================================================================

def _estimate_conversion_time(file_size: int, source_format: str, to_format: str) -> float:
    """Estimate conversion time based on file size and complexity"""
    base_time = 2.0  # Base time in seconds
    size_factor = file_size / (1024 * 1024)  # Size in MB
    
    # Format complexity multipliers
    complexity_map = {
        ('docx', 'markdown'): 1.5,
        ('html', 'markdown'): 1.2,
        ('markdown', 'docx'): 2.0,
        ('txt', 'docx'): 1.8,
    }
    
    complexity = complexity_map.get((source_format, to_format), 1.0)
    return base_time + (size_factor * complexity)

@mcp.tool
async def convert_document(
    file_path: Annotated[str, Field(description="File path (absolute or relative to home directory)")],
    to_format: Annotated[str, Field(description="Target format (docx, markdown, html)")],
    ctx: Context
) -> Dict[str, str]:
    """
    Converts a specified file to a different format. The new file is saved in the same directory as the original.
    
    Args:
        file_path: File path (absolute or relative to home directory)
        to_format: The target format to convert the file into
        
    Returns:
        Dictionary with new_file_path key containing the absolute path of converted file
    """
    start_time = time.time()
    
    try:
        await ctx.report_progress(5, 100, "Starting conversion...")
        
        # Validate and resolve file path
        source_path = _validate_path(file_path)
        
        if not source_path.exists():
            raise ToolError(
                f"File not found: {file_path}. Please check the spelling and location. Try: 'Desktop/filename.txt'",
                ERROR_CODES['PATH_INVALID']
            )
        
        if not source_path.is_file():
            raise ToolError(
                f"Path points to a folder, not a file: {file_path}. Please specify the actual file.",
                ERROR_CODES['PATH_INVALID']
            )
        
        await ctx.report_progress(10, 100, "Validating file...")
        
        # Check file size (20MB limit)
        file_size = source_path.stat().st_size
        file_size_mb = file_size / (1024 * 1024)
        
        if file_size >= 20 * 1024 * 1024:
            raise ToolError(
                f"File too large: {file_size_mb:.1f}MB (limit: 20MB). Try: 1) Compress images, 2) Split into smaller files, 3) Remove embedded media",
                ERROR_CODES['FILE_SIZE_LIMIT']
            )
        
        # Warn about large files
        if file_size > 5 * 1024 * 1024:  # 5MB
            estimated_time = _estimate_conversion_time(file_size, "unknown", to_format)
            await ctx.info(f"Large file detected ({file_size_mb:.1f}MB) - conversion may take up to {estimated_time:.0f} seconds")
        
        await ctx.report_progress(20, 100, "Analyzing file format...")
        
        # Detect source format
        source_format = _detect_format_by_content(source_path)
        
        # Handle self-conversion (reformatting)
        if source_format == to_format:
            await ctx.info(f"Reformatting {source_format.upper()} file (same format conversion for cleanup)")
        
        # Verify conversion is supported
        conversion_id = f"{source_format}-to-{to_format}"
        if not any(cap.id == conversion_id for cap in CONVERSION_CAPABILITIES) and source_format != to_format:
            supported_targets = [cap.to_format for cap in CONVERSION_CAPABILITIES if cap.from_format == source_format]
            if supported_targets:
                raise ToolError(
                    f"Cannot convert {source_format.upper()} to {to_format.upper()}. From {source_format.upper()}, I can convert to: {', '.join(supported_targets).upper()}",
                    ERROR_CODES['FORMAT_UNSUPPORTED']
                )
            else:
                raise ToolError(
                    f"No conversions available from {source_format.upper()} format.",
                    ERROR_CODES['FORMAT_UNSUPPORTED']
                )
        
        await ctx.report_progress(30, 100, f"Reading {file_size_mb:.1f}MB file...")
        
        # Read source file with better encoding handling
        try:
            input_text = source_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            try:
                # Try common alternative encodings
                for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        input_text = source_path.read_text(encoding=encoding)
                        await ctx.info(f"Note: File was encoded as {encoding}, converted to UTF-8")
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    raise ToolError(
                        "Unable to read file due to encoding issues. Try: 1) Save as UTF-8 text, 2) Open in text editor and re-save",
                        ERROR_CODES['ENCODING_ERROR']
                    )
            except Exception:
                raise ToolError(
                    "Unable to read file. Please ensure it's a text file and try again.",
                    ERROR_CODES['ENCODING_ERROR']
                )
        
        # Final content validation
        if not input_text.strip():
            raise ToolError(
                "File appears to be empty or contains only whitespace. Please add some content first.",
                ERROR_CODES['EMPTY_FILE']
            )
        
        await ctx.report_progress(50, 100, "Preparing conversion...")
        
        # Generate output file path (same directory as source)
        source_dir = source_path.parent
        base_name = source_path.stem
        timestamp = int(time.time())
        
        # Handle long filenames
        if len(base_name) > 200:
            base_name = base_name[:200]
            await ctx.info("Filename was very long - truncated for compatibility")
        
        output_filename = f"{base_name}_{timestamp}.{to_format}"
        output_path = source_dir / output_filename
        
        # Prepare format-specific pandoc arguments
        extra_args = ['--standalone']
        if source_format == 'docx' and to_format == 'markdown':
            extra_args.extend(['--extract-media', str(source_dir / f"{base_name}_media")])
        elif source_format == 'html' and to_format == 'markdown':
            extra_args.extend(['--wrap=none'])
        
        await ctx.report_progress(70, 100, f"Converting {source_format.upper()} to {to_format.upper()}...")
        
        # Execute conversion with better error handling
        try:
            pypandoc.convert_text(
                source=input_text,
                to=to_format,
                format=source_format,
                extra_args=extra_args,
                outputfile=str(output_path),
            )
        except RuntimeError as e:
            error_msg = str(e).lower()
            if 'pandoc' in error_msg and 'not found' in error_msg:
                raise ToolError(
                    "Pandoc is not installed. Please install Pandoc to enable file conversion.",
                    ERROR_CODES['FORMAT_UNSUPPORTED']
                )
            elif 'memory' in error_msg or 'out of memory' in error_msg:
                raise ToolError(
                    "File too complex for conversion. Try: 1) Simplify formatting, 2) Split into smaller files",
                    ERROR_CODES['FILE_SIZE_LIMIT']
                )
            else:
                raise ToolError(
                    f"Conversion failed. Try: 1) Different output format, 2) Simplify document formatting, 3) Check for unusual characters. Details: {str(e)}",
                    ERROR_CODES['FORMAT_UNSUPPORTED']
                )
        
        await ctx.report_progress(90, 100, "Finalizing...")
        
        # Verify output file was created
        if not output_path.exists():
            raise ToolError(
                "Conversion completed but output file was not created. Please try again.",
                ERROR_CODES['FORMAT_UNSUPPORTED']
            )
        
        conversion_time = time.time() - start_time
        output_size_mb = output_path.stat().st_size / (1024 * 1024)
        
        await ctx.report_progress(100, 100, "Conversion complete!")
        await ctx.info(f"✅ Conversion completed in {conversion_time:.1f}s - Output: {output_size_mb:.1f}MB")
        
        return {
            "new_file_path": str(output_path).replace('\\', '/')
        }
        
    except ToolError:
        raise
    except Exception as e:
        raise ToolError(
            f"Unexpected error during conversion. Please try again or contact support. Details: {str(e)}",
            ERROR_CODES['FORMAT_UNSUPPORTED']
        )

@mcp.tool
def detect_format(
    file_path: Annotated[str, Field(description="File path (absolute or relative to home directory)")]
) -> Dict[str, str]:
    """
    Intelligently detects a file's true format by inspecting its contents, 
    which is more reliable than trusting a file extension.
    
    Args:
        file_path: File path (absolute or relative to home directory)
        
    Returns:
        Dictionary with format key containing the detected file format
    """
    try:
        # Validate and resolve file path
        source_path = _validate_path(file_path)
        
        if not source_path.exists():
            raise ToolError(
                f"File not found: {file_path}. Please check the path and try: 'Desktop/filename.txt'",
                ERROR_CODES['PATH_INVALID']
            )
        
        if not source_path.is_file():
            raise ToolError(
                f"Path points to a folder, not a file: {file_path}. Please specify the actual file.",
                ERROR_CODES['PATH_INVALID']
            )
        
        detected_format = _detect_format_by_content(source_path)
        
        return {
            "format": detected_format
        }
        
    except ToolError:
        raise
    except Exception as e:
        raise ToolError(
            f"Error detecting file format: {str(e)}. Please ensure the file is accessible.",
            ERROR_CODES['PATH_INVALID']
        )

def main():
    """Main entry point for the MCP server"""
    parser = argparse.ArgumentParser(description="Huoshui File Converter MCP Server")
    parser.add_argument(
        "--dir", "-d", 
        type=str, 
        help="Working directory for file operations"
    )
    
    args = parser.parse_args()
    
    # Set working directory if provided
    if args.dir:
        os.environ["HUOSHUI_WORKING_DIR"] = args.dir
    
    # Run the server
    mcp.run()

# Main execution
if __name__ == "__main__":
    main()
