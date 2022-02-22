import RAKE


def keyword_extract(message,
                    stopWordPath='/Users/sanjivjha/PycharmProjects/ContexualExplainerSystem/contextual_explainer/src/keywordExtraction/stop-words.txt',
                    custom_separator=None):
    keywords = []
    stop_words = stopWordPath
    rake_object = RAKE.Rake(stop_words)
    key_array = rake_object.run(message)

    # with open(stop_words, 'a+') as file:
    #     contents = file.read()
    #
    #     if not custom_separator in contents:
    #         print('word not found')
    #         file.write("\n"+custom_separator)

    for key in key_array:
        for k in key[0].split(' '):
            keywords.append(k)

    return set(keywords)
