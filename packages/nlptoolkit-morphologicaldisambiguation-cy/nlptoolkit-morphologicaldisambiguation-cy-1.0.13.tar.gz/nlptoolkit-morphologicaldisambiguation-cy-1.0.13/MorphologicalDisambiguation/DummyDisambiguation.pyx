from random import randrange

from DisambiguationCorpus.DisambiguationCorpus cimport DisambiguationCorpus
from MorphologicalDisambiguation.MorphologicalDisambiguator cimport MorphologicalDisambiguator
from MorphologicalAnalysis.FsmParseList cimport FsmParseList


cdef class DummyDisambiguation(MorphologicalDisambiguator):

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
        Overridden disambiguate method takes an array of FsmParseList and loops through its items, if the current
        FsmParseList's size is greater than 0, it adds a random parse of this list to the correctFsmParses list.

        PARAMETERS
        ----------
        fsmParses : list
            FsmParseList to disambiguate.

        RETURNS
        -------
        list
            CorrectFsmParses list.
        """
        cdef list correct_fsm_parses
        cdef FsmParseList fsm_parse_list
        correct_fsm_parses = []
        for fsm_parse_list in fsmParses:
            if fsm_parse_list.size() > 0:
                correct_fsm_parses.append(fsm_parse_list.getFsmParse(randrange(fsm_parse_list.size())))
        return correct_fsm_parses
