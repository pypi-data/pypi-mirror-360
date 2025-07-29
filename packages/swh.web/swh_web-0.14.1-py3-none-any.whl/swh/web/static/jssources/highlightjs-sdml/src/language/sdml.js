/*
  Language: Simple Domain Modeling Language (SDML)
  Author: Simon Johnston <johnstone@gmail.com>
  Description: language definition for the SDML language
  Website: https://sdml.io/
  Category: modelling
*/

sdml = function (hljs) {
    const IDENT = '[\p{Lu}\p{Ll}][\p{Lu}\p{Ll}\p{Nd}]*(?:_[\p{Lu}\p{Ll}\p{Nd}]+)*';
    const IDENTREF = IDENT + '(?::' + IDENT + ')?';
    const ANNIDENT = '@' + IDENTREF;
    var KEYWORDS = {
        keyword: 'as base datatype end entity enum event group ' +
            'identity import is module of property ref source ' +
            'structure union ' +
            // embedded constraint language
        'and assert def exists forall iff implies in not ;9uor ' +
            // sequence constraints
            'ordered unordered unique nonunique',
        type: 'boolean decimal double integer iri string unknown',
        literal: 'true false ⊥ ⊤'
    };
    var SELFS = {
        className: 'variable.language',
        begin: /[Ss]elf/
    };
    var PUNCTUATION = {
        className: 'punctuation',
        begin: /[\{\}\(\)\[\]]/,
    };
    var OPERATORS = {
        className: 'operator',
        begin: /=|<-|->|\.\.|:=|≔|¬|∧|∨|⊻|==>|⇒|∀|∃|∈/
    };
    var ANNOTATIONS = {
        className: 'attribute',
        begin: /@[\p{Lu}\p{Ll}][\p{Lu}\p{Ll}\p{Nd}]*(?:_[\p{Lu}\p{Ll}\p{Nd}]+)*(?::[\p{Lu}\p{Ll}][\p{Lu}\p{Ll}\p{Nd}]*(?:_[\p{Lu}\p{Ll}\p{Nd}]+)*)?/
    };
    var STRING = {
        className: 'string',
        contains: [hljs.BACKSLASH_ESCAPE],
        variants: [
            {
                begin: '"', end: '"',
                contains: [hljs.BACKSLASH_ESCAPE],
            },
            {
                begin: '\'', end: '\'',
                contains: [hljs.BACKSLASH_ESCAPE],
            }
        ]
    };
    var IRI = {// https://www.w3.org/TR/turtle/#grammar-production-IRIREF
        className: 'literal',
        relevance: 1,
        begin: /</,
        end: />/,
        illegal: /[^\x00-\x20<>"{}|^`]/,
    };
    var NUMBER = {
        className: 'number',
        begin: hljs.C_NUMBER_RE + 'n?',
        relevance: 0
    };

    return {
        name: 'sdml',
        case_insensitive: false,
        unicodeRegex: true,
        keywords: KEYWORDS,
        contains: [
            hljs.COMMENT(';', '$'),
            NUMBER,
            STRING,
            //IRI,
            SELFS,
            PUNCTUATION,
            OPERATORS,
            ANNOTATIONS
        ],
    }
}
