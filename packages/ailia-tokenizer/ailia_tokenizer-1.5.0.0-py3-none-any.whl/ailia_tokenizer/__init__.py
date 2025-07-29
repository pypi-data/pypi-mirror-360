import ctypes
import os
import sys
import re

import numpy
import platform
import typing

import logging
logger = logging.getLogger(__name__)

from collections import namedtuple

#### dependency check
if sys.platform == "win32":
    import ctypes
    try:
        for library in ["vcruntime140.dll", "vcruntime140_1.dll", "msvcp140.dll"]:
            ctypes.windll.LoadLibrary(library)
    except:
        print("  WARNING Please install MSVC 2015-2019 runtime from https://docs.microsoft.com/ja-jp/cpp/windows/latest-supported-vc-redist")


#### loading DLL / DYLIB / SO  ####
if sys.platform == "win32":
    dll_platform = "windows/x64"
    dll_name = "ailia_tokenizer.dll"
    load_fn = ctypes.WinDLL
elif sys.platform == "darwin":
    dll_platform = "mac"
    dll_name = "libailia_tokenizer.dylib"
    load_fn = ctypes.CDLL
else:
    is_arm = "arm" in platform.machine() or platform.machine() == "aarch64"
    if is_arm:
        if platform.architecture()[0] == "32bit":
            dll_platform = "linux/armeabi-v7a"
        else:
            dll_platform = "linux/arm64-v8a"
    else:
        dll_platform = "linux/x64"
    dll_name = "libailia_tokenizer.so"
    load_fn = ctypes.CDLL

dll_found = False
candidate = ["", str(os.path.dirname(os.path.abspath(__file__))) + str(os.sep), str(os.path.dirname(os.path.abspath(__file__))) + str(os.sep) + dll_platform + str(os.sep)]
for dir in candidate:
    try:
        dll = load_fn(dir + dll_name)
        dll_found = True
    except:
        pass
if not dll_found:
    msg = "DLL load failed : \'" + dll_name + "\' is not found"
    raise ImportError(msg)

# ==============================================================================

from ctypes import *

AILIA_TOKENIZER_STATUS_SUCCESS = ( 0 )

AILIA_TOKENIZER_TYPE_WHISPER = ( 0 )
AILIA_TOKENIZER_TYPE_CLIP = ( 1 )
AILIA_TOKENIZER_TYPE_XLM_ROBERTA = ( 2 )
AILIA_TOKENIZER_TYPE_MARIAN = ( 3 )
AILIA_TOKENIZER_TYPE_BERT_JAPANESE_WORDPIECE = ( 4 )
AILIA_TOKENIZER_TYPE_BERT_JAPANESE_CHARACTER = ( 5 )
AILIA_TOKENIZER_TYPE_T5 = ( 6 )
AILIA_TOKENIZER_TYPE_ROBERTA = ( 7 )
AILIA_TOKENIZER_TYPE_BERT = ( 8 )
AILIA_TOKENIZER_TYPE_GPT2 = ( 9 )
AILIA_TOKENIZER_TYPE_LLAMA = ( 10 )

AILIATokenizer = c_void_p

AILIA_TOKENIZER_FLAG_NONE = 0
AILIA_TOKENIZER_FLAG_UTF8_SAFE = 1

