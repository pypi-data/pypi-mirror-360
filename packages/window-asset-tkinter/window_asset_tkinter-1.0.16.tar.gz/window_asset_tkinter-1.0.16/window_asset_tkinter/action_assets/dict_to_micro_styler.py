"""
File in charge of converting a dictionnary or list to the micro-styler format
"""


class DictToMicroStyler:
    """ Class in charge of converting a dictionnary or list to the micro-styler format """

    def __init__(self, text: dict, font_family: str, font_size: int = 12, emoji_font_name: str = "Noto Color Emoji", enable_debug: bool = False) -> None:
        # ---- Input data ----
        self.result = []
        self.input = ""
        self.text = text
        self.y = 1
        # ---- GUI info ----
        self.font_size = font_size
        self.font_family = font_family
        # ---- Markdown info ----

        # Default font size
        self.default_font_size = font_size
        if self.default_font_size < 3:
            self.default_font_size = 3

        # Header sizes
        self.h1 = self.default_font_size+12
        self.h2 = self.default_font_size+6
        self.h3 = self.default_font_size+2
        self.h4 = self.default_font_size
        self.h5 = self.default_font_size - 1
        self.h6 = self.default_font_size - 2

        # Header identifications
        self.h1_id = "#"
        self.h2_id = "##"
        self.h3_id = "###"
        self.h4_id = "####"
        self.h5_id = "#####"
        self.h6_id = "######"

        # Header style
        self.h1_style = "B"
        self.h2_style = "B"
        self.h3_style = "B"
        self.h4_style = "B"
        self.h5_style = "B"
        self.h6_style = "B"

        # Alternate Header identifications
        self.h1_id_alt = "="
        self.h2_id_alt = "-"

        # Header correlations
        self.header_correlations = {
            self.h1_id: {"size": self.h1, "style": self.h1_style},
            self.h2_id: {"size": self.h2, "style": self.h2_style},
            self.h3_id: {"size": self.h3, "style": self.h3_style},
            self.h4_id: {"size": self.h4, "style": self.h4_style},
            self.h5_id: {"size": self.h5, "style": self.h5_style},
            self.h6_id: {"size": self.h6, "style": self.h6_style},
            self.h1_id_alt: {"size": self.h1, "style": self.h1_style},
            self.h2_id_alt: {"size": self.h2, "style": self.h2_style}
        }

        # Markdown styles
        self.bold_id = "**"
        self.italic_id = "*"
        self.italic_alt_id = "_"
        self.bold_italic_id = "***"
        self.bold_italic_underline_id = "___"
        self.bold_underline_id = "____"
        self.underline_id = "__"
        self.strikethrough_id = "~~"
        self.code_id = "`"
        self.code_block_id = "```"
        self.quote_id = ">"
        self.link_id = "["
        self.image_id = "!["
        self.highlight_id = "=="
        self.subscript_id = "~"
        self.superscript_id = "^"
        self.emoji_id = ":"

        # emoji_font
        self.emoji_font_name = emoji_font_name

        # Markdown styles correlations
        self.styles_correlations = {
            self.bold_id: {"style": "B"},
            self.italic_id: {"style": "I"},
            self.italic_alt_id: {"style": "I"},
            self.bold_italic_id: {"style": "BI"},
            self.bold_italic_underline_id: {"style": "BIU"},
            self.bold_underline_id: {"style": "BU"},
            self.underline_id: {"style": "U"},
            self.strikethrough_id: {"style": "S"},
            self.code_id: {"bkg": "#2D333B", "fg": "#9EAAB6", "colour": "#9EAAB6"},
            self.code_block_id: {"bkg": "#2D333B", "fg": "#9EAAB6", "colour": "#9EAAB6"},
            self.quote_id: {"bkg": "#2D333B", "fg": "#5F6A75", "colour": "#5F6A75", "pre_text": "⏸"},
            self.link_id: {"hyperlink": "", "hyperlink_legend": ""},
            self.image_id: {"image_url": "", "image_legend": "", "image_width": "", "image_height": ""},
            self.highlight_id: {"bkg": "#FFE875"},
            self.subscript_id: {"size": self.h4},
            self.superscript_id: {"size": self.h1},
            self.emoji_id: {"font": self.emoji_font_name, "special": "EMOJI"}
        }

        # Markdown comments
        self.comment_open_id = "<!--"
        self.comment_close_id = "-->"

        # Markdown list
        self.list_id = "*"
        self.list_id_alt = "-"
        self.list_id_alt2 = "+"
        self.list_id_alt3 = "1."
        self.list_id_alt4 = "2."
        self.list_id_alt5 = "3."
        self.list_id_alt6 = "4."
        self.list_id_alt7 = "5."
        self.list_id_alt8 = "6."
        self.list_id_alt9 = "7."
        self.list_id_alt10 = "8."
        self.list_id_alt11 = "9."
        self.list_id_alt12 = "0."

        # List options
        self.list_options = {
            self.list_id: "•",
            self.list_id_alt: "•",
            self.list_id_alt2: "•",
            self.list_id_alt3: "1.",
            self.list_id_alt4: "2.",
            self.list_id_alt5: "3.",
            self.list_id_alt6: "4.",
            self.list_id_alt7: "5.",
            self.list_id_alt8: "6.",
            self.list_id_alt9: "7.",
            self.list_id_alt10: "8.",
            self.list_id_alt11: "9.",
            self.list_id_alt12: "0."
        }

        # Markdown Tasks
        self.todo_todo = "[ ]"
        self.todo_done = "[x]"
        self.todo_ongoing = "[o]"
        self.todo_deleted = "[-]"
        self.todo_question = "[?]"
        self.todo_important = "[!]"
        # self.todo_important_done = "[x!]"
        # self.todo_important_deleted = "[-!]"
        # self.todo_important_ongoing = "[o!]"
        # self.todo_important_question = "[!?]"
        # self.todo_important_question_done = "[x!?]"
        # self.todo_important_ongoing_deleted = "[-o!]"
        # self.todo_important_question_ongoing = "[o!?]"
        # self.todo_important_question_deleted = "[-!?]"
        # self.todo_important_question_ongoing_done = "[x!?o]"
        # self.todo_important_question_ongoing_deleted = "[-o!?]"
        # self.todo_important_question_ongoing_done_deleted = "[-x!?o]"

        # Markdown task colours:
        self.todo_todo_colour = "#7BAF6F"
        self.todo_done_colour = "#555860"
        self.todo_question_colour = "#4EB6C3"
        self.todo_important_colour = "#C66CC7"
        self.todo_ongoing_colour = "#CE9178"
        self.todo_deleted_colour = "#2E3F55"

        # Markdown task styles:
        self.todo_todo_styles = ""
        self.todo_done_styles = "I"
        self.todo_question_styles = ""
        self.todo_important_styles = "B"
        self.todo_ongoing_styles = ""
        self.todo_deleted_styles = "IS"

        # Markdown Tasks correlations
        self.tasks_correlations = {
            self.todo_todo: {
                "style": self.todo_todo_styles,
                "fg": self.todo_todo_colour,
                "colour": self.todo_todo_colour
            },
            self.todo_done: {
                "style": self.todo_done_styles,
                "fg": self.todo_done_colour,
                "colour": self.todo_done_colour
            },
            self.todo_question: {
                "style": self.todo_question_styles,
                "fg": self.todo_question_colour,
                "colour": self.todo_question_colour
            },
            self.todo_important: {
                "style": self.todo_important_styles,
                "fg": self.todo_important_colour,
                "colour": self.todo_important_colour
            },
            self.todo_ongoing: {
                "style": self.todo_ongoing_styles,
                "fg": self.todo_ongoing_colour,
                "colour": self.todo_ongoing_colour
            },
            self.todo_deleted: {
                "style": self.todo_deleted_styles,
                "fg": self.todo_deleted_colour,
                "colour": self.todo_deleted_colour
            }  # ,
            # self.todo_important_question: {
            #     "style": self.todo_question_styles,
            #     "fg": self.todo_important_colour,
            #     "colour": self.todo_important_colour
            # },
            # self.todo_important_done: {
            #     "style": self.todo_done_styles,
            #     "fg": self.todo_done_colour,
            #     "colour": self.todo_done_colour
            # },
            # self.todo_important_question_done: {
            #     "style": self.todo_done_styles,
            #     "fg": self.todo_important_colour,
            #     "colour": self.todo_important_colour
            # },
            # self.todo_important_ongoing: {
            #     "style": self.todo_ongoing_styles,
            #     "fg": self.todo_todo_colour,
            #     "colour": self.todo_todo_colour
            # },
            # self.todo_important_deleted: {
            #     "style": self.todo_deleted_styles,
            #     "fg": self.todo_todo_colour,
            #     "colour": self.todo_todo_colour
            # },
            # self.todo_important_ongoing_deleted: {
            #     "style": self.todo_deleted_styles,
            #     "fg": self.todo_todo_colour,
            #     "colour": self.todo_todo_colour
            # },
            # self.todo_important_question_ongoing: {
            #     "style": self.todo_ongoing_styles,
            #     "fg": self.todo_todo_colour,
            #     "colour": self.todo_todo_colour
            # },
            # self.todo_important_question_deleted: {
            #     "style": self.todo_deleted_styles,
            #     "fg": self.todo_todo_colour,
            #     "colour": self.todo_todo_colour
            # },
            # self.todo_important_question_ongoing_deleted: {
            #     "style": self.todo_deleted_styles,
            #     "fg": self.todo_todo_colour,
            #     "colour": self.todo_todo_colour
            # },
            # self.todo_important_question_ongoing_done: {
            #     "style": self.todo_done_styles,
            #     "fg": self.todo_todo_colour,
            #     "colour": self.todo_todo_colour
            # },
            # self.todo_important_question_ongoing_done_deleted: {
            #     "style": self.todo_deleted_styles,
            #     "fg": self.todo_todo_colour,
            #     "colour": self.todo_todo_colour
            # }
        }

        # Inner conversions
        self.styles_len_3 = [
            self.bold_italic_id,
            self.bold_italic_underline_id
        ]
        self.styles_len_2 = [
            self.bold_id,
            self.underline_id,
            self.strikethrough_id,
            self.highlight_id
        ]
        self.styles_len_1 = [
            self.italic_id,
            self.italic_alt_id,
            self.subscript_id,
            self.emoji_id
        ]

        # Tracking data
        self.current_line = ""
        self.skip_delay = 0

        # Offset display
        if enable_debug is True:
            self.offset_char = ".."
        else:
            self.offset_char = "  "
        self.debug_enabled = enable_debug

    def dms_print_debug(self, string: str) -> None:
        """ Print the string if the debug mode is enabled """
        if self.debug_enabled is True:
            print(f"(dms) {string}")

    def dms_compile_characters(self, char: str, nb: int) -> str:
        """ Compile a character a specific number of times """
        string = ""
        while nb > 0:
            string += char
            nb -= 1
        return string

    def dms_is_link(self, string: str) -> bool:
        """ Check if the string is a link """
        if string.startswith("http") == True:
            return True
        if string.startswith("www.") == True:
            return True
        return False

    def clean_link(self, string: str, current_style: dict[str, any]) -> list[dict, dict]:
        """ Remove small additions that could have come from the parsing of the data """
        buffer = {"text": ""}
        if current_style["from"] == "list" and string.endswith(",") == True:
            searched_character = ","
            temporary_string = string.split(searched_character)
            if len(temporary_string) > 1:
                temporary_string.pop(-1)
            string = searched_character.join(temporary_string)
            buffer["text"] = ", "
        elif current_style["from"] == "list" and string.endswith(", ") == True:
            searched_character = ", "
            temporary_string = string.split(searched_character)
            if len(temporary_string) > 1:
                temporary_string.pop(-1)
            string = searched_character.join(temporary_string)
            buffer["text"] = ", "
        elif current_style["from"] == "dict" and string.endswith(":") == True:
            searched_character = ":"
            temporary_string = string.split(searched_character)
            if len(temporary_string) > 1:
                temporary_string.pop(-1)
            string = searched_character.join(temporary_string)
            buffer["text"] = ": "
        elif current_style["from"] == "dict" and string.endswith(": ") == True:
            searched_character = ": "
            temporary_string = string.split(searched_character)
            if len(temporary_string) > 1:
                temporary_string.pop(-1)
            string = searched_character.join(temporary_string)
            buffer["text"] = ": "
        # else:
        #     forbidden_list = [
        #         "{", "}", "|", "\\",
        #         "^", "~", "[", "]",
        #         "`", "(", ")"
        #     ]
        #     for i in forbidden_list:
        #         if string.endswith(i):
        #             string = string[:-len(i)]
        #             buffer["text"] = i
        #             break
        return [string, buffer]

    def dms_add_simple_text(self, string: str, parent_style: dict) -> None:
        """ Add a string of text to the list of dictionaries """
        self.dms_print_debug(f"Adding simple text: {string}")
        current_style = parent_style.copy()
        string_length = len(string)
        buffer = {"text": ""}
        if self.dms_is_link(string) == True:
            if string_length > 0:
                cleaned_link = self.clean_link(
                    string=string,
                    current_style=current_style
                )
                string = cleaned_link[0]
                buffer = cleaned_link[1]
            current_style["hyperlink"] = string
            current_style["hyperlink_legend"] = string
            current_style["text"] = ""
        else:
            current_style["text"] = string
        self.dms_print_debug(f"Current line: {self.current_line}")
        self.dms_print_debug(f"Current style: {current_style}")
        self.result.append(current_style)
        if len(buffer["text"]) > 0:
            self.result.append(buffer)

    def dms_check_link(self, string: str, parent_style: dict) -> None:
        """ Check if there are any links in the text """
        base_style = parent_style.copy()
        buffer = ""
        bufferise = False
        string_length = len(string)
        for index, content in enumerate(string):
            if bufferise == False and content == "h" and index < string_length and string[index+1] == "t":
                bufferise = True
                if buffer != "":
                    self.dms_add_simple_text(buffer, base_style)
                    buffer = ""
                buffer += content
            elif bufferise == False and content == "w" and index < string_length and string[index+1] == "w":
                bufferise = True
                if buffer != "":
                    self.dms_add_simple_text(buffer, base_style)
                    buffer = ""
                buffer += content
            elif bufferise == True and (content == " " or content == "\0" or content == "\t"):
                bufferise = False
                if buffer != "":
                    self.dms_add_simple_text(buffer, base_style)
                    buffer = ""
            else:
                buffer += content
        self.dms_add_simple_text(buffer, base_style)

    def dms_insert_correct_format(self, posx: int, offset: int = 0, content: str = "\n", from_type: str = "str") -> None:
        """ Insert the content with specific styling """
        processed_content = self.dms_compile_characters(
            self.offset_char,
            offset
        )
        self.result.append({"text": processed_content})
        processed_content = ""
        posx += offset * len(self.offset_char)
        style = {"text": ""}
        if from_type == "dict":
            style = self.styles_correlations[self.bold_underline_id]
            style["from"] = "dict"
        elif from_type == "list":
            style = self.styles_correlations[self.italic_id]
            style["from"] = "list"
        elif from_type == "str":
            style["from"] = "str"
        else:
            style["from"] = "normal"
        processed_content += content
        style["family"] = self.font_family
        style["size"] = self.font_size
        self.dms_check_link(processed_content, style)

    def dms_insert_list(self, json_list: list, offset: int = 0) -> None:
        """ PRocess a list comming from a json """
        length = len(json_list) - 1
        posx = 0
        for progress, i in enumerate(json_list):
            self.dms_print_debug(
                f"(in for) self.y = {self.y}, posx = {posx}, i = {i}")
            if isinstance(i, dict):
                self.dms_insert_correct_format(
                    posx,
                    offset,
                    "\n",
                    "list"
                )
                self.y += 1
                self.dms_process_json_content(
                    i,
                    offset+1
                )
                continue
            if isinstance(i, list):
                self.dms_insert_correct_format(
                    posx,
                    offset,
                    "\n",
                    "list"
                )
                self.y += 1
                self.dms_insert_list(
                    i,
                    offset+1
                )
                continue
            text_input = ""
            my_offset = offset
            if progress == 0:
                self.dms_print_debug(
                    f"(if) progress = {progress}, length = {length}"
                )
                my_offset = offset
                text_input = f"{i}, "
            elif progress < length and isinstance(json_list[progress+1], (dict, list)) is False:
                self.dms_print_debug(
                    f"(elif) progress = {progress}, length = {length}"
                )
                my_offset = 0
                text_input = f"{i}, "
            else:
                self.dms_print_debug(
                    f"(else) progress = {progress}, length = {length}"
                )
                my_offset = 0
                text_input = f"{i}\n"
            self.dms_insert_correct_format(
                posx,
                my_offset,
                text_input,
                "list"
            )
            if progress == 0:
                posx += len(text_input) + offset * len(self.offset_char)
            elif progress < length and isinstance(json_list[progress+1], (dict, list)) is False:
                posx += len(text_input) + 1
            else:
                self.y += 1

    def dms_process_json_content(self, json_content: dict, offset: int = 0) -> None:
        """ Process the json content """
        for i in json_content:
            posx = (offset * len(self.offset_char))
            self.dms_print_debug(
                f"(in for) self.y = {self.y}, posx = {posx}, i = {i}, json_content[i] = {json_content[i]}"
            )
            if isinstance(json_content[i], dict):
                self.dms_insert_correct_format(
                    posx,
                    offset,
                    f"{i}:\n",
                    "dict"
                )
                self.y += 1
                self.dms_process_json_content(
                    json_content[i],
                    offset+1
                )
                continue
            if isinstance(json_content[i], list):
                self.dms_insert_correct_format(
                    posx,
                    offset,
                    f"{i}:\n",
                    "dict"
                )
                self.y += 1
                self.dms_insert_list(
                    json_content[i],
                    offset+1
                )
                continue
            term_input = f"{i}:"
            def_input = f" {json_content[i]}\n"
            self.dms_print_debug(
                f"len(my_term_input) = {len(term_input)}, len(def_input) = {len(def_input)}"
            )
            self.dms_print_debug(
                f"(bt) term_input = '{term_input}', def_input = '{def_input}', posx = '{posx}', self.y = '{self.y}'"
            )
            self.dms_print_debug(
                f"(bt) len(term_input) = {len(term_input)}, len(def_input) = {len(def_input)}, offset = {offset}, len(self.offset_char) = {len(self.offset_char)}, offset_len = {offset * len(self.offset_char)}"
            )
            self.dms_insert_correct_format(
                posx,
                offset,
                term_input,
                "dict"
            )
            posx += len(term_input)
            self.dms_print_debug(
                f"(bd) term_input = '{term_input}', def_input = '{def_input}', posx = '{posx}', self.y = '{self.y}'"
            )
            self.dms_insert_correct_format(
                posx,
                0,
                def_input,
                "string"
            )
            posx += len(def_input)
            self.y += 1

    def dms_main(self) -> list[dict[str, any]]:
        """ The main function of the class """
        self.dms_print_debug("In dms_main")
        self.dms_process_json_content(
            json_content=self.text,
            offset=0
        )
        self.dms_print_debug("Out of dms_main")
        return self.result


