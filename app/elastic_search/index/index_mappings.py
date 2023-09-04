default_mapping = {
    'properties': {
        'bases': {
            'type': 'text',
            'search_analyzer': 'ngram_search_analyzer'
        },
        'name': {
            'type': 'text'
        },
        'createdAt': {
            'type': 'date'
        },
        'creator': {
            'properties': {
                'id': {
                    'type': 'keyword'
                },
                'name': {
                    'type': 'text'
                },
                'handle': {
                    'type': 'text'
                }
            }
        }
    }
}