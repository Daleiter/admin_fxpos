import jinja2
import locale
import pdfkit
import base64
import io
import tempfile
import os
from datetime import datetime, date
from barcode import EAN13_GUARD, EAN8_GUARD
from barcode.writer import SVGWriter


class LablelPdfGen():
    def __init__(self, data, label_type, date_to) -> None:
        self.data = data
        locale.setlocale(locale.LC_TIME, "uk_UA.utf8")
        self.data['date_to'] = date_to.strftime("%d %b %Y")
        self.label_type = label_type

    def _gen_barcode(self, barcode):
        file_in_memory = io.BytesIO()
        writer = SVGWriter()
        writer.set_options({'quiet_zone':0, 'text_distance':1, 'font_size':5, 'module_width':1 , 'module_height': 0.5, 'margin_top':0})
        if len(barcode) > 7:
            EAN13_GUARD(barcode, writer=writer).write(file_in_memory)
        else:
            EAN8_GUARD(barcode, writer=writer).write(file_in_memory)
        file_in_memory.seek(0)
        base64_bytes = base64.b64encode(file_in_memory.getvalue())
        return base64_bytes.decode('ascii')
    
    def _gen_pdf(self, size_h, size_w):
            letter_spacing =  '0px;'
            self.data['barcode_base64'] = self._gen_barcode(self.data['barcode'])
            if len(self.data['ingredients']) > 800:
                 letter_spacing = '-0.09rem;'
                 
                 
            _template = """
<style>
@import url('https://fonts.cdnfonts.com/css/smartgothic');
</style>
<div class="header" style="text-align: left;">{{ name }}</div>
<div class="mass" style="text-align: left;">{{ weight }}</div>
<div class="dstu" style="text-align: left;">{{ delta }} {{ ttu }}</div>
<div class="sklad"><b>Склад: </b>{{ ingredients }}</div>
<div class="made" style="text-align: left;"><b>Виробник та адреса потужностей виробництва: </b>{{ manufacturer }}</div>
<div class="made" ><b>Поживна цінність у 100 г (g) продукту: </b>{{ nutrition }}</div>
<div class="made" style="text-align: left;"><b>{{ storage }}</b></div>

<div style="position: absolute; bottom: 1px; left: 10px;">
<div class="made">Вжити до:    <b style="font-size: 12px;">{{ date_to }}</b></br>Номер партії</div>
<div class="made">відповідає даті «вжити до» </div>

</div>
<img style="position: absolute; bottom: 0px; right: -10px; z-index: -1;" src="data:image/svg+xml;base64,{{ barcode_base64 }}"/>

            """
            css = """
img{
    width: 160px;
        height: 50px;
       clip: rect(15px, 139px, 50px, 15px);
}
            
div {
font-family: 'SmartGothic', sans-serif;

}
.header {
     font-size: 14px;
     font-weight: bold;
}
 .mass {
     font-size: 14px;
     font-weight: bold;
}

 .dstu {
     font-size: 0.55rem;
     font-weight: bold;
     line-height: 100%;
}

 .sklad {
     
     font-size: 0.5rem;
     font-weight: normal;
     text-align: justify;
     line-height: 100%;
     letter-spacing:""" + letter_spacing + """
}
 .made {
     font-size: 0.50rem;
     line-height: 100%;
}
            """
            with tempfile.NamedTemporaryFile(delete=False) as temp_file_css:
                temp_file_css.write(css.encode('utf-8'))
                temp_file_css.flush()  # Flush the changes to ensure they are written to the file
                file_path = temp_file_css.name  # Get the file path
            options = {
                'page-width': '2.24in',
                'page-height' : '2.42in',
                #'page-size': '58.928mmx56.896mm',
                'margin-top': '0.03in',
                'margin-right': '0.00in',
                'margin-bottom': '0.00in',
                'margin-left': '0.00in',
                'encoding': "UTF-8",
                'enable-forms': True,
                #'orientation': 'landscape'
            }
            template_loader = jinja2.FileSystemLoader('./')
            template_env = jinja2.Environment(loader=template_loader)

            template = template_env.from_string(_template)
            output_text = template.render(self.data )
            
            # Create a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_file_path = temp_file.name
            config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
            pdfkit.from_string(output_text, temp_file_path, configuration=config, css=temp_file_css.name , options=options)
            return temp_file_path