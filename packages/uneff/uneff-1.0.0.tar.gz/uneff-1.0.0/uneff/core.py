#!/usr/bin/env python3
"""
Uneff - A tool to remove BOM and problematic Unicode characters from files

This module can be used both as a command-line script, as an imported package,
or with custom storage systems.
"""

import sys
import os
import csv
import io
from typing import List, Tuple, Dict, Optional, Union


def get_default_mappings_csv() -> str:
    """
    Generate default character mappings as a CSV string.
    
    Returns:
        str: CSV content with default problematic character mappings
    """
    # Default problematic Unicode characters with Replacement column
    default_mappings = [
        ["Character", "Unicode", "Name", "Remove", "Replacement"],
        ["�", "\\ufffd", "Replacement Character", "True", ""],
        ["", "\\u0000", "NULL", "True", ""],
        ["", "\\u001a", "Substitute", "True", ""],
        ["", "\\u001c", "File Separator", "True", ""],
        ["", "\\u001d", "Group Separator", "True", ""],
        ["", "\\u001e", "Record Separator", "True", ""],
        ["", "\\u001f", "Unit Separator", "True", ""],
        ["", "\\u2028", "Line Separator", "True", " "],
        ["", "\\u2029", "Paragraph Separator", "True", "\n"],
        ["", "\\u200b", "Zero Width Space", "True", ""],
        ["", "\\u200c", "Zero Width Non-Joiner", "True", ""],
        ["", "\\u200d", "Zero Width Joiner", "True", ""],
        ["", "\\u200e", "Left-to-Right Mark", "True", ""],
        ["", "\\u200f", "Right-to-Left Mark", "True", ""],
        ["", "\\u202a", "Left-to-Right Embedding", "True", ""],
        ["", "\\u202b", "Right-to-Left Embedding", "True", ""],
        ["", "\\u202c", "Pop Directional Formatting", "True", ""],
        ["", "\\u202d", "Left-to-Right Override", "True", ""],
        ["", "\\u202e", "Right-to-Left Override", "True", ""],
        ["⁡", "\\u2061", "Function Application", "True", ""],
        ["⁢", "\\u2062", "Invisible Times", "True", ""],
        ["⁣", "\\u2063", "Invisible Separator", "True", ""],
        ["⁤", "\\u2064", "Invisible Plus", "True", ""],
        ["", "\\u2066", "Left-to-Right Isolate", "True", ""],
        ["", "\\u2067", "Right-to-Left Isolate", "True", ""],
        ["", "\\u2068", "First Strong Isolate", "True", ""],
        ["", "\\u2069", "Pop Directional Isolate", "True", ""],
        ["﻿", "\\ufeff", "BOM (in middle of file)", "True", ""],
        
        # Smart quotes and typographic characters
        ["'", "\\u2018", "Left Single Quotation Mark", "False", "'"],
        ["'", "\\u2019", "Right Single Quotation Mark", "False", "'"],
        [""", "\\u201c", "Left Double Quotation Mark", "False", "\""],
        [""", "\\u201d", "Right Double Quotation Mark", "False", "\""],
        ["‹", "\\u2039", "Single Left-Pointing Angle Quotation Mark", "False", "<"],
        ["›", "\\u203a", "Single Right-Pointing Angle Quotation Mark", "False", ">"],
        ["«", "\\u00ab", "Left-Pointing Double Angle Quotation Mark", "False", "<<"],
        ["»", "\\u00bb", "Right-Pointing Double Angle Quotation Mark", "False", ">>"],
        ["–", "\\u2013", "En Dash", "False", "-"],
        ["—", "\\u2014", "Em Dash", "False", "--"],
        ["…", "\\u2026", "Horizontal Ellipsis", "False", "..."],
        ["′", "\\u2032", "Prime", "False", "'"],
        ["″", "\\u2033", "Double Prime", "False", "\""],
        ["‐", "\\u2010", "Hyphen", "False", "-"],
        ["‑", "\\u2011", "Non-Breaking Hyphen", "False", "-"],
        ["‒", "\\u2012", "Figure Dash", "False", "-"],
        ["•", "\\u2022", "Bullet", "False", "*"],
        ["·", "\\u00b7", "Middle Dot", "False", "."],
        
        # Common problematic diacritics with replacements
        ["á", "\\u00e1", "Latin Small Letter A with Acute", "False", "a"],
        ["à", "\\u00e0", "Latin Small Letter A with Grave", "False", "a"],
        ["â", "\\u00e2", "Latin Small Letter A with Circumflex", "False", "a"],
        ["ä", "\\u00e4", "Latin Small Letter A with Diaeresis", "False", "a"],
        ["ã", "\\u00e3", "Latin Small Letter A with Tilde", "False", "a"],
        ["å", "\\u00e5", "Latin Small Letter A with Ring Above", "False", "a"],
        ["ç", "\\u00e7", "Latin Small Letter C with Cedilla", "False", "c"],
        ["é", "\\u00e9", "Latin Small Letter E with Acute", "False", "e"],
        ["è", "\\u00e8", "Latin Small Letter E with Grave", "False", "e"],
        ["ê", "\\u00ea", "Latin Small Letter E with Circumflex", "False", "e"],
        ["ë", "\\u00eb", "Latin Small Letter E with Diaeresis", "False", "e"],
        ["í", "\\u00ed", "Latin Small Letter I with Acute", "False", "i"],
        ["ì", "\\u00ec", "Latin Small Letter I with Grave", "False", "i"],
        ["î", "\\u00ee", "Latin Small Letter I with Circumflex", "False", "i"],
        ["ï", "\\u00ef", "Latin Small Letter I with Diaeresis", "False", "i"],
        ["ñ", "\\u00f1", "Latin Small Letter N with Tilde", "False", "n"],
        ["ó", "\\u00f3", "Latin Small Letter O with Acute", "False", "o"],
        ["ò", "\\u00f2", "Latin Small Letter O with Grave", "False", "o"],
        ["ô", "\\u00f4", "Latin Small Letter O with Circumflex", "False", "o"],
        ["ö", "\\u00f6", "Latin Small Letter O with Diaeresis", "False", "o"],
        ["õ", "\\u00f5", "Latin Small Letter O with Tilde", "False", "o"],
        ["ø", "\\u00f8", "Latin Small Letter O with Stroke", "False", "o"],
        ["ú", "\\u00fa", "Latin Small Letter U with Acute", "False", "u"],
        ["ù", "\\u00f9", "Latin Small Letter U with Grave", "False", "u"],
        ["û", "\\u00fb", "Latin Small Letter U with Circumflex", "False", "u"],
        ["ü", "\\u00fc", "Latin Small Letter U with Diaeresis", "False", "u"],
        ["ý", "\\u00fd", "Latin Small Letter Y with Acute", "False", "y"],
        ["ÿ", "\\u00ff", "Latin Small Letter Y with Diaeresis", "False", "y"],
        ["ß", "\\u00df", "Latin Small Letter Sharp S", "False", "ss"],
        ["æ", "\\u00e6", "Latin Small Letter AE", "False", "ae"],
        ["œ", "\\u0153", "Latin Small Ligature OE", "False", "oe"],
        
        # Capital letter diacritics
        ["Á", "\\u00c1", "Latin Capital Letter A with Acute", "False", "A"],
        ["À", "\\u00c0", "Latin Capital Letter A with Grave", "False", "A"],
        ["Â", "\\u00c2", "Latin Capital Letter A with Circumflex", "False", "A"],
        ["Ä", "\\u00c4", "Latin Capital Letter A with Diaeresis", "False", "A"],
        ["Ã", "\\u00c3", "Latin Capital Letter A with Tilde", "False", "A"],
        ["Å", "\\u00c5", "Latin Capital Letter A with Ring Above", "False", "A"],
        ["Ç", "\\u00c7", "Latin Capital Letter C with Cedilla", "False", "C"],
        ["É", "\\u00c9", "Latin Capital Letter E with Acute", "False", "E"],
        ["È", "\\u00c8", "Latin Capital Letter E with Grave", "False", "E"],
        ["Ê", "\\u00ca", "Latin Capital Letter E with Circumflex", "False", "E"],
        ["Ë", "\\u00cb", "Latin Capital Letter E with Diaeresis", "False", "E"],
        ["Í", "\\u00cd", "Latin Capital Letter I with Acute", "False", "I"],
        ["Ì", "\\u00cc", "Latin Capital Letter I with Grave", "False", "I"],
        ["Î", "\\u00ce", "Latin Capital Letter I with Circumflex", "False", "I"],
        ["Ï", "\\u00cf", "Latin Capital Letter I with Diaeresis", "False", "I"],
        ["Ñ", "\\u00d1", "Latin Capital Letter N with Tilde", "False", "N"],
        ["Ó", "\\u00d3", "Latin Capital Letter O with Acute", "False", "O"],
        ["Ò", "\\u00d2", "Latin Capital Letter O with Grave", "False", "O"],
        ["Ô", "\\u00d4", "Latin Capital Letter O with Circumflex", "False", "O"],
        ["Ö", "\\u00d6", "Latin Capital Letter O with Diaeresis", "False", "O"],
        ["Õ", "\\u00d5", "Latin Capital Letter O with Tilde", "False", "O"],
        ["Ø", "\\u00d8", "Latin Capital Letter O with Stroke", "False", "O"],
        ["Ú", "\\u00da", "Latin Capital Letter U with Acute", "False", "U"],
        ["Ù", "\\u00d9", "Latin Capital Letter U with Grave", "False", "U"],
        ["Û", "\\u00db", "Latin Capital Letter U with Circumflex", "False", "U"],
        ["Ü", "\\u00dc", "Latin Capital Letter U with Diaeresis", "False", "U"],
        ["Ý", "\\u00dd", "Latin Capital Letter Y with Acute", "False", "Y"],
        ["Æ", "\\u00c6", "Latin Capital Letter AE", "False", "AE"],
        ["Œ", "\\u0152", "Latin Capital Ligature OE", "False", "OE"],
        
        # Less common but still problematic diacritics
        ["ă", "\\u0103", "Latin Small Letter A with Breve", "False", "a"],
        ["ą", "\\u0105", "Latin Small Letter A with Ogonek", "False", "a"],
        ["ć", "\\u0107", "Latin Small Letter C with Acute", "False", "c"],
        ["č", "\\u010d", "Latin Small Letter C with Caron", "False", "c"],
        ["đ", "\\u0111", "Latin Small Letter D with Stroke", "False", "d"],
        ["ę", "\\u0119", "Latin Small Letter E with Ogonek", "False", "e"],
        ["ě", "\\u011b", "Latin Small Letter E with Caron", "False", "e"],
        ["ğ", "\\u011f", "Latin Small Letter G with Breve", "False", "g"],
        ["ı", "\\u0131", "Latin Small Letter Dotless I", "False", "i"],
        ["ł", "\\u0142", "Latin Small Letter L with Stroke", "False", "l"],
        ["ń", "\\u0144", "Latin Small Letter N with Acute", "False", "n"],
        ["ň", "\\u0148", "Latin Small Letter N with Caron", "False", "n"],
        ["ő", "\\u0151", "Latin Small Letter O with Double Acute", "False", "o"],
        ["ř", "\\u0159", "Latin Small Letter R with Caron", "False", "r"],
        ["ś", "\\u015b", "Latin Small Letter S with Acute", "False", "s"],
        ["š", "\\u0161", "Latin Small Letter S with Caron", "False", "s"],
        ["ť", "\\u0165", "Latin Small Letter T with Caron", "False", "t"],
        ["ů", "\\u016f", "Latin Small Letter U with Ring Above", "False", "u"],
        ["ű", "\\u0171", "Latin Small Letter U with Double Acute", "False", "u"],
        ["ź", "\\u017a", "Latin Small Letter Z with Acute", "False", "z"],
        ["ż", "\\u017c", "Latin Small Letter Z with Dot Above", "False", "z"],
        ["ž", "\\u017e", "Latin Small Letter Z with Caron", "False", "z"]
    ]
    
    # Write to string buffer
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    for row in default_mappings:
        writer.writerow(row)
    
    return output.getvalue()


