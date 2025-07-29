cdef class MorphologicalDisambiguator:

    cpdef train(self, DisambiguationCorpus corpus):
        """
        Method to train the given DisambiguationCorpus.

        PARAMETERS
        ----------
        corpus : DisambiguationCorpus
            DisambiguationCorpus to train.
        """
        pass

    cpdef list disambiguate(self, list fsmParses):
        """
        Method to disambiguate the given FsmParseList.

        PARAMETERS
        ----------
        fsmParses : list
            FsmParseList to disambiguate.

        RETURNS
        -------
        list
            List of FsmParse.
        """
        pass

    cpdef saveModel(self):
        """
        Method to save a model.
        """
        pass

    cpdef loadModel(self):
        """
        Method to load a model.
        """
        pass
