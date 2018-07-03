# TOPOTAGGER
Subcorpus for personal research

# REPORT STRUCTURE
#  0 : match          - complete match as a key
#  1 : display        - reformatted match for display
#  2 : ng1            - ngrams (tagged-3)
#  3 : ng2            - ngrams (tagged-2)
#  4 : ng3            - ngrams (tagged-1)
#  5 : tagged (ng4)   - ngrams (tagged-0)
#  6 : ng5            - ngrams (tagged+1)
#  7 : ng6            - ngrams (tagged+2)
#  8 : ng7            - ngrams (tagged+3)
#  9 : "status"       - status of review
# 10 : "probability"  - probabilities, based on ngram extrapolations
# 11 : "ngram"        - ngrams (numbers), for matches exclude/include
# 12 : "position"     - position in the text broken into list on space
# 13 : "middleTag"    - tagged item as it appears in the text
# 14 : "gazForm"      - gazetteer form of an item


# Auto-tagger

The idea: take a gazetteer (of terms, phrases, etc.) and tag their occurrences in a text;

# Files

## TopDesc

1. Exclude R, if there is a S with the same name
2. Otherwise, keep other regions

# Algorithm

1. **TopDesc** > **Tagging Dictionary**
	1. convert into a tagging dictionary
	2. if there are homonyms, combine URIs into the TAG
		1. i.e., first, build a dictionary, with a denormalized forms as keys
		2. this will allow appending URIs
	3. apply long tags (@TOPX1:URI[:URI]+_entity)
	3. reorder the dictionary into a List of lists, as a List can be ordered to have longer items first
		1. length of an entity in words
		2. search word
			1. denormalize
		3. tag to replace 2 with
			1. generate multiple lines for lemma versions and for words with prefixes
2. **Text** [A text tagged in detail does not need Milestone tags; this should also be a version with an ID of a tagger: any text changes are allowed here]
	1. Check if a report exists:
		1. if not, create an empty one; load an empty file
		2. if yes, load the report
	2. Load the text:
		1. Split header from the text
		2. Combine broken lines into strings
	3. Start tagging
		1. loop through the tagging list
		2. find all instances > list(set(list(res)))
		3. loop through instances:
			1. first, check the report file:
				1. if there, move to the next one
				2. if not, tag in the text
	4. After tagging, update the report:
		1. loop through the report
		2. search and count instances of tagged
		3. update numbers
		4. AutoTagged, False Positives, True Positives, TAG (since the longest, put TAG the end)
	5. Upon completion, save a **report** into a file with a name "Text.Gazetteer"
	6. Save **Text**.
3. **Report** format
	1. a CSV file with the following (CE -- current count during the reload/rerun)
		1. # of autotagged entities (AE)
		2. # of true positives (CE)
		3. # of false positives (AE-CE)
		4. the TAG
4. **Extrapolator**
	1. Manually tag some entities in the text [TAG@TOPXX@NOURI#]
	2. ...
5. **Verifier** *&* **DataCollector**
	1. A script that loads an autotagged file and loops through tags, showing them in context and allowing one to choose whether it is false or true; also collects ngram data on false positives, that can be used later to disambiguate false/true automatically.
	2. *Steps*:
	3. Find all autotags @TOP@ (manual, or disambiguated > @T@) + 3 words before and three words after (if possible).
	4. Loop through the results and show one by one
	5.
	3. [+2] [+1] [0] [-1] [-2]
	4. [Options to save a string]
