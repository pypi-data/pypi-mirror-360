from .vocabs import vocabs
from .xml_module import XML
from .new_word import Holder
class dictionaryJ:
    __instance = None

    def __new__(cls, input_file):
        if cls.__instance is None:
            cls.__instance = super(dictionaryJ, cls).__new__(cls)
        return cls.__instance

    def __init__(self, input_file):
        if not hasattr(self, '_initialized'):
            self.__input_file = input_file
            self.__vocab_list = input_file.read()
            dic = vocabs(self.__vocab_list)
            self.__vocab_dict = dic.convert(self.__vocab_list)
            self.__load()
            self._initialized = True

    def __search_exact(self, search_text):
        return self.__vocab_dict.get(search_text)

    def __add(self, en, th):
        if en in self.__vocab_dict:
            return f"The word '{en}' already exists. Please use update instead."
        else:
            self.__vocab_dict[en] = th
            Holder.append_log("ADD", en, th)
            return f"Added new word: '{en}': '{th}'"

    def __delete(self, search_text):
        if search_text in self.__vocab_dict:
            del self.__vocab_dict[search_text]
            Holder.append_log("DELETE", search_text)
            return f"Deleted {search_text}"
        return "Word not found."

    def __update(self, en, th):
        if en in self.__vocab_dict:
            temp = list(self.__vocab_dict[en].split(", "))
            if th not in temp:
                updated_th = self.__vocab_dict[en] + ", " + th
                self.__vocab_dict[en] = updated_th
                Holder.append_log("UPDATE", en, th)
                return f"Updated '{en}' with new translation: '{th}'"
            else: return f"The translation '{th}' already exists for '{en}'."
        else:
            return f"The word '{en}' was not found in the dictionary."

    def __load(self):
        logs = Holder.read_log()
        for line in logs:
            if line.startswith("ADD:"):
                try:
                    _, rest = line.split("ADD: ", 1)
                    key, val = rest.split(": ", 1)
                    self.__vocab_dict[key] = val
                except ValueError:
                    pass
            elif line.startswith("UPDATE:"):
                try:
                    _, rest = line.split("UPDATE: ", 1)
                    key, val = rest.split(": ", 1)
                    if key in self.__vocab_dict:
                        self.__vocab_dict[key] += ", " + val
                except ValueError:
                    pass
            elif line.startswith("DELETE:"):
                try:
                    _, key = line.split("DELETE: ", 1)
                    if key in self.__vocab_dict:
                        del self.__vocab_dict[key]
                except ValueError:
                    pass