import sys
import os


class Context:
    def __init__(self):
        self.macros = dict()
        self.done = set()
        self.loaded_files = dict()
        self.processed_files = dict()

    def get_id(self, full_file_name):
        return full_file_name.split("/")[-1].upper()

    def look_for_files(self, dir):
        files = []
        for dir_entry in os.scandir(dir):
            if dir_entry.is_dir():
                files.extend(self.look_for_files(
                    "%s/%s" % (dir, dir_entry.name)))
            else:
                files.append("%s/%s" % (dir, dir_entry.name))
        return files

    def preprocess(self, src_dir, target_dir):
        """ main preprocessing method, this will iterate over all files

        files are processed with the process_file method

        each time a files includes another one, the processing is "paused"
        and included file is processed immediately, then processed file is included into original file 

        processed files are cached in self.processed_file dict. 
        this is wrong because macros are not the same in each include, but this will do for now
        """
        todo = self.look_for_files(src_dir)

        while len(todo) > 0:
            full_file_name = todo.pop(0)
            file_id = self.get_id(full_file_name)

            self.process_file(file_id, full_file_name)
            target_file_dir = target_dir + \
                "/".join(full_file_name.split("/")[1:-1])
            os.makedirs(target_file_dir, exist_ok=True)

            with open("%s/%s" % (target_file_dir, file_id), "w") as processed_file:
                processed_file.write(self.processed_files[file_id])

            # break
            self.done.add(file_id)

    def get_next_stop_pos(self, text):
        try:
            eol_pos = text.index("\n")
            while text[:eol_pos].strip()[-1] == "\\":
                # print("was a \\ before an eol : %s" % text[:eol_pos])
                eol_pos = text[eol_pos+1:].index("\n") + eol_pos + 1
        except ValueError:
            eol_pos = len(text) - 1
        return eol_pos

    def update_macros(self, buffer, current_macros):
        breakers = [" ", "(", ")", "\t", "\n", ",", ";"]
        identifier = ""
        pos = 0
        buffer_len = len(buffer)

        in_string = False
        updated_buffer = ""
        while pos < buffer_len:
            next_char = buffer[pos]
            if next_char == "\"":
                in_string = not in_string
                updated_buffer += "\""
            elif not in_string and next_char in breakers:
                if identifier.upper() in current_macros:
                    ttype, value = current_macros[identifier.upper()]
                    if ttype == "STATIC":
                        updated_buffer += value
                        #print("apply %s macro for %s" % (ttype, identifier))
                    elif ttype == "FUNCTION":
                        if next_char != "(":
                            # find closing parenthesis, split parameters, apply macros "recursively" ?
                            print("apply function on ??? %s " %
                                  (identifier + next_char))
                        else:
                            pass

                else:
                    updated_buffer += identifier
                updated_buffer += next_char
                identifier = ""
            else:
                identifier += next_char
            pos += 1

        return updated_buffer

    def process_file(self, file_id, file_name):
        if file_id not in self.loaded_files:
            with open(file_name, 'r', encoding="utf-8") as file:
                self.loaded_files[file_id] = file.read()
                self.processed_files[file_id] = ""
                self.macros[file_id] = dict()
        else:
            return

        print("processing %s" % file_name)

        current_file_text = self.loaded_files[file_id]
        current_macros = self.macros[file_id]
        processed_text = self.processed_files[file_id]

        text_length = len(current_file_text)
        current_pos = 0
        buffer = ""

        while current_pos < text_length:
            new_char = current_file_text[current_pos]

            # if character is a whitespace or end of line, this may be the end of an insctruction
            if new_char == "/":
                next_char = current_file_text[current_pos + 1]
                if next_char == "*" or next_char == "/":
                    # next is comment, check current buffer
                    # print("processed: %s" % buffer)
                    processed_text += buffer
                    buffer = ""

                if next_char == "*":
                    # block comment
                    eoc_pos = current_file_text[current_pos:].index("*/")
                    # print("remove comment block from %d to %d: %s" % (
                    #    current_pos, eoc_pos, current_file_text[current_pos:current_pos+eoc_pos + 2]))
                    current_pos += eoc_pos + 2
                    next_ending = "*/"
                    continue

                elif next_char == "/":
                    # one line comment
                    try:
                        eol_pos = current_file_text[current_pos:].index("\n")
                    except ValueError:
                        # end of file
                        break
                    # print("remove comment line from %d to %d: %s" % (
                    #    current_pos, eoc_pos, current_file_text[current_pos:current_pos+eol_pos + 1]))
                    current_pos += eol_pos
                    continue

            else:
                buffer += new_char
                if new_char == "\n":
                    processed_text += buffer
                    buffer = ""
            current_pos += 1

        processed_text += buffer
        buffer = ""

        current_file_text = processed_text
        processed_text = ""
        text_length = len(current_file_text)
        current_pos = 0

        in_def_block = False
        in_def_bool = False

        while current_pos < text_length:
            # print("%s %d" % (file_id, current_pos))
            # read character after character
            new_char = current_file_text[current_pos]

            # if character is a whitespace or end of line, this may be the end of an insctruction
            if new_char == "#":
                if current_file_text[current_pos:current_pos+8] == "#include":
                    eol_pos = self.get_next_stop_pos(
                        current_file_text[current_pos:]) + current_pos
                    include_relative = current_file_text[current_pos+8:eol_pos].strip()[
                        1:-1]
                    current_pos = eol_pos

                    include_id = self.get_id(include_relative)
                    include_path = file_name[:file_name.rindex(
                        "/")] + "/" + include_relative
                    # print("include file ***%s***" % include_relative)
                    # print("include file path is %s" % include_path)

                    self.process_file(include_id, include_path)
                    include_text = self.processed_files[include_id]
                    include_macros = self.macros[include_id]

                    current_macros.update(include_macros)
                    processed_text += include_text
                    continue
                elif current_file_text[current_pos:current_pos+7] == "#define":
                    eol_pos = self.get_next_stop_pos(
                        current_file_text[current_pos:]) + current_pos

                    macro = current_file_text[current_pos +
                                              7:eol_pos].strip().upper()

                    key = macro
                    value = None
                    # if "TOWN" in key:
                    #    print("define: %s" % key)
                    if " " in macro:
                        sep_index = macro.index(" ")
                        if "\t" in macro[:sep_index]:
                            sep_index = macro.index("\t")
                        key = macro[:sep_index].strip()
                        value = macro[sep_index:].strip()
                        # print("define a macro %s --> %s" % (key, value))
                    elif "\t" in macro:
                        sep_index = macro.index("\t")
                        key = macro[:sep_index].strip()
                        value = macro[sep_index:].strip()
                        # print("define a macro %s --> %s" % (key, value))

                    type = "DEFINE"
                    if value != None:
                        type = "STATIC"
                        if "(" in key and ")" in key:
                            type = "FUNCTION"

                    current_macros[key] = (type, value)
                    # print("define a value %s" % (macro))
                    current_pos = eol_pos
                    continue
                elif current_file_text[current_pos:current_pos+6] == "#ifdef":
                    in_def_block = True

                    eol_pos = self.get_next_stop_pos(
                        current_file_text[current_pos:]) + current_pos

                    key = current_file_text[current_pos +
                                            6:eol_pos].strip().upper()
                    in_def_bool = key in current_macros and current_macros[key][0] == "DEFINE"
                    #print("check for %s in macros: %s " % (key, in_def_bool))

                    # print("skipping %s" %
                    #      current_file_text[current_pos:eol_pos])
                    current_pos = eol_pos
                    continue
                elif current_file_text[current_pos:current_pos+7] == "#ifndef":
                    eol_pos = self.get_next_stop_pos(
                        current_file_text[current_pos:]) + current_pos
                    # print("skipping %s" %
                    #      current_file_text[current_pos:eol_pos])
                    current_pos = eol_pos
                    continue
                elif current_file_text[current_pos:current_pos+6] == "#endif":
                    eol_pos = self.get_next_stop_pos(
                        current_file_text[current_pos:]) + current_pos
                    # print("skipping %s" %
                    #      current_file_text[current_pos:eol_pos])
                    current_pos = eol_pos
                    continue
                elif current_file_text[current_pos:current_pos+5] == "#else":
                    eol_pos = self.get_next_stop_pos(
                        current_file_text[current_pos:]) + current_pos
                    # print("skipping %s" %
                    #      current_file_text[current_pos:eol_pos])
                    current_pos = eol_pos
                    continue
            else:
                buffer += new_char
                if new_char == "\n":

                    # replace macros
                    buffer = self.update_macros(buffer, current_macros)

                    # if buffer != "\n":
                    processed_text += buffer
                    buffer = ""
            current_pos += 1

        self.processed_files[file_id] = processed_text
        # with open("abbey_out.txt", "w") as outfile:
        #    outfile.write(processed_text)

        # load include in macro context
        # for each #define macro, add to macro context map
        # for each defined pattern, replace

        # write file in target folder, same file/folder tree ?


def main(argv):
    if len(sys.argv) < 3:
        print("USAGE:", sys.argv[0], "SST_SOURCE_DIR",
              "SST_PREPROCESSED_DIR")
        print("example: python preprocess.py ./src ./preprocessed")
        return

    SST_SOURCE_DIR = sys.argv[1]
    SST_TARGET_DIR = sys.argv[2]

    context = Context()
    context.preprocess(SST_SOURCE_DIR, SST_TARGET_DIR)


if __name__ == '__main__':
    main(sys.argv)
