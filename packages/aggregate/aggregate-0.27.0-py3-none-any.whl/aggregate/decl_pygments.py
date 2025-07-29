"""
pygments lexer for the Dec Language  using standard colorings.

"""


from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexer import RegexLexer, include,  words
from pygments.token import (Text, Comment, Operator, Keyword, Number,
                            Punctuation, Name, Generic)

__all__ = ['AggLexer']


class AggLexer(RegexLexer):
    """
    Aggregate program language lexer. (Based on Python lexer. )
    """

    name = 'Aggregate'
    aliases = ['aggregate', 'agg', 'decl', 'dec']
    filenames = ['*.agg', '*.dec', '*.decl']
    url = 'http://www.github.com/mynl/aggregate'
    version = '0.16.0'

    mimetypes = ['text/x-agg', 'text/x-aggregate', 'text/x-decl',
                 'text/x-dec']

    tokens = {

        'root': [
            (r'\n', Text),
            (r'\\\n', Text),
            (r'\\', Text),
            (r'note\{', Name.Type, 'note'),
            (r'\}', Name.Type),
            (r'#.*$', Comment),
            ('!', Generic.Heading),
            # these are for documenation
            # (r'\<|\>', Generic.Heading),
            # the regex for an ID from parser.py
            (r'mixed ', Operator, 'mixed_freq'),
            (r'and',  Generic.Heading),
            (r'splice',  Generic.Heading),
            (r'wts', Name.Type),
            include('numbers'),
            include('keywords'),
            include('expr'),
            # for the help
            (r'<[A-Z_0-9*]+>', Generic.Heading),
            # match ID in parser.py
            (r'[a-zA-Z][\._:~a-zA-Z0-9\-]*\b', Name),
        ],

        'note': [
            (r'[^\}]*', Comment, '#pop'),
            ],

        'mixed_freq': [
            (words(('gamma', 'delaporte', 'ig', 'sig', 'beta', 'sichel', "<DISTRIBUTION>"),
                   # last item is a hack for the AAS paper
                   suffix=' '
                   ), Name.Function, '#pop'),
            (r'sichel\.',  Name.Function)
        ],

        'expr': [
            (r'[^\S\n]+', Text),
            (r'!=|==|<<|>>|:=|[-~+/*%=<>&^|.]', Operator),
            (r'[]{}:(),;[]', Punctuation),
            (r'(in|is|and|or|not)\b', Operator.Word),
        ],

        'keywords': [
            # freq dists
            (words(
                ('binomial', 'pascal', 'poisson', 'bernoulli', 'geometric',
                    'fixed', 'neyman' 'neymana', 'neymanA', 'logarithmic',
                    'dfreq', 'negbin'),
                suffix=r'\b'
            ), Name.Function),

            # sev dists
            # zero param
            (words((
                'anglit', 'arcsine', 'cauchy', 'cosine', 'expon', 'gilbrat', 'gumbel_l',
                          'gumbel_r', 'halfcauchy', 'halflogistic', 'halfnorm', 'hypsecant',
                          'kstwobign', 'laplace', 'levy', 'levy_l', 'logistic', 'maxwell', 'moyal',
                          'norm', 'rayleigh', 'semicircular', 'uniform', 'wald'
            ),
                suffix=r'\b'
            ), Name.Function),
            # one param
            (words((
                'alpha', 'argus', 'bradford', 'chi', 'chi2', 'dgamma', 'dweibull', 'erlang',
                'exponnorm', 'exponpow', 'fatiguelife', 'fisk', 'foldcauchy', 'foldnorm',
                'gamma', 'genextreme', 'genhalflogistic', 'genlogistic', 'gennorm', 'genpareto',
                'gompertz', 'halfgennorm', 'invgamma', 'invgauss', 'invweibull', 'kappa3', 'ksone',
                'kstwo', 'laplace_asymmetric', 'loggamma', 'loglaplace', 'lognorm', 'lomax',
                'nakagami', 'pareto', 'pearson3', 'powerlaw', 'powernorm', 'rdist', 'recipinvgauss',
                'rice', 'skewcauchy', 'skewnorm', 't', 'triang', 'truncexpon', 'tukeylambda',
                'vonmises', 'vonmises_line', 'weibull_max', 'weibull_min', 'wrapcauchy'
            ),
                suffix=r'\b'
            ), Name.Class),
            # two param
            (words((
                'beta', 'betaprime', 'burr', 'burr12', 'crystalball', 'exponweib', 'f', 'gengamma',
                'geninvgauss', 'johnsonsb', 'johnsonsu', 'kappa4', 'levy_stable', 'loguniform',
                'mielke', 'nct', 'ncx2', 'norminvgauss', 'powerlognorm', 'reciprocal',
                          'studentized_range', 'trapezoid', 'trapz', 'truncnorm'
            ),
                suffix=r'\b'
            ), Name.Namespace),
            # historgram
            (words(('dhistogram', 'chistogram', 'dsev',
                    ),
                   suffix=r'\b'
                   ), Name.Label),

            # built in sev or agg dists pattern
            (r'(sev|agg)\.[a-zA-Z][a-zA-Z0-9._:~]*', Name.Builtin),

            # all IDs from the parser.py file
            (words(
                ('occurrence', 'distortion', 'unlimited', 'aggregate', 'exposure', 'tweedie',
                    'premium', 'tower', 'unlim', 'picks', 'prem',
                    'claims', 'ceded', 'claim', 'loss', 'dist',
                    'port', 'rate', 'net', 'sev', 'agg', 'xps', 'wts',
                    'inf', 'and', 'exp', 'wt', 'at', 'cv', 'lr', 'xs',
                    'of', 'to', 'po', 'so', 'zm', 'zt', 'x', ),
                suffix=r'\b'
            ), Keyword),
        ],

        'numbers': [
            (r'(\d(?:_?\d)*\.(?:\d(?:_?\d)*)?|(?:\d(?:_?\d)*)?\.\d(?:_?\d)*)'
                r'([eE][+-]?\d(?:_?\d)*)?', Number),
            (r'\d(?:_?\d)*[eE][+-]?\d(?:_?\d)*j?', Number),
            # current definition of number in parser.py
            (r'\-?(\d+\.?\d*|\d*\.\d+)([eE](\+|\-)?\d+)?%?|\-?inf', Number),
            (r'\d(?:_?\d)*', Number.Integer),
        ],
    }
