from pylatex import Document,NoEscape,Command

DEFAULT_FONT_SIZE = "10pt"

DEFAULT_COMPILER = "pdflatex"

DEFAULT_TOP_MARGIN = "1.2cm"

DEFAULT_BOTTOM_MARGIN = "2.2cm"

DEFAULT_LEFT_MARGIN = "0.5cm"

DEFAULT_RIGHT_MARGIN = "0.5cm"

DEFAULT_HEADER_HEIGHT = DEFAULT_TOP_MARGIN

REPORT_PACKAGES_LATEX = r"""
\usepackage[T1]{fontenc}%
\usepackage[utf8]{inputenc}%
\usepackage{lmodern}%
\usepackage{textcomp}%
\usepackage{lastpage}%
\usepackage{geometry}%
\usepackage{lmodern}                % For various font options
\usepackage{textcomp}               % For various text symbols
\usepackage{lastpage} 
\usepackage[ddmmyyyy]{datetime}
\usepackage[none]{hyphenat}         % For prevents hyphenation throughout the document
\usepackage{draftwatermark}         % Grey textual watermark on document pages
\usepackage{xcolor}                 % For color options
\usepackage{ragged2e}               % For changing the typeset alignment of text
\usepackage{array}                  % Extended implementation of the array and tabular environments which extends the options for column formats
\usepackage{longtable}              % Allows you to write tables that continue to the next page.
\usepackage{fancyhdr}               % Constructing and controlling page headers and footers
\usepackage{float}                  % Place the figure at that exact location in the page
\usepackage[hidelinks]{hyperref}    % Creating a clickable link
\usepackage{pgfplots}               % For creating plots and graphics
\usepackage{multicol}               % For dividing the pages into columns
\usepackage{multirow}               % For combining the rows and columns in the tables
\usepackage{colortbl}               % Changing the color of the table cells
\usepackage{pgffor}
\usepackage{pifont}                 %For correct and wrong symbols for ding{}
\usepackage{tabularx}               %For correct and wrong symbols for ding{}



"""



class BaseReport(Document):

    def __init__(
            self,
            font_size=DEFAULT_FONT_SIZE,
            top_margin=DEFAULT_TOP_MARGIN,
            bottom_margin=DEFAULT_BOTTOM_MARGIN,
            left_margin=DEFAULT_LEFT_MARGIN,
            right_margin=DEFAULT_RIGHT_MARGIN,
            head_height=DEFAULT_HEADER_HEIGHT,
            *args,
            **kwargs
        ):

        self.font_size = font_size

        self.CURRENT_PAGE_NO = r'\thepage'

        self.geometry_options = {
            "top": top_margin,
            "bottom" : bottom_margin,
            "left" : left_margin,
            "right" : right_margin
        }

        super().__init__(geometry_options=self.geometry_options)

        self.append(NoEscape(r'\setlength{\headheight}{'+head_height+'}'))

        self.add_watermark(**kwargs)

        self.preamble.append(NoEscape(REPORT_PACKAGES_LATEX))

        
    def add_watermark(self,watermark_text:str="Learn Basics", watermark_text_opacity:float=0.95,watermark_text_scale:float=0.7):

        water_mark_text = r"""\SetWatermarkLightness{ """ + str(watermark_text_opacity) + r"""}
        \SetWatermarkText{ """ + watermark_text + r""" }
        \SetWatermarkScale{ """ + str(watermark_text_scale) + r"""}"""

        self.append(NoEscape(water_mark_text))
    
    def add_header_footer(
        self,
        left_header_latex:str = "",
        center_header_latex:str = "",
        right_header_latex:str = "",
        left_footer_latex:str = "Learn Basics",
        center_footer_latex:str = "",
        right_footer_latex:str = "",
        header_rule_width:int=1,
        footer_rule_width:int=1
        ):

        header_rule_width = str(header_rule_width) + r'pt'

        footer_rule_width = str(footer_rule_width) + r'pt'

        header_footer_code = r'''
    \pagestyle{fancy}

    \fancyhf{}

            \fancyhfinit{%
            
            \renewcommand{\footrulewidth}{0.7pt}%

            \fancyhead[L]{%
                ''' + left_header_latex + r'''
            }%

            \fancyhead[C]{%
                ''' + center_header_latex + r'''
            }%

            \fancyhead[R]{%
                ''' + right_header_latex + r'''
            }%
            
                        
            \fancyfoot[L]{
                ''' + left_footer_latex + r'''
            }

            \fancyfoot[C]{
                ''' + center_footer_latex + r'''
            }

            \fancyfoot[R]{%
                ''' + right_footer_latex + r'''
            }%

            \renewcommand{\headrulewidth}{''' + header_rule_width + r'''}

            \renewcommand{\footrulewidth}{''' + footer_rule_width + r'''}%        

        }'''
    
        self.preamble.append(NoEscape(header_footer_code))

    


class BaseA4PotraitReport(BaseReport):

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.documentclass = Command('documentclass', options=[self.font_size,'a4paper'], arguments=['article'])



class BaseA4LandscapeReport(BaseReport):

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.documentclass = Command('documentclass', options=[self.font_size, 'a4paper','landscape'], arguments=['article'])


class BaseA3LandscapeReport(BaseReport):

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.documentclass = Command('documentclass', options=[self.font_size, 'a3paper','landscape'], arguments=['article'])

class BaseA3PotraitReport(BaseReport):

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)

        self.documentclass = Command('documentclass', options=[self.font_size, 'a3paper'], arguments=['article'])