class ailia_tokenizer:
    def __init__(self):
        self.lib = dll
        self.lib.ailiaTokenizerCreate.restype = c_int
        self.lib.ailiaTokenizerCreate.argtypes = (POINTER(c_void_p), c_int32, c_int32)
        
        self.lib.ailiaTokenizerDestroy.restype = None
        self.lib.ailiaTokenizerDestroy.argtypes = (c_void_p, )

        self.lib.ailiaTokenizerOpenModelFileW.restype = ctypes.c_int
        self.lib.ailiaTokenizerOpenModelFileW.argtypes = (
            ctypes.c_void_p,                 # net
            ctypes.c_wchar_p,                # path
        )
        self.lib.ailiaTokenizerOpenModelFileA.restype = ctypes.c_int
        self.lib.ailiaTokenizerOpenModelFileA.argtypes = (
            ctypes.c_void_p,                 # net
            ctypes.c_char_p,                 # path
        )

        self.lib.ailiaTokenizerOpenDictionaryFileW.restype = ctypes.c_int
        self.lib.ailiaTokenizerOpenDictionaryFileW.argtypes = (
            ctypes.c_void_p,                 # net
            ctypes.c_wchar_p,                # path
        )
        self.lib.ailiaTokenizerOpenDictionaryFileA.restype = ctypes.c_int
        self.lib.ailiaTokenizerOpenDictionaryFileA.argtypes = (
            ctypes.c_void_p,                 # net
            ctypes.c_char_p,                 # path
        )

        self.lib.ailiaTokenizerOpenVocabFileW.restype = ctypes.c_int
        self.lib.ailiaTokenizerOpenVocabFileW.argtypes = (
            ctypes.c_void_p,                 # net
            ctypes.c_wchar_p,                # path
        )
        self.lib.ailiaTokenizerOpenVocabFileA.restype = ctypes.c_int
        self.lib.ailiaTokenizerOpenVocabFileA.argtypes = (
            ctypes.c_void_p,                 # net
            ctypes.c_char_p,                 # path
        )

        self.lib.ailiaTokenizerOpenMergeFileW.restype = ctypes.c_int
        self.lib.ailiaTokenizerOpenMergeFileW.argtypes = (
            ctypes.c_void_p,                 # net
            ctypes.c_wchar_p,                # path
        )
        self.lib.ailiaTokenizerOpenMergeFileA.restype = ctypes.c_int
        self.lib.ailiaTokenizerOpenMergeFileA.argtypes = (
            ctypes.c_void_p,                 # net
            ctypes.c_char_p,                 # path
        )

        self.lib.ailiaTokenizerOpenAddedTokensFileW.restype = ctypes.c_int
        self.lib.ailiaTokenizerOpenAddedTokensFileW.argtypes = (
            ctypes.c_void_p,                 # net
            ctypes.c_wchar_p,                # path
        )
        self.lib.ailiaTokenizerOpenAddedTokensFileA.restype = ctypes.c_int
        self.lib.ailiaTokenizerOpenAddedTokensFileA.argtypes = (
            ctypes.c_void_p,                 # net
            ctypes.c_char_p,                 # path
        )

        self.lib.ailiaTokenizerOpenTokenizerConfigFileW.restype = ctypes.c_int
        self.lib.ailiaTokenizerOpenTokenizerConfigFileW.argtypes = (
            ctypes.c_void_p,                 # net
            ctypes.c_wchar_p,                # path
        )
        self.lib.ailiaTokenizerOpenTokenizerConfigFileA.restype = ctypes.c_int
        self.lib.ailiaTokenizerOpenTokenizerConfigFileA.argtypes = (
            ctypes.c_void_p,                 # net
            ctypes.c_char_p,                 # path
        )

        self.lib.ailiaTokenizerEncode.restype = ctypes.c_int
        self.lib.ailiaTokenizerEncode.argtypes = (
            ctypes.c_void_p,                 # net
            ctypes.c_char_p,                 # utf8
        )
        self.lib.ailiaTokenizerEncodeWithSpecialTokens.restype = ctypes.c_int
        self.lib.ailiaTokenizerEncodeWithSpecialTokens.argtypes = (
            ctypes.c_void_p,                 # net
            ctypes.c_char_p,                 # utf8
        )

        dll.ailiaTokenizerGetTokenCount.restype = ctypes.c_int
        dll.ailiaTokenizerGetTokenCount.argtypes = (
            ctypes.c_void_p,                 # net
            ctypes.POINTER(ctypes.c_uint),   # count
        )
        dll.ailiaTokenizerGetTokens.restype = ctypes.c_int
        dll.ailiaTokenizerGetTokens.argtypes = (
            ctypes.c_void_p,                 # net
            numpy.ctypeslib.ndpointer(
                dtype=numpy.int32, flags='CONTIGUOUS'
            ),                               # tokens
            ctypes.c_uint                    # count
        )
        dll.ailiaTokenizerGetWordIDs.restype = ctypes.c_int
        dll.ailiaTokenizerGetWordIDs.argtypes = (
            ctypes.c_void_p,                 # net
            numpy.ctypeslib.ndpointer(
                dtype=numpy.int32, flags='CONTIGUOUS'
            ),                               # tokens
            ctypes.c_uint                    # count
        )
        dll.ailiaTokenizerGetCharStarts.restype = ctypes.c_int
        dll.ailiaTokenizerGetCharStarts.argtypes = (
            ctypes.c_void_p,                 # net
            numpy.ctypeslib.ndpointer(
                dtype=numpy.int32, flags='CONTIGUOUS'
            ),                               # tokens
            ctypes.c_uint                    # count
        )
        dll.ailiaTokenizerGetCharEnds.restype = ctypes.c_int
        dll.ailiaTokenizerGetCharEnds.argtypes = (
            ctypes.c_void_p,                 # net
            numpy.ctypeslib.ndpointer(
                dtype=numpy.int32, flags='CONTIGUOUS'
            ),                               # tokens
            ctypes.c_uint                    # count
        )
        self.lib.ailiaTokenizerDecode.restype = ctypes.c_int
        self.lib.ailiaTokenizerDecode.argtypes = (
            ctypes.c_void_p,                 # net
            numpy.ctypeslib.ndpointer(
                dtype=numpy.int32, flags='CONTIGUOUS'
            ),                               # tokens
            ctypes.c_uint                    # token_count
        )
        self.lib.ailiaTokenizerDecodeWithSpecialTokens.restype = ctypes.c_int
        self.lib.ailiaTokenizerDecodeWithSpecialTokens.argtypes = (
            ctypes.c_void_p,                 # net
            numpy.ctypeslib.ndpointer(
                dtype=numpy.int32, flags='CONTIGUOUS'
            ),                               # tokens
            ctypes.c_uint                    # token_count
        )
        dll.ailiaTokenizerGetTextLength.restype = ctypes.c_int
        dll.ailiaTokenizerGetTextLength.argtypes = (
            ctypes.c_void_p,                 # net
            ctypes.POINTER(ctypes.c_uint),   # count
        )
        dll.ailiaTokenizerGetText.restype = ctypes.c_int
        dll.ailiaTokenizerGetText.argtypes = (
            ctypes.c_void_p,                 # net
            numpy.ctypeslib.ndpointer(
                dtype=numpy.byte, flags='CONTIGUOUS'
            ),                               # text
            ctypes.c_uint                    # len
        )
        dll.ailiaTokenizerGetVocabSize.restype = ctypes.c_int
        dll.ailiaTokenizerGetVocabSize.argtypes = (
            ctypes.c_void_p,                 # net
            ctypes.POINTER(ctypes.c_uint),   # count
        )
        self.lib.ailiaTokenizerGetVocab.restype = ctypes.c_int
        self.lib.ailiaTokenizerGetVocab.argtypes = (
            ctypes.c_void_p,                 # net
            ctypes.c_int,                    # token
            ctypes.POINTER(ctypes.c_char_p)  # utf8
        )
        self.lib.ailiaTokenizerAddSpecialTokens.restype = ctypes.c_int
        self.lib.ailiaTokenizerAddSpecialTokens.argtypes = (
            ctypes.c_void_p,                 # net
            ctypes.POINTER(ctypes.c_char_p), # tokens
            ctypes.c_uint                    # count
        )

    def __check(self, status):
        if status != AILIA_TOKENIZER_STATUS_SUCCESS:
            raise AiliaTokenizerError(f"ailia tokenizer error", status)

    def Create(self, arg0, arg1, arg2):
        self.__check(self.lib.ailiaTokenizerCreate(cast(pointer(arg0), POINTER(c_void_p)), arg1, arg2))

    def Destroy(self, arg0):
        self.lib.ailiaTokenizerDestroy(cast(arg0, c_void_p))

    def OpenModelFile(self, arg0, arg1):
        if sys.platform == "win32":
            self.__check(self.lib.ailiaTokenizerOpenModelFileW(cast(arg0, c_void_p), ctypes.create_unicode_buffer(arg1)))
        else:
            self.__check(self.lib.ailiaTokenizerOpenModelFileA(cast(arg0, c_void_p), ctypes.create_string_buffer(arg1.encode("utf-8"))))

    def OpenDictionaryFile(self, arg0, arg1):
        if sys.platform == "win32":
            self.__check(self.lib.ailiaTokenizerOpenDictionaryFileW(cast(arg0, c_void_p), ctypes.create_unicode_buffer(arg1)))
        else:
            self.__check(self.lib.ailiaTokenizerOpenDictionaryFileA(cast(arg0, c_void_p), ctypes.create_string_buffer(arg1.encode("utf-8"))))

    def OpenVocabFile(self, arg0, arg1):
        if sys.platform == "win32":
            self.__check(self.lib.ailiaTokenizerOpenVocabFileW(cast(arg0, c_void_p), ctypes.create_unicode_buffer(arg1)))
        else:
            self.__check(self.lib.ailiaTokenizerOpenVocabFileA(cast(arg0, c_void_p), ctypes.create_string_buffer(arg1.encode("utf-8"))))

    def OpenMergeFile(self, arg0, arg1):
        if sys.platform == "win32":
            self.__check(self.lib.ailiaTokenizerOpenMergeFileW(cast(arg0, c_void_p), ctypes.create_unicode_buffer(arg1)))
        else:
            self.__check(self.lib.ailiaTokenizerOpenMergeFileA(cast(arg0, c_void_p), ctypes.create_string_buffer(arg1.encode("utf-8"))))

    def OpenAddedTokensFile(self, arg0, arg1):
        if sys.platform == "win32":
            self.__check(self.lib.ailiaTokenizerOpenAddedTokensFileW(cast(arg0, c_void_p), ctypes.create_unicode_buffer(arg1)))
        else:
            self.__check(self.lib.ailiaTokenizerOpenAddedTokensFileA(cast(arg0, c_void_p), ctypes.create_string_buffer(arg1.encode("utf-8"))))

    def OpenTokenizerConfigFile(self, arg0, arg1):
        if sys.platform == "win32":
            self.__check(self.lib.ailiaTokenizerOpenTokenizerConfigFileW(cast(arg0, c_void_p), ctypes.create_unicode_buffer(arg1)))
        else:
            self.__check(self.lib.ailiaTokenizerOpenTokenizerConfigFileA(cast(arg0, c_void_p), ctypes.create_string_buffer(arg1.encode("utf-8"))))

    def Encode(self, arg0, arg1):
        self.__check(self.lib.ailiaTokenizerEncode(cast(arg0, c_void_p), ctypes.create_string_buffer(arg1.encode("utf-8"))))
    
        count = ctypes.c_uint(0)
        self.__check(self.lib.ailiaTokenizerGetTokenCount(cast(arg0, c_void_p), ctypes.byref(count)))

        buf = numpy.zeros((count.value), dtype=numpy.int32, order='C')

        self.__check(self.lib.ailiaTokenizerGetTokens(cast(arg0, c_void_p), buf, count))

        return buf

    def EncodeWithSpecialTokens(self, arg0, arg1):
        self.__check(self.lib.ailiaTokenizerEncodeWithSpecialTokens(cast(arg0, c_void_p), ctypes.create_string_buffer(arg1.encode("utf-8"))))
    
        count = ctypes.c_uint(0)
        self.__check(self.lib.ailiaTokenizerGetTokenCount(cast(arg0, c_void_p), ctypes.byref(count)))

        buf = numpy.zeros((count.value), dtype=numpy.int32, order='C')

        self.__check(self.lib.ailiaTokenizerGetTokens(cast(arg0, c_void_p), buf, count))

        return buf

    def GetWordIDs(self, arg0):
        count = ctypes.c_uint(0)
        self.__check(self.lib.ailiaTokenizerGetTokenCount(cast(arg0, c_void_p), ctypes.byref(count)))

        buf = numpy.zeros((count.value), dtype=numpy.int32, order='C')

        self.__check(self.lib.ailiaTokenizerGetWordIDs(cast(arg0, c_void_p), buf, count))

        return buf

    def GetCharStarts(self, arg0):
        count = ctypes.c_uint(0)
        self.__check(self.lib.ailiaTokenizerGetTokenCount(cast(arg0, c_void_p), ctypes.byref(count)))

        buf = numpy.zeros((count.value), dtype=numpy.int32, order='C')

        self.__check(self.lib.ailiaTokenizerGetCharStarts(cast(arg0, c_void_p), buf, count))

        return buf

    def GetCharEnds(self, arg0):
        count = ctypes.c_uint(0)
        self.__check(self.lib.ailiaTokenizerGetTokenCount(cast(arg0, c_void_p), ctypes.byref(count)))

        buf = numpy.zeros((count.value), dtype=numpy.int32, order='C')

        self.__check(self.lib.ailiaTokenizerGetCharEnds(cast(arg0, c_void_p), buf, count))

        return buf

    def Decode(self, arg0, arg1, arg2):
        buf = numpy.zeros((len(arg1)), dtype=numpy.int32, order='C')
        for i in range(len(arg1)):
            buf[i] = arg1[i]

        self.__check(self.lib.ailiaTokenizerDecode(cast(arg0, c_void_p), buf, arg2))
    
        count = ctypes.c_uint(0)
        self.__check(self.lib.ailiaTokenizerGetTextLength(cast(arg0, c_void_p), ctypes.byref(count)))

        buf = numpy.zeros((count.value), dtype=numpy.int8, order='C')

        self.__check(self.lib.ailiaTokenizerGetText(cast(arg0, c_void_p), buf, count))

        return bytes(buf[0:len(buf) - 1]).decode("utf-8")

    def DecodeWithSpecialTokens(self, arg0, arg1, arg2):
        buf = numpy.zeros((len(arg1)), dtype=numpy.int32, order='C')
        for i in range(len(arg1)):
            buf[i] = arg1[i]

        self.__check(self.lib.ailiaTokenizerDecodeWithSpecialTokens(cast(arg0, c_void_p), buf, arg2))
    
        count = ctypes.c_uint(0)
        self.__check(self.lib.ailiaTokenizerGetTextLength(cast(arg0, c_void_p), ctypes.byref(count)))

        buf = numpy.zeros((count.value), dtype=numpy.int8, order='C')

        self.__check(self.lib.ailiaTokenizerGetText(cast(arg0, c_void_p), buf, count))

        return bytes(buf[0:len(buf) - 1]).decode("utf-8")

    def GetVocabSize(self, arg0):
        count = ctypes.c_uint(0)
        self.__check(self.lib.ailiaTokenizerGetVocabSize(cast(arg0, c_void_p), ctypes.byref(count)))
        return count.value

    def GetVocab(self, arg0, arg1):
        utf8 = c_char_p()
        utf8_ptr = ctypes.pointer(utf8)
        self.__check(self.lib.ailiaTokenizerGetVocab(cast(arg0, c_void_p), arg1, utf8_ptr))
        return utf8_ptr.contents.value.decode('utf-8')

    def AddSpecialTokens(self, arg0, arg1):
        byte_str_list = [s.encode('utf-8') for s in arg1]
        c_char_p_array = (ctypes.c_char_p * len(byte_str_list))(*byte_str_list)
        c_char_p_pointer = ctypes.cast(c_char_p_array, ctypes.POINTER(ctypes.c_char_p))
        self.__check(self.lib.ailiaTokenizerAddSpecialTokens(cast(arg0, c_void_p), c_char_p_pointer, len(arg1)))

