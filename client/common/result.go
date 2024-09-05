package common

type DrawResult struct {
	winners []string
}

// DrawResultFromDocuments Initializes a new draw result from a list of documents
func DrawResultFromDocuments(documents []string) *DrawResult {
	return &DrawResult{
		winners: documents,
	}
}

// winnerCount Returns the number of winners
func (dr *DrawResult) winnerCount() int {
	return len(dr.winners)
}
