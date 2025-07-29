import clr
clr.AddReference("System")

from NaxToPy.Core.Reference_Finder.__Reference_Finder import __reference_finder

if __name__ == 'NaxToPy.Core':
    __reference_finder()