def create_default_mappings(mapping_file: str) -> None:
    """
    Create a default mapping file with common problematic characters.
    
    Args:
        mapping_file (str): Path to save the mappings file
    """
    print(f"Mappings file not found at: {mapping_file}")
    print("Creating default mappings file...")
    
    mappings_csv = get_default_mappings_csv()
    
    # Write to file
    with open(mapping_file, 'w', newline='', encoding='utf-8') as f:
        f.write(mappings_csv)
    
    print(f"Default mappings saved to: {mapping_file}")


def parse_mapping_csv(csv_content: str) -> List[Tuple[str, str, str]]:
    """
    Parse character mappings from CSV content string.
    
    Args:
        csv_content (str): Content of the mappings CSV
        
    Returns:
        list: List of tuples with (char, name, replacement) for chars to process
    """
    mappings = []
    
    # Use CSV reader on string content
    reader = csv.reader(io.StringIO(csv_content))
    header = next(reader, None)  # Get header row
    
    # Check if we have the Replacement column
    has_replacement_col = header and len(header) >= 5 and header[4].strip().lower() == "replacement"
    
    for row in reader:
        if len(row) < 4:
            continue
            
        # Get values from fields
        unicode_str = row[1].strip()
        name = row[2].strip()
        remove = row[3].strip().lower() == 'true'
        
        # Get replacement character if available
        replacement = ""
        if has_replacement_col and len(row) >= 5:
            replacement = row[4]
        
        # Only add to mappings if set to remove
        if remove:
            # Convert unicode escape sequence to the actual character
            try:
                # Handle the unicode escape sequence
                char = bytes(unicode_str, 'utf-8').decode('unicode_escape')
                mappings.append((char, name, replacement))
            except Exception:
                continue
    
    return mappings


