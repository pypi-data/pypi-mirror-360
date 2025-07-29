import sys
import re
from typing import List, Optional, Tuple


class SignatureConverter:
    """
    Class to convert signatures between formats:
    - spaced: bytes separated by spaces, '?' for wildcard
    - escaped: string with \\xHH bytes and '.' for wildcard
    - bytesmask: two strings: hex and mask with 'x' and '?'
    """
    def __init__(self, byte_values: List[Optional[int]], mask: str):
        self.byte_values = byte_values  # list of int or None (wildcard)
        self.mask = mask  # string of 'x' and '?'

    @classmethod
    def from_spaced(cls, s: str) -> "SignatureConverter":
        """
        Parse spaced format, e.g.: "48 8B 05 ? ? ? ? 41"
        """
        parts = s.strip().split()
        byte_values = []
        mask = ''
        for p in parts:
            if p in ('?', '??'):
                byte_values.append(None)
                mask += '?'
            else:
                try:
                    byte_values.append(int(p, 16))
                    mask += 'x'
                except ValueError:
                    raise ValueError(f"Invalid byte value in spaced format: {p}")
        return cls(byte_values, mask)

    @classmethod
    def from_escaped(cls, s: str) -> "SignatureConverter":
        """
        Parse escaped format, e.g.: "\\x48\\x8B\\x05....\\x41"
        '.' - wildcard, \\xHH - byte
        """
        if not re.fullmatch(r'(\\x[0-9A-Fa-f]{2}|[.])+', s.strip()):
            raise ValueError("Invalid characters found in escaped format input")

        tokens = re.findall(r'\\x([0-9A-Fa-f]{2})|(\.)', s)
        byte_values = []
        mask = ''
        for hex_byte, dot in tokens:
            if dot:
                byte_values.append(None)
                mask += '?'
            else:
                byte_values.append(int(hex_byte, 16))
                mask += 'x'
        return cls(byte_values, mask)

    @classmethod
    def from_bytesmask(cls, hex_string: str, mask: str) -> "SignatureConverter":
        """
        Parse bytesmask format: hex string + mask
        hex_string can contain:
        - plain hex digits (e.g. 488B05...)
        - or escaped bytes like "\\x48\\x8B\\x05"
        - may contain spaces, commas, quotes
        """
        # Remove spaces, commas, quotes
        clean_str = hex_string.strip().strip('\'"').replace(' ', '').replace(',', '')
        # If string contains \x, remove them and keep hex digits only
        if clean_str.startswith('\\x') or '\\x' in clean_str:
            # Remove all \x sequences, keep hex digits only
            clean_str = re.sub(r'\\x', '', clean_str)

        # Now clean_str should be a hex string like '488B05...'
        if len(clean_str) % 2 != 0:
            raise ValueError("Hex string length must be even")

        b = bytes.fromhex(clean_str)
        if len(b) != len(mask):
            raise ValueError("Length of byte string and mask must be equal")
        byte_values = [b[i] if mask[i] == 'x' else None for i in range(len(b))]
        return cls(byte_values, mask)

    def to_spaced(self) -> str:
        """
        Convert to spaced format
        """
        return ' '.join(f'{b:02X}' if b is not None else '?' for b in self.byte_values)

    def to_escaped(self) -> str:
        """
        Convert to escaped format
        """
        return ''.join(f'\\x{b:02X}' if b is not None else '.' for b in self.byte_values)

    def to_bytesmask(self) -> Tuple[str, str]:
        """
        Convert to bytesmask (hex string, mask)
        """
        b = bytes([b if b is not None else 0 for b in self.byte_values])
        return b.hex().upper(), self.mask


def detect_format(input_data: str, mask: Optional[str] = None) -> str:
    """
    Detect input format:
    - bytesmask (if mask provided)
    - escaped (contains \\x or .)
    - spaced (bytes and ? separated by spaces)
    - hex (no spaces)
    """
    input_data = input_data.strip()
    if mask is not None:
        return 'bytesmask'

    if '\\x' in input_data or '.' in input_data:
        if re.fullmatch(r'(\\x[0-9A-Fa-f]{2}|[.])+', input_data):
            return 'escaped'
        else:
            raise ValueError("Input contains \\x or '.' but does not match escaped format fully")

    if re.fullmatch(r'([0-9A-Fa-f]{2}|\?{1,2})(\s([0-9A-Fa-f]{2}|\?{1,2}))*', input_data):
        return 'spaced'

    if re.fullmatch(r'[0-9A-Fa-f]+', input_data):
        raise ValueError("Hex string detected without mask. For bytesmask format, mask is required.")

    raise ValueError("Cannot detect input format. Please specify explicitly.")


