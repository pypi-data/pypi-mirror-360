#!/usr/bin/env python3

import npyscreen
import curses
import argparse
import re
import json
from pathlib import Path

def parse_sta_report(report):
    with open(report, 'r') as f:
        content = f.read()

    blocks = re.split(r'\n\s*Startpoint:', content)
    results = []

    for idx, block in enumerate(blocks[1:]):
        block_text = f"  Startpoint:{block}"  # reattach trimmed Startpoint
        try:
            start_raw = re.search(r"^  Startpoint: ([^()]+)", block_text, re.M).group(1).strip()
            end_raw = re.search(r"^  Endpoint: ([^()]+)", block_text, re.M).group(1).strip()
            slack = float(re.search(r"^\s*slack.*?(-?\d+\.\d+)", block_text, re.M).group(1))
        except AttributeError:
            continue  # skip malformed block

        # Normalize startpoint and endpoint
        startpoint = re.sub(r'(reg(?:_+\d+)+)_+', 'reg*', start_raw)
        endpoint  = re.sub(r'(reg(?:_+\d+)+)_+', 'reg*', end_raw)

        point_lines = re.findall(r"^\s*(\S+)(?: \([^)]+\))?\s+(\d+\.\d+)\s+\S+", block_text, re.M)
        logic_paths = []

        for full_path, incr in point_lines:
            if float(incr) == 0.0:
                continue
            path_clean = re.sub(r"\([^)]*\)", "", full_path).strip()
            path_clean = re.sub(r"U\d+/(Z|ZN|CO)$", "", path_clean)
            if len(path_clean) == 0:
                path_clean = "  "
            logic_paths.append(path_clean)

        # Collapse consecutive identical paths
        collapsed = []
        last = None
        count = 0
        for path in logic_paths:
            if path == last:
                count += 1
            else:
                if last:
                    collapsed.append(f"{last}/logic+{count}")
                last = path
                count = 1
        if last:
            collapsed.append(f"{last}/logic+{count}")

        results.append({
            "startpoint": startpoint,
            "endpoint": endpoint,
            "slack": slack,
            "collapsed_paths": collapsed
        })

    return results

def get_min_max_slack(results):
    slacks = [entry["slack"] for entry in results]
    return min(slacks), max(slacks)

def get_unique_startpoints(results):
    return sorted(set(entry["startpoint"] for entry in results))

def get_unique_endpoints(results):
    return sorted(set(entry["endpoint"] for entry in results))

def get_unique_collapsed_path_elements(results):
    path_set = set()
    for entry in results:
        path_set.update(entry["collapsed_paths"])
    return sorted(path_set)

