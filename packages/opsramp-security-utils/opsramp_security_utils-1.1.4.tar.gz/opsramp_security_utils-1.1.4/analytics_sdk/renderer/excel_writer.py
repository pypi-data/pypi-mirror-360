import xlsxwriter
from analytics_sdk.utilities import (
    APP_ID,
    APP_DISPLAY_NAME,
    upload_file
)
    
def lastColumnOfChart(chart_width,chart_pos):
    return int(-(-chart_width*9//553))+ord(chart_pos[0])-1


class ExcelWriter:

    DATA_PER_SHEET_LIMIT = 1000001
    ROW_START = 3
    CONTENT_ROW_START = 0
    def __init__(self, run_id, file_name, app_id):
        self.run_id = run_id
        self.file_name = file_name
        self.app_id = app_id
        self.wb = xlsxwriter.Workbook(self.file_name, {'constant_memory':True, 'nan_inf_to_errors': True})
        self.total_sheet_row_counts = {}
        self.active_sheet_title = ''
        self.sheet_refs = {}
        self.run_params = None


    def create_sheet(self, sheet_title):
        sheet_title = self.get_page_title(sheet_title, 0)
        if sheet_title in self.sheet_refs:
            return self.sheet_refs[sheet_title]
        ws = self.wb.add_worksheet(sheet_title)
        self.sheet_refs[sheet_title] = ws
        # self.add_headers(ws)
        return ws
    
    def close_wb(self):
        if self.wb:
            self.wb.close()
    
    def get_page_title(self, title, page_no):
        pg_title = ''
        if page_no > 0:
            pg_title = f'.. {page_no}'
        pg_title_len = len(pg_title)
        remain_len = 29 - pg_title_len
        title = title[0:remain_len]
        title = title + pg_title
        return title
    

    def write_summary_data(self, summary_data):
        ws = self.create_sheet('SUMMARY')
        self.fill_sheet_bg_colors(ws)
        ws.set_column('B:B', 24)
        ws.set_column('C:C', 24)
        # Rendering Run Summary information
        if summary_data is not None and len(summary_data) > 0:
            cell_no = ExcelWriter.ROW_START
            for entry in summary_data:
                ws.write(f'B{cell_no}', entry, self.wb.add_format({'color':'00598B', 'bg_color' : 'eeeeee'}))
                ws.write(f'C{cell_no}', summary_data[entry], self.wb.add_format({'color':'000000', 'bg_color' : 'eeeeee'}))
                cell_no += 1
            if self.run_params and self.run_params is not None and len(self.run_params) > 0:
                opsql_params = None
                if 'opsql_query' in self.run_params:
                    opsql_params = self.run_params['opsql_query']
                if opsql_params is not None:
                    for key in opsql_params.keys():
                        display_name = self.get_display_name(key)
                        display_value = self.get_display_value(opsql_params[key])

                        ws.write(f'B{cell_no}', display_name, self.wb.add_format({'color':'00598B', 'bg_color' : 'eeeeee'}))
                        ws.write(f'C{cell_no}', display_value, self.wb.add_format({'color':'000000', 'bg_color' : 'eeeeee'}))
                        cell_no += 1
        


    def write_glossary_data(self, glossary_data):
        ws = self.create_sheet('GLOSSARY')
        if ws:
            self.fill_sheet_bg_colors(ws)
            data_len = 30
            if glossary_data is not None and len(glossary_data) >= data_len:
                data_len = len(glossary_data)+5
            
            # self.fill_sheet_bg_colors(ws, start_row=1, end_row=data_len)
            ws.set_column('B:B', 50)
            ws.set_column('C:C', 24)

            cell_no = 3
            if glossary_data is not None:
                data = glossary_data
                for key in data.keys():
                    display_name = key
                    display_value = data[key]

                    ws.write(f'B{cell_no}', display_name, self.wb.add_format({'color':'00598B', 'bg_color' : 'eeeeee'}))
                    ws.write(f'C{cell_no}', display_value, self.wb.add_format({'color':'000000', 'bg_color' : 'eeeeee'}))

                    cell_no += 1


    def get_value(self, value):
        if value:
            try:
                value = float(value)
                return value
            except ValueError:
                return value
            except Exception as e:
                return value
        return value
    

    def _prepare_chunk_data(self, data, _chunk_size):
        chunk_data = []
        for _record in data:
            chunk_data.append(_record)
            if len(chunk_data) >= _chunk_size:
                yield chunk_data
                chunk_data = []
        if chunk_data:
            yield chunk_data
    
    
    def render_table(self, ws, title, headers, data, row_start=1, col_start=1):
        if APP_ID == 'AVAILABILITY-DETAILS':
            self.render_available_details_table(ws, title, headers, data, row_start, col_start)
            return
        
        column_widths = {}
        row_no = ExcelWriter.CONTENT_ROW_START - 1 + row_start
        # Adding table title here
        header_format = self.wb.add_format({'bold': True, 'border': 1, 'bg_color': '#7D92AF', 'font_color':'#FFFFFF', 'border': 2, 'border_color': '#FFFFFF'})
        data_format = self.wb.add_format({'bg_color': '#DCE6F1', 'border': 1, 'border_color': '#FFFFFF'})
        if headers:
            ws.write_row(row_no, 0, headers[0], header_format)
            for col_delta, val in enumerate(headers[0]):
                column_widths[col_delta] = max(len(str(val)), 8)
            row_no += 1

        _chunk_size = 10000
        _row_count = 0
        for chunk_data in self._prepare_chunk_data(data, _chunk_size):
            for row_delta, _row in enumerate(chunk_data):
                _row_count +=1
                
                ws.write_row(row_no, 0, _row, data_format)
                for col_delta, val in enumerate(_row):
                    if col_delta in column_widths:
                        column_widths[col_delta] = max(len(str(val)), column_widths[col_delta])
                    else:
                        column_widths[col_delta] = max(len(str(val)), 8)
                row_no += 1
            del chunk_data
            
        for col, column_width in column_widths.items():
            col_name = xlsxwriter.utility.xl_col_to_name(col)
            ws.set_column(f'{col_name}:{col_name}', column_width + 2)


    def render_metric_table(self, ws, component_data, merge_cells, title, headers, data, row_start=1, col_start=1):
        column_widths = {}
        if data:
            if merge_cells:
                for merge_cell in merge_cells:
                    ws.merge_range(merge_cell, '')
            
            row_no = ExcelWriter.CONTENT_ROW_START - 1 + row_start
            
            header_format = self.wb.add_format({'align': 'center', 'bold': True, 'bg_color': '#7D92AF', 'font_color':'#FFFFFF', 'border': 0, 'border_color': '#FFFFFF'})
            data_format = self.wb.add_format({'bg_color': '#DCE6F1', 'border': 1, 'border_color': '#FFFFFF'})
            if headers:
                for header in headers:
                    ws.write_row(row_no, 0, header, header_format)
                    for col_delta, val in enumerate(header):
                        if col_delta in column_widths:
                            column_widths[col_delta] = max(len(str(val)), column_widths[col_delta])
                        else:
                            column_widths[col_delta] = max(len(str(val)), 8)
                    row_no += 1

            _chunk_size = 10000
            for chunk_data in self._prepare_chunk_data(data, _chunk_size):
                for row_delta, _row in enumerate(chunk_data):
                    ws.write_row(row_no, 0, _row, data_format)
                    for col_delta, val in enumerate(_row):
                        if col_delta in column_widths:
                            column_widths[col_delta] = max(len(str(val)), column_widths[col_delta])
                        else:
                            column_widths[col_delta] = max(len(str(val)), 8)
                    row_no += 1
                del chunk_data
            
            for col, column_width in column_widths.items():
                col_name = xlsxwriter.utility.xl_col_to_name(col)
                ws.set_column(f'{col_name}:{col_name}', column_width + 2)

                

    def render_available_details_table(self, ws, title, headers, data, row_start=1, col_start=1):
        column_widths = {}
        row_no = ExcelWriter.CONTENT_ROW_START - 1 + row_start
        header_format = self.wb.add_format({'bold': True, 'border': 1, 'bg_color': '#7D92AF', 'font_color':'#FFFFFF', 'border': 2, 'border_color': '#FFFFFF'})
        # Adding table title here
        if headers:
            ws.write_row(row_no, 0, headers[0], header_format)

            for col_delta, val in enumerate(headers[0]):
                column_widths[col_delta] = max(len(str(val)), 8)
            row_no += 1

        _chunk_size = 10000
        for chunk_data in self._prepare_chunk_data(data, _chunk_size):
            for row_delta, _row in enumerate(chunk_data):
                for col_delta, val in enumerate(_row):
                    cell_position = xlsxwriter.utility.xl_rowcol_to_cell(row_no, col_delta-1+col_start)
                    bg_color = '#DCE6F1'
                    try:
                        if APP_ID == 'AVAILABILITY-DETAILS':
                            if isinstance(val, str) and 'COLOR-CODE_' in val:
                                vals = val.split('_') #COLOR-CODE_{color_code}_100.0
                                if len(vals) == 3:
                                    val = vals[2]
                                    if vals[1] is not None and len(vals[1]):
                                        bg_color = vals[1]
                        val = self.get_value(val)
                    except Exception as e:
                            print('ExcelWriter: found exception... value is :: ', val)
                            try:
                                val = str(val)
                            except Exception as ex:
                                val = ''
                    ws.write(cell_position, val, self.wb.add_format({'bg_color': bg_color, 'border': 1, 'border_color': '#FFFFFF'}))
                    if col_delta in column_widths:
                        column_widths[col_delta] = max(len(str(val)), column_widths[col_delta])
                    else:
                        column_widths[col_delta] = max(len(str(val)), 8)
                row_no += 1
            del chunk_data

        for col, column_width in column_widths.items():
            col_name = xlsxwriter.utility.xl_col_to_name(col)
            ws.set_column(f'{col_name}:{col_name}', column_width + 2)



    def render_old_table(self, ws, title, headers, data, row_start=1, col_start=1):
        column_widths = {}
        if data:
            sheet_count = 1
            # ws = self.create_sheet(title)
            #self.add_headers(ws)
            new_title = title
            self.active_sheet_title = title
            if self.active_sheet_title not in self.total_sheet_row_counts:
                self.total_sheet_row_counts[self.active_sheet_title] = 0
            row_no = ExcelWriter.CONTENT_ROW_START - 1 + row_start
            if new_title in self.total_sheet_row_counts and self.total_sheet_row_counts[new_title] > 0:
                row_no = self.total_sheet_row_counts[new_title]
            for row_delta, _row in enumerate(data):
                if self.total_sheet_row_counts[new_title] >= ExcelWriter.DATA_PER_SHEET_LIMIT:
                    row_no = ExcelWriter.CONTENT_ROW_START - 1 + row_start
                    new_title = self.get_page_title(title, sheet_count)
                    sheet_count += 1
                    self.active_sheet_title = new_title
                    # ws = self.create_sheet(new_title)
                    self.add_headers(ws)
                    if self.active_sheet_title not in self.total_sheet_row_counts:
                        self.total_sheet_row_counts[self.active_sheet_title] = 0
                if row_no == ExcelWriter.CONTENT_ROW_START:
                    # Adding table title here
                    # ws.write_row(row_no-1, 0, [title], self.wb.add_format({'font_color': '00598B', 'bold':True}))
                    ws.write_row(row_no, 0, headers[0], self.wb.add_format({'bold': True, 'border': 1, 'bg_color': '#7D92AF', 'font_color':'#FFFFFF', 'border': 2, 'border_color': '#FFFFFF'}))
                    row_no += 1
                for col_delta, val in enumerate(_row):
                    cell_position = xlsxwriter.utility.xl_rowcol_to_cell(row_no, col_delta)
                    bg_color = '#DCE6F1'
                    try:
                        if APP_ID == 'AVAILABILITY-DETAILS':
                            if isinstance(val, str) and 'COLOR-CODE_' in val:
                                vals = val.split('_') #COLOR-CODE_{color_code}_100.0
                                if len(vals) == 3:
                                    val = vals[2]
                                    if vals[1] is not None and len(vals[1]):
                                        bg_color = vals[1]
                        val = self.get_value(val)
                    except Exception as e:
                        print('ExcelWriter: found exception... value is :: ', val)
                        try:
                            val = str(val)
                        except Exception as ex:
                            val = ''
                    ws.write(cell_position, val, self.wb.add_format({'bg_color': bg_color, 'border': 1, 'border_color': '#FFFFFF'}))
                    if col_delta in column_widths:
                        column_widths[col_delta] = max(len(str(val)), column_widths[col_delta])
                    else:
                        column_widths[col_delta] = max(len(str(val)), 8)
                row_no += 1
                self.total_sheet_row_counts[new_title] = row_no
        for col, column_width in column_widths.items():
            col_name = xlsxwriter.utility.xl_col_to_name(col)
            ws.set_column(f'{col_name}:{col_name}', column_width + 2)

    
    def prepare_report_summary_data(self, run_id, run_summary, tenant_info, user_params, run_start_time, run_completion_time):
        summary_data = {}
        summary_data['App'] = APP_DISPLAY_NAME.replace('-', ' ').title()
        c_name = ''
        if tenant_info is not None and len(tenant_info) > 0:
            result = self.client_names_ids(tenant_info)
            c_name = result[0]
        summary_data['Tenant Name'] = c_name
        summary_data['Run date'] = run_start_time
        summary_data['Completion date'] = run_completion_time
        first_name = run_summary.json()['analysisRun']['createdBy']['firstName']
        last_name = run_summary.json()['analysisRun']['createdBy']['lastName']
        login_name = run_summary.json()['analysisRun']['createdBy']['loginName']
        summary_data['User'] = f'{first_name} {last_name} ({login_name})'
        if user_params is not None:
            for key in user_params.keys():
                summary_data[self.get_display_name(key)] = self.get_display_value(user_params[key])
        return summary_data
    
                                                                                                                                                                                     
    def add_headers(self, ws):
        ws.merge_range('A1:A2', '')
        ws.merge_range('B1:Z2', '')
        ws.write('B1', self.app_id.title(), self.wb.add_format({'font_color': '00598B', 'bg_color': 'eeeeee', 'bold':True, 'align':'vcenter'}))
        ws.write('A1', '', self.wb.add_format({'font_color': '00598B', 'bg_color': 'eeeeee'}))


    def _set_title_as_header(self, ws, sheet_data):
        header_format = self.wb.add_format({'bold': True, 'font_color': '#00598B', 'align': 'left', 'valign': 'vcleft', 'font_size': 12, # 'bg_color': '#eeeeee'
            })

        row_format = self.wb.add_format({'bg_color': '#eeeeee'     # Row background fill color
        })

        # Apply row formatting to rows above header
        for row_idx in range(1):  # 0-based indexing; 'ROW_START - 1'
            ws.set_row(row_idx, None, row_format)  # Set row format
        ws.merge_range('A1:RR2', sheet_data['insights-title-header'].replace('-', ' ').title(), header_format)


    def fill_sheet_bg_colors(self, ws, start_row=0, end_row=30, fill_type="solid", color="eeeeee"):
        if ws:
            format=self.wb.add_format({'bg_color': color})
            ws.conditional_format(start_row, 0, end_row, 30, {'type': 'blanks', 'format': format})
            # ws.conditional_format(f'A{start_row}:C{end_row}', {'type': 'no_blanks', 'format': format})
            # ws.set_column(0, 30, None, self.wb.add_format({'bg_color': color}))
            # ws.set_row(0, 30, self.wb.add_format({'bg_color': 'eeeeee'}))

    def generate_excel_file(self, form, resp, report_summary_data, reportname, filepath):
        if resp:
            if 'excel-data' in resp:
                excel_data = []
                excel_data.append(
                    {
                        'title': 'SUMMARY',
                        'summary' : 'true',
                        'header': {},
                        'data': report_summary_data
                    }
                )
                if 'sheets' in resp['excel-data']:
                    for sheet in resp['excel-data']['sheets']:
                        excel_data.append(sheet)
                resp['excel-data']['sheets'] = excel_data
                self.render(resp['excel-data'])
                self.wb.close()
                # saving excel file
                excel_url = upload_file(form.get_run_id(), reportname, filepath)
                resp['excel_url'] = excel_url
        return resp

    
    def client_names_ids(self, customer_name):
        names = ''
        client_id = ''
        if customer_name and customer_name is not None:
            for i in customer_name:
                for j in i.items():
                    names+=j[1]['name']
                    client_id+=j[1]['uniqueId']
                    names+=', '
                    client_id+=', '
            names = names.rstrip(', ')
            client_id = client_id.rstrip(', ')
            return names, client_id
        else:
            return names, client_id
        

    def get_display_name(self, key):
        if key == 'filterCriteria':
            return 'Query'
        if key == 'fields':
            return 'Attributes'
        if key == 'groupBy':
            return 'Group By'
        if key == 'soryBy':
            return 'Sort By'
        if key == 'sortByOrder':
            return 'Sort By Order'
        return key


    def get_display_value(self, value):
        if value is None and len(value) <= 0:
            return '-'
        else:
            if isinstance(value, list):
                all_values = ', '.join([val for val in value])
                return all_values
        return value
    
        
    def add_doughnut_chart(self,ws,component_data):
        chart=self.wb.add_chart({'type':'doughnut', 'name':component_data['chart-title']})
        cell_format1 = self.wb.add_format()
        cell_format1.set_bold()
        cell_format1.set_font_color('#0066CC')

        # inserting data to our sheet
        cell_position = xlsxwriter.utility.xl_rowcol_to_cell(component_data['start-row']-2, component_data['start-col']-1)
        ws.write(cell_position, component_data['chart-title'], cell_format1)
        row_number=component_data['start-row']-1
        for row_delta, row_val in enumerate(component_data['data']):
            for col_delta, val in enumerate(row_val):
                cell_position = xlsxwriter.utility.xl_rowcol_to_cell((row_number + row_delta), component_data['start-col'] - 1 + col_delta)
                if row_delta == 0:
                    ws.write(cell_position, self.get_value(val), self.wb.add_format({'bold': True, 'border': 1, 'bg_color': '#7D92AF', 'font_color':'#FFFFFF', 'border': 2, 'border_color': '#FFFFFF'}))
                else:
                    ws.write(cell_position, self.get_value(val))
                    # ws.write(cell_position, val, self.wb.add_format({'bg_color': '#DCE6F1', 'border': 1, 'border_color': '#FFFFFF'}))

        colors=["#0077C8", "#00A3E0", "#673AB7", "#9C27B0", "#E91E63", "#F47925"]
        color_fill = []
        for i in colors:
            color_fill.append({"fill": {"color": i}})

        series_data = {
                "categories":f"='{ws.name}'!${chr(component_data['start-col']+64)}${component_data['start-row']+1}:${chr(component_data['start-col']+64)}${len(component_data['data'])+component_data['start-row']-1}",
                "values":f"='{ws.name}'!${chr(component_data['start-col']+65)}${component_data['start-row']+1}:${chr(component_data['start-col']+65)}${len(component_data['data'])+component_data['start-row']-1}",
                "points" : color_fill
            }
        chart.add_series(
            series_data
        )

        if 'width' in component_data:     
            chart.set_size({'width':component_data['width']*0.36*96,'height':component_data['height']*0.388*96})
            if lastColumnOfChart(component_data['width']*0.36*96,component_data['chart-position'])>=component_data['start-col'] and ord(component_data['chart-position'][0])<component_data['start-col']+64:
                ws.set_column_pixels(component_data['start-col']-2,component_data['start-col']-2,558)
        
        chart.set_title({'name':component_data['chart-title'],'name_font':{'color':'black'}})

        chart.set_style(10)

        if "hole-size" in component_data:
            chart.set_hole_size(component_data["hole-size"])

        ws.insert_chart(component_data['chart-position'], chart)     
        
    
    
    def add_pie_chart(self,ws,component_data):
        chart=self.wb.add_chart({'type':'pie'})
        cell_format=self.wb.add_format()
        cell_format.set_bold()
        cell_format.set_font_color('#0066CC')
        # inserting data row-wise as we have the data in our map row-wise only
        ws.write(component_data['start-row']-2,component_data['start-col']-1,component_data['chart-title'],cell_format)
        row_number=component_data['start-row']-1
        lst=component_data['data']
        ptr=0
        while  ptr<len(component_data['data']):
            ws.write_row(row_number,component_data['start-col']-1,lst[ptr])        
            row_number+=1
            ptr+=1 

        colors=["#0077C8", "#00A3E0", "#673AB7", "#9C27B0", "#E91E63", "#F47925"]
        color_fill = []
        for i in colors:
           color_fill.append({"fill": {"color": i}})  
        chart.add_series(
            {
                "categories":f"='{ws.name}'!${chr(component_data['start-col']+64)}${component_data['start-row']+1}:${chr(component_data['start-col']+64)}${len(component_data['data'])+component_data['start-row']-1}",
                "values":f"='{ws.name}'!${chr(component_data['start-col']+65)}${component_data['start-row']+1}:${chr(component_data['start-col']+65)}${len(component_data['data'])+component_data['start-row']-1}",
                # filling the custom colors to chart
                "points" : color_fill,
            }
        )
        if 'width' in component_data:
            chart.set_size({'width':component_data['width']*0.36*96,'height':component_data['height']*0.388*96})
            if lastColumnOfChart(component_data['width']*0.36*96,component_data['chart-position'])>=component_data['start-col'] and ord(component_data['chart-position'][0])<component_data['start-col']+64:
                ws.set_column_pixels(component_data['start-col']-2,component_data['start-col']-2,558)
        chart.set_title({'name':component_data['chart-title'],'name_font':{'color':'black'}})
        if 'hole-size' in component_data:
            chart.set_hole_size(component_data['hole-size'])
        ws.insert_chart(component_data['chart-position'],chart)  


    # def add_bar_chart(self,ws,component_data):
    #     chart=self.wb.add_chart({"type":"column"})
    #     cell_format=self.wb.add_format()
    #     cell_format.set_bold()
    #     cell_format.set_font_color('#00598B')
    #     # inserting data row-wise as we have the data in our map row-wise only
    #     ws.write(component_data['start-row']-2,component_data['start-col']-1,component_data['chart-title'],cell_format)
    #     row_number=component_data['start-row']-1
    #     lst=component_data['data']
    #     ptr=0
    #     while  ptr<len(component_data['data']):
    #         ws.write_row(row_number,component_data['start-col']-1,lst[ptr])
    #         row_number+=1
    #         ptr+=1

    #     ptr2=component_data['start-col']+1
    #     while(ptr2<len(component_data['data'][0])+component_data['start-col']):
    #         chart.add_series(
    #             {
    #                 "name":f"='{ws.name}'!${chr(ptr2+64)}${component_data['start-row']}",
    #                 "categories":f"='{ws.name}'!${chr(component_data['start-col']+64)}${component_data['start-row']+1}:${chr(component_data['start-col']+64)}${len(component_data['data'])+component_data['start-row']-1}",
    #                 "values":f"='{ws.name}'!${chr(ptr2+64)}${component_data['start-row']+1}:${chr(ptr2+64)}${len(component_data['data'])+component_data['start-row']-1}",
    #             }
    #         )
    #         ptr2+=1

    #     # Set custom bar colors if provided
    #     # Check if the chart should be multicolored
    #     if component_data.get('is-multicolored-chart', False):
    #         colors = component_data.get('colors', [])
    #         for i, color in enumerate(colors):
    #             chart.add_series({
    #             "categories": f"='{ws.name}'!${chr(component_data['start-col'] + 64)}${component_data['start-row'] + i + 1}",
    #             "values": f"='{ws.name}'!${chr(component_data['start-col'] + 65)}${component_data['start-row'] + i + 1}",
    #             "fill": {"color": color},
    #         })

    #     if 'width' in component_data:
    #         chart.set_size({'width':component_data['width']*0.36*96,'height':component_data['height']*0.388*96})
    #         if lastColumnOfChart(component_data['width']*0.36*96,component_data['chart-position'])>=component_data['start-col'] and ord(component_data['chart-position'][0])<component_data['start-col']+64:
    #             ws.set_column_pixels(component_data['start-col']-2,component_data['start-col']-2,558)
    #     chart.set_title({"name":component_data['chart-title'],'name_font':{'color':'black'}})
    #     chart.set_x_axis({"name":component_data['x-axis-title']})
    #     chart.set_y_axis({"name":component_data['y-axis-title']})
    #     ws.insert_chart(component_data['chart-position'],chart)



    def add_bar_chart(self, ws, component_data):
        for row_num, row_data in enumerate(component_data['data']):
            ws.write_row(row_num + component_data['start-row'], component_data['start-col'], row_data)

        chart = self.wb.add_chart({'type': 'column'})

        last_row = component_data['start-row'] + len(component_data['data'])

        bar_gap = None
        if 'bar-gap' in component_data and component_data['bar-gap'] is not None:
            bar_gap = component_data['bar-gap']
        chart.add_series({
            'categories': f"='{ws.name}'!${chr(65 + component_data['start-col'])}{component_data['start-row'] + 2}:"
                          f"${chr(65 + component_data['start-col'])}{last_row}",
            'values': f"='{ws.name}'!${chr(66 + component_data['start-col'])}{component_data['start-row'] + 2}:"
                      f"${chr(66 + component_data['start-col'])}{last_row}",
            'name': component_data['data'][0][1],
            'fill': {'color': component_data['colors'][0]},
            'gap': bar_gap
        })

        chart.set_title({'name': component_data['chart-title'], 'name_font': {'color': component_data['title-color']}})
        chart.set_legend({'position': 'none'})

        chart.set_x_axis({
            'name': component_data['x-axis-title'],
            'min': 0,  # Minimum range for X-axis
            'max': len(component_data['data']) - 2,  # Maximum range for X-axis (based on number of categories)
        })

        chart.set_y_axis({'name': component_data['y-axis-title'], 'min': 0})

        chart.set_size({'width': component_data['width'], 'height': component_data['height']})
        ws.insert_chart(component_data['chart-position'], chart)

    
    def add_scatter_chart(self,ws,component_data):
        chart=self.wb.add_chart({"type":"scatter"}) 
        cell_format=self.wb.add_format()
        cell_format.set_bold()
        cell_format.set_font_color('#0066CC')
        # inserting data row-wise as we have the data in our map row-wise only
        ws.write(component_data['start-row']-2,component_data['start-col']-1,component_data['chart-title'],cell_format)
        row_number=component_data['start-row']-1
        lst=component_data['data']
        ptr=0
        while  ptr<len(component_data['data']):
            ws.write_row(row_number,component_data['start-col']-1,lst[ptr])        
            row_number+=1
            ptr+=1
        ptr2=component_data['start-col']+1
        while(ptr2<len(component_data['data'][0])+component_data['start-col']):
            chart.add_series(
                {
                    "name":f"='{ws.name}'!${chr(ptr2+64)}${component_data['start-row']}",
                    "categories":f"='{ws.name}'!${chr(component_data['start-col']+64)}${component_data['start-row']+1}:${chr(component_data['start-col']+64)}${len(component_data['data'])+component_data['start-row']-1}",
                    "values":f"='{ws.name}'!${chr(ptr2+64)}${component_data['start-row']+1}:${chr(ptr2+64)}${len(component_data['data'])+component_data['start-row']-1}",
                }
            )
            ptr2+=1
        if 'width' in component_data:
            chart.set_size({'width':component_data['width']*0.36*96,'height':component_data['height']*0.388*96})
            if lastColumnOfChart(component_data['width']*0.36*96,component_data['chart-position'])>=component_data['start-col'] and ord(component_data['chart-position'][0])<component_data['start-col']+64:
                ws.set_column_pixels(component_data['start-col']-2,component_data['start-col']-2,558)
        chart.set_title({"name":component_data['chart-title'],'name_font':{'color':'black'}})
        chart.set_x_axis({"name":component_data['x-axis-title']})
        chart.set_y_axis({"name":component_data['y-axis-title']})
        ws.insert_chart(component_data['chart-position'],chart)       

    def add_line_chart(self,ws,component_data):
        chart=self.wb.add_chart({"type":"line"}) 
        cell_format=self.wb.add_format()
        cell_format.set_bold()
        cell_format.set_font_color('#0066CC')
        # inserting data row-wise as we have the data in our map row-wise only
        ws.write(component_data['start-row']-2,component_data['start-col']-1,component_data['chart-title'],cell_format)
        row_number=component_data['start-row']-1
        lst=component_data['data']
        ptr=0
        while  ptr<len(component_data['data']):
            ws.write_row(row_number,component_data['start-col']-1,lst[ptr])        
            row_number+=1
            ptr+=1 
        ptr2=component_data['start-col']+1
        while(ptr2<len(component_data['data'][0])+component_data['start-col']):
            chart.add_series(
                {
                    "name":f"='{ws.name}'!${chr(ptr2+64)}${component_data['start-row']}",
                    "categories":f"='{ws.name}'!${chr(component_data['start-col']+64)}${component_data['start-row']+1}:${chr(component_data['start-col']+64)}${len(component_data['data'])+component_data['start-row']-1}",
                    "values":f"='{ws.name}'!${chr(ptr2+64)}${component_data['start-row']+1}:${chr(ptr2+64)}${len(component_data['data'])+component_data['start-row']-1}",
                }
            )
            ptr2+=1
        if 'width' in component_data:
            chart.set_size({'width':component_data['width']*0.36*96,'height':component_data['height']*0.388*96})
            if lastColumnOfChart(component_data['width']*0.36*96,component_data['chart-position'])>=component_data['start-col'] and ord(component_data['chart-position'][0])<component_data['start-col']+64:
                ws.set_column_pixels(component_data['start-col']-2,component_data['start-col']-2,558)
        chart.set_title({"name":component_data['chart-title'],'name_font':{'color':'black'}})
        chart.set_x_axis({"name":component_data['x-axis-title']})
        chart.set_y_axis({"name":component_data['y-axis-title']})
        ws.insert_chart(component_data['chart-position'],chart)


    def add_stack_bar_chart(self,ws,component_data):
        chart=self.wb.add_chart({"type":"line","subtype":"stacked"}) 
        cell_format=self.wb.add_format()
        cell_format.set_bold()
        cell_format.set_font_color('#0066CC')
        # inserting data row-wise as we have the data in our map row-wise only
        ws.write(component_data['start-row']-2,component_data['start-col']-1,component_data['chart-title'],cell_format)
        row_number=component_data['start-row']-1
        lst=component_data['data']
        ptr=0
        while  ptr<len(component_data['data']):
            ws.write_row(row_number,component_data['start-col']-1,lst[ptr])        
            row_number+=1
            ptr+=1
        ptr2=component_data['start-col']+1
        while(ptr2<len(component_data['data'][0])+component_data['start-col']):
            chart.add_series(
                {
                    "name":f"='{ws.name}'!${chr(ptr2+64)}${component_data['start-row']}",
                    "categories":f"='{ws.name}'!${chr(component_data['start-col']+64)}${component_data['start-row']+1}:${chr(component_data['start-col']+64)}${len(component_data['data'])+component_data['start-row']-1}",
                    "values":f"='{ws.name}'!${chr(ptr2+64)}${component_data['start-row']+1}:${chr(ptr2+64)}${len(component_data['data'])+component_data['start-row']-1}",
                }
            )
            ptr2+=1
        if 'width' in component_data:
            chart.set_size({'width':component_data['width']*0.36*96,'height':component_data['height']*0.388*96})
            if lastColumnOfChart(component_data['width']*0.36*96,component_data['chart-position'])>=component_data['start-col'] and ord(component_data['chart-position'][0])<component_data['start-col']+64:
                ws.set_column_pixels(component_data['start-col']-2,component_data['start-col']-2,558)
        chart.set_title({"name":component_data['chart-title'],'name_font':{'color':component_data['title-color']}})
        chart.set_x_axis({"name":component_data['x-axis-title']})
        chart.set_y_axis({"name":component_data['y-axis-title']})
        ws.insert_chart(component_data['chart-position'],chart,{'x_scale':component_data['chart-width'],'y_scale':component_data['chart-height']})


    def add_bar_line_trend_chart(self,ws,component_data):
        cell_format=self.wb.add_format()
        cell_format.set_bold()
        cell_format.set_font_color('#0066CC')
        # inserting data row-wise as we have the data in our map row-wise only
        ws.write(component_data['start-row']-2,component_data['start-col']-1,component_data['chart-title'],cell_format)
        row_number=component_data['start-row']-1
        lst=component_data['data']
        ptr=0
        while  ptr<len(component_data['data']):
            ws.write_row(row_number,component_data['start-col']-1,lst[ptr])      
            row_number+=1
            ptr+=1
        ws.set_column(f'{chr(component_data["start-col"]+64)}:{chr(component_data["start-col"]+64)}',80)
        chart1 = self.wb.add_chart({"type": "column"})
        # adding data series to the chart 
        # if 'x-axis-date-format' in component_data:
        ptr1=component_data['start-col']+1
        while(ptr1<len(component_data['data'][0])+component_data['start-col']):
            chart1.add_series(
                {
                    "name":f"='{ws.name}'!${chr(ptr1+64)}${component_data['start-row']}",
                    # "date_axis":True,
                    "categories":f"='{ws.name}'!${chr(component_data['start-col']+64)}${component_data['start-row']+1}:${chr(component_data['start-col']+64)}${len(component_data['data'])+component_data['start-row']-1}",
                    "values":f"='{ws.name}'!${chr(ptr1+64)}${component_data['start-row']+1}:${chr(ptr1+64)}${len(component_data['data'])+component_data['start-row']-1}",
                }
            )
            ptr1+=1   
        chart2 = self.wb.add_chart({"type": "line"})
        # adding data series to the chart 
        ptr2=component_data['start-col']+1
        while(ptr2<len(component_data['data'][0])+component_data['start-col']):
            chart2.add_series(
                {
                    "name":f"='{ws.name}'!${chr(ptr2+64)}${component_data['start-row']}",
                    "categories":f"='{ws.name}'!${chr(component_data['start-col']+64)}${component_data['start-row']+1}:${chr(component_data['start-col']+64)}${len(component_data['data'])+component_data['start-row']-1}",
                    "values":f"='{ws.name}'!${chr(ptr2+64)}${component_data['start-row']+1}:${chr(ptr2+64)}${len(component_data['data'])+component_data['start-row']-1}",
                }
            )
            ptr2+=1
        chart1.combine(chart2)
        if 'width' in component_data:
            chart1.set_size({'width':component_data['width']*0.36*96,'height':component_data['height']*0.388*96})
            if lastColumnOfChart(component_data['width']*0.36*96,component_data['chart-position'])>=component_data['start-col'] and ord(component_data['chart-position'][0])<component_data['start-col']+64:
                ws.set_column_pixels(component_data['start-col']-2,component_data['start-col']-2,558)
        chart1.set_title({"name":component_data['chart-title'],'name_font':{'color':'black'}})
        chart1.set_x_axis({"name": component_data['x-axis-title'],"date_axis":True,'num_font':  {'rotation': -90}})
        chart1.set_y_axis({"name": component_data['y-axis-title']})
        chart1.set_legend({'none': True})
        ws.insert_chart(component_data['chart-position'], chart1)


    def add_insights_table(self, ws, component_data):
        # Extract starting row and column
        row_start = component_data['start-row'] + ExcelWriter.ROW_START + 1  # Adjust for 1-based indexing
        col_start = component_data['start-col']

        # Add table title if provided
        if 'title' in component_data:
            title_format = self.wb.add_format({'bold': True, 'font_color': '#00598B'})
            ws.write(row_start - 1, col_start, component_data['title'], title_format)

        # Handle single value as table data
        if isinstance(component_data['data'], (int, float, str)):
            ws.write(row_start, col_start, component_data['data'])
            col_width = len(str(component_data['data']))
            ws.set_column(col_start, col_start, col_width + 2)
        else:
            col_widths = [len(str(header)) for header in component_data['data'][0]]  # Start with header row
            for row in component_data['data']:
                col_widths = [max(col_widths[i], len(str(item))) for i, item in enumerate(row)]

            col_widths = [width + 2 for width in col_widths]  # Add padding

            for col_idx, width in enumerate(col_widths):
                ws.set_column(col_start + col_idx, col_start + col_idx, width)

            header_format = self.wb.add_format({'bold': True, 'bg_color': '#5884be', 'align': 'left', 'font_color': 'white', 'border': 1, 'border_color': '#FFFFFF'}) #4F81BD
            for col_idx, header in enumerate(component_data['data'][0]):
                ws.write(row_start, col_start + col_idx, header, header_format)

            row_format_odd = self.wb.add_format({'bg_color': '#B8CCE4', 'align': 'left', 'border': 1, 'border_color': '#FFFFFF'})  # Light gray
            row_format_even = self.wb.add_format({'bg_color': '#DCE6F1', 'align': 'left', 'border': 1, 'border_color': '#FFFFFF'})  # White

            for row_idx, row_data in enumerate(component_data['data'][1:], start=1):  # Skip header row
                current_format = row_format_odd if row_idx % 2 == 1 else row_format_even
                for col_idx, value in enumerate(row_data):
                    ws.write(row_start + row_idx, col_start + col_idx, value, current_format)


    def add_component_title(self, ws, component_data):
        """
        add component title
        """
        if 'title' in component_data and component_data['title'] is not None and len(component_data['title']) > 0:
            cell_position = xlsxwriter.utility.xl_rowcol_to_cell(component_data['start-row'], component_data['start-col'])
            ws.write(cell_position, component_data['title'], self.wb.add_format({'bold': True, 'font_color':'#00598B'}))


    def _add_component_title(self, ws, component_data):
        color = component_data.get('title-color', '#00598B')  # Default color if not provided
        title_format = self.wb.add_format({'font_color': f'{color}', 'bold': True})
        ws.write(component_data['start-row'] - 1, component_data['start-col'] - 1, component_data['_title'], self.wb.add_format({'font_color': f'{color}', 'bold': True}))  # Adjust for 0-based index
        # ws = self.wb.add_worksheet()


    def _set_title_as_header(self, ws, sheet_data):
        header_format = self.wb.add_format({'bold': True, 'font_color': '#00598B', 'align': 'left', 'valign': 'vcleft', 'font_size': 13, # 'bg_color': '#eeeeee'
            })
        row_format = self.wb.add_format({'bg_color': '#eeeeee'     # Row background fill color
        })

        for row_idx in range(1):  # 0-based indexing; 'ROW_START - 1'
            ws.set_row(row_idx, None, row_format)  # Set row format
        ws.merge_range('A1:RR2', sheet_data['tab-title-header'].replace('_', ' ').title(), header_format)


    def add_component(self, ws, component_data, title):
        if component_data:
            if 'type' in component_data:
                if component_data['type'] == 'name':
                    if 'title' in component_data and component_data.get('title'):
                        self.add_component_title(ws, component_data)
                    elif '_title' in component_data and component_data.get('_title'):
                        self._add_component_title(ws, component_data)
                if component_data['type'] == 'table' and 'is-insights-type-table' in component_data and component_data['is-insights-type-table'] and component_data['is-insights-type-table'] == True:
                    self.add_insights_table(ws, component_data)
                elif component_data['type'] == 'table':
                    if title:
                        start_row = 1
                        start_col = 1
                        if 'data' in component_data and len(component_data['data']) > 0:
                            headers = component_data['data'][0:1]
                            data = component_data['data'][1:len(component_data['data'])]
                        if 'start-row' in component_data and 'start-col' in component_data:
                            start_row = component_data['start-row']
                            start_col = component_data['start-col']
                        # if 'title' in component_data and component_data.get('title'):
                        #     self.add_component_title(ws, component_data)
                        if 'metric_sheet' in component_data and component_data['metric_sheet'] == True:
                            headers = component_data['data'][0:2]
                            data = component_data['data'][2:len(component_data['data'])]
                            self.render_metric_table(ws, component_data, component_data['merge_cells'], title, headers, data, start_row, start_col)
                        # elif 'is-insights-type-table' in component_data and component_data['is-insights-type-table'] and component_data['is-insights-type-table'] == True:
                        #     self.add_table(ws, component_data)
                        else:
                            self.render_table(ws, title, headers, data, start_row, start_col)
                elif component_data['type']=='doughnut-chart':
                    self.add_doughnut_chart(ws,component_data)
                elif component_data['type']=='pie-chart':
                    self.add_pie_chart(ws,component_data) 
                elif component_data['type']=='scatter-chart':    
                    self.add_scatter_chart(ws,component_data)
                elif component_data['type']=='bar-chart':
                    self.add_bar_chart(ws,component_data) 
                elif component_data['type']=='line-chart':
                    self.add_line_chart(ws,component_data)
                elif component_data['type']=='stack-bar-chart':
                    self.add_stack_bar_chart(ws,component_data)
                elif component_data['type']=='bar-line-trend-chart':
                    self.add_bar_line_trend_chart(ws,component_data) 
        

    def render(self, excel_data):
        if excel_data:
            for sheet in excel_data['sheets']:
                if (('title' in sheet and len(sheet['title']) > 0 and sheet['title'].lower() == 'summary') or ('summary' in sheet and sheet['summary'] == 'true')):
                    self.write_summary_data(sheet['data'])
                elif 'documentation' in sheet and sheet['documentation'] == 'true':
                    self.write_glossary_data(sheet['data'])
                else:
                    title = None
                    if 'title' in sheet:
                        title = sheet['title']
                    if title is None or len(title) <= 0:
                        if 'title' in component_data and component_data['title'] is not None and len(component_data['title']) > 0:
                            title = component_data['title']
                    ws = self.create_sheet(title)

                    if 'tab-title-header' in sheet:
                        self._set_title_as_header(ws, sheet)

                    for component_data in sheet['components']:
                        self.add_component(ws, component_data, title)