if __name__ == "__main__":
    import tkinter as tk
    from micro_styler import MicroStyler
    INPUT_TEXT = {
        "e": "r",
        "r": "l",
        "u": {
            "r": {
                "o": "p"
            }
        },
        "m": [
            "m1", "m2", "m3", "m4", "m5", "m6",
            "m7", "m8", "m9", "m10", "m11", "m12",
            "m13", "m14", "m15", "m16", "m17", "m18",
            "m19", "m20", "m21", "m22", "m23", "m24",
            "m25", "m26", "m27", "m28", "m29", "m30",
            "m31", "m32", "m33", "m34", "m35", "m36",
            "m37", "m38", "m39", "m40", "m41", "m42",
            "m43", "m44", "m45", "m46", "m47", "m48",
            "m49", "m50", "m51", "m52", "m53", "m54",
            "m55", "m56", "m57", "m58", "m59", "m60",
            "m61", "m62", "m63", "m64", "m65", "m66",
            {"small_term": "small_definition"}
        ],
        "o": "m",
        "links": {
            "www.google.com": "www.yahoo.com",
            "https://www.gmail.com": "https://web.whatsapp.com/",
            "list_of_links": [
                "https://scanurl.net/", "https://www.phishtank.com/", "https://www.makeuseof.com/geek-squad-email-scam/", "https://www.makeuseof.com/types-of-phishing-attack/", "https://www.virustotal.com/gui/home/upload",
                "https://www.urlvoid.com/", "https://sitecheck.sucuri.net/", "https://www.psafe.com/dfndr-lab/", "https://www.ipvoid.com/", "https://www.apivoid.com/api/url-reputation/", "https://transparencyreport.google.com/",
                "https://www.makeuseof.com/internet-safety-dos-and-donts/",
                {"www.bing.com": "https://hellmart666.com/"},
                "{www.google.com }", "(www.bing.com )", "[www.yahoo.com ]"
            ]
        }
    }
    DMS = DictToMicroStyler(
        text=INPUT_TEXT,
        font_family="Times New Roman",
        font_size=12,
        emoji_font_name="Noto Color Emoji",
        enable_debug=True
    )
    RESPONSE = DMS.dms_main()
    print(f"Result: dms_main:\n{RESPONSE}")
    TT = tk.Tk()
    TT.geometry("800x400")
    TT["bg"] = "#666666"
    MS = MicroStyler(
        frame=TT,
        fg="#000000",
        bkg="#FFFFFF",
        height=95,
        width=95,
        padx_text=0,
        pady_text=0,
        block_cursor=True,
        font=(
            "Times New Roman",
            12
        ),
        cursor="xterm",
        export_selection=True,
        highlight_colour="#0077FF",
        relief=tk.FLAT,
        undo=False,
        wrap="word",
        fill=tk.BOTH,
        side=tk.TOP,
        padx_pack=0,
        pady_pack=0,
        ipadx=0,
        ipady=0,
        content=RESPONSE,
        emoji_dict={},
        row=-1,
        column=-1
    )
    TT.wait_window()