# ==============================================================================
# BaseTokenizer
# ==============================================================================

class AiliaTokenizerError(RuntimeError):
    def __init__(self, message, code):
        super().__init__(f"{message} code:{code}")
        self.code = code

class AiliaTokenizerResult:
    def __init__(self, input_ids, attention_mask, sequence_ids, word_ids, char_starts, char_ends):
        self.input_ids = input_ids
        self.attention_mask = attention_mask
        self._sequence_ids = sequence_ids
        self._word_ids = word_ids
        self._char_starts = char_starts
        self._char_ends = char_ends

    def __getitem__(self, key):
        if key in self.__dict__:
            return getattr(self, key)
        raise KeyError(f"No such key: {key}")

    def keys(self):
        return {key: value for key, value in self.__dict__.items() if key != '_sequence_ids' and key != '_word_ids' and key != '_char_starts' and key != '_char_ends'}.keys()

    def items(self):
        return {key: value for key, value in self.__dict__.items() if key != '_sequence_ids' and key != '_word_ids' and key != '_char_starts' and key != '_char_ends'}.items()
    
    def __repr__(self):
        return str({key: value for key, value in self.__dict__.items() if key != '_sequence_ids' and key != '_word_ids' and key != '_char_starts' and key != '_char_ends'})

    def sequence_ids(self, batch):
        return self._sequence_ids[batch]

    def word_ids(self, batch_index = 0):
        if self._word_ids is None:
            raise AiliaTokenizerError("this tokenizer not supported word_ids.", -1) 
        ret_list = self._word_ids[batch_index]
        if type(ret_list) != list:
            return ret_list.tolist() # numpy to list
        return ret_list

    def token_to_word(self, batch_or_token_index, token_index = None):
        if self._word_ids is None:
            raise AiliaTokenizerError("this tokenizer not supported word_ids.", -1) 
        if token_index is None:
            batch_index = 0
            token_index = batch_or_token_index
        else:
            batch_index  = batch_or_token_index
        return self._word_ids[batch_index][token_index]

    def word_to_chars(self, batch_or_word_index, word_index = None, sequence_index = None):
        if self._word_ids is None:
            raise AiliaTokenizerError("this tokenizer not supported word_ids.", -1) 
        if word_index is None:
            batch_index = 0
            word_index = batch_or_word_index
        else:
            batch_index = batch_or_word_index
        if batch_index is None:
            batch_index = 0
        if word_index is None:
            word_index = 0
        CharSpan = namedtuple('CharSpan', ['start', 'end'])
        for i in range(len(self._word_ids[batch_index])):
            sequence__id = self._sequence_ids[batch_index][i]
            if sequence_index is not None:
                if sequence__id != sequence_index:
                    continue
            cur_word = self._word_ids[batch_index][i]
            if cur_word is None:
                continue
            if word_index <= cur_word:
                return CharSpan(start = self._char_starts[batch_index][i], end = self._char_ends[batch_index][i])
        return None

    def char_to_token(self, batch_or_char_index: int, char_index = None):
        if self._word_ids is None:
            raise AiliaTokenizerError("this tokenizer not supported word_ids.", -1) 
        if char_index is None:
            batch_index = 0
            char_index = batch_or_char_index
        else:
            batch_index  = batch_or_char_index
        for i in range(len(self._char_starts[batch_index])):
            cur_char_start = self._char_starts[batch_index][i]
            cur_char_end = self._char_ends[batch_index][i]
            if cur_char_start is None or cur_char_end is None:
                continue
            # char_index < cur_char_startは文頭のspaceがスキップされることを考慮
            if char_index < cur_char_start or (cur_char_start <= char_index and char_index < cur_char_end):
                return i
        return None