def print_usage():
    print("Usage:")
    print("  sigconv <to_format> <input> [mask_for_bytesmask]")
    print()
    print("to_format:")
    print("  escaped    - output escaped format with '\\xHH' bytes and '.' for wildcard")
    print("  spaced     - output bytes separated by spaces, '?' for wildcard")
    print("  bytesmask  - output as a pair (hex string, mask), e.g.: \"\\x48\\x8B\\x05\\x00\", \"xxx?\"")
    print()
    print("Input formats supported:")
    print("  spaced:   bytes in hex separated by spaces, e.g.:")
    print("            48 8B 05 ? ? ? ? 41")
    print("            '?' or '??' denotes wildcard byte")
    print()
    print("  escaped:  string with escaped bytes '\\xHH' and '.' for wildcard, e.g.:")
    print("            \\x48\\x8B\\x05....\\x41")
    print()
    print("  bytesmask: two input styles:")
    print("    1) hex string and mask as separate arguments, e.g.:")
    print("       488B050000000041 xxx????x")
    print("    2) hex and mask combined in one argument, separated by a comma (spaces optional), e.g.:")
    print("       \"\\x48\\x8B\\x05\\x00\\x00\\x00\\x00\\x41\", \"xxx????x\"")
    print()
    print("Examples:")
    print("  # Convert escaped to spaced")
    print("  sigconv spaced \"\\x48\\x8B\\x05....\\x41\"")
    print()
    print("  # Convert spaced to escaped")
    print("  sigconv escaped \"48 8B 05 ? ? ? ? 41\"")
    print()
    print("  # Convert bytesmask (hex+mask as separate args) to spaced")
    print("  sigconv spaced 488B050000000041 xxx????x")
    print()
    print("  # Convert bytesmask (hex and mask combined with comma) to spaced")
    print("  sigconv spaced \"\\x48\\x8B\\x05\\x00\\x00\\x00\\x00\\x41\", \"xxx????x\"")
    print()
    print("Output examples:")
    print("  spaced:   48 8B 05 ? ? ? ? 41")
    print("  escaped:  \\x48\\x8B\\x05....\\x41")
    print("  bytesmask: \"\\x48\\x8B\\x05\\x00\\x00\\x00\\x00\\x41\", \"xxx????x\"")
    print()
    print("Notes:")
    print("  - Use quotes around inputs with spaces or backslashes to avoid shell issues.")
    print("  - For bytesmask input, mask can be passed as a separate third argument")
    print("    or together with the hex in the second argument separated by a comma.")
    print("  - Wildcard bytes are '?' in spaced, '.' in escaped, and '?' in bytesmask mask.")
    print("  - Hex string input without mask will cause an error.")
    print()


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print_usage()
        sys.exit(0)

    if len(sys.argv) < 3:
        print("Error: Missing required arguments.\n")
        print_usage()
        sys.exit(1)

    to_fmt = sys.argv[1].lower()
    input_data = sys.argv[2]
    mask = sys.argv[3] if len(sys.argv) > 3 else None

    # Handle combined bytesmask input with comma (hex and mask)
    if mask is None and ',' in input_data:
        parts = [part.strip().strip('\"\'') for part in input_data.split(',', 1)]
        if len(parts) == 2:
            input_data, mask = parts[0], parts[1]

    if not input_data:
        print("Error: input string cannot be empty")
        sys.exit(1)

    try:
        from_fmt = detect_format(input_data, mask)
    except Exception as e:
        print(f"Error detecting format: {e}")
        sys.exit(1)

    try:
        if from_fmt == 'escaped':
            sig = SignatureConverter.from_escaped(input_data)
        elif from_fmt == 'spaced':
            sig = SignatureConverter.from_spaced(input_data)
        elif from_fmt == 'bytesmask':
            if mask is None:
                print("Error: mask is required for bytesmask input format.")
                sys.exit(1)
            sig = SignatureConverter.from_bytesmask(input_data, mask)
        else:
            print(f"Unsupported input format: {from_fmt}")
            sys.exit(1)
    except Exception as e:
        print(f"Error parsing input: {e}")
        sys.exit(1)

    if to_fmt == 'spaced':
        print(sig.to_spaced())
    elif to_fmt == 'escaped':
        print(sig.to_escaped())
    elif to_fmt == 'bytesmask':
        bstr, mstr = sig.to_bytesmask()
        escaped = ''.join(f'\\x{int(bstr[i:i+2],16):02X}' for i in range(0, len(bstr), 2))
        print(f'"{escaped}", "{mstr}"')
    else:
        print(f"Unknown output format: {to_fmt}")
        sys.exit(1)


if __name__ == "__main__":
    main()