def bin_results_by_slack(results, min_slack, max_slack, num_bins):
    bin_width = (max_slack - min_slack) / num_bins
    bins = [[] for _ in range(num_bins)]

    for record in results:
        s = record["slack"]
        if s == max_slack:
            index = num_bins - 1
        elif s > max_slack:
            continue
        else:
            index = int((s - min_slack) // bin_width)
        bins[index].append(record)

    return bins

class HistogramWidget(npyscreen.MultiLineAction):
    def __init__(self, *args, **kwargs):
        self.bins = []
        self.selected_bin = 0
        super().__init__(*args, **kwargs)

    def update_histogram(self):
        height = self.height - 4  # space for borders + X axis labels
        width = self.width - 2    # inside box border
        max_count = max(len(b) for b in self.bins) if self.bins else 1
        bin_width = 1  # fixed as per assumption
        bin_count = len(self.bins)

        # Reset content
        display_lines = [" " * width for _ in range(height)]

        for x in range(bin_count):
            bin_len = len(self.bins[x])
            bin_height = int((bin_len / max_count) * height)
            char = '.'
            if x == self.selected_bin:
                char = "#"

            for y in range(bin_height):
                row = height - y - 1
                line = list(display_lines[row])
                line[x] = char
                display_lines[row] = "".join(line)

        # Label X-axis with start slack of each bin
        slack_labels = [""] * width
        slack_range = self.max_slack - self.min_slack
        slack_step = slack_range / bin_count
        for x in range(0, width, max(1, width // 8)):
            slack_value = self.min_slack + (x * slack_step)
            label = f"{slack_value:.3f}"
            for i, ch in enumerate(label):
                if x + i < width:
                    slack_labels[x + i] = ch
        display_lines.append("".join(ch or " " for ch in slack_labels))

        # Label top Y-axis
        selected_count = len(self.bins[self.selected_bin])
        selected_slack = slack_step * self.selected_bin + self.min_slack
        display_lines.insert(0, f"max={max_count} selected={selected_count}({selected_slack:.4f}ns)".ljust(width))

        self.values = display_lines
        self.display()

    def handle_input(self, key):
        # npyscreen.notify_confirm(f"Key code: {key}", title="Debug")
        if key in (curses.KEY_LEFT, curses.KEY_RIGHT, 452, 454): # curses.KEY_B1, curses.KEY_B3
            self.selected_bin = max(0, min(
                self.selected_bin + (1 if key in ((curses.KEY_RIGHT, 454)) else -1), # curses.KEY_B3
                len(self.bins) - 1
            ))
            self.selected_bin = self.selected_bin
            self.update_histogram()
            self.parent.update_display()
            self.display()
        elif key in ((ord('+'), ord('-'))):
            if key == ord('+'): # zoom in
                span = self.max_slack - self.min_slack
                self.max_slack = self.min_slack + span / 2
            else: # zoom out
                self.max_slack = min(self.max_slack * 2, self.absmax_slack)
            bins = bin_results_by_slack(self.paths, self.min_slack, self.max_slack, self.width - 2)
            self.bins = bins
            self.update_histogram()
            self.parent.update_display()
            self.display()
        else:
            return super().handle_input(key)

    def filter(self, filter_string):
        is_negative = False
        is_regex = False
        pattern = None
        paths = []

        # Detect negative filters.
        if filter_string.startswith('-'):
            is_negative = True
            filter_string = filter_string[1:]

        # Detect raw regex pattern: starts with r" and ends with "
        if filter_string.startswith('r"') and filter_string.endswith('"') and len(filter_string) > 3:
            try:
                pattern = re.compile(filter_string[2:-1])
                is_regex = True
            except re.error:
                npyscreen.notify_confirm(f"Invalid regular expression, ignoring.", title="Notice")
                return  # Invalid regex: ignore filtering

        for path in self.paths:
            target_fields = [path['startpoint'], path['endpoint']]
            target_fields += path.get('collapsed_paths', [])

            if is_regex:
                if any(pattern.search(field) for field in target_fields):
                    if not is_negative:
                        paths.append(path)
                elif is_negative:
                    paths.append(path)
            else:
                if any(filter_string in field for field in target_fields):
                    if not is_negative:
                        paths.append(path)
                elif is_negative:
                    paths.append(path)

        if len(paths) > 0:
            # use the current "zoom" settings
            bins = bin_results_by_slack(paths, self.min_slack, self.max_slack, self.width - 2)
            self.bins = bins
            self.update_histogram()
            self.parent.update_display()
            self.display()
        else:
            npyscreen.notify_confirm(f"Filter matched nothing, ignoring.", title="Notice")

class DetailPopup(npyscreen.ActionFormV2):
    preloaded_content = ""

    def create(self):
        self.text_widget = self.add(
            npyscreen.Pager,
            name="Details",
        )

    def beforeEditing(self):
        if self.preloaded_content:
            content = []
            content += [self.preloaded_content['startpoint']]
            for line in self.preloaded_content['collapsed_paths']:
                content += [f"  {line}"]
            content += [self.preloaded_content['endpoint']]
            content += [f"Slack: {self.preloaded_content['slack']}"]
            self.text_widget.values = content

    def set_text(self, content):
        self.preloaded_content = content

    def on_ok(self):
        self.parentApp.setNextForm("MAIN")

    def on_cancel(self):
        self.parentApp.setNextForm("MAIN")

    def handle_input(self, key):
        if key not in (curses.KEY_UP, curses.KEY_DOWN, 450, 456):
            self.on_cancel()
            self.editing = False
            self.exit_editing()
            return
        return super().handle_input(key)

class SelectableMultiLine(npyscreen.MultiLine):
    def handle_input(self, key):
        if key in ("KEY_UP", "KEY_DOWN"):
            return super().handle_input(key)
        elif key in (" ", "^M"):
            self.parent.toggle_item(self.cursor_line)
        else:
            return super().handle_input(key)
class PathListWidget(npyscreen.MultiLineAction):
    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)
        self.scrollbar = True
        self.add_handlers({
            "^M": self.actionHighlighted,   # Enter
            " ": self.actionHighlighted,    # Space
        })

    def actionHighlighted(self, act_on_this=None, key_press=None):
        details = self.entry_data[self.cursor_line]
        form = self.parent.parentApp.getForm("DETAIL_POPUP")
        form.preloaded_content = details
        self.parent.parentApp.switchForm("DETAIL_POPUP")

    def update_paths(self, paths):
        self.entry_data = paths
        self.values = [f"{p['startpoint']} -> {p['endpoint']} ({p['slack']})" for p in paths]
        self.display()

    def handle_input(self, key):
        # Normalize Windows-specific arrow keys
        if key in (450,):  # Windows Up curses.KEY_A2
            key = curses.KEY_UP
        elif key in (456,):  # Windows Down curses.KEY_C2
            key = curses.KEY_DOWN
        return super().handle_input(key)

    def display_value(self, vl):
        return f"  {vl}"  # add margin to avoid text against scrollbar

class PathDetailPopup(npyscreen.Popup):
    def create(self):
        self.detail_text = self.add(npyscreen.Pager)


class MainApp(npyscreen.NPSAppManaged):
    def __init__(self, report, output):
        self.report = report

        report_path = Path(report)

        if report_path.suffix == ".json":
            self.paths = paths = json.loads(report_path.read_text())
        else:
            self.paths = paths = parse_sta_report(report_path)

        self.min_slack, self.max_slack = get_min_max_slack(paths)

        if output:
            json_path = report_path.with_suffix(".json")
            json_path.write_text(json.dumps(self.paths, indent=2))

        super().__init__()

    def onStart(self):
        self.addForm("MAIN", MainForm, name="Path Delay UI")
        self.addForm("DETAIL_POPUP", DetailPopup)

    def onCleanExit(self):
        print("Exiting app")

class FilterText(npyscreen.TitleText):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key in (curses.ascii.NL, curses.ascii.CR, 10, 13):
            self.entry_widget.handlers[key] = self._on_enter

    def _on_enter(self, *args, **keywords):
        self.parent.apply_filter(self.value)

class MainForm(npyscreen.FormBaseNew):
    def create(self):
        max_y, max_x = self.useable_space()
        max_y = max_y - 1
        # Define available height chunks
        hist_height = max_y // 2
        path_height = max_y // 2 - 3  # leave room for input

        self.selected_bin = 0
        self.data = []  # Replace with actual data
        self.filtered_data = self.data

        self.histogram = self.add(HistogramWidget, name="Delay Histogram",
                                  relx=0, rely=0, max_height=hist_height)
        histo_width = self.histogram.width - 2 # space for border
        bins = bin_results_by_slack(self.parentApp.paths, self.parentApp.min_slack, self.parentApp.max_slack, histo_width)
        self.histogram.bins = bins
        self.histogram.min_slack = self.parentApp.min_slack
        self.histogram.max_slack = self.parentApp.max_slack
        self.histogram.absmax_slack = self.parentApp.max_slack
        self.histogram.paths = self.parentApp.paths

        self.path_list = self.add(PathListWidget, name="Paths in Bin",
                                  relx=2, rely=hist_height, max_height=path_height)

        # Filter input box (bottom line)
        self.filter_input = self.add(FilterText, name="Filter:",
                                     relx=0, rely=hist_height + path_height,
                                     max_height=1, max_width=max_x - 4)
        # self.filter_input.when_value_edited = self.on_filter_change

        self.pane_order = [self.histogram, self.path_list, self.filter_input]

        # setup default
        self.set_editing(self.histogram)
        self.update_display()

    def update_display(self):
        self.histogram.update_histogram()
        self.path_list.update_paths(self.get_paths_in_selected_bin())

    def get_paths_in_selected_bin(self):
        return self.histogram.bins[self.histogram.selected_bin]

    def handle_input(self, key):
        if key != -1:
            self.process_key(key)
        super().handle_input(key)
        self.update_display()

    def process_key(self, key):
        if key == ord('q'):
            exit(0)

    def apply_filter(self, filter_string):
        self.histogram.filter(filter_string)

    def on_filter_change(self):
        filter_val = self.filter_input.value.strip()
        self.apply_filter(filter_val)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Slack navigator", prog="slacknav")
    parser.add_argument(
        "--report", required=True, help="Delay file to parse", type=str
    )
    parser.add_argument(
        "--output", action="store_true", help = "Write the processed report to a redacted output file."
    )
    args = parser.parse_args()

    app = MainApp(args.report, args.output)
    app.run()
