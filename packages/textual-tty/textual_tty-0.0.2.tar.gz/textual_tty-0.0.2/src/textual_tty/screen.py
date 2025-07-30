"""
Terminal Screen: Rich Console-based terminal screen implementation.

This module provides the Screen class that uses rich.Console as the underlying
representation for terminal content. It manages both main and alternate screen
buffers and provides methods for the Parser to manipulate terminal state.
"""

from __future__ import annotations

from typing import List, Optional

from rich.console import Console
from rich.style import Style
from rich.text import Text, Span


class TerminalScreen:
    """
    A terminal screen that uses rich.Console for content representation.

    This class manages both main and alternate screen buffers, cursor position,
    terminal modes, and provides methods for content manipulation that the
    Parser can use.
    """

    def __init__(self, width: int, height: int) -> None:
        """Initialize the screen with given dimensions."""
        self.width = width
        self.height = height

        # Dual console system for main/alt buffers
        self.main_console = Console(
            width=width,
            height=height,
            legacy_windows=False,
            force_terminal=True,
            _environ={},
        )
        self.alt_console = Console(
            width=width,
            height=height,
            legacy_windows=False,
            force_terminal=True,
            _environ={},
        )

        # Current active console (starts with main)
        self.current_console = self.main_console
        self.in_alt_screen = False

        # Cursor state
        self.cursor_x = 0
        self.cursor_y = 0
        self.cursor_visible = True

        # Terminal modes
        self.auto_wrap = True
        self.insert_mode = False
        self.application_keypad = False
        self.mouse_tracking = False

        self._mode_map = {
            1: "application_keypad",
            4: "insert_mode",
            7: "auto_wrap",
            25: "cursor_visible",
        }
        self.saved_lines: list[Text] | None = None

        # Scroll region (top, bottom) - 0-indexed
        self.scroll_top = 0
        self.scroll_bottom = height - 1

        # Character attributes for next write
        self.current_style = Style()

        # Saved cursor state (for DECSC/DECRC)
        self.saved_cursor_x = 0
        self.saved_cursor_y = 0
        self.saved_style = Style()

        # Content buffer - we'll use this to track screen lines
        self.lines: List[Text] = [Text() for _ in range(height)]

    def resize(self, width: int, height: int) -> None:
        """Resize the screen to new dimensions."""
        self.width = width
        self.height = height

        # Recreate consoles with new size
        self.main_console = Console(
            width=width,
            height=height,
            legacy_windows=False,
            force_terminal=True,
            _environ={},
        )
        self.alt_console = Console(
            width=width,
            height=height,
            legacy_windows=False,
            force_terminal=True,
            _environ={},
        )

        # Update current console reference
        self.current_console = self.alt_console if self.in_alt_screen else self.main_console

        # Adjust scroll region
        self.scroll_bottom = height - 1

        # Resize content buffer
        if len(self.lines) < height:
            # Add new lines
            self.lines.extend([Text() for _ in range(height - len(self.lines))])
        elif len(self.lines) > height:
            # Remove excess lines
            self.lines = self.lines[:height]

        # Clamp cursor position
        self.cursor_x = min(self.cursor_x, width - 1)
        self.cursor_y = min(self.cursor_y, height - 1)

    def get_content(self) -> List[Text]:
        """Get the current screen content as a list of Rich Text objects."""
        return self.lines.copy()

    def write_cell(self, character: str, style: Optional[Style] = None) -> None:
        """Write a single styled character at the cursor position."""
        if style is None:
            style = self.current_style

        # Ensure we have a valid cursor position
        if not (0 <= self.cursor_y < self.height):
            return

        # Handle line wrapping or clipping
        if self.cursor_x >= self.width:
            if self.auto_wrap:
                self.line_feed(is_wrapped=True)
                self.cursor_x = 0
            else:
                self.cursor_x = self.width - 1

        # Ensure the line exists and has enough content
        line = self.lines[self.cursor_y]

        # Insert or overwrite character
        if self.insert_mode:
            # Insert character at cursor position
            if self.cursor_x < len(line.plain):
                # Insert in middle of existing line
                new_line = line[: self.cursor_x] + Text(character, style) + line[self.cursor_x :]
            else:
                # Append to end of line
                new_line = line.copy()
                # Pad with spaces if needed
                while len(new_line.plain) < self.cursor_x:
                    new_line.append(" ")
                new_line.append(character, style)

            # Truncate if line becomes too long
            if len(new_line.plain) > self.width:
                # Preserve styles when truncating
                new_line = new_line[: self.width]

            self.lines[self.cursor_y] = new_line
        else:
            # Overwrite character
            if self.cursor_x < len(line.plain):
                # Replace character in existing line
                new_line = line[: self.cursor_x] + Text(character, style) + line[self.cursor_x + 1 :]
                self.lines[self.cursor_y] = new_line
            else:
                # Append to end of line
                new_line = line.copy()
                # Pad with spaces if needed
                while len(new_line.plain) < self.cursor_x:
                    new_line.append(" ")
                new_line.append(character, style)
                self.lines[self.cursor_y] = new_line

        # Move cursor forward
        if self.auto_wrap or self.cursor_x < self.width - 1:
            self.cursor_x += 1

    def clear_rect(self, sx: int, sy: int, ex: int, ey: int, style: Optional[Style] = None) -> None:
        """Clear a rectangular region."""
        if style is None:
            style = Style()

        for y in range(max(0, sy), min(self.height, ey + 1)):
            line = self.lines[y]

            # If line is empty or sx is beyond line length, nothing to clear
            if not line.plain or sx >= len(line.plain):
                continue

            # Build character array and span list
            plain_chars = list(line.plain)
            spans = []

            # Clear the specified range
            clear_start = max(0, sx)
            clear_end = min(len(plain_chars), ex + 1)
            for x in range(clear_start, clear_end):
                plain_chars[x] = " "

            # Reconstruct spans properly
            plain_text = "".join(plain_chars)

            # Copy original spans that don't overlap with cleared region
            for span in line.spans:
                if span.end <= clear_start:
                    # Span is completely before cleared region
                    spans.append(span)
                elif span.start >= clear_end:
                    # Span is completely after cleared region
                    spans.append(span)
                else:
                    # Span overlaps with cleared region, need to split it
                    if span.start < clear_start:
                        # Part before cleared region
                        spans.append(Span(span.start, clear_start, span.style))
                    if span.end > clear_end:
                        # Part after cleared region
                        spans.append(Span(clear_end, span.end, span.style))

            # Add span for the cleared region if it exists
            if clear_end > clear_start:
                spans.append(Span(clear_start, clear_end, style))

            # Sort spans by start position
            spans.sort(key=lambda s: s.start)

            # Create new Text with explicit spans
            new_line = Text(plain_text, spans=spans)
            self.lines[y] = new_line

    def clear_screen(self, mode: int = 0) -> None:
        """Clear screen (ED sequence)."""
        if mode == 0:  # Clear from cursor to end of screen
            # Clear from cursor to end of current line
            self.clear_line(0)
            # Clear all lines below cursor
            for y in range(self.cursor_y + 1, self.height):
                self.lines[y] = Text()
        elif mode == 1:  # Clear from beginning of screen to cursor
            # Clear all lines above cursor
            for y in range(0, self.cursor_y):
                self.lines[y] = Text()
            # Clear from beginning of current line to cursor
            self.clear_line(1)
        elif mode == 2:  # Clear entire screen
            self.lines = [Text() for _ in range(self.height)]

    def clear_line(self, mode: int = 0) -> None:
        """Clear line (EL sequence)."""
        if not (0 <= self.cursor_y < self.height):
            return

        line = self.lines[self.cursor_y]
        plain_text = list(line.plain)

        if mode == 0:  # Clear from cursor to end of line
            plain_text = plain_text[: self.cursor_x]
        elif mode == 1:  # Clear from beginning of line to cursor
            plain_text = [" "] * self.cursor_x + plain_text[self.cursor_x :]
        elif mode == 2:  # Clear entire line
            plain_text = []

        # Rebuild line
        new_line = Text()
        for char in plain_text:
            new_line.append(char)
        self.lines[self.cursor_y] = new_line

    def insert_lines(self, count: int) -> None:
        """Insert blank lines at cursor position."""
        for _ in range(count):
            self.lines.insert(self.cursor_y, Text())
            # Remove lines from bottom to maintain screen height
            self.lines.pop()

    def delete_lines(self, count: int) -> None:
        """Delete lines at cursor position."""
        for _ in range(count):
            self.lines.pop(self.cursor_y)
            # Add blank line at bottom
            self.lines.append(Text())

    def insert_characters(self, count: int) -> None:
        """Insert blank characters at cursor position."""
        if not (0 <= self.cursor_y < self.height):
            return

        line = self.lines[self.cursor_y]
        plain_text = list(line.plain)

        # Insert spaces
        for _ in range(count):
            plain_text.insert(self.cursor_x, " ")

        # Truncate if line becomes too long
        if len(plain_text) > self.width:
            plain_text = plain_text[: self.width]

        # Rebuild line
        new_line = Text()
        for char in plain_text:
            new_line.append(char)
        self.lines[self.cursor_y] = new_line

    def delete_characters(self, count: int) -> None:
        """Delete characters at cursor position."""
        if not (0 <= self.cursor_y < self.height):
            return

        line = self.lines[self.cursor_y]
        plain_text = list(line.plain)

        # Delete characters
        for _ in range(count):
            if self.cursor_x < len(plain_text):
                plain_text.pop(self.cursor_x)

        # Rebuild line
        new_line = Text()
        for char in plain_text:
            new_line.append(char)
        self.lines[self.cursor_y] = new_line

    def scroll_up(self, count: int) -> None:
        """Scroll content up within scroll region."""
        # Remove lines from top of scroll region
        for _ in range(count):
            self.lines.pop(self.scroll_top)
            # Add blank line at bottom of scroll region
            self.lines.insert(self.scroll_bottom, Text())

    def scroll_down(self, count: int) -> None:
        """Scroll content down within scroll region."""
        # Insert blank lines at top of scroll region
        for _ in range(count):
            self.lines.insert(self.scroll_top, Text())
            # Remove lines from bottom of scroll region
            self.lines.pop(self.scroll_bottom + 1)

    def set_cursor(self, x: Optional[int], y: Optional[int]) -> None:
        """Set cursor position."""
        if x is not None:
            self.cursor_x = max(0, min(x, self.width - 1))
        if y is not None:
            self.cursor_y = max(0, min(y, self.height - 1))

    def line_feed(self, is_wrapped: bool = False) -> None:
        """Perform line feed."""
        if self.cursor_y >= self.scroll_bottom:
            # Scroll up within scroll region
            self.scroll_up(1)
        else:
            # Move cursor down
            self.cursor_y += 1

    def carriage_return(self) -> None:
        """Move cursor to beginning of line."""
        self.cursor_x = 0

    def backspace(self) -> None:
        """Move cursor back one position."""
        if self.cursor_x > 0:
            self.cursor_x -= 1
        elif self.cursor_y > 0:
            # Wrap to end of previous line
            self.cursor_y -= 1
            self.cursor_x = self.width - 1

    def set_scroll_region(self, top: int, bottom: int) -> None:
        """Set scroll region."""
        self.scroll_top = max(0, min(top, self.height - 1))
        self.scroll_bottom = max(self.scroll_top, min(bottom, self.height - 1))

    def save_cursor(self) -> None:
        """Save cursor position and attributes (DECSC)."""
        self.saved_cursor_x = self.cursor_x
        self.saved_cursor_y = self.cursor_y
        self.saved_style = self.current_style

    def restore_cursor(self) -> None:
        """Restore cursor position and attributes (DECRC)."""
        self.cursor_x = self.saved_cursor_x
        self.cursor_y = self.saved_cursor_y
        self.current_style = self.saved_style

    def alternate_screen_on(self) -> None:
        """Switch to alternate screen buffer."""
        if not self.in_alt_screen:
            self.saved_lines = self.lines[:]
            self.lines = [Text() for _ in range(self.height)]
            self.in_alt_screen = True
            self.current_console = self.alt_console

    def alternate_screen_off(self) -> None:
        """Switch back to main screen buffer."""
        if self.in_alt_screen:
            if self.saved_lines is not None:
                self.lines = self.saved_lines
                self.saved_lines = None
            self.in_alt_screen = False
            self.current_console = self.main_console

    def set_mode(self, mode: int, private: bool) -> None:
        """Set terminal mode."""
        if private:
            if mode in self._mode_map:
                setattr(self, self._mode_map[mode], True)
        else:
            if mode in self._mode_map:
                setattr(self, self._mode_map[mode], True)

    def clear_mode(self, mode: int, private: bool) -> None:
        """Clear terminal mode."""
        if private:
            if mode in self._mode_map:
                setattr(self, self._mode_map[mode], False)
        else:
            if mode in self._mode_map:
                setattr(self, self._mode_map[mode], False)

    def alignment_test(self) -> None:
        """Fill screen with 'E' characters for alignment test."""
        for y in range(self.height):
            line = Text()
            for x in range(self.width):
                line.append("E")
            self.lines[y] = line