class AiliaTokenizerResultWithTokenTypeIds(AiliaTokenizerResult):
    def __init__(self, input_ids, attention_mask, sequence_ids, word_ids, char_starts, char_ends, token_type_ids):
        super().__init__(input_ids, attention_mask, sequence_ids, word_ids, char_starts, char_ends)
        self.token_type_ids = token_type_ids

class PreTrainedTokenizer:
    _pad_token_id = -1
    _initialized = False
    _token_type_ids = False
    _vocab = None
    _sot_offset = 1 # SOTが存在する場合は1、存在しない場合は0
    _eot_offset = 1 # EOTが存在する場合は1、存在しない場合は0
    _retain_eot = False # text_pairを結合する際にtextのeotを残すか
    _retain_sot = False # text_pairを結合する際にtext_pairのsotを残すか
    _retain_sot_replace_to_eot = False # text_pairを結合する際にtext_pairのsotをeotに置き換えるか
    _special_token_type_pair0 = -1
    _special_token_type_pair1 = -2
    _word_ids_enable = False

    def __init__(self):
        self.instance = AILIATokenizer()
        self.dll = ailia_tokenizer()

    def __del__(self):
        if self.instance:
            self.dll.Destroy(self.instance)
    
    def _padding_true(self, sequence1):
        if self._pad_token_id == -1:
            raise AiliaTokenizerError("unknown padding token id.", -1)

        for key in sequence1.keys():
            max_len = 0
            for batch in range(len(sequence1[key])):
                max_len = max(max_len, sequence1[key][batch].shape[0])

            padding = []

            for batch in range(len(sequence1[key])):
                if key == "input_ids":
                    padding.append(numpy.array([self._pad_token_id] * max_len, dtype = sequence1[key][batch].dtype))
                else:
                    padding.append(numpy.array([0] * max_len, dtype = sequence1[key][batch].dtype))
                padding[batch][:len(sequence1[key][batch])] = sequence1[key][batch]
            
            sequence1[key] = padding

        return sequence1

    def _padding_max_length(self, sequence1, max_length):
        for key in sequence1.keys():
            for batch in range(len(sequence1[key])):
                original_len = sequence1[key][batch].shape[0]
                if original_len < max_length:
                    padding_data = numpy.zeros((max_length), dtype=sequence1[key][batch].dtype)
                    padding_data[0:original_len] = sequence1[key][batch]
                    if key == "input_ids":
                        padding_data[original_len:max_length] = self._pad_token_id
                    sequence1[key][batch] = padding_data

        return sequence1

    def _padding(self, sequence1, padding, max_length):
        if padding == True or padding == "longest": # not max_length
            sequence1 = self._padding_true(sequence1)
        elif padding == "max_length":
            sequence1 = self._padding_max_length(sequence1, max_length)

        return sequence1

    def _truncation_one(self, sequence1, batch, max_length, add_special_tokens):
        # シンボルをmax_lengthまで切り詰める
        for key in sequence1.keys():
            if self._eot_offset == 1 and add_special_tokens == True:
                sequence1[key][batch][max_length - 1] = sequence1[key][batch][-1]
            sequence1[key][batch] = sequence1[key][batch][0:max_length]

        return sequence1

    def _truncation_single(self, sequence1, truncation, max_length, add_special_tokens):
        if (truncation == True or truncation == "longest_first" or truncation == "only_first") and max_length is not None:
            for batch in range(len(sequence1["input_ids"])):
                original_len = sequence1["input_ids"][batch].shape[0]
                if original_len > max_length:
                    sequence1 = self._truncation_one(sequence1, batch, max_length, add_special_tokens)
        return sequence1

    def _get_concat_reduce_len(self, add_special_tokens):
        # txt_pairをconcatした結果、何トークン減少するかを計算する
        # txtとtxt_pairをconcatした場合、末尾のeotと、先頭のsotが削除される
        # ただし、モデルによってretainする場合もある
        if self._retain_eot:
            reduce_len = 0
        else:
            reduce_len = self._eot_offset
        if self._retain_sot:
            reduce_len = reduce_len
        else:
            reduce_len = reduce_len + self._sot_offset
        if add_special_tokens == False:
            reduce_len = 0
        return reduce_len

    def _truncation_longest(self, sequence1, sequence2, max_length, add_special_tokens):
        # 長い方から優先的にtruncateする
        for batch in range(len(sequence1["input_ids"])):
            while True:
                original_len1 = sequence1["input_ids"][batch].shape[0]
                original_len2 = sequence2["input_ids"][batch].shape[0]
                reduce_len = self._get_concat_reduce_len(add_special_tokens)
                remove_tokens = original_len1 + original_len2 - reduce_len - max_length # min_lenはconcatで削除される
                if remove_tokens <= 0 or (original_len1 == reduce_len and original_len2 == reduce_len):
                    break
                if remove_tokens > 0:
                    if original_len1 > original_len2:
                        target_length = max(reduce_len, original_len1 - 1)
                        sequence1 = self._truncation_one(sequence1, batch, target_length, add_special_tokens)
                    else:
                        target_length = max(reduce_len, original_len2 - 1)
                        sequence2 = self._truncation_one(sequence2, batch, target_length, add_special_tokens)
        return sequence1, sequence2

    def _truncation_only_first_or_seocond(self, sequence1, sequence2, truncation, max_length, add_special_tokens):
        # textかtext_pairのどちらかからtruncateする
        truncate_failed = False
        for batch in range(len(sequence1["input_ids"])):
            original_len1 = sequence1["input_ids"][batch].shape[0]
            original_len2 = sequence2["input_ids"][batch].shape[0]
            reduce_len = self._get_concat_reduce_len(add_special_tokens)
            remove_tokens = original_len1 + original_len2 - reduce_len - max_length # min_lenはconcatで削除される
            if remove_tokens > 0:
                token_size_under_limit = 1 + self._eot_offset + self._sot_offset # transformersでは3トークン未満にできないように制約されている
                if add_special_tokens == False:
                    token_size_under_limit = 1
                if truncation == "only_first":
                    target_length = max(token_size_under_limit, original_len1 - remove_tokens)
                    if original_len1 - target_length != remove_tokens:
                        truncate_failed = True
                    else:
                        sequence1 = self._truncation_one(sequence1, batch, target_length, add_special_tokens)
                if truncation == "only_second":
                    target_length = max(token_size_under_limit, original_len2 - remove_tokens)
                    if original_len2 - target_length != remove_tokens:
                        truncate_failed = True
                    else:
                        sequence2 = self._truncation_one(sequence2, batch, target_length, add_special_tokens)
        if truncate_failed:
            logger.warning("Please select another truncation strategy than TruncationStrategy.ONLY_SECOND, for instance 'longest_first' or 'only_first'.")
        return sequence1, sequence2

    def _truncation_pair(self, sequence1, sequence2, truncation, max_length, add_special_tokens):
        if (truncation == "longest_first" or truncation == True):
            if max_length is None:
                raise("max_length must be set for this truncation mode.")
            return self._truncation_longest(sequence1, sequence2, max_length, add_special_tokens)
        if (truncation == "only_first" or truncation == "only_second"):
            if max_length is None:
                raise("max_length must be set for this truncation mode.")
            return self._truncation_only_first_or_seocond(sequence1, sequence2, truncation, max_length, add_special_tokens)
        if truncation == "do_not_truncate" or truncation == False:
            return sequence1, sequence2
        raise("unknown truncation type.")

    def _concat(self, sequence1, sequence2, add_special_tokens):
        for key in sequence1.keys():
            for batch in range(len(sequence1[key])):
                if not self._retain_eot and self._eot_offset == 1 and add_special_tokens == True:
                    sequence1[key][batch] = sequence1[key][batch][:-1]

                if not self._retain_sot and self._sot_offset == 1 and add_special_tokens == True:
                    sequence2[key][batch] = sequence2[key][batch][1:]

                if key == "input_ids":
                    if self._retain_sot and self._retain_sot_replace_to_eot and add_special_tokens == True:
                        sequence2[key][batch][0] = sequence2[key][batch][-1] # SOTをEOTに置き換え

                sequence1[key][batch] = numpy.concatenate((sequence1[key][batch][:], sequence2[key][batch][:]), axis=0)
        return sequence1

    def _return_tensors(self, sequence1, return_tensors):
        for key in sequence1.keys():
            if return_tensors == 'np':
                is_same_shape = True
                for batch in range(len(sequence1[key]) - 1):
                    if sequence1[key][batch].shape[0] != sequence1[key][batch + 1].shape[0]:
                        is_same_shape = False
                if is_same_shape == False:
                    sequence1[key] = numpy.array(sequence1[key], dtype=object)
                else:
                    new_data = numpy.zeros((len(sequence1[key]), sequence1[key][0].shape[0]), dtype=sequence1[key][0].dtype)
                    for batch in range(len(sequence1[key])):
                        new_data[batch, :] = sequence1[key][batch]
                    sequence1[key] = new_data
            else:
                for batch in range(0, len(sequence1[key])):
                    sequence1[key][batch] = sequence1[key][batch].tolist()
        return sequence1

    def _encode_one_sequence(self, text, pair_id, split_special_tokens, add_special_tokens):
        input_ids = []
        attention_masks = []
        token_type_ids = []
        word_ids = []
        char_starts = []
        char_ends = []

        for t in text:
            if split_special_tokens:
                input_id = self.dll.Encode(self.instance, t).astype(numpy.int64)
            else:
                input_id = self.dll.EncodeWithSpecialTokens(self.instance, t).astype(numpy.int64)
            if self._word_ids_enable:
                input_word_id = self.dll.GetWordIDs(self.instance).astype(numpy.int64)
                input_char_start = self.dll.GetCharStarts(self.instance).astype(numpy.int64)
                input_char_end = self.dll.GetCharEnds(self.instance).astype(numpy.int64)
                word_id = input_word_id.astype(object)
                char_start = input_char_start.astype(object)
                char_end = input_char_end.astype(object)
                word_id[input_word_id<0] = None
                char_start[input_char_start<0] = None
                char_end[input_char_end<0] = None
            else:
                word_id = numpy.zeros((input_id.shape[0]), dtype=object)
                char_start = numpy.zeros((input_id.shape[0]), dtype=object)
                char_end = numpy.zeros((input_id.shape[0]), dtype=object)
            if add_special_tokens == False:
                if self._sot_offset == 1:
                    input_id = input_id[1:]
                    word_id = word_id[1:]
                    char_start = char_start[1:]
                    char_end = char_end[1:]
                if self._eot_offset == 1:
                    input_id = input_id[:-1]
                    word_id = word_id[:-1]
                    char_start = char_start[:-1]
                    char_end = char_end[:-1]
            attention_mask = numpy.zeros((input_id.shape[0]), dtype=numpy.int64)
            attention_mask[:input_id.shape[0]] = 1
            token_type_id = numpy.zeros((input_id.shape[0]), dtype=numpy.int64)
            token_type_id[:] = pair_id
            if self._sot_offset == 1 and add_special_tokens == True:
                token_type_id[0] = self._special_token_type_pair0 if (pair_id == 0) else self._special_token_type_pair1
            if self._eot_offset == 1 and add_special_tokens == True:
                token_type_id[-1] = self._special_token_type_pair0 if (pair_id == 0) else self._special_token_type_pair1
            input_ids.append(input_id)
            attention_masks.append(attention_mask)
            token_type_ids.append(token_type_id)
            word_ids.append(word_id)
            char_starts.append(char_start)
            char_ends.append(char_end)

        return {"input_ids":input_ids, "attention_masks":attention_masks, "token_type_ids":token_type_ids, "word_ids":word_ids, "char_starts":char_starts, "char_ends":char_ends}

    def _sequence_ids(self, sequence1):
        sequence_ids = []
        for batch in range(len(sequence1["token_type_ids"])):
            sequence_ids.append(sequence1["token_type_ids"][batch].copy().astype(object))
            sequence_ids[batch][sequence_ids[batch] < 0] = None
            sequence1["token_type_ids"][batch][sequence1["token_type_ids"][batch] == self._special_token_type_pair0] = 0
            sequence1["token_type_ids"][batch][sequence1["token_type_ids"][batch] == self._special_token_type_pair1] = 1
            sequence1["sequence_ids"] = sequence_ids
        return sequence1

    def _encode(self, text: typing.Union[str, typing.List[str], typing.List[typing.List[str]]], text_pair=None, padding=True, truncation=True, return_tensors=None, max_length = None, split_special_tokens = False, return_token_type_ids = None, add_special_tokens = True):
        if not self._initialized:
            raise AiliaTokenizerError("from_pretrained not called.", -1)
        if return_tensors != 'np' and return_tensors != None:
            raise AiliaTokenizerError("return tensors pt not supported. please use np.", -1)
        if padding != False and padding != True and padding != "max_length" and padding != "do_not_pad" and padding != "longest":
            raise AiliaTokenizerError("unknown padding type", -1)
        if truncation != False and truncation != True and truncation != "longest_first" and truncation != "only_first" and truncation != "only_second":
            raise AiliaTokenizerError("unknown truncation type", -1)
        if return_token_type_ids == True and add_special_tokens == False:
            raise AiliaTokenizerError("return token_type_ids while setting add_special_tokens to False results in an undefined behavior", -1)

        if type(text) is list:
            if type(text[0]) is list:
                if not(text_pair is None):
                    raise AiliaTokenizerError("text_pair not supported.", -1)
                text_first = []
                text_pair = []
                for batch in range(len(text)):
                    if len(text[batch]) != 2:
                        raise AiliaTokenizerError("text must be pair not supported.", -1)
                    text_first.append(text[batch][0])
                    text_pair.append(text[batch][1])
                text = text_first

        reduce_axis = False
        if type(text) == str:
            text = [text]
            if return_tensors != 'np':
                reduce_axis = True

        if type(text_pair) == str:
            text_pair = [text_pair]
            if len(text) != len(text_pair):
                raise AiliaTokenizerError("text and text_pair must be same length", -1)

        sequence1 = self._encode_one_sequence(text, 0, split_special_tokens, add_special_tokens)

        if text_pair is not None:
            sequence2 = self._encode_one_sequence(text_pair, 1, split_special_tokens, add_special_tokens)
            sequence1, sequence2 = self._truncation_pair(sequence1, sequence2, truncation, max_length, add_special_tokens)
            sequence1 = self._concat(sequence1, sequence2, add_special_tokens)
        else:
            sequence1 = self._truncation_single(sequence1, truncation, max_length, add_special_tokens)
        sequence1 = self._padding(sequence1, padding, max_length)
        sequence1 = self._sequence_ids(sequence1)
        sequence1 = self._return_tensors(sequence1, return_tensors)

        if reduce_axis:
            sequence1["input_ids"] = sequence1["input_ids"][0]
            sequence1["attention_masks"] = sequence1["attention_masks"][0]
            sequence1["token_type_ids"] = sequence1["token_type_ids"][0]
        
        if not self._word_ids_enable:
            sequence1["word_ids"] = None
        
        if (return_token_type_ids == None and self._token_type_ids) or (return_token_type_ids == True):
            return AiliaTokenizerResultWithTokenTypeIds(input_ids=sequence1["input_ids"], attention_mask=sequence1["attention_masks"], sequence_ids=sequence1["sequence_ids"], word_ids=sequence1["word_ids"], char_starts=sequence1["char_starts"], char_ends=sequence1["char_ends"], token_type_ids=sequence1["token_type_ids"])
        else:
            return AiliaTokenizerResult(input_ids=sequence1["input_ids"], attention_mask=sequence1["attention_masks"], sequence_ids=sequence1["sequence_ids"], word_ids=sequence1["word_ids"], char_starts=sequence1["char_starts"], char_ends=sequence1["char_ends"])

    def encode(self, text: typing.Union[str], text_pair=None, padding=True, truncation=True, return_tensors=None, max_length = None, split_special_tokens = False, return_token_type_ids = None, add_special_tokens = True):
        if not (type(text) is str):
            raise AiliaTokenizerError("batch encode not supported.", -1)
        return self._encode(text, text_pair, padding, truncation, return_tensors, max_length, split_special_tokens, return_token_type_ids, add_special_tokens)["input_ids"]

    def encode_plus(self, text: typing.Union[str], text_pair=None, padding=True, truncation=True, return_tensors=None, max_length = None, split_special_tokens = False, return_token_type_ids = None, add_special_tokens = True):
        if not (type(text) is str):
            raise AiliaTokenizerError("batch encode not supported.", -1)
        return self._encode(text, text_pair, padding, truncation, return_tensors, max_length, split_special_tokens, return_token_type_ids, add_special_tokens)

    def batch_encode_plus(self, text: typing.Union[str, typing.List[str], typing.List[typing.List[str]]], text_pair=None, padding=True, truncation=True, return_tensors=None, max_length = None, split_special_tokens = False, return_token_type_ids = None, add_special_tokens = True):
        if type(text) is str:
            batch_text = []
            for t in text:
                batch_text.append(t)
            text = batch_text
        return self._encode(text, text_pair, padding, truncation, return_tensors, max_length, split_special_tokens, return_token_type_ids, add_special_tokens)

    def __call__(self, text: typing.Union[str, typing.List[str], typing.List[typing.List[str]]], text_pair=None, padding=True, truncation=True, return_tensors=None, max_length = None, split_special_tokens = False, return_token_type_ids = None, add_special_tokens = True):
        return self._encode(text, text_pair, padding, truncation, return_tensors, max_length, split_special_tokens, return_token_type_ids, add_special_tokens)

    def decode(self, input_ids: typing.Union[typing.List[int]], skip_special_tokens = False) -> typing.Union[str]:
        if not self._initialized:
            raise AiliaTokenizerError("from_pretrained not called.", -1)
        if skip_special_tokens:
            text = self.dll.Decode(self.instance, input_ids, len(input_ids))
        else:
            text = self.dll.DecodeWithSpecialTokens(self.instance, input_ids, len(input_ids))
        return text

    def batch_decode(self, sequences: typing.Union[typing.List[typing.List[int]]], skip_special_tokens = False) -> typing.Union[typing.List[str]]:
        if not self._initialized:
            raise AiliaTokenizerError("from_pretrained not called.", -1)
        texts = []
        for batch in range(len(sequences)):
            if skip_special_tokens:
                text = self.dll.Decode(self.instance, sequences[batch], len(sequences[batch]))
            else:
                text = self.dll.DecodeWithSpecialTokens(self.instance, sequences[batch], len(sequences[batch]))
            texts.append(text)
        return texts

    def _load_vocab(self):
        if self._vocab == None:
            self._vocab = {}
            size = self.dll.GetVocabSize(self.instance)
            for i in range(size):
                vocab = self.dll.GetVocab(self.instance, i)
                self._vocab[vocab] = i

    def tokenize(self, text: typing.Union[str]) -> typing.Union[typing.List[str]]:
        if type(text) == list:
            raise AiliaTokenizerError("only support str.", -1)
        ids = self.encode_plus(text)["input_ids"]
        tokens = self.convert_ids_to_tokens(ids[self._sot_offset: len(ids) - self._eot_offset])
        assert isinstance(tokens, list), "Expected 'convert_ids_to_tokens' to return 'str'" # for mypy
        return tokens
        
    def convert_ids_to_tokens(self, ids: typing.Union[int, typing.List[int]]) -> typing.Union[str, typing.List[str]]:
        if not (type(ids) == list):
            return self.dll.GetVocab(self.instance, ids)
        result = []
        for i in range(0, len(ids)):
            vocab = self.dll.GetVocab(self.instance, ids[i])
            result.append(vocab)
        return result

    def convert_tokens_to_ids(self, tokens: typing.Union[str, typing.List[str]]) -> typing.Union[int, typing.List[int]]:
        is_str = False
        if type(tokens) == str:
            tokens = [tokens]
            is_str = True

        self._load_vocab()

        assert self._vocab is not None, "Expected vocab exists" # for mypy

        ids = []
        for token in tokens:
            if token in self._vocab:
                id = self._vocab[token]
                ids.append(id)
        
        if is_str:
            return ids[0]

        return ids

    def add_special_tokens(self, special_tokens_dict):
        if "additional_special_tokens" in special_tokens_dict:
            self.dll.AddSpecialTokens(self.instance, special_tokens_dict["additional_special_tokens"])
        else:
            for key in special_tokens_dict.keys():
                if key == "pad_token":
                    self._pad_token_id = self.convert_tokens_to_ids(special_tokens_dict["pad_token"])
                else:
                    raise AiliaTokenizerError("add_special_tokens only supports pad_token.", -1)

