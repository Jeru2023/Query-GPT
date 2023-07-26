import json
from streamlit_echarts import st_echarts
from streamlit_echarts import JsCode
import pandas as pd


def render_piechart(data):
    pass


def render_linechart(x_list, y_list):
    option = {
        "xAxis": {
            "type": "category",
            "data": x_list,
        },
        "yAxis": {"type": "value"},
        "series": [{"data": y_list, "type": "line"}],
    }
    st_echarts(
        options=option, height="400px",
    )


def render_multi_linechart(data):
    pass


def render_barchart(data):
    pass


def render_multi_barchart(data):
    pass


def make_options(df, chart_type):
    string_columns = []
    float_columns = []
    for col in df.columns:
        # 使用dtype属性获取列的数据类型，然后使用str属性判断是否为字符串类型
        if pd.to_numeric(df[col], errors='coerce').notnull().all() and col != 'month':
            float_columns.append(col)
        else:
            string_columns.append(col)

    print(string_columns)
    print(float_columns)
    # Convert DataFrame to the required format
    z_name = 'brand' if 'brand' in string_columns else string_columns[0]
    x_name = 'month' if 'month' in string_columns else string_columns[0]
    y_name = float_columns[0]
    series_data = [
        {
            'name': x,
            'type': chart_type,
            'data': df[df[z_name] == x][float_columns[0]].tolist(),  # 计算列默认取第0个
        }
        for x in df[z_name].unique()
    ]

    x_data = df[x_name].unique().tolist()

    # Create the ECharts option
    if string_columns.__len__() == 1 and float_columns.__len__() == 1:
        x_list = df[string_columns[0]].to_list()
        y_list = df[float_columns[0]].to_list()
        option = {
            "xAxis": {
                "type": "category",
                "data": x_list,
            },
            "yAxis": {"type": "value"},
            "series": [{"data": y_list, "type": "line"}],
        }
    else:

        option = {
            'tooltip': {'trigger': 'axis'},
            'legend': {'data': df[z_name].unique().tolist()},
            'xAxis': {'data': x_data, "name": x_name},
            'yAxis': {"name": y_name},
            'series': series_data
        }

    # Output the ECharts option
    print(option)
    return option


def render_chart(data, chart_type, multi_series):
    """
        如果列名为这样子：month	total_sales_volumn	total_sales_amount	brand
        就不能简单的拿前两列
    """
    y_list = data.iloc[:, -1].to_list()
    columes_num = data.shape[1]
    x_list = data.iloc[:, -2].to_list()
    # judge_chart_columns(data)
    option = make_options(data, chart_type)
    st_echarts(
        options=option, height="400px",
    )
    # if (chart_type == 'pie'):
    #     render_piechart(data)
    # elif (chart_type == "line"):
    #     print('------ line chart')
    #     if (multi_series == 'yes'):
    #         render_linechart(x_list, y_list)
    #     else:
    #         x_list = data.iloc[:, -2].to_list()
    #         print(f"x_list is {x_list}")
    #         print(f"y_list is {y_list}")
    #         print(f"columes number is {columes_num}")
    #         render_linechart(x_list, y_list)
    # elif (chart_type == 'bar'):
    #     if (multi_series == 'yes'):
    #         render_multi_barchart(data)
    #     else:
    #         render_barchart(data)
