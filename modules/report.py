from odf.opendocument import OpenDocumentText
from odf.table import Table, TableRow, TableCell, TableColumn
from odf.text import P
from odf.style import Style, PageLayout, PageLayoutProperties, TableColumnProperties, ParagraphProperties, MasterPage, TextProperties
from datetime import datetime, timedelta

# Константы лучше выносить на уровень модуля
MONTHS = {
    12: "Декабрь", 1: "Январь",   2: "Февраль",
    3: "Март",     4: "Апрель",   5: "Май",
    6: "Июнь",     7: "Июль",     8: "Август",
    9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь"
}

# Конфигурация таблицы тоже лучше как константа
TABLE_HEADERS = {
    'Наименование работы':                     "3.5cm",
    'Примечание':                              "11cm",
    'Статус':                                  "2.5cm",
    'Затраченное время за отчётный период':    "2.5cm",
    'Необходимо затратить в следующий период': "3cm",
    'Срок завершения':                         "2.5cm"
}


class Report:
    """Класс для работы с документом отчета"""

    def __init__(self) -> None:
        self.report_data = {"current": [], "next": []}
        self.doc = OpenDocumentText()
        self._init_styles()

    def _create_paragraph_style(self, name, fontsize="10pt", fontfamily="Calibri", 
                                textalign=None, padding="5pt", fontweight=None):
        """Утилита для создания стилей параграфа"""
        style = Style(name=name, family="paragraph")

        # Параметры абзаца
        para_props = {}
        if textalign:
            para_props["textalign"] = textalign
        if padding:
            para_props["padding"] = padding

        if para_props:
            style.addElement(ParagraphProperties(**para_props))
        
        # Параметры текста
        text_props = {
            "fontsize":   fontsize,
            "fontfamily": fontfamily
        }
        if fontweight:
            text_props["fontweight"] = fontweight

        style.addElement(TextProperties(**text_props))
        return style

    def _init_styles(self):
        """Инициализация базовых стилей документа"""
        # Создаем и добавляем стили с помощью нашей утилиты
        default_style = self._create_paragraph_style("Default")
        self.doc.styles.addElement(default_style)

        center_style = self._create_paragraph_style("Center", textalign="center")
        self.doc.styles.addElement(center_style)

        header_style = self._create_paragraph_style(
            "Header", 
            textalign="center", 
            fontfamily="Times New Roman", 
            fontweight="bold"
        )
        self.doc.styles.addElement(header_style)

        # Настройка макета страницы
        page_layout = PageLayout(name="LandscapeLayout")
        page_props = PageLayoutProperties(
            pagewidth='29.7cm',
            pageheight='21cm',
            printorientation="landscape",
            margintop='1cm',
            marginleft='1cm',
            marginbottom='0.5cm',
            marginright='1cm',
            writingmode='lr-tb'
        )
        page_layout.addElement(page_props)
        self.doc.automaticstyles.addElement(page_layout)

        master = MasterPage(name="Standard", pagelayoutname=page_layout)
        self.doc.masterstyles.addElement(master)

    def get_data(self):
        return self.report_data

    def add_report(self, table_header: str, data: list) -> None:
        """Добавление в отчет таблицы с заголовком"""
        # Добавляем заголовок таблицы
        self.doc.text.addElement(P(text=table_header, stylename="Default"))

        # Создаем таблицу
        table = Table()

        # Добавляем столбцы с нужными ширинами
        for i, width in enumerate(TABLE_HEADERS.values()):
            col_style = Style(name=f"col_{i}", family="table-column")
            col_style.addElement(TableColumnProperties(columnwidth=width))
            self.doc.automaticstyles.addElement(col_style)
            table.addElement(TableColumn(stylename=f"col_{i}"))

        # Заголовки таблицы
        header_row = TableRow()
        for header in TABLE_HEADERS:
            cell = TableCell()
            cell.addElement(P(text=header, stylename="Header"))
            header_row.addElement(cell)
        table.addElement(header_row)

        # Данные таблицы
        for item in data:
            row = TableRow()
            for key in TABLE_HEADERS:
                value = str(item.get(key, '') or '')
                cell = TableCell()
                cell.addElement(P(text=value, stylename="Center"))
                row.addElement(cell)
            table.addElement(row)
        self.doc.text.addElement(table)

    def create_odt_report(self, firstname: str, initials: str) -> str:
        """Создание ежемесячного отчета (в формате .odt)"""
        cur_month = datetime.now().replace(day=15)
        next_month = cur_month + timedelta(weeks=4)

        # Форматируем заголовки
        cur_header = f"{firstname} {initials} Отчет за {MONTHS[cur_month.month]} {cur_month.year} г."
        next_header = f"{firstname} {initials} План на {MONTHS[next_month.month]} {next_month.year} г."

        # Добавляем отчеты
        self.add_report(cur_header, self.report_data['current'])
        self.doc.text.addElement(P(text="", stylename="Default"))
        self.add_report(next_header, self.report_data['next'])

        # Создаем имя файла
        filename = f"Отчет_{firstname}_{MONTHS[cur_month.month]}.odt"
        self.doc.save(filename)
        return filename