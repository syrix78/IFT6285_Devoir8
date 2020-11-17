from nltk.corpus import treebank
from nltk import treetransforms
from nltk import induce_pcfg
from nltk.parse import pchart
from nltk import Nonterminal
from nltk import Production
from nltk.parse import ViterbiParser

train = treebank.fileids()[:190]
test = treebank.fileids()[190:]


def train_grammar(unknown_words=[]):

    productions = []

    for item in train:
        for tree in treebank.parsed_sents(item):
            # perform optional tree transformations, e.g.:
            tree.collapse_unary(collapsePOS=False)  # Remove branches A-B-C into A-B+C
            tree.chomsky_normal_form(horzMarkov=2)  # Remove A->(B,C,D) into A->B,C+D->D
            tree_prods = tree.productions()
            unknown_words_prods = []
            for u in unknown_words:
                rhs = [u]
                for p in tree_prods:
                    lhs = p._lhs
                    new_prod = Production(lhs, rhs)
                    unknown_words_prods.append(new_prod)

            productions += tree.productions()
            productions += unknown_words_prods



    S = Nonterminal('S')
    #print(productions)
    grammar = induce_pcfg(S, productions)


    return grammar

def get_fixed_grammer(grammar, tokens):
    missing = [tok for tok in tokens if not grammar._lexical_index.get(tok)]

    return train_grammar(missing)

def test_sentences(grammar):
    demos = ['I saw John with my telescope']
    sent = demos[0]

    for t in test:
        print("Processing: " + str(t))
        reference = list(treebank.tagged_words(t))


        tokens = list(treebank.words(t))



        # Tokenize the sentence.
        #tokens = sent.split()
        print("fixing grammar.....")
        # Checks if grammar covers all words in the sentence
        fixed_grammar = get_fixed_grammer(grammar, tokens)

        print("fixed grammar")
        print("Building Parser....")
        parser = ViterbiParser(fixed_grammar)

        print("Parsing...")
        #Gets list of all possible trees, the most likely tree is at index 0
        parses = parser.parse_all(tokens)
        leafs = parses[0].pos()

        correct_tags = 0.0
        for i in range(len(leafs)):
            if leafs[i] == reference[i]:
                correct_tags += 1.0


        print(str(correct_tags/len(leafs)))

if __name__ == "__main__":
    grammar = train_grammar()
    test_sentences(grammar)
    #print(grammar)
