"""
File in charge of changing a markdown to the format required for the function micro styler
"""


class MdToMicroStyler:
    """
    The class in charge of converting the markdown langage to the micro_styler language
    Markdown references:
    * https://www.markdownguide.org/basic-syntax
    Todo references
    * https://marketplace.visualstudio.com/items?itemName=blunt1337.todo-language
    """

    def __init__(self, text: str, initial_font_size: int = 12, emoji_font_name: str = "Noto Color Emoji") -> None:
        # ---- Input data ----
        self.result = []
        self.input = ""
        self.text = text
        # ---- Markdown info ----

        # Default font size
        self.default_font_size = initial_font_size
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

        # emojy_font
        self.emoji_font_name = emoji_font_name

        # Markdown styles correlations
        self.styles_correlations = {
            self.bold_id: {"style": "B"},
            self.italic_id: {"style": "I"},
            self.italic_alt_id: {"style": "I"},
            self.bold_italic_id: {"style": "BI"},
            self.bold_italic_underline_id: {"style": "BIU"},
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

    def get_nb_start_symbols(self, char: str, string: str) -> str:
        """ Get the number of start symbols in a string """
        result = ""
        for c in string:
            if c == char:
                result += c
            else:
                break
        return result

    def replace_beginning_chr(self, chr: str, string: str) -> str:
        """ Replace the beginning character of a string """
        result = ""
        item_replaced = False
        just_after_item = False

        for item in string:
            if item == chr and item_replaced == False:
                just_after_item = True
                result += ""
            elif (item == " " or item == "\t") and just_after_item == True and item_replaced == False:
                result += ""
                item_replaced = True
            else:
                result += item
        return result

    def my_pop(self, string: str, index: int) -> str:
        """ Split string at index """
        before = string[:index]
        if index == -1:
            return before
        else:
            after = string[index+1:]
        final = before+after
        return final

    def has_comment(self, line: str) -> bool:
        """ Check if the mardown contains comments '`<!-- -->`' """
        comment_id_open_length = len(self.comment_open_id)
        if len(line) >= comment_id_open_length:
            if self.comment_open_id == line[:comment_id_open_length]:
                return True
        return False

    def has_quote(self) -> bool:
        """ Check if the line has a quote '`> quote`' """
        if len(self.current_line) > 0:
            if self.quote_id == self.current_line[0]:
                return True
        return False

    def has_header(self) -> bool:
        """ Check if the line has a header '`# header`' """
        if len(self.current_line) > 0:
            if self.h1_id == self.current_line[0]:
                return True
        return False

    def has_list(self) -> bool:
        """ Check if the line has a list '`*, +, -, etc...`' """
        line_length = len(self.current_line)
        if line_length > 2:
            tmp_node = self.current_line.split(" ", 1)[0]
            tmp_node_length = len(tmp_node)
            if tmp_node_length > 2:
                tmp_node = tmp_node[-2:]
            if tmp_node in self.list_options:
                if tmp_node_length < line_length and self.current_line[tmp_node_length] == " ":
                    return True
        return False

    def has_todo(self) -> bool:
        """ Check if the line has a todo '`[ ]`' """
        todo_length = len(self.todo_done)
        if len(self.current_line) >= todo_length:
            if self.current_line[:todo_length] in self.tasks_correlations:
                return True
        return False

    def has_code_block(self, line) -> bool:
        """
Check if the line has a code block '\n
`` `\n
code block\n
`` `\n
'"""
        if len(line) == 3:
            if self.code_block_id == line[:3]:
                return True
        return False

    def has_bold(self) -> bool:
        """ Check if the line has a bold character '`** bold **` """
        bold_id_length = len(self.bold_id)
        if len(self.current_line) > bold_id_length:
            if self.bold_id == self.current_line[:bold_id_length]:
                return True
        return False

    def has_italic(self) -> bool:
        """ Check if the line has a italic character '`* italic *`'"""
        italic_id_length = len(self.italic_id)
        if len(self.current_line) > italic_id_length:
            if self.italic_id == self.current_line[:italic_id_length]:
                return True
        return False

    def has_bold_italic(self) -> bool:
        """ Check if the line has a bold_italic character '`*** bold-italic ***`' """
        bold_italic_id_length = len(self.bold_italic_id)
        if len(self.current_line) > bold_italic_id_length:
            if self.bold_italic_id == self.current_line[:bold_italic_id_length]:
                return True
        return False

    def has_bold_italic_underline(self) -> bool:
        """ Check if the line has a bold_italic_underline character '`___ bold_italic_underline ___`' """
        bold_italic_underline_id_length = len(self.bold_italic_underline_id)
        if len(self.current_line) > bold_italic_underline_id_length:
            if self.bold_italic_underline_id == self.current_line[:bold_italic_underline_id_length]:
                return True
        return False

    def has_underline(self) -> bool:
        """ Check if the line has a underline character '`__ underline __`' """
        underline_id_length = len(self.underline_id)
        if len(self.current_line) > underline_id_length:
            if self.underline_id == self.current_line[:underline_id_length]:
                return True
        return False

    def has_strikethrough(self) -> bool:
        """ Check if the line has a strikethrough character '`~~ strikethrough ~~`' """
        strikethrough_id_length = len(self.strikethrough_id)
        if len(self.current_line) > strikethrough_id_length:
            if self.strikethrough_id == self.current_line[:strikethrough_id_length]:
                return True
        return False

    def has_code(self) -> bool:
        """ Check if the line has a code character '``` ` code ` ```' """
        code_id_length = len(self.code_id)
        if len(self.current_line) > code_id_length:
            if self.code_id == self.current_line[:code_id_length]:
                return True
        return False

    def has_link(self) -> bool:
        """ Check if the line has a link character '`[description](url)`' """
        link_id_length = len(self.link_id)
        if len(self.current_line) > link_id_length:
            if self.link_id == self.current_line[:link_id_length]:
                if self.current_line.startswith(self.link_id) == True:
                    return True
        return False

    def has_image(self) -> bool:
        """ Check if the line has a image character '`![description](url)`'"""
        image_id_length = len(self.image_id)
        if len(self.current_line) > image_id_length:
            if self.image_id == self.current_line[:image_id_length]:
                return True
        return False

    def has_subscript(self) -> bool:
        """ Check if the line has a subscript character '`~ subscript ~`' """
        subscript_id_length = len(self.subscript_id)
        if len(self.current_line) > subscript_id_length:
            if self.subscript_id == self.current_line[:subscript_id_length]:
                return True
        return False

    def has_superscript(self) -> bool:
        """ Check if the line has a subscript character '`^ superscript ^`' """
        subscript_id_length = len(self.superscript_id)
        if len(self.current_line) > subscript_id_length:
            if self.superscript_id == self.current_line[:subscript_id_length]:
                return True
        return False

    def has_highlight(self) -> bool:
        """ Check if the line has a highlight character '`== hilight ==`' """
        highlight_id_length = len(self.highlight_id)
        if len(self.current_line) > highlight_id_length:
            if self.highlight_id == self.current_line[:highlight_id_length]:
                return True
        return False

    def check_header(self) -> dict[str, any]:
        """ Check if the line is a header """
        header = self.get_nb_start_symbols(self.h1_id, self.current_line)
        if header != "":
            if len(header) <= len(self.h6_id):
                self.current_line = self.replace_beginning_chr(
                    self.h1_id,
                    self.current_line
                )
                if len(self.current_line) > 0 and self.current_line[0] == " ":
                    self.current_line = self.current_line[1:]
                return self.header_correlations[header].copy()
            else:
                return self.header_correlations[self.h6_id].copy()
        else:
            if len(self.current_line) > 0:
                if self.h1_id_alt == self.current_line[0]:
                    self.current_line = self.replace_beginning_chr(
                        self.h1_id_alt,
                        self.current_line
                    )
                    if self.current_line[0] == " ":
                        self.current_line = self.current_line[1:]
                    return self.header_correlations[self.h1_id_alt].copy()
                elif self.h2_id_alt == self.current_line[0]:
                    self.current_line = self.replace_beginning_chr(
                        self.h2_id_alt,
                        self.current_line
                    )
                    if self.current_line[0] == " ":
                        self.current_line = self.current_line[1:]
                    return self.header_correlations[self.h2_id_alt].copy()
        return None

    def check_quote(self) -> dict[str, any]:
        """ Check if the line is a quote """
        if len(self.current_line) > 0:
            if self.quote_id == self.current_line[0]:
                self.current_line = self.replace_beginning_chr(
                    self.quote_id,
                    self.current_line
                )
                if self.current_line[0] == " ":
                    self.current_line = self.current_line[1:]
                return self.styles_correlations[self.quote_id].copy()
        return None

    def check_list(self) -> dict[str, any]:
        """ Check if the line is a list """
        if len(self.current_line) > 0:
            current_node = self.current_line.split(" ", 1)[0]
            if current_node in self.list_options:
                response = self.list_options[current_node]
                self.current_line = self.current_line[len(current_node):]
                if self.current_line[0] == " ":
                    self.current_line = self.current_line[1:]
                return response
        return None

    def check_todo(self) -> dict[str, any]:
        """ Check if the line is a todo """
        if len(self.current_line) > 3:
            snipset = self.current_line[:3]
            if snipset in self.tasks_correlations:
                response = self.tasks_correlations[snipset].copy()
                self.current_line = self.current_line[len(snipset):]
                if self.current_line[0] == " ":
                    self.current_line = self.current_line[1:]
                return response
        return None

    def check_link(self, usr_input: str = "[test](link)") -> dict[str, any]:
        """ Check the link in usr_input """
        result = self.styles_correlations[self.link_id]
        temp_input = usr_input.split("](", maxsplit=1)
        link = ""
        description = ""
        if len(temp_input) == 2:
            if temp_input[0][0] == "[":
                temp_input[0] = self.my_pop(temp_input[0], 0)
            description = temp_input[0]
            if temp_input[1][-1] == ")":
                temp_input[1] = self.my_pop(temp_input[1], -1)
            link = temp_input[1]
        else:
            if temp_input[0][0] == "[":
                temp_input[0] = self.my_pop(temp_input[0], 0)
            elif temp_input[0][0] == "(":
                temp_input[0] = self.my_pop(temp_input[0], 0)
            if temp_input[0][-1] == ")":
                temp_input[0] = self.my_pop(temp_input[0], -1)
            elif temp_input[0][-1] == "]":
                temp_input[0] = self.my_pop(temp_input[0], -1)
            description = temp_input[0]
            link = description
        result["hyperlink"] = link
        result["hyperlink_legend"] = description
        return result

    def check_image(self, usr_input: str = "[test](link)") -> dict[str, any]:
        """ Check the image link in usr_input """
        result = self.styles_correlations[self.image_id]
        temp_input = usr_input.split("](", maxsplit=1)
        link = ""
        description = ""
        if len(temp_input) == 2:
            if temp_input[0][0] == "!":
                temp_input[0] = self.my_pop(temp_input[0], 0)
            if temp_input[0][0] == "[":
                temp_input[0] = self.my_pop(temp_input[0], 0)
            description = temp_input[0]
            if temp_input[1][-1] == ")":
                temp_input[1] = self.my_pop(temp_input[1], -1)
            link = temp_input[1]
        else:
            if temp_input[0][0] == "!":
                temp_input[0] = self.my_pop(temp_input[0], 0)
            if temp_input[0][0] == "[":
                temp_input[0] = self.my_pop(temp_input[0], 0)
            elif temp_input[0][0] == "(":
                temp_input[0] = self.my_pop(temp_input[0], 0)
            if temp_input[0][-1] == ")":
                temp_input[0] = self.my_pop(temp_input[0], -1)
            elif temp_input[0][-1] == "]":
                temp_input[0] = self.my_pop(temp_input[0], -1)
            description = temp_input[0]
            link = description
        result["image_url"] = link
        result["image_legend"] = description
        return result

    def check_highlight(self, usr_input: str = "[test](link)") -> dict[str, any]:
        """ Check the highlight in usr_input """
        result = self.styles_correlations[self.highlight_id]
        content = usr_input.split(self.highlight_id, 2)
        if len(content) > 1:
            result["text"] = content[1]
        else:
            result["text"] = content[0]
        return result

    def check_subscript(self, usr_input: str = "") -> dict[str, any]:
        result = self.styles_correlations[self.subscript_id]
        content = usr_input.split(self.subscript_id, 2)
        if len(content) > 1:
            result["text"] = content[1]
        else:
            result["text"] = content[0]
        return result

    def check_superscript(self, usr_input: str = "") -> dict[str, any]:
        result = self.styles_correlations[self.superscript_id]
        content = usr_input.split(self.superscript_id, 2)
        if len(content) > 1:
            result["text"] = content[1]
        else:
            result["text"] = content[0]
        return result

    def check_code(self, index: int) -> dict[str, any]:
        """ Get the section in the txt where it is a code section """
        result = self.styles_correlations[self.code_id]
        is_in_code = False
        buffer = self.current_line[index:]
        for i in buffer:
            if i == self.code_id:
                if is_in_code == False:
                    is_in_code = True
                    continue
                else:
                    is_in_code = False
                    break
            if is_in_code == True:
                result["text"] += i
            self.skip_delay += 1
        return result

    def get_tag(self, string: str, end_string: str) -> dict[str, any]:
        """ Get the tag from the string """
        buffer = ""
        index = 0
        end_string_length = len(end_string)
        string_length = len(string)
        default_data = self.styles_correlations[end_string].copy()
        if index + end_string_length < string_length:
            end_term = string[index:index+end_string_length]
        else:
            end_term = string[index:]
        while index < string_length:
            if index + end_string_length < string_length:
                end_term = string[index:index+end_string_length]
            else:
                end_term = string[index:]
            if end_term == end_string:
                break
            else:
                buffer += string[index]
            index += 1
        default_data["text"] = buffer
        default_data["index"] = index+end_string_length
        return default_data

    def check_style(self, index: int) -> list[dict]:
        """Update the style for the string input"""
        result = []
        has_been_found = False
        index = index
        string_length = len(self.current_line)
        search_term = ""
        tag = dict()
        inner_buffer = ""
        while index < string_length:
            has_been_found = False
            index_offset = 3
            if string_length > index + index_offset:
                search_term = self.current_line[index:index+index_offset]
                for i in self.styles_len_3:
                    if i == search_term:
                        if inner_buffer != "":
                            result.append({"text": inner_buffer})
                            inner_buffer = ""
                        tag = self.get_tag(
                            self.current_line[index+index_offset:],
                            i
                        )
                        index += index_offset+tag["index"]
                        result.append(tag)
                        has_been_found = True
                        break
            index_offset = 2
            if has_been_found == False and string_length > index + index_offset:
                search_term = self.current_line[index:index+index_offset]
                for i in self.styles_len_2:
                    if i == search_term:
                        if inner_buffer != "":
                            result.append({"text": inner_buffer})
                            inner_buffer = ""
                        tag = self.get_tag(
                            self.current_line[index+index_offset:],
                            i
                        )
                        index += index_offset+tag["index"]
                        result.append(tag)
                        has_been_found = True
                        break
            index_offset = 1
            if has_been_found == False and string_length > index + index_offset:
                search_term = self.current_line[index:index+index_offset]
                for i in self.styles_len_1:
                    if i == search_term:
                        if inner_buffer != "":
                            result.append({"text": inner_buffer})
                            inner_buffer = ""
                        tag = self.get_tag(
                            self.current_line[index+index_offset:],
                            i
                        )
                        index += index_offset+tag["index"]
                        result.append(tag)
                        has_been_found = True
                        break
            if has_been_found == False and index < string_length:
                inner_buffer += self.current_line[index]
                index += 1
        if len(inner_buffer) > 0:
            result.append({"text": inner_buffer})
        return result

    def process_node(self, index: int) -> list[dict[str, any]]:
        """ Process a node """
        self.current_line = self.current_line[index:]
        debug_buffer = self.current_line
        print(f"debug_buffer = {debug_buffer}")
        response = dict()
        is_bold = self.has_bold()
        is_italic = self.has_italic()
        is_underline = self.has_underline()
        is_strikethrough = self.has_strikethrough()
        is_bold_italic = self.has_bold_italic()
        is_bold_italic_underline = self.has_bold_italic_underline()
        is_code = self.has_code()
        is_link = self.has_link()
        is_image = self.has_image()
        is_highlight = self.has_highlight()
        is_subscript = self.has_subscript()
        is_superscript = self.has_superscript()

        if is_code == True:
            response = [self.check_code(index)]
        elif is_bold == True or is_italic == True or is_underline == True or is_strikethrough == True or is_bold_italic == True or is_bold_italic_underline == True:
            response = self.check_style(index)
        elif is_link == True:
            response = [self.check_link(self.current_line)]
        elif is_image == True:
            response = [self.check_image(self.current_line)]
        elif is_highlight == True:
            response = self.check_highlight(self.current_line)
        elif is_subscript == True:
            response = self.check_subscript()
        elif is_superscript == True:
            response = self.check_superscript()
        else:
            response["text"] = self.current_line
        return response

    def process_sub_content(self, current: dict) -> list[dict[str, any]]:
        """ Process sub content like bold, italic, underline, etc... """
        result = []
        current_text = self.current_line
        if "text" in current:
            current_text = current["text"]
        else:
            current["text"] = current_text
        self.current_line = current_text
        if current_text != "":
            buffer = ""
            has_been_given_to_source = False
            for index, item in enumerate(self.current_line):
                if self.skip_delay > 0:
                    self.skip_delay -= 1
                    continue
                if item in self.styles_correlations:  # or buffer in self.styles_correlations:
                    if has_been_given_to_source == False:
                        if buffer != "":
                            current["text"] = buffer
                            result.append(current)
                            current = {}
                            buffer = ""
                            has_been_given_to_source = True
                    else:
                        response = self.process_node(index)
                        if isinstance(response, dict) == True:
                            result.append(response)
                        else:
                            result.extend(response)
                else:
                    buffer += item
        result = result
        return result

    def convert_line(self, line: str) -> dict[str, any]:
        """ The function in charge of converting a line of text into the corresponding design required """
        result = []
        self.current_line = line
        if self.has_header() == True:
            response = self.check_header()
            if response != None:
                response["text"] = self.current_line
                response2 = self.process_sub_content(response)
                if isinstance(response, dict) == True:
                    result.append(response)
                else:
                    result.extend(response)
                result.extend(response2)
        elif self.has_quote() == True:
            response = self.check_quote()
            if response != None:
                response["text"] = response["pre_text"]
                response2 = self.process_sub_content({})
                if isinstance(response, dict) == True:
                    result.append(response)
                else:
                    result.extend(response)
                result.extend(response2)
        elif self.has_list() == True:
            response = self.check_list()
            if response != None:
                response2 = self.process_sub_content({})
                response = {"text": response}
                if isinstance(response, dict) == True:
                    result.append(response)
                else:
                    result.extend(response)
                result.extend(response2)
        elif self.has_todo() == True:
            response = self.check_todo()
            if response != None:
                response["text"] = self.current_line
                response2 = self.process_sub_content(response)
                if isinstance(response, dict) == True:
                    result.append(response)
                else:
                    result.extend(response)
                result.extend(response2)
        else:
            result.extend(self.process_sub_content({}))
        result.append({"text": "\n"})
        return result

    def main(self) -> list[dict[str, any]]:
        """
        The main function of the program
        Important !
        The converter is currently not functional, so the input will be the same as the output
        """
        # self.result = []
        # lines = self.text.split("\n")
        # is_in_code = False
        # is_in_comment = False
        # for line in lines:
        #     if self.has_comment(line) == True or is_in_comment == True:
        #         is_in_comment = True
        #         if self.comment_close_id in line and is_in_comment == True:
        #             is_in_comment = False
        #         continue
        #     has_code = self.has_code_block(line)
        #     if has_code == True or is_in_code == True:
        #         if has_code == True and is_in_code == True:
        #             is_in_code = False
        #         else:
        #             is_in_code = True
        #         if has_code == False:
        #             response = self.styles_correlations[self.code_block_id].copy(
        #             )
        #             response["text"] = line+'\n'
        #             self.result.append(response)
        #     else:
        #         response = self.convert_line(line)
        #         self.result.extend(response)
        self.result = [{"text": self.text}]
        return self.result


if __name__ == "__main__":
    INPUT_DATA = """<!--
# Header 1
## Header 2
### Header 3
#### Header 4
##### Header 5
###### Header 6
-->
**bold**
<!--
*italic*
***bold italic***
___bold italic underline___
__underline__
~~strikethrough~~
-->
`code`
```
code block
```
```
multi line
code block
```
<!--
> quote
[link](https://www.google.com)
![image](https://www.google.com)-->
==highlight==
<!--* list
- list
+ list
1. list
2. list
3. list
4. list
5. list
6. list
7. list
8. list
9. list
0. list

[ ] todo
[x] todo
[o] todo
[-] todo
[?] todo
[!] todo
-->
== End of text ==
<!-- This is a
multi line comment -->
<!-- This is a one-liner comment -->
"""

    DEFAULT_FONT = 12
    MTMSI = MdToMicroStyler(
        text=INPUT_DATA,
        initial_font_size=DEFAULT_FONT
    )
    # RESULT = MTMSI.main()
    # print(f"RESULT = '{RESULT}'")

    TEST_INPUT = [
        "# Header 1",
        "## Header 2",
        "### Header 3",
        "#### Header 4",
        "##### Header 5",
        "###### Header 6",
        "**bold**",
        "*italic*",
        "***bold italic***",
        "___bold italic underline___",
        "__underline__",
        "~~strikethrough~~",
        "`code`",
        """```
code block
```""",
        """```
multi line
code block
```""",
        "> quote",
        "[link](https://www.google.com)",
        "![image](https://www.google.com)",
        "==highlight==",
        "* list",
        "- list",
        "+ list",
        "0. list",
        "1. list",
        "2. list",
        "3. list",
        "4. list",
        "5. list",
        "6. list",
        "7. list",
        "8. list",
        "9. list",
        "",
        "[ ] todo",
        "[x] todo",
        "[o] todo",
        "[-] todo",
        "[?] todo",
        "[!] todo",
        "== End of text ==",
        """<!-- This is a
multi line comment -->""",
        "<!-- This is a one-liner comment -->"
    ]
    for i in TEST_INPUT:
        MTMSI.text = i
        result = MTMSI.main()
        print(f"Result for '{i}' is '{result}'")