# ==============================================================================
# Whisper
# ==============================================================================

class WhisperTokenizer(PreTrainedTokenizer):
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path = None):
        target = WhisperTokenizer()
        mode = AILIA_TOKENIZER_TYPE_WHISPER
        flags = AILIA_TOKENIZER_FLAG_NONE
        target.dll.Create(target.instance, ctypes.c_int32(mode), ctypes.c_int32(flags))
        if pretrained_model_name_or_path is not None:
            target.dll.OpenVocabFile(target.instance, os.path.join(pretrained_model_name_or_path, "vocab.json"))
        if pretrained_model_name_or_path is not None:
            target.dll.OpenMergeFile(target.instance, os.path.join(pretrained_model_name_or_path, "merges.txt"))
        if pretrained_model_name_or_path is not None:
            target.dll.OpenAddedTokensFile(target.instance, os.path.join(pretrained_model_name_or_path, "added_tokens.json"))
        target._initialized = True
        target._pad_token_id = 50257 # PADではなくEOSでPADする
        target.all_special_ids = []
        target._load_vocab()
        for token in target._vocab.keys():
            if re.match(r"<\|[^>0-9\.]+\|>", token): # timestampはspecial tokensから除外
                target.all_special_ids.append(target._vocab[token])
        return target

# ==============================================================================
# Clip
# ==============================================================================

