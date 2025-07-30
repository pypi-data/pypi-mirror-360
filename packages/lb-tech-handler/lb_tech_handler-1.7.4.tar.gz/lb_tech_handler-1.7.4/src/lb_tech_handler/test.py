from lb_tech_handler import report_templates
from pylatex import NoEscape

class SampleReport(report_templates.BaseA3LandscapeReport):
    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)
        
        self.append(NoEscape("Hello World"))

        self.add_header_footer(left_header_latex=r'\includegraphics[width=4cm]{logo.png}')

        self.generate_pdf(filepath='test.pdf',clean_tex=False,compiler=report_templates.DEFAULT_COMPILER)

if __name__ == "__main__":
    SampleReport()