def read_char_mappings(mapping_file: str, verbose: bool = True) -> List[Tuple[str, str, str]]:
    """
    Read character mappings from CSV file.
    Creates default file if it doesn't exist.
    
    Args:
        mapping_file (str): Path to the mappings file
        verbose (bool): Whether to print status messages
        
    Returns:
        list: List of tuples with (char, name, replacement) for chars to process
    """
    try:
        # Create default file if it doesn't exist
        if not os.path.exists(mapping_file):
            if verbose:
                create_default_mappings(mapping_file)
            else:
                # Create silently if not verbose
                with open(mapping_file, 'w', newline='', encoding='utf-8') as f:
                    f.write(get_default_mappings_csv())
        
        # Read file content
        with open(mapping_file, 'r', encoding='utf-8') as f:
            csv_content = f.read()
        
        # Parse the CSV content
        mappings = parse_mapping_csv(csv_content)
        
        if verbose:
            print(f"Loaded {len(mappings)} problematic character mappings from: {mapping_file}")
        
        return mappings
        
    except Exception as e:
        if verbose:
            print(f"Error reading mappings file: {str(e)}")
            print("Using default mappings instead.")
        
        # Use the default mappings in memory
        mappings_csv = get_default_mappings_csv()
        return parse_mapping_csv(mappings_csv)


def clean_content(content: Union[bytes, str], mappings_csv: Optional[str] = None) -> Tuple[str, Dict[str, int]]:
    """
    Clean content by removing/replacing problematic Unicode characters.
    
    Args:
        content (bytes or str): Content to clean
        mappings_csv (str, optional): CSV content with character mappings
        
    Returns:
        tuple: (cleaned_content, char_counts)
    """
    # Process content based on type
    if isinstance(content, bytes):
        # Handle BOM at start of binary content
        if content.startswith(b'\xef\xbb\xbf'):  # UTF-8 BOM
            content = content[3:]
        elif content.startswith(b'\xfe\xff') or content.startswith(b'\xff\xfe'):  # UTF-16 BOM
            content = content[2:]
        elif content.startswith(b'\x00\x00\xfe\xff') or content.startswith(b'\xff\xfe\x00\x00'):  # UTF-32 BOM
            content = content[4:]
        
        # Try to decode to text
        try:
            text_content = content.decode('utf-8')
        except UnicodeDecodeError:
            # Try with error handling
            try:
                text_content = content.decode('utf-8', errors='replace')
            except:
                # Last resort
                text_content = content.decode('latin-1')
    else:
        text_content = content
    
    # Load character mappings
    if mappings_csv is None:
        mappings_csv = get_default_mappings_csv()
    
    problematic_chars = parse_mapping_csv(mappings_csv)
    
    # Check and remove BOM if present at start of string
    cleaned_content = text_content
    if text_content and ord(text_content[0]) == 0xFEFF:
        cleaned_content = text_content[1:]
    
    # Count and replace problematic characters
    char_counts = {}
    
    for char, name, replacement in problematic_chars:
        count = cleaned_content.count(char)
        if count > 0:
            char_counts[name] = count
            cleaned_content = cleaned_content.replace(char, replacement)
    
    return cleaned_content, char_counts


