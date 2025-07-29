from MorphologicalAnalysis.FsmMorphologicalAnalyzer cimport FsmMorphologicalAnalyzer
from MorphologicalAnalysis.FsmParse cimport FsmParse


cdef class AutoDisambiguator:

    cdef FsmMorphologicalAnalyzer morphological_analyzer
