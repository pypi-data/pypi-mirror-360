from MorphologicalDisambiguation.MorphologicalDisambiguator cimport MorphologicalDisambiguator
from NGram.NGram cimport NGram


cdef class NaiveDisambiguation(MorphologicalDisambiguator):

    cdef NGram word_uni_gram_model
    cdef NGram ig_uni_gram_model

    cpdef saveModel(self)
    cpdef loadModel(self)