def analyze_content(content: Union[bytes, str], mappings_csv: Optional[str] = None) -> Dict:
    """
    Analyze content for problematic Unicode characters without changing it.
    
    Args:
        content (bytes or str): Content to analyze
        mappings_csv (str, optional): CSV content with character mappings
        
    Returns:
        dict: Analysis results with detailed line and column locations
    """
    # Process content based on type
    if isinstance(content, bytes):
        # Check for BOM at start
        has_bom = False
        bom_type = None
        
        if content.startswith(b'\xef\xbb\xbf'):  # UTF-8 BOM
            has_bom = True
            bom_type = "UTF-8 BOM"
        elif content.startswith(b'\xfe\xff'):
            has_bom = True
            bom_type = "UTF-16 BE BOM"
        elif content.startswith(b'\xff\xfe'):
            has_bom = True
            bom_type = "UTF-16 LE BOM"
        elif content.startswith(b'\x00\x00\xfe\xff'):
            has_bom = True
            bom_type = "UTF-32 BE BOM"
        elif content.startswith(b'\xff\xfe\x00\x00'):
            has_bom = True
            bom_type = "UTF-32 LE BOM"
        
        # Try to decode to text
        try:
            text_content = content.decode('utf-8')
            encoding = "utf-8"
            encoding_errors = False
        except UnicodeDecodeError:
            # Try with error handling
            try:
                text_content = content.decode('utf-8', errors='replace')
                encoding = "utf-8 (with replacement)"
                encoding_errors = True
            except:
                # Last resort
                text_content = content.decode('latin-1')
                encoding = "latin-1 (fallback)"
                encoding_errors = True
    else:
        text_content = content
        encoding = "string (already decoded)"
        encoding_errors = False
        has_bom = text_content and ord(text_content[0]) == 0xFEFF
        bom_type = "UTF-8 BOM" if has_bom else None
    
    # Load character mappings
    if mappings_csv is None:
        mappings_csv = get_default_mappings_csv()
    
    problematic_chars = parse_mapping_csv(mappings_csv)
    
    # Analyze problematic characters
    char_counts = {}
    character_details = []
    
    # Split content into lines for location analysis
    lines = text_content.split('\n')
    
    for char, name, replacement in problematic_chars:
        # Skip if character is not present
        if char not in text_content:
            continue
            
        count = text_content.count(char)
        char_counts[name] = count
        
        # Find all occurrences with detailed location information
        all_locations = []
        
        # Track absolute position in the file
        absolute_pos = 0
        
        for line_idx, line in enumerate(lines):
            # Process each character in the line
            for col_idx, c in enumerate(line):
                if c == char:
                    # Calculate context (15 chars before and after)
                    context_start = max(0, col_idx - 15)
                    context_end = min(len(line), col_idx + 15)
                    context = line[context_start:context_end].replace(char, "↯")
                    
                    location_info = {
                        'line': line_idx + 1,  # 1-based line number
                        'column': col_idx + 1,  # 1-based column number
                        'absolute_position': absolute_pos,
                        'context': context
                    }
                    all_locations.append(location_info)
                
                absolute_pos += 1
            
            # Account for newline character in absolute position
            absolute_pos += 1
        
        # Limit sample locations to first 10 for display
        sample_locations = all_locations[:10]
        
        character_details.append({
            'character': char,
            'unicode': f"U+{ord(char):04X}",
            'name': name,
            'replacement': replacement,
            'count': count,
            'sample_locations': sample_locations,
            'all_locations': all_locations  # Include all locations for potential use
        })
    
    # Compile results
    results = {
        'has_bom': has_bom,
        'bom_type': bom_type,
        'encoding': encoding,
        'encoding_errors': encoding_errors,
        'total_length': len(text_content),
        'line_count': len(lines),
        'problematic_char_count': sum(char_counts.values()),
        'character_counts': char_counts,
        'character_details': character_details
    }
    
    return results


