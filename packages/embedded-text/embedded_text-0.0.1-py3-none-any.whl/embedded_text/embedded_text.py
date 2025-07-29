#!/usr/bin/env python3
import os
import re
import inspect
import typing
import sys

class EmbeddedText(object):
    """
    EmbeddedText: Utility to extract text contents embedded in file
    """

    VERSION     = "0.0.1"
    HEADSPACE   = re.compile(r'^(?P<indent>\s*).*')
    EMPTYLINE   = re.compile(r'^\s*$')
    TRIPLEQUATE = re.compile(r"^\s*(?P<triplequote>'{3}|\"{3})(?P<rest>.*)$")

    class FormatFilter(object):
        
        def __init__(self, 
                     keyword_table:dict=None, 
                     format_variables:dict=None,
                     **cmd_args):
            self.keyword_table    = keyword_table
            self.format_variables = format_variables
            self.flg_filters      = (isinstance(self.keyword_table,dict),
                                     isinstance(self.format_variables,dict))
            if self.flg_filters[0]:
                self.keyword_table.update(cmd_args)
            if self.flg_filters[1]:
                self.format_variables.update(cmd_args)

        def __call__(self, line:str)->str:
            if self.flg_filters[1]:
                line = line.format(**self.format_variables)
            if self.flg_filters[0]:
                for k,v in self.keyword_table.items():
                    line = line.replace(k, v)
            return line

    def __init__(self, s_marker:str=None, e_marker:str=None,
                 include_markers:bool=True,
                 multi_match:bool=False,
                 dedent:bool=False, unquote:bool=False,
                 skip_head_emptyline:bool=False,
                 skip_tail_emptyline:bool=False,
                 format_filter=None, keyword_table:dict=None,
                 format_variables:dict=None, encoding:str='utf-8'):

        self.s_pttrn = ( s_marker if isinstance(s_marker, re.Pattern) 
                         else ( re.compile(s_marker) 
                                if isinstance(s_marker, str) and s_marker else None))

        self.e_pttrn = ( e_marker if isinstance(e_marker, re.Pattern) 
                         else ( re.compile(e_marker) 
                                if isinstance(e_marker, str) and e_marker else None))
        if format_filter is None:
            if keyword_table is None and format_variables is None:
                self.format_filter = None
            else:
                self.format_filter = self.__class__.FormatFilter(keyword_table=keyword_table, 
                                                                 format_variables=format_variables)
        else:
            self.format_filter = format_filter

        self.include_markers     = include_markers
        self.multi_match         = multi_match
        self.dedent              = dedent
        self.unquote             = unquote
        self.skip_head_emptyline = skip_head_emptyline
        self.skip_tail_emptyline = skip_tail_emptyline
        self.encoding            = encoding

    def lines(self, input_path:str=None) -> typing.Iterator[str]:
        return self.__class__.extract_from_file(infile=input_path, 
                                                s_marker=self.s_pttrn, e_marker=self.e_pttrn,
                                                include_markers=self.include_markers,
                                                multi_match=self.multi_match,
                                                dedent=self.dedent, unquote=self.unquote,
                                                skip_head_emptyline=self.skip_head_emptyline,
                                                skip_tail_emptyline=self.skip_tail_emptyline, 
                                                format_filter=self.format_filter,
                                                encoding=self.encoding)

    def dump(self, output_path, input_path:str=None, open_mode:str='w'):
        self.__class__.extract_to_file(outfile=output_path, infile=input_path,
                                       s_marker=self.s_pttrn, e_marker=self.e_pttrn,
                                       include_markers=self.include_markers,
                                       multi_match=self.multi_match,
                                       dedent=self.dedent, unquote=self.unquote,
                                       format_filter=self.format_filter,
                                       encoding=self.encoding, open_mode=open_mode)

    @classmethod
    def extract_raw_to_file(cls, outfile, infile:str=None, s_marker:str=None, e_marker:str=None,
                            include_markers:bool=True, multi_match:bool=False,
                            dedent:bool=False, format_filter=None, 
                            open_mode='w', encoding:str='utf-8'):
        
        fout = sys.stdout if outfile is None else open(outfile, mode=open_mode, encoding=encoding)
        for line in cls.extract_raw_from_file(infile=infile, s_marker=s_marker, e_marker=e_marker,
                                              include_markers=include_markers,
                                              multi_match=multi_match, dedent=dedent, 
                                              format_filter=format_filter, encoding=encoding):
            fout.write(line)
        if outfile is not None:
            fout.close()

    @classmethod
    def extract_raw_from_file(cls, infile:str=None, s_marker:str=None, e_marker:str=None,
                              include_markers:bool=True, multi_match:bool=False,
                              dedent:bool=False, format_filter=None,
                              encoding:str='utf-8') -> typing.Iterator[str]:

        input_path = ( infile if isinstance(infile,str) and infile
                       else inspect.getsourcefile(inspect.currentframe()))
        with open(input_path, encoding=encoding) as fin:
            for line in cls.extract_raw(fin, s_marker=s_marker, e_marker=e_marker,
                                        include_markers=include_markers,
                                        multi_match=multi_match,
                                        dedent=dedent, format_filter=format_filter):
                yield line

    @classmethod
    def extract_raw(cls, lines: typing.Iterable[str],
                    s_marker:str=None, e_marker:str=None,
                    include_markers:bool=True, multi_match:bool=False,
                    dedent:bool=False, format_filter=None) -> typing.Iterator[str]:

        s_pttrn = ( s_marker if isinstance(s_marker, re.Pattern) 
                    else ( re.compile(s_marker) 
                           if isinstance(s_marker, str) and s_marker else None))
        e_pttrn = ( e_marker if isinstance(e_marker, re.Pattern) 
                     else ( re.compile(e_marker) 
                            if isinstance(e_marker, str) and e_marker else None))

        indent     = ''
        in_range = True if s_pttrn is None else False
        for line in lines:
            if not in_range:
                if s_pttrn is None or s_pttrn.match(line):
                    if dedent:
                        m_indent = cls.HEADSPACE.match(line)
                        if m_indent:
                            indent = m_indent.group('indent')
                            line = line.removeprefix(indent)
                    in_range = True
                    if include_markers:
                        yield format_filter(line) if callable(format_filter) else line
            else:
                line = line.removeprefix(indent)
                if e_pttrn is None:
                    yield format_filter(line) if callable(format_filter) else line
                elif e_pttrn.match(line):
                    if include_markers:
                        yield format_filter(line) if callable(format_filter) else line
                    if multi_match and s_pttrn is not None:
                        in_range   = False
                        indent     = ''
                    else:
                        return
                else:
                    yield format_filter(line) if callable(format_filter) else line

    @classmethod
    def extract_unquote_to_file(cls, outfile, infile:str=None, s_marker:str=None, e_marker:str=None,
                                include_markers:bool=True, multi_match:bool=False,
                                dedent:bool=False, unquote:bool=False,
                                format_filter=None, open_mode='w', encoding:str='utf-8'):
        
        fout = sys.stdout if outfile is None else open(outfile, mode=open_mode, encoding=encoding)
        for line in cls.extract_unquote_from_file(infile=infile, s_marker=s_marker, e_marker=e_marker,
                                                  include_markers=include_markers,
                                                  multi_match=multi_match, dedent=dedent, 
                                                  unquote=unquote, format_filter=format_filter, encoding=encoding):
            fout.write(line)
        if outfile is not None:
            fout.close()

    @classmethod
    def extract_unquote_from_file(cls, infile:str=None, s_marker:str=None, e_marker:str=None,
                                  include_markers:bool=True, multi_match:bool=False,
                                  dedent:bool=False, unquote:bool=True, format_filter=None,
                                  encoding:str='utf-8') -> typing.Iterator[str]:

        input_path = ( infile if isinstance(infile,str) and infile
                       else inspect.getsourcefile(inspect.currentframe()))
        with open(input_path, encoding=encoding) as fin:
            for line in cls.extract_unquote(fin, s_marker=s_marker, e_marker=e_marker,
                                            include_markers=include_markers,
                                            multi_match=multi_match,
                                            dedent=dedent, unquote=unquote,
                                            format_filter=format_filter):
                yield line

    @classmethod
    def extract_unquote(cls, lines: typing.Iterable[str],
                        s_marker:str=None, e_marker:str=None,
                        include_markers:bool=True, multi_match:bool=False,
                        dedent:bool=False, unquote:bool=True, 
                        format_filter=None) -> typing.Iterator[str]:

        s_pttrn = ( s_marker if isinstance(s_marker, re.Pattern) 
                    else ( re.compile(s_marker) 
                           if isinstance(s_marker, str) and s_marker else None))
        e_pttrn = ( e_marker if isinstance(e_marker, re.Pattern) 
                     else ( re.compile(e_marker) 
                            if isinstance(e_marker, str) and e_marker else None))

        quote_mrkr = ''
        for line in cls.extract_raw(lines=lines,
                                    s_marker=s_pttrn,
                                    e_marker=e_pttrn,
                                    include_markers=include_markers,
                                    multi_match=multi_match,
                                    dedent=dedent,
                                    format_filter=format_filter):
            if unquote:
                if quote_mrkr:
                    pos = line.find(quote_mrkr)
                    if pos>=0:
                        line = line[0:pos] + line[pos+len(quote_mrkr):]
                        quote_mrkr = ''

                m_triquote = cls.TRIPLEQUATE.match(line)
                while m_triquote:
                    quote_mrkr = m_triquote.group('triplequote')
                    line = m_triquote.group('rest')+os.linesep
                    
                    pos = line.find(quote_mrkr)
                    if pos>=0:
                        line = line[0:pos]+line[pos+len(quote_mrkr):]
                        quote_mrkr = ''
                    else:
                        break
                    m_triquote = cls.TRIPLEQUATE.match(line)
                    
            yield line

    @classmethod
    def extract(cls,lines: typing.Iterable[str],
                s_marker:str=None,
                e_marker:str=None,
                include_markers:bool=True,
                multi_match:bool=False,
                dedent:bool=False,
                unquote:bool=False,
                skip_head_emptyline:bool=False,
                skip_tail_emptyline:bool=False, 
                format_filter=None) -> typing.Iterator[str]:

        s_pttrn = ( s_marker if isinstance(s_marker, re.Pattern) 
                    else ( re.compile(s_marker) 
                           if isinstance(s_marker, str) and s_marker else None))
        e_pttrn = ( e_marker if isinstance(e_marker, re.Pattern) 
                     else ( re.compile(e_marker) 
                            if isinstance(e_marker, str) and e_marker else None))
        el_buf     = []
        el_bfr_hdr = True
        in_range = True if s_pttrn is None else False
        for line in cls.extract_unquote(lines=lines,
                                        s_marker=s_pttrn, e_marker=e_pttrn,
                                        include_markers=True,
                                        multi_match=multi_match,
                                        dedent=dedent, unquote=unquote,
                                        format_filter=format_filter):
            if not in_range:
                if s_pttrn is None or s_pttrn.match(line):
                    in_range = True
                    if include_markers:
                        yield line
            else:
                m_el = cls.EMPTYLINE.match(line)
                if m_el:
                    el_buf.append(line)
                else:
                    if el_bfr_hdr and skip_head_emptyline:
                        el_bfr_hdr = False
                        el_buf=[]

                if e_pttrn is not None and e_pttrn.match(line):
                    if not skip_tail_emptyline:
                        yield from el_buf
                        el_buf = []
                    if include_markers:
                        yield line
                    if multi_match or (s_pttrn is not None):
                        el_buf     = []
                        el_bfr_hdr = True
                        in_range   = False
                    else:
                        return
                elif not m_el:
                    yield from el_buf
                    el_buf = []
                    yield line

        if e_pttrn is None and (not skip_tail_emptyline):
            yield from el_buf
            el_buf = []

    @classmethod
    def extract_from_file(cls, infile:str=None, s_marker:str=None, e_marker:str=None,
                          include_markers:bool=True, multi_match:bool=False,
                          dedent:bool=False, skip_head_emptyline:bool=False,
                          skip_tail_emptyline:bool=False, unquote:bool=False,
                          format_filter=None, encoding:str='utf-8') -> typing.Iterator[str]:

        input_path = ( infile if isinstance(infile,str) and infile
                       else inspect.getsourcefile(inspect.currentframe()))
        with open(input_path, encoding=encoding) as fin:
            for line in cls.extract(fin, 
                                    s_marker=s_marker,
                                    e_marker=e_marker,
                                    include_markers=include_markers,
                                    multi_match=multi_match,
                                    dedent=dedent, unquote=unquote,
                                    format_filter=format_filter,
                                    skip_head_emptyline=skip_head_emptyline,
                                    skip_tail_emptyline=skip_tail_emptyline):
                yield line

    @classmethod
    def extract_to_file(cls, outfile, infile:str=None, s_marker:str=None, e_marker:str=None,
                        include_markers:bool=True, multi_match:bool=False,
                        dedent:bool=False, skip_head_emptyline:bool=False,
                        skip_tail_emptyline:bool=False, unquote:bool=False,
                        format_filter=None, open_mode='w', encoding:str='utf-8'):
        
        fout = sys.stdout if outfile is None else open(outfile, mode=open_mode, encoding=encoding)
        for line in cls.extract_from_file(infile=infile, 
                                          s_marker=s_marker, e_marker=e_marker,
                                          include_markers=include_markers,
                                          multi_match=multi_match, dedent=dedent, 
                                          skip_head_emptyline=skip_head_emptyline,
                                          skip_tail_emptyline=skip_tail_emptyline,
                                          unquote=unquote, format_filter=format_filter, encoding=encoding):
            fout.write(line)
        if outfile is not None:
            fout.close()

    @classmethod
    def main(cls):

        import argparse

        argprsr = argparse.ArgumentParser(description='Example of class EmbeddedText')

        pattern_default = { 'code' : { 'start': r'\s*#{5,}\s*Embedded\s+Code\s+Start\s*#{5,}',
                                       'end'  : r'\s*#{5,}\s*Embedded\s+Code\s+End\s*#{5,}'},
                            'text' : { 'start': r'\s*#{5,}\s*Embedded\s+Text\s+Start\s*#{5,}',
                                       'end'  : r'\s*#{5,}\s*Embedded\s+Text\s+End\s*#{5,}'}}

        argprsr.add_argument('-c', '--code-extraction-mode', action='store_true', dest='code_mode', default=False, help='Code extraction mode')
        argprsr.add_argument('-t', '--text-extraction-mode', action='store_false',dest='code_mode', default=False, help='Text extraction mode (default)')

        argprsr.add_argument('-s', '--start-pattern',  help='Start marker pattern (Regular Expression)')
        argprsr.add_argument('-e', '--end-pattern',    help='Start marker pattern (Regular Expression)')

        argprsr.add_argument('-m', '--multi-match',  action='store_true',  help='Can be match mulitple regions')
        argprsr.add_argument('-H', '--class-help',   action='store_true',  help='Show class help')
        argprsr.add_argument('-V', '--version',      action='store_true',  help='Show version')
        argprsr.add_argument('-K', '--keep-indent',  action='store_false', dest='dedent', help='Keep indent of original text')
        argprsr.add_argument('-I', '--ignore-case',  action='store_true', help='Ignore Case for marker matching')
        argprsr.add_argument('-M', '--keep-markers', action='store_true',  help='Keep region start/end marker lines')
        argprsr.add_argument('-r', '--keep-head-el', action='store_false', default=True, dest='skip_head_emptyline', help='Keep empty lines at head')
        argprsr.add_argument('-R', '--keep-tail-el', action='store_false', default=True, dest='skip_tail_emptyline', help='Keep empty lines at tail')
        argprsr.add_argument('-u', '--unquote',  action='store_true',  help='Remove triple-quote')
        argprsr.add_argument('-E', '--encoding', default='utf-8',  help='Remove triple-quote')
        argprsr.add_argument('-i', '--input-file',  help='Input file path (Default: show to standar output)')
        argprsr.add_argument('-o', '--output-file', help='Output file path (Default: show to standar output)')
        argprsr.add_argument('-a', '--append-output', help='Append to output file (meaning less without -o, --output)')
        argprsr.add_argument('-x', '--exclusive-output', help='Exclusive opening of output file (meaning less without -o, --output)')

        argprsr.add_argument('-k', '--keywords',  nargs=2, action='append', metavar=('keyword',  'value'), help='Add keywords for word replacement')
        argprsr.add_argument('-v', '--variables', nargs=2, action='append', metavar=('variable', 'value'), help='define variable for word formatting')
        
        args = argprsr.parse_args()
        run_mode = 'code' if args.code_mode else 'text'

        s_regex = args.start_pattern if args.start_pattern else pattern_default[run_mode]['start']
        e_regex = args.end_pattern   if args.end_pattern   else pattern_default[run_mode]['end']

        s_pttrn = re.compile(s_regex, re.I if args.ignore_case else 0)
        e_pttrn = re.compile(e_regex, re.I if args.ignore_case else 0)

        keywords  = { v[0]: v[1] for v in args.keywords  } if (isinstance(args.keywords,  list) and len(args.keywords)>0  ) else None
        variables = { v[0]: v[1] for v in args.variables } if (isinstance(args.variables, list) and len(args.variables)>0 ) else None

        extractor = EmbeddedText(s_marker=s_pttrn, e_marker=e_pttrn,
                                 include_markers=args.keep_markers,
                                 multi_match=args.multi_match,
                                 dedent=args.dedent,
                                 unquote=(args.unquote or run_mode == 'text'),
                                 skip_head_emptyline=args.skip_head_emptyline,
                                 skip_tail_emptyline=args.skip_tail_emptyline,
                                 keyword_table=keywords, format_variables=variables,
                                 format_filter=None, encoding=args.encoding)
        if args.class_help:
            help(EmbeddedText)
            help(EmbeddedText.FormatFilter)
            return
        elif args.version:
            print("%s (version : %s)" % (cls.__name__,
                                         cls.VERSION))
            return

        if args.output_file:
            extractor.dump(output_path=args.output_file, input_path=args.input_file, 
                           open_mode=('x' if args.exclusive_output else ('a' if args.append_output else 'w')))
        else:
            for line in extractor.lines(input_path=args.input_file):
                sys.stdout.write(line)


def main():
    return EmbeddedText.main()

if __name__ == "__main__":
    EmbeddedText.main()

    if False:

        ############# Embedded Text Start #######################
        
        """
        # .gitignore
        *.py[cod]
        *$py.class
        # For emacs backup file
        *~
        lib/python/site-packages/*
        !{____GITDUMMYFILE____}
        """
        
        ############# Embedded Text End #######################


        ############# Embedded Code Start #######################
    
        #!/usr/bin/env python3
    
        def main():
            print ('This is the sample : ____OUTPUT_WORDS____')
            
            if __name__ == '__main__':
                main()
            
        ############# Embedded Code End #######################