class CLIPTokenizer(PreTrainedTokenizer):
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path = None):
        target = CLIPTokenizer()
        mode = AILIA_TOKENIZER_TYPE_CLIP
        flags = AILIA_TOKENIZER_FLAG_NONE
        target.dll.Create(target.instance, ctypes.c_int32(mode), ctypes.c_int32(flags))
        target._initialized = True
        target._pad_token_id = 49407 # PADではなくEOSでPADする
        target._retain_eot = True
        target._retain_sot = True
        target._retain_sot_replace_to_eot = True
        return target

# ==============================================================================
# XLMRoberta
# ==============================================================================

class XLMRobertaTokenizer(PreTrainedTokenizer):
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path):
        target = XLMRobertaTokenizer()
        mode = AILIA_TOKENIZER_TYPE_XLM_ROBERTA
        flags = AILIA_TOKENIZER_FLAG_NONE
        target.dll.Create(target.instance, ctypes.c_int32(mode), ctypes.c_int32(flags))
        target.dll.OpenModelFile(target.instance, os.path.join(pretrained_model_name_or_path, "sentencepiece.bpe.model"))
        target._initialized = True
        target._pad_token_id = 1 # spmではなくfairseqのpadが入る
        target._retain_eot = True
        target._retain_sot = True
        target._retain_sot_replace_to_eot = True
        return target

