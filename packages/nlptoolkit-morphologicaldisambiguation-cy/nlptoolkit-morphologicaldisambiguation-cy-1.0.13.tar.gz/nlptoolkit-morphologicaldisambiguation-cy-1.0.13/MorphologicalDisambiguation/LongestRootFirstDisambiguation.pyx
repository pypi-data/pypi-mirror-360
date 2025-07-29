import pkg_resources
from MorphologicalDisambiguation.AutoDisambiguator import AutoDisambiguator
from DisambiguationCorpus.DisambiguationCorpus cimport DisambiguationCorpus
from MorphologicalDisambiguation.MorphologicalDisambiguator cimport MorphologicalDisambiguator
from MorphologicalAnalysis.FsmParseList cimport FsmParseList
from MorphologicalAnalysis.FsmParse cimport FsmParse


cdef class LongestRootFirstDisambiguation(MorphologicalDisambiguator):

    cdef dict root_list

    def __init__(self, fileName=None):
        """
        Constructor for the longest root first disambiguation algorithm. The method reads a list of (surface form, most
        frequent root word for that surface form) pairs from a given file.
        :param fileName: File that contains list of (surface form, most frequent root word for that surface form) pairs.
        """
        self.root_list = {}
        if fileName is None:
            self.__readFromFile(pkg_resources.resource_filename(__name__, 'data/rootlist.txt'))
        else:
            self.__readFromFile(fileName)

    cpdef __readFromFile(self, str fileName):
        """
        Reads the list of (surface form, most frequent root word for that surface form) pairs from a given file.
        :param fileName: Input file name.
        """
        cdef list lines
        cdef list word_list
        cdef str line
        input_file = open(fileName, "r", encoding="utf8")
        lines = input_file.readlines()
        for line in lines:
            word_list = line.split()
            if len(word_list) == 2:
                self.root_list[word_list[0]] = word_list[1]
        input_file.close()

    cpdef train(self, DisambiguationCorpus corpus):
        """
        Train method implements method in MorphologicalDisambiguator.

        PARAMETERS
        ----------
        corpus : DisambiguationCorpus
            DisambiguationCorpus to train.
        """
        pass

    cpdef list disambiguate(self, list fsmParses):
        """
        The disambiguate method gets an array of fsmParses. Then loops through that parses and finds the longest root
        word. At the end, gets the parse with longest word among the fsmParses and adds it to the correctFsmParses
        list.

        PARAMETERS
        ----------
        fsmParses : list
            FsmParseList to disambiguate.

        RETURNS
        -------
        list
            CorrectFsmParses list.
        """
        cdef int i
        cdef list correct_fsm_parses
        cdef FsmParseList fsm_parse_list
        cdef FsmParse best_parse, new_best_parse
        cdef str surface_form, best_root
        cdef bint root_found
        correct_fsm_parses = []
        i = 0
        for fsm_parse_list in fsmParses:
            surface_form = fsm_parse_list.getFsmParse(0).getSurfaceForm()
            best_root = None
            root_found = False
            if surface_form in self.root_list:
                best_root = self.root_list[surface_form]
                for j in range(fsm_parse_list.size()):
                    if fsm_parse_list.getFsmParse(j).getWord().getName() == best_root:
                        root_found = True
            if best_root is None or not root_found:
                best_parse = fsm_parse_list.getParseWithLongestRootWord()
                fsm_parse_list.reduceToParsesWithSameRoot(best_parse.getWord().getName())
            else:
                fsm_parse_list.reduceToParsesWithSameRoot(best_root)
            new_best_parse = AutoDisambiguator.caseDisambiguator(i, fsmParses, correct_fsm_parses)
            if new_best_parse is not None:
                best_parse = new_best_parse
            else:
                best_parse = fsm_parse_list.getFsmParse(0)
            correct_fsm_parses.append(best_parse)
            i = i + 1
        return correct_fsm_parses

    cpdef saveModel(self):
        pass

    cpdef loadModel(self):
        pass