def clean_file(file_path: str, mapping_file: Optional[str] = None, 
              output_path: Optional[str] = None, verbose: bool = True,
              return_content: bool = False) -> Union[bool, str]:
    """
    Remove BOM and replace problematic Unicode characters from a file.
    
    Args:
        file_path (str): Path to the file to clean
        mapping_file (str, optional): Path to character mappings file. If None, uses default.
        output_path (str, optional): Path to save cleaned file. If None, adds 'uneffd_' prefix.
        verbose (bool): Whether to print status messages
        return_content (bool): Whether to return the cleaned content as string
        
    Returns:
        bool or str: True if successful, False if error, or the cleaned content if return_content=True
    """
    if verbose:
        print(f"Processing file: {file_path}")
    
    try:
        # Use default mapping file if none provided
        if mapping_file is None:
            package_dir = os.path.dirname(os.path.abspath(__file__))
            mapping_file = os.path.join(package_dir, 'uneff_mappings.csv')
        
        # Read problematic character mappings - this will create the file if it doesn't exist
        mappings = read_char_mappings(mapping_file, verbose)
        
        # Read the file content as binary
        with open(file_path, 'rb') as file:
            binary_content = file.read()
        
        # Create output filename if not provided
        if output_path is None:
            file_dir = os.path.dirname(file_path)
            file_name = os.path.basename(file_path)
            output_path = os.path.join(file_dir, f"uneffd_{file_name}")
        
        # Generate mappings CSV from the mappings
        mappings_csv = io.StringIO()
        writer = csv.writer(mappings_csv, quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        writer.writerow(["Character", "Unicode", "Name", "Remove", "Replacement"])
        for char, name, replacement in mappings:
            writer.writerow(["", f"\\u{ord(char):04x}", name, "True", replacement])
        
        # Clean the content
        cleaned_content, char_counts = clean_content(binary_content, mappings_csv.getvalue())
        
        # Write to new file without problematic characters
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(cleaned_content)
        
        # Log results
        if verbose:
            if char_counts:
                print("\nProblematic characters found and processed:")
                for name, count in char_counts.items():
                    print(f"  - {name}: {count} instance(s)")
                print(f"\nCleaned file saved to: {output_path}")
            else:
                print("No problematic characters found.")
                print(f"Clean copy saved to: {output_path}")
        
        # Return content if requested
        if return_content:
            return cleaned_content
        return True
    
    except Exception as e:
        if verbose:
            print(f"Error processing file: {str(e)}")
        return False


def analyze_file(file_path: str, mapping_file: Optional[str] = None, 
                verbose: bool = True) -> Dict:
    """
    Analyze a file for problematic Unicode characters.
    
    Args:
        file_path (str): Path to the file to analyze
        mapping_file (str, optional): Path to character mappings file
        verbose (bool): Whether to print status messages
        
    Returns:
        dict: Analysis results with detailed line and column locations
    """
    if verbose:
        print(f"Analyzing file: {file_path}")
    
    try:
        # Use default mapping file if none provided
        if mapping_file is None:
            package_dir = os.path.dirname(os.path.abspath(__file__))
            mapping_file = os.path.join(package_dir, 'uneff_mappings.csv')
        
        # Ensure mapping file exists (this will create it if it doesn't)
        read_char_mappings(mapping_file, verbose)
        
        # Now it's safe to read the file
        with open(mapping_file, 'r', encoding='utf-8') as f:
            mappings_csv = f.read()
        
        # Read the file content as binary
        with open(file_path, 'rb') as file:
            binary_content = file.read()
        
        # Analyze the content
        results = analyze_content(binary_content, mappings_csv)
        
        # Add file info
        results['file_path'] = file_path
        results['file_size'] = os.path.getsize(file_path)
        
        # Print results if verbose
        if verbose:
            print(f"\nFile: {file_path}")
            print(f"Size: {results['file_size']} bytes")
            print(f"Encoding: {results['encoding']}")
            print(f"Lines: {results['line_count']}")
            
            if results['has_bom']:
                print(f"BOM: {results['bom_type']} detected at start")
            
            if results['problematic_char_count'] > 0:
                print(f"\nFound {results['problematic_char_count']} problematic characters:")
                for detail in results['character_details']:
                    print(f"\n  Character: '{detail['name']}' [Unicode: {detail['unicode']}]")
                    print(f"  Count: {detail['count']} instances")
                    
                    # Print detailed location information
                    print("  Locations (showing up to 10 instances):")
                    for idx, loc in enumerate(detail['sample_locations'], 1):
                        print(f"    #{idx}: Line {loc['line']}, Column {loc['column']} (Pos: {loc['absolute_position']})")
                        print(f"        Context: ...{loc['context']}...")
                    
                    if detail['count'] > 10:
                        print(f"    ... and {detail['count'] - 10} more instances")
            else:
                print("\nNo problematic characters found.")
        
        return results
    
    except Exception as e:
        if verbose:
            print(f"Error analyzing file: {str(e)}")
        return {'error': str(e)}


def clean_text(text: str, mapping_file: Optional[str] = None, 
              verbose: bool = False) -> str:
    """
    Replace problematic Unicode characters from a text string.
    
    Args:
        text (str): Text string to clean
        mapping_file (str, optional): Path to character mappings file
        verbose (bool): Whether to print status messages
        
    Returns:
        str: Cleaned text
    """
    try:
        # Use default mapping file if none provided
        if mapping_file is None:
            package_dir = os.path.dirname(os.path.abspath(__file__))
            mapping_file = os.path.join(package_dir, 'uneff_mappings.csv')
        
        # Ensure mapping file exists (this will create it if it doesn't)
        read_char_mappings(mapping_file, verbose)
        
        # Now it's safe to read the file
        with open(mapping_file, 'r', encoding='utf-8') as f:
            mappings_csv = f.read()
        
        # Clean the content
        cleaned_text, char_counts = clean_content(text, mappings_csv)
        
        # Log results
        if verbose and char_counts:
            print("Problematic characters found and processed:")
            for name, count in char_counts.items():
                print(f"  - {name}: {count} instance(s)")
        
        return cleaned_text
    
    except Exception as e:
        if verbose:
            print(f"Error cleaning text: {str(e)}")
        # Return original text if there's an error
        return text


def main():
    """
    Main function to handle command line arguments and call clean_file function.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Remove BOM and process problematic Unicode characters from files.')
    parser.add_argument('file', help='Path to the file to clean')
    parser.add_argument('-m', '--mapping', help='Path to custom character mappings file')
    parser.add_argument('-o', '--output', help='Path to save the cleaned file (default: adds uneffd_ prefix)')
    parser.add_argument('-q', '--quiet', action='store_true', help='Suppress status messages')
    parser.add_argument('-a', '--analyze', action='store_true', help='Only analyze file without cleaning')
    
    args = parser.parse_args()
    
    file_path = args.file
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return 1
    
    if args.analyze:
        analyze_file(
            file_path=file_path,
            mapping_file=args.mapping,
            verbose=not args.quiet
        )
    else:
        clean_file(
            file_path=file_path, 
            mapping_file=args.mapping,
            output_path=args.output,
            verbose=not args.quiet
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())