# ==============================================================================
# Marian
# ==============================================================================

class MarianTokenizer(PreTrainedTokenizer):
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path):
        target = MarianTokenizer()
        mode = AILIA_TOKENIZER_TYPE_MARIAN
        flags = AILIA_TOKENIZER_FLAG_NONE
        target.dll.Create(target.instance, ctypes.c_int32(mode), ctypes.c_int32(flags))
        target.dll.OpenModelFile(target.instance, os.path.join(pretrained_model_name_or_path, "source.spm"))
        target._initialized = True
        target._pad_token_id = 32000
        target._sot_offset = 0 # SOTはない
        return target

# ==============================================================================
# BertJapaneseTokenizer
# ==============================================================================

class BertJapaneseWordPieceTokenizer(PreTrainedTokenizer):
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path, dict_path):
        target = BertJapaneseWordPieceTokenizer()
        mode = AILIA_TOKENIZER_TYPE_BERT_JAPANESE_WORDPIECE
        flags = AILIA_TOKENIZER_FLAG_NONE
        target.dll.Create(target.instance, ctypes.c_int32(mode), ctypes.c_int32(flags))
        target.dll.OpenDictionaryFile(target.instance, dict_path)
        target.dll.OpenVocabFile(target.instance, os.path.join(pretrained_model_name_or_path, "vocab.txt"))
        target._initialized = True
        target._pad_token_id = target.dll.EncodeWithSpecialTokens(target.instance, "[PAD]").astype(numpy.int64)[1]
        target._token_type_ids = True
        target._retain_eot = True
        target._retain_sot = False
        return target

