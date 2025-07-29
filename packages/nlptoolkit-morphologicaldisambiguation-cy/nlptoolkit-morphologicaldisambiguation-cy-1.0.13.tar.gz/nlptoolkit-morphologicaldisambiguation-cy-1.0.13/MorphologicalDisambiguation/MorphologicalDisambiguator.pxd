from DisambiguationCorpus.DisambiguationCorpus cimport DisambiguationCorpus


cdef class MorphologicalDisambiguator:

    cpdef train(self, DisambiguationCorpus corpus)
    cpdef list disambiguate(self, list fsmParses)
    cpdef saveModel(self)
    cpdef loadModel(self)
