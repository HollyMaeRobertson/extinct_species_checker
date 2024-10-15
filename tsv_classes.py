#classes for tsv files, dependency for iucn_search.py

class Entry:
    def __init__(self, line, file_index):

        entries = line.strip("\n").split("\t")

        self.genus = entries[file_index.genus]
        self.subgenus = entries[file_index.subgenus]
        self.specific_epithet = entries[file_index.specific_epithet]
        self.species_name = entries[file_index.species_name]
        self.infraspecies = entries[file_index.infraspecies]
        if file_index.organism_name:
            self.organism_name = entries[file_index.organism_name]
        self.has_subspecies = False
        self.subspecies = ""
        if file_index.prep:
            self.prep = entries[file_index.prep]

class Index:
    def __init__(self, line):

        entries = line.strip("\n").split("\t")
        try:
            self.prep = entries.index("preparations")
        except: 
            self.prep = None
        self.genus = entries.index("genus")
        self.subgenus = entries.index("subgenus")
        self.specific_epithet = entries.index("specificEpithet")
        self.species_name = entries.index("scientificName")
        self.infraspecies = entries.index("infraspecificEpithet")
        try:
            self.organism_name = entries.index("organismName")
        except:
            self.organism_name = None
        self.record = entries.index("basisOfRecord")
