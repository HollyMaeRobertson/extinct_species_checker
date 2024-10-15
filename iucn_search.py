import sys
import subprocess
import csv
from tsv_classes import Entry,Index


if len(sys.argv) != 3:
    print("\nusage:\npython2 " + sys.argv[0] + " file_to_search.tsv redlist_reference.csv\n")
    sys.exit()

file = sys.argv[1]
redlist_file = sys.argv[2]
outf = sys.argv[1][0:-4] + "_WITH-REDLIST.tsv"

counter = 0
multi_count = 0
multi_count_final = 0

with open(redlist_file, 'r') as f:
    redlist_index = f.readlines()[0].strip("\n\r").split(",")


scientificName = redlist_index.index("scientificName")
assessmentId_index = redlist_index.index("assessmentId")
redlistCategory_index = redlist_index.index("redlistCategory")
redlistCriteria_index = redlist_index.index("redlistCriteria")
criteriaVersion_index = redlist_index.index("criteriaVersion")
populationTrend_index = redlist_index.index("populationTrend")
scope_index = redlist_index.index("scopes")


lines = int(subprocess.check_output(["wc", "-l", file]).split()[0]) - 1


with open(file, 'r') as f:
    for line in f:

        # Progress tracker.
        percent = round(100*(float(counter)/float(lines)), 3)
        sys.stderr.write("reading " + str(percent) + "% complete.\r")
        
        # Make an index and/or entry for the current line.
        if counter == 0:
            file_index = Index(line)
            counter += 1
            with open(outf, 'w') as out:
                out.write(line.strip() + "\tinRedlist?\tassessmentId\tredlistCategory\tredlistCriteria\tpopulationTrend\tscopes\t\n")
            continue
        else:
            new = Entry(line, file_index)

        # Generate the search name.
        search_name = new.genus + " " + new.specific_epithet
         
        # If there is no search name (???) skip this line now!
        if search_name == " ":
            additions = ["unableToGenerateSearchName", "NA", "NA", "NA", "NA", "NA"]
            # aaaaaaaaaaaaaaaaaaaaaaaaaa

            outline = line.strip("\n") + "\t" + "\t".join(additions)
            with open(outf, "a") as out:
                out.write(outline + "\n")
            continue

        # Searching the redlist.
        try:
            redlist_entry = subprocess.check_output(["grep", "-F", search_name, redlist_file], text=True).split("\n")
        except:
            redlist_entry = [] 

        redlist_entry = list(filter(lambda x: x != "", redlist_entry))
        
        # Dealing with the rare case where there are multiple entries in the redlist.
        if len(redlist_entry) > 1:
            
            # Need to find the best entry of those returned.
            newlist = []
            for i in redlist_entry:
                entries = [j for j in csv.reader([i])]
                entries = entries[0]
                
                # criteria 
                # first of all how many of them actually have the right species
                if entries[scientificName] == search_name:
                    newlist.append(i)

            redlist_entry = newlist
            newlist = []

            if len(redlist_entry) > 1:
                multi_count += 1

                # next: global entries are better
                newlist = []
                for i in redlist_entry:
                    entries = [j for j in csv.reader([i])]
                    entries = entries[0]

                    if entries[scope_index] == "Global":
                        newlist.append(i)
                
                # (if none of them are global we just keep all the entries (handled further down))
                if len(newlist) > 0:
                    redlist_entry = newlist
                    newlist = []
                    

        # Now to actually write the output.
        if len(redlist_entry) == 1:
            
            # Grab the info from the redlist.
            entries = [j for j in csv.reader([redlist_entry[0]])]
            entries = entries[0]
            additions = ["inRedlist", entries[assessmentId_index], entries[redlistCategory_index], entries[redlistCriteria_index], entries[populationTrend_index], entries[scope_index]]
        
        elif len(redlist_entry) == 0:

            # Nothing in the redlist so we make a note and move on.
            additions = ["notInRedlist", "NA", "NA", "NA", "NA", "NA"]
            pass

        else:
            # This should be a rare case.
            multi_count_final += 1
            
            ids = []
            categories = []
            criterias = []
            trends = []
            scopes = []

            for i in redlist_entry:
                entries = [j for j in csv.reader([i])]
                entries = entries[0]
                ids.append(entries[assessmentId_index])
                categories.append(entries[redlistCategory_index])
                criterias.append(entries[redlistCriteria_index]) 
                trends.append(entries[populationTrend_index])
                scopes.append(entries[scope_index])

            additions = ["multiple redlist entries - semicolon-separated", ";".join(ids), ";".join(categories), ";".join(criterias), ";".join(trends), ";".join(scopes)]
        
        outline = line.strip("\n") + "\t" + "\t".join(additions)
        with open(outf, "a") as out:
            out.write(outline + "\n")

        counter += 1
