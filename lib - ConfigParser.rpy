# Это чуть изменённый пакет работы с ini-файлами из дистрибутива Питона.
init python:
    #
    # Secret Labs' Regular Expression Engine
    #
    # re-compatible interface for the sre matching engine
    #
    # Copyright (c) 1998-2001 by Secret Labs AB.  All rights reserved.
    #
    # This version of the SRE library can be redistributed under CNRI's
    # Python 1.6 license.  For any other use, please contact Secret Labs
    # AB (info@pythonware.com).
    #
    # Portions of this engine have been developed in cooperation with
    # CNRI.  Hewlett-Packard provided funding for 1.6 integration and
    # other compatibility work.
    #

    r"""Support for regular expressions (RE).

    This module provides regular expression matching operations similar to
    those found in Perl.  It supports both 8-bit and Unicode strings; both
    the pattern and the strings being processed can contain null bytes and
    characters outside the US ASCII range.

    Regular expressions can contain both special and ordinary characters.
    Most ordinary characters, like "A", "a", or "0", are the simplest
    regular expressions; they simply match themselves.  You can
    concatenate ordinary characters, so last matches the string 'last'.

    The special characters are:
        "."      Matches any character except a newline.
        "^"      Matches the start of the string.
        "$"      Matches the end of the string or just before the newline at
                 the end of the string.
        "*"      Matches 0 or more (greedy) repetitions of the preceding RE.
                 Greedy means that it will match as many repetitions as possible.
        "+"      Matches 1 or more (greedy) repetitions of the preceding RE.
        "?"      Matches 0 or 1 (greedy) of the preceding RE.
        *?,+?,?? Non-greedy versions of the previous three special characters.
        {m,n}    Matches from m to n repetitions of the preceding RE.
        {m,n}?   Non-greedy version of the above.
        "\\"     Either escapes special characters or signals a special sequence.
        []       Indicates a set of characters.
                 A "^" as the first character indicates a complementing set.
        "|"      A|B, creates an RE that will match either A or B.
        (...)    Matches the RE inside the parentheses.
                 The contents can be retrieved or matched later in the string.
        (?iLmsux) Set the I, L, M, S, U, or X flag for the RE (see below).
        (?:...)  Non-grouping version of regular parentheses.
        (?P<name>...) The substring matched by the group is accessible by name.
        (?P=name)     Matches the text matched earlier by the group named name.
        (?#...)  A comment; ignored.
        (?=...)  Matches if ... matches next, but doesn't consume the string.
        (?!...)  Matches if ... doesn't match next.
        (?<=...) Matches if preceded by ... (must be fixed length).
        (?<!...) Matches if not preceded by ... (must be fixed length).
        (?(id/name)yes|no) Matches yes pattern if the group with id/name matched,
                           the (optional) no pattern otherwise.

    The special sequences consist of "\\" and a character from the list
    below.  If the ordinary character is not on the list, then the
    resulting RE will match the second character.
        \number  Matches the contents of the group of the same number.
        \A       Matches only at the start of the string.
        \Z       Matches only at the end of the string.
        \b       Matches the empty string, but only at the start or end of a word.
        \B       Matches the empty string, but not at the start or end of a word.
        \d       Matches any decimal digit; equivalent to the set [0-9].
        \D       Matches any non-digit character; equivalent to the set [^0-9].
        \s       Matches any whitespace character; equivalent to [ \t\n\r\f\v].
        \S       Matches any non-whitespace character; equiv. to [^ \t\n\r\f\v].
        \w       Matches any alphanumeric character; equivalent to [a-zA-Z0-9_].
                 With LOCALE, it will match the set [0-9_] plus characters defined
                 as letters for the current locale.
        \W       Matches the complement of \w.
        \\       Matches a literal backslash.

    This module exports the following functions:
        match    Match a regular expression pattern to the beginning of a string.
        search   Search a string for the presence of a pattern.
        sub      Substitute occurrences of a pattern found in a string.
        subn     Same as sub, but also return the number of substitutions made.
        split    Split a string by the occurrences of a pattern.
        findall  Find all occurrences of a pattern in a string.
        finditer Return an iterator yielding a match object for each match.
        compile  Compile a pattern into a RegexObject.
        purge    Clear the regular expression cache.
        escape   Backslash all non-alphanumerics in a string.

    Some of the functions in this module takes flags as optional parameters:
        I  IGNORECASE  Perform case-insensitive matching.
        L  LOCALE      Make \w, \W, \b, \B, dependent on the current locale.
        M  MULTILINE   "^" matches the beginning of lines (after a newline)
                       as well as the string.
                       "$" matches the end of lines (before a newline) as well
                       as the end of the string.
        S  DOTALL      "." matches any character at all, including the newline.
        X  VERBOSE     Ignore whitespace and comments for nicer looking RE's.
        U  UNICODE     Make \w, \W, \b, \B, dependent on the Unicode locale.

    This module also defines an exception 'error'.

    """

    import sys
    import sre_compile
    import sre_parse

    # public symbols
    __all__ = [ "match", "search", "sub", "subn", "split", "findall",
        "compile", "purge", "template", "escape", "I", "L", "M", "S", "X",
        "U", "IGNORECASE", "LOCALE", "MULTILINE", "DOTALL", "VERBOSE",
        "UNICODE", "error" ]

    __version__ = "2.2.1"

    # flags
    I = IGNORECASE = sre_compile.SRE_FLAG_IGNORECASE # ignore case
    L = LOCALE = sre_compile.SRE_FLAG_LOCALE # assume current 8-bit locale
    U = UNICODE = sre_compile.SRE_FLAG_UNICODE # assume unicode locale
    M = MULTILINE = sre_compile.SRE_FLAG_MULTILINE # make anchors look for newline
    S = DOTALL = sre_compile.SRE_FLAG_DOTALL # make dot match newline
    X = VERBOSE = sre_compile.SRE_FLAG_VERBOSE # ignore whitespace and comments

    # sre extensions (experimental, don't rely on these)
    T = TEMPLATE = sre_compile.SRE_FLAG_TEMPLATE # disable backtracking
    DEBUG = sre_compile.SRE_FLAG_DEBUG # dump pattern after compilation

    # sre exception
    error = sre_compile.error

    # --------------------------------------------------------------------
    # public interface

    def match(pattern, string, flags=0):
        """Try to apply the pattern at the start of the string, returning
        a match object, or None if no match was found."""
        return _compile(pattern, flags).match(string)

    def search(pattern, string, flags=0):
        """Scan through string looking for a match to the pattern, returning
        a match object, or None if no match was found."""
        return _compile(pattern, flags).search(string)

    def sub(pattern, repl, string, count=0):
        """Return the string obtained by replacing the leftmost
        non-overlapping occurrences of the pattern in string by the
        replacement repl.  repl can be either a string or a callable;
        if a string, backslash escapes in it are processed.  If it is
        a callable, it's passed the match object and must return
        a replacement string to be used."""
        return _compile(pattern, 0).sub(repl, string, count)

    def subn(pattern, repl, string, count=0):
        """Return a 2-tuple containing (new_string, number).
        new_string is the string obtained by replacing the leftmost
        non-overlapping occurrences of the pattern in the source
        string by the replacement repl.  number is the number of
        substitutions that were made. repl can be either a string or a
        callable; if a string, backslash escapes in it are processed.
        If it is a callable, it's passed the match object and must
        return a replacement string to be used."""
        return _compile(pattern, 0).subn(repl, string, count)

    def split(pattern, string, maxsplit=0):
        """Split the source string by the occurrences of the pattern,
        returning a list containing the resulting substrings."""
        return _compile(pattern, 0).split(string, maxsplit)

    def findall(pattern, string, flags=0):
        """Return a list of all non-overlapping matches in the string.

        If one or more groups are present in the pattern, return a
        list of groups; this will be a list of tuples if the pattern
        has more than one group.

        Empty matches are included in the result."""
        return _compile(pattern, flags).findall(string)

    if sys.hexversion >= 0x02020000:
        __all__.append("finditer")
        def finditer(pattern, string, flags=0):
            """Return an iterator over all non-overlapping matches in the
            string.  For each match, the iterator returns a match object.

            Empty matches are included in the result."""
            return _compile(pattern, flags).finditer(string)

    def compile(pattern, flags=0):
        "Compile a regular expression pattern, returning a pattern object."
        return _compile(pattern, flags)

    def purge():
        "Clear the regular expression cache"
        _cache.clear()
        _cache_repl.clear()

    def template(pattern, flags=0):
        "Compile a template pattern, returning a pattern object"
        return _compile(pattern, flags|T)

    _alphanum = {}
    for c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890':
        _alphanum[c] = 1
    del c

    def escape(pattern):
        "Escape all non-alphanumeric characters in pattern."
        s = list(pattern)
        alphanum = _alphanum
        for i in range(len(pattern)):
            c = pattern[i]
            if c not in alphanum:
                if c == "\000":
                    s[i] = "\\000"
                else:
                    s[i] = "\\" + c
        return pattern[:0].join(s)

    # --------------------------------------------------------------------
    # internals

    _cache = {}
    _cache_repl = {}

    _pattern_type = type(sre_compile.compile("", 0))

    _MAXCACHE = 100

    def _compile(*key):
        # internal: compile pattern
        cachekey = (type(key[0]),) + key
        p = _cache.get(cachekey)
        if p is not None:
            return p
        pattern, flags = key
        if isinstance(pattern, _pattern_type):
            if flags:
                raise ValueError('Cannot process flags argument with a compiled pattern')
            return pattern
        if not sre_compile.isstring(pattern):
            raise TypeError, "first argument must be string or compiled pattern"
        try:
            p = sre_compile.compile(pattern, flags)
        except error, v:
            raise error, v # invalid expression
        if len(_cache) >= _MAXCACHE:
            _cache.clear()
        _cache[cachekey] = p
        return p

    def _compile_repl(*key):
        # internal: compile replacement pattern
        p = _cache_repl.get(key)
        if p is not None:
            return p
        repl, pattern = key
        try:
            p = sre_parse.parse_template(repl, pattern)
        except error, v:
            raise error, v # invalid expression
        if len(_cache_repl) >= _MAXCACHE:
            _cache_repl.clear()
        _cache_repl[key] = p
        return p

    def _expand(pattern, match, template):
        # internal: match.expand implementation hook
        template = sre_parse.parse_template(template, pattern)
        return sre_parse.expand_template(template, match)

    def _subx(pattern, template):
        # internal: pattern.sub/subn implementation helper
        template = _compile_repl(template, pattern)
        if not template[0] and len(template[1]) == 1:
            # literal replacement
            return template[1][0]
        def filter(match, template=template):
            return sre_parse.expand_template(template, match)
        return filter

    # register myself for pickling

    import copy_reg

    def _pickle(p):
        return _compile, (p.pattern, p.flags)

    copy_reg.pickle(_pattern_type, _pickle, _compile)

    # --------------------------------------------------------------------
    # experimental stuff (see python-dev discussions for details)

    class Scanner:
        def __init__(self, lexicon, flags=0):
            from sre_constants import BRANCH, SUBPATTERN
            self.lexicon = lexicon
            # combine phrases into a compound pattern
            p = []
            s = sre_parse.Pattern()
            s.flags = flags
            for phrase, action in lexicon:
                p.append(sre_parse.SubPattern(s, [
                    (SUBPATTERN, (len(p)+1, sre_parse.parse(phrase, flags))),
                    ]))
            s.groups = len(p)+1
            p = sre_parse.SubPattern(s, [(BRANCH, (None, p))])
            self.scanner = sre_compile.compile(p)
        def scan(self, string):
            result = []
            append = result.append
            match = self.scanner.scanner(string).match
            i = 0
            while 1:
                m = match()
                if not m:
                    break
                j = m.end()
                if i == j:
                    break
                action = self.lexicon[m.lastindex-1][1]
                if hasattr(action, '__call__'):
                    self.match = m
                    action = action(self, m.group())
                if action is not None:
                    append(action)
                i = j
            return result, string[i:]


    __all__ = ["NoSectionError", "DuplicateSectionError", "NoOptionError",
               "InterpolationError", "InterpolationDepthError",
               "InterpolationSyntaxError", "ParsingError",
               "MissingSectionHeaderError",
               "ConfigParser", "SafeConfigParser", "RawConfigParser",
               "DEFAULTSECT", "MAX_INTERPOLATION_DEPTH"]

    DEFAULTSECT = "DEFAULT"

    MAX_INTERPOLATION_DEPTH = 10



    # exception classes
    class Error(Exception):
        """Base class for ConfigParser exceptions."""

        def _get_message(self):
            """Getter for 'message'; needed only to override deprecation in
            BaseException."""
            return self.__message

        def _set_message(self, value):
            """Setter for 'message'; needed only to override deprecation in
            BaseException."""
            self.__message = value

        # BaseException.message has been deprecated since Python 2.6.  To prevent
        # DeprecationWarning from popping up over this pre-existing attribute, use
        # a new property that takes lookup precedence.
        message = property(_get_message, _set_message)

        def __init__(self, msg=''):
            self.message = msg
            Exception.__init__(self, msg)

        def __repr__(self):
            return self.message

        __str__ = __repr__

    class NoSectionError(Error):
        """Raised when no section matches a requested option."""

        def __init__(self, section):
            Error.__init__(self, 'No section: %r' % (section,))
            self.section = section

    class DuplicateSectionError(Error):
        """Raised when a section is multiply-created."""

        def __init__(self, section):
            Error.__init__(self, "Section %r already exists" % section)
            self.section = section

    class NoOptionError(Error):
        """A requested option was not found."""

        def __init__(self, option, section):
            Error.__init__(self, "No option %r in section: %r" %
                           (option, section))
            self.option = option
            self.section = section

    class InterpolationError(Error):
        """Base class for interpolation-related exceptions."""

        def __init__(self, option, section, msg):
            Error.__init__(self, msg)
            self.option = option
            self.section = section

    class InterpolationMissingOptionError(InterpolationError):
        """A string substitution required a setting which was not available."""

        def __init__(self, option, section, rawval, reference):
            msg = ("Bad value substitution:\n"
                   "\tsection: [%s]\n"
                   "\toption : %s\n"
                   "\tkey    : %s\n"
                   "\trawval : %s\n"
                   % (section, option, reference, rawval))
            InterpolationError.__init__(self, option, section, msg)
            self.reference = reference

    class InterpolationSyntaxError(InterpolationError):
        """Raised when the source text into which substitutions are made
        does not conform to the required syntax."""

    class InterpolationDepthError(InterpolationError):
        """Raised when substitutions are nested too deeply."""

        def __init__(self, option, section, rawval):
            msg = ("Value interpolation too deeply recursive:\n"
                   "\tsection: [%s]\n"
                   "\toption : %s\n"
                   "\trawval : %s\n"
                   % (section, option, rawval))
            InterpolationError.__init__(self, option, section, msg)

    class ParsingError(Error):
        """Raised when a configuration file does not follow legal syntax."""

        def __init__(self, filename):
            Error.__init__(self, 'File contains parsing errors: %s' % filename)
            self.filename = filename
            self.errors = []

        def append(self, lineno, line):
            self.errors.append((lineno, line))
            self.message += '\n\t[line %2d]: %s' % (lineno, line)

    class MissingSectionHeaderError(ParsingError):
        """Raised when a key-value pair is found before any section header."""

        def __init__(self, filename, lineno, line):
            Error.__init__(
                self,
                'File contains no section headers.\nfile: %s, line: %d\n%r' %
                (filename, lineno, line))
            self.filename = filename
            self.lineno = lineno
            self.line = line


    class RawConfigParser:
        def __init__(self, defaults=None, dict_type=dict):
            self._dict = dict_type
            self._sections = self._dict()
            self._defaults = self._dict()
            if defaults:
                for key, value in defaults.items():
                    self._defaults[self.optionxform(key)] = value

        def defaults(self):
            return self._defaults

        def sections(self):
            """Return a list of section names, excluding [DEFAULT]"""
            # self._sections will never have [DEFAULT] in it
            return self._sections.keys()

        def add_section(self, section):
            """Create a new section in the configuration.

            Raise DuplicateSectionError if a section by the specified name
            already exists. Raise ValueError if name is DEFAULT or any of it's
            case-insensitive variants.
            """
            if section.lower() == "default":
                raise ValueError, 'Invalid section name: %s' % section

            if section in self._sections:
                raise DuplicateSectionError(section)
            self._sections[section] = self._dict()

        def has_section(self, section):
            """Indicate whether the named section is present in the configuration.

            The DEFAULT section is not acknowledged.
            """
            return section in self._sections

        def options(self, section):
            """Return a list of option names for the given section name."""
            try:
                opts = self._sections[section].copy()
            except KeyError:
                raise NoSectionError(section)
            opts.update(self._defaults)
            if '__name__' in opts:
                del opts['__name__']
            return opts.keys()

        def read(self, filenames):
            """Read and parse a filename or a list of filenames.

            Files that cannot be opened are silently ignored; this is
            designed so that you can specify a list of potential
            configuration file locations (e.g. current directory, user's
            home directory, systemwide directory), and all existing
            configuration files in the list will be read.  A single
            filename may also be given.

            Return list of successfully read files.
            """
            if isinstance(filenames, basestring):
                filenames = [filenames]
            read_ok = []
            for filename in filenames:
                try:
                    fp = open(filename)
                except IOError:
                    raise
                    #continue
                self._read(fp, filename)
                fp.close()
                read_ok.append(filename)
            return read_ok

        def readfp(self, fp, filename=None):
            """Like read() but the argument must be a file-like object.

            The `fp' argument must have a `readline' method.  Optional
            second argument is the `filename', which if not given, is
            taken from fp.name.  If fp has no `name' attribute, `<???>' is
            used.

            """
            if filename is None:
                try:
                    filename = fp.name
                except AttributeError:
                    filename = '<???>'
            self._read(fp, filename)

        def get(self, section, option):
            opt = self.optionxform(option)
            if section not in self._sections:
                if section != DEFAULTSECT:
                    raise NoSectionError(section)
                if opt in self._defaults:
                    return self._defaults[opt]
                else:
                    raise NoOptionError(option, section)
            elif opt in self._sections[section]:
                return self._sections[section][opt]
            elif opt in self._defaults:
                return self._defaults[opt]
            else:
                raise NoOptionError(option, section)

        def items(self, section):
            try:
                d2 = self._sections[section]
            except KeyError:
                if section != DEFAULTSECT:
                    raise NoSectionError(section)
                d2 = self._dict()
            d = self._defaults.copy()
            d.update(d2)
            if "__name__" in d:
                del d["__name__"]
            return d.items()

        def _get(self, section, conv, option):
            return conv(self.get(section, option))

        def getint(self, section, option):
            return self._get(section, int, option)

        def getfloat(self, section, option):
            return self._get(section, float, option)

        _boolean_states = {'1': True, 'yes': True, 'true': True, 'on': True,
                           '0': False, 'no': False, 'false': False, 'off': False}

        def getboolean(self, section, option):
            v = self.get(section, option)
            if v.lower() not in self._boolean_states:
                raise ValueError, 'Not a boolean: %s' % v
            return self._boolean_states[v.lower()]

        def optionxform(self, optionstr):
            return optionstr.lower()

        def has_option(self, section, option):
            """Check for the existence of a given option in a given section."""
            if not section or section == DEFAULTSECT:
                option = self.optionxform(option)
                return option in self._defaults
            elif section not in self._sections:
                return False
            else:
                option = self.optionxform(option)
                return (option in self._sections[section]
                        or option in self._defaults)

        def set(self, section, option, value):
            """Set an option."""
            if not section or section == DEFAULTSECT:
                sectdict = self._defaults
            else:
                try:
                    sectdict = self._sections[section]
                except KeyError:
                    raise NoSectionError(section)
            sectdict[self.optionxform(option)] = value

        def write(self, fp):
            """Write an .ini-format representation of the configuration state."""
            if self._defaults:
                fp.write("[%s]\n" % DEFAULTSECT)
                for (key, value) in self._defaults.items():
                    fp.write("%s = %s\n" % (key, str(value).replace('\n', '\n\t')))
                fp.write("\n")
            for section in self._sections:
                fp.write("[%s]\n" % section)
                for (key, value) in self._sections[section].items():
                    if key != "__name__":
                        fp.write("%s = %s\n" %
                                 (key, str(value).replace('\n', '\n\t')))
                fp.write("\n")

        def remove_option(self, section, option):
            """Remove an option."""
            if not section or section == DEFAULTSECT:
                sectdict = self._defaults
            else:
                try:
                    sectdict = self._sections[section]
                except KeyError:
                    raise NoSectionError(section)
            option = self.optionxform(option)
            existed = option in sectdict
            if existed:
                del sectdict[option]
            return existed

        def remove_section(self, section):
            """Remove a file section."""
            existed = section in self._sections
            if existed:
                del self._sections[section]
            return existed

        #
        # Regular expressions for parsing section headers and options.
        #
        SECTCRE = compile(
            r'\['                                 # [
            r'(?P<header>[^]]+)'                  # very permissive!
            r'\]'                                 # ]
            )
        OPTCRE = compile(
            r'(?P<option>[^:=\s][^:=]*)'          # very permissive!
            r'\s*(?P<vi>[:=])\s*'                 # any number of space/tab,
                                                  # followed by separator
                                                  # (either : or =), followed
                                                  # by any # space/tab
            r'(?P<value>.*)$'                     # everything up to eol
            )

        def _read(self, fp, fpname):
            """Parse a sectioned setup file.

            The sections in setup file contains a title line at the top,
            indicated by a name in square brackets (`[]'), plus key/value
            options lines, indicated by `name: value' format lines.
            Continuations are represented by an embedded newline then
            leading whitespace.  Blank lines, lines beginning with a '#',
            and just about everything else are ignored.
            """
            cursect = None                            # None, or a dictionary
            optname = None
            lineno = 0
            e = None                                  # None, or an exception
            while True:
                line = fp.readline()
                if not line:
                    break
                lineno = lineno + 1
                # comment or blank line?
                if line.strip() == '' or line[0] in '#;':
                    continue
                if line.split(None, 1)[0].lower() == 'rem' and line[0] in "rR":
                    # no leading whitespace
                    continue
                    
                # open_bracket = line.find('[')    
                # if open_bracket is not -1:
                    # file = open(config.gamedir +"\\"+"parser.log","a")
                    # file.write(line+"\n")
                    # file.write(line[open_bracket:]+"\n")
                    # file.close()
                    # line = line[open_bracket:]
                    #(line.find(']'))
                    
                # continuation line?
                if line[0].isspace() and cursect is not None and optname:
                    value = line.strip()
                    if value:
                        cursect[optname] = "%s\n%s" % (cursect[optname], value)
                # a section header or option header?
                else:
                    # is it a section header?
                    mo = self.SECTCRE.match(line)
                    if mo:
                        sectname = mo.group('header')
                        if sectname in self._sections:
                            cursect = self._sections[sectname]
                        elif sectname == DEFAULTSECT:
                            cursect = self._defaults
                        else:
                            cursect = self._dict()
                            cursect['__name__'] = sectname
                            self._sections[sectname] = cursect
                        # So sections can't start with a continuation line
                        optname = None
                    # no section header in the file?
                    elif cursect is None:
                        #raise MissingSectionHeaderError(fpname, lineno, line)
                        continue
                    # an option line?
                    else:
                        mo = self.OPTCRE.match(line)
                        if mo:
                            optname, vi, optval = mo.group('option', 'vi', 'value')
                            if vi in ('=', ':') and ';' in optval:
                                # ';' is a comment delimiter only if it follows
                                # a spacing character
                                pos = optval.find(';')
                                if pos != -1 and optval[pos-1].isspace():
                                    optval = optval[:pos]
                            optval = optval.strip()
                            # allow empty values
                            if optval == '""':
                                optval = ''
                            optname = self.optionxform(optname.rstrip())
                            cursect[optname] = optval
                        else:
                            # a non-fatal parsing error occurred.  set up the
                            # exception but keep going. the exception will be
                            # raised at the end of the file and will contain a
                            # list of all bogus lines
                            if not e:
                                e = ParsingError(fpname)
                            e.append(lineno, repr(line))
            # if any parsing errors occurred, raise an exception
            if e:
                raise e


    class ConfigParser(RawConfigParser):

        def get(self, section, option, raw=False, vars=None):
            """Get an option value for a given section.

            All % interpolations are expanded in the return values, based on the
            defaults passed into the constructor, unless the optional argument
            `raw' is true.  Additional substitutions may be provided using the
            `vars' argument, which must be a dictionary whose contents overrides
            any pre-existing defaults.

            The section DEFAULT is special.
            """
            d = self._defaults.copy()
            try:
                d.update(self._sections[section])
            except KeyError:
                if section != DEFAULTSECT:
                    raise NoSectionError(section)
            # Update with the entry specific variables
            if vars:
                for key, value in vars.items():
                    d[self.optionxform(key)] = value
            option = self.optionxform(option)
            try:
                value = d[option]
            except KeyError:
                raise NoOptionError(option, section)

            if raw:
                return value
            else:
                return self._interpolate(section, option, value, d)

        def items(self, section, raw=False, vars=None):
            """Return a list of tuples with (name, value) for each option
            in the section.

            All % interpolations are expanded in the return values, based on the
            defaults passed into the constructor, unless the optional argument
            `raw' is true.  Additional substitutions may be provided using the
            `vars' argument, which must be a dictionary whose contents overrides
            any pre-existing defaults.

            The section DEFAULT is special.
            """
            d = self._defaults.copy()
            try:
                d.update(self._sections[section])
            except KeyError:
                if section != DEFAULTSECT:
                    raise NoSectionError(section)
            # Update with the entry specific variables
            if vars:
                for key, value in vars.items():
                    d[self.optionxform(key)] = value
            options = d.keys()
            if "__name__" in options:
                options.remove("__name__")
            if raw:
                return [(option, d[option])
                        for option in options]
            else:
                return [(option, self._interpolate(section, option, d[option], d))
                        for option in options]

        def _interpolate(self, section, option, rawval, vars):
            # do the string interpolation
            value = rawval
            depth = MAX_INTERPOLATION_DEPTH
            while depth:                    # Loop through this until it's done
                depth -= 1
                if "%(" in value:
                    value = self._KEYCRE.sub(self._interpolation_replace, value)
                    try:
                        value = value % vars
                    except KeyError, e:
                        raise InterpolationMissingOptionError(
                            option, section, rawval, e.args[0])
                else:
                    break
            if "%(" in value:
                raise InterpolationDepthError(option, section, rawval)
            return value

        _KEYCRE = compile(r"%\(([^)]*)\)s|.")

        def _interpolation_replace(self, match):
            s = match.group(1)
            if s is None:
                return match.group()
            else:
                return "%%(%s)s" % self.optionxform(s)


    class SafeConfigParser(ConfigParser):

        def _interpolate(self, section, option, rawval, vars):
            # do the string interpolation
            L = []
            self._interpolate_some(option, L, rawval, section, vars, 1)
            return ''.join(L)

        _interpvar_re = compile(r"%\(([^)]+)\)s")

        def _interpolate_some(self, option, accum, rest, section, map, depth):
            if depth > MAX_INTERPOLATION_DEPTH:
                raise InterpolationDepthError(option, section, rest)
            while rest:
                p = rest.find("%")
                if p < 0:
                    accum.append(rest)
                    return
                if p > 0:
                    accum.append(rest[:p])
                    rest = rest[p:]
                # p is no longer used
                c = rest[1:2]
                if c == "%":
                    accum.append("%")
                    rest = rest[2:]
                elif c == "(":
                    m = self._interpvar_re.match(rest)
                    if m is None:
                        raise InterpolationSyntaxError(option, section,
                            "bad interpolation variable reference %r" % rest)
                    var = self.optionxform(m.group(1))
                    rest = rest[m.end():]
                    try:
                        v = map[var]
                    except KeyError:
                        raise InterpolationMissingOptionError(
                            option, section, rest, var)
                    if "%" in v:
                        self._interpolate_some(option, accum, v,
                                               section, map, depth + 1)
                    else:
                        accum.append(v)
                else:
                    raise InterpolationSyntaxError(
                        option, section,
                        "'%%' must be followed by '%%' or '(', found: %r" % (rest,))

        def set(self, section, option, value):
            """Set an option.  Extend ConfigParser.set: check for string values."""
            if not isinstance(value, basestring):
                raise TypeError("option values must be strings")
            # check for bad percent signs:
            # first, replace all "good" interpolations
            tmp_value = value.replace('%%', '')
            tmp_value = self._interpvar_re.sub('', tmp_value)
            # then, check if there's a lone percent sign left
            percent_index = tmp_value.find('%')
            if percent_index != -1:
                raise ValueError("invalid interpolation syntax in %r at "
                                 "position %d" % (value, percent_index))
            ConfigParser.set(self, section, option, value)