class BertJapaneseCharacterTokenizer(PreTrainedTokenizer):
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path, dict_path):
        target = BertJapaneseCharacterTokenizer()
        mode = AILIA_TOKENIZER_TYPE_BERT_JAPANESE_CHARACTER
        flags = AILIA_TOKENIZER_FLAG_NONE
        target.dll.Create(target.instance, ctypes.c_int32(mode), ctypes.c_int32(flags))
        target.dll.OpenDictionaryFile(target.instance, dict_path)
        target.dll.OpenVocabFile(target.instance, os.path.join(pretrained_model_name_or_path, "vocab.txt"))
        target._initialized = True
        target._pad_token_id = target.dll.EncodeWithSpecialTokens(target.instance, "[PAD]").astype(numpy.int64)[1]
        target._token_type_ids = True
        target._retain_eot = True
        target._retain_sot = False
        return target

# ==============================================================================
# T5
# ==============================================================================

class T5Tokenizer(PreTrainedTokenizer):
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path):
        target = T5Tokenizer()
        mode = AILIA_TOKENIZER_TYPE_T5
        flags = AILIA_TOKENIZER_FLAG_NONE
        target.dll.Create(target.instance, ctypes.c_int32(mode), ctypes.c_int32(flags))
        target.dll.OpenModelFile(target.instance, os.path.join(pretrained_model_name_or_path, "spiece.model"))
        target._initialized = True
        target._pad_token_id = 0
        target._sot_offset = 0 # SOTはない
        target._retain_eot = True
        return target

# ==============================================================================
# Roberta
# ==============================================================================

class RobertaTokenizer(PreTrainedTokenizer):
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path):
        target = RobertaTokenizer()
        mode = AILIA_TOKENIZER_TYPE_ROBERTA
        flags = AILIA_TOKENIZER_FLAG_NONE
        target.dll.Create(target.instance, ctypes.c_int32(mode), ctypes.c_int32(flags))
        target.dll.OpenVocabFile(target.instance, os.path.join(pretrained_model_name_or_path, "vocab.json"))
        target.dll.OpenMergeFile(target.instance, os.path.join(pretrained_model_name_or_path, "merges.txt"))
        target._initialized = True
        target._pad_token_id = 1
        target._retain_sot = True
        target._retain_eot = True
        target._retain_sot_replace_to_eot = True
        target._word_ids_enable = True
        return target

# ==============================================================================
# BERT
# ==============================================================================

class BertTokenizer(PreTrainedTokenizer):
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path):
        target = BertTokenizer()
        mode = AILIA_TOKENIZER_TYPE_BERT
        flags = AILIA_TOKENIZER_FLAG_NONE
        target.dll.Create(target.instance, ctypes.c_int32(mode), ctypes.c_int32(flags))
        target.dll.OpenVocabFile(target.instance, os.path.join(pretrained_model_name_or_path, "vocab.txt"))
        target.dll.OpenTokenizerConfigFile(target.instance, os.path.join(pretrained_model_name_or_path, "tokenizer_config.json"))
        target._initialized = True
        target._pad_token_id = target.dll.EncodeWithSpecialTokens(target.instance, "[PAD]").astype(numpy.int64)[1]
        target._token_type_ids = True
        target._retain_eot = True
        target._retain_sot = False
        target._word_ids_enable = True
        return target

# ==============================================================================
# 互換性用
# ==============================================================================

class BertUncasedTokenizer(PreTrainedTokenizer):
    @classmethod
    def from_pretrained(cls, vocab_path):
        logger.warning("This class will be removed in a future version. Please use BertTokenizer.")
        target = BertUncasedTokenizer()
        mode = AILIA_TOKENIZER_TYPE_BERT
        flags = AILIA_TOKENIZER_FLAG_NONE
        target.dll.Create(target.instance, ctypes.c_int32(mode), ctypes.c_int32(flags))
        target.dll.OpenVocabFile(target.instance, vocab_path)
        tokenizer_config_path = vocab_path.replace("vocab.txt", "tokenizer_config.json")
        target.dll.OpenTokenizerConfigFile(target.instance, tokenizer_config_path)
        target._initialized = True
        target._pad_token_id = target.dll.EncodeWithSpecialTokens(target.instance, "[PAD]").astype(numpy.int64)[1]
        target._token_type_ids = True
        target._retain_eot = True
        target._retain_sot = False
        target._retain_sot_replace_to_eot = True
        return target

class BertCasedTokenizer(PreTrainedTokenizer):
    @classmethod
    def from_pretrained(cls, vocab_path):
        logger.warning("This class will be removed in a future version. Please use BertTokenizer.")
        target = BertCasedTokenizer()
        mode = AILIA_TOKENIZER_TYPE_BERT
        flags = AILIA_TOKENIZER_FLAG_NONE
        target.dll.Create(target.instance, ctypes.c_int32(mode), ctypes.c_int32(flags))
        target.dll.OpenVocabFile(target.instance, vocab_path)
        tokenizer_config_path = vocab_path.replace("vocab.txt", "tokenizer_config.json")
        target.dll.OpenTokenizerConfigFile(target.instance, tokenizer_config_path)
        target._initialized = True
        target._pad_token_id = target.dll.EncodeWithSpecialTokens(target.instance, "[PAD]").astype(numpy.int64)[1]
        target._token_type_ids = True
        target._retain_eot = True
        target._retain_sot = False
        return target

# ==============================================================================
# GPT2
# ==============================================================================

class GPT2Tokenizer(PreTrainedTokenizer):
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path):
        target = GPT2Tokenizer()
        mode = AILIA_TOKENIZER_TYPE_GPT2
        flags = AILIA_TOKENIZER_FLAG_NONE
        target.dll.Create(target.instance, ctypes.c_int32(mode), ctypes.c_int32(flags))
        target.dll.OpenVocabFile(target.instance, os.path.join(pretrained_model_name_or_path, "vocab.json"))
        target.dll.OpenMergeFile(target.instance, os.path.join(pretrained_model_name_or_path, "merges.txt"))
        target._initialized = True
        target._pad_token_id = 50256 # PADではなくEOSでPADする
        target._sot_offset = 0 # sotはない
        target._eot_offset = 0 # eotはない
        return target

# ==============================================================================
# LLAMA
# ==============================================================================

class LlamaTokenizer(PreTrainedTokenizer):
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path):
        target = LlamaTokenizer()
        mode = AILIA_TOKENIZER_TYPE_LLAMA
        flags = AILIA_TOKENIZER_FLAG_NONE
        target.dll.Create(target.instance, ctypes.c_int32(mode), ctypes.c_int32(flags))
        target.dll.OpenModelFile(target.instance, os.path.join(pretrained_model_name_or_path, "tokenizer.model"))
        target._initialized = True
        target._pad_token_id = 0
        target._eot_offset = 0 # eotはない
        target._retain_sot = True
        return target
