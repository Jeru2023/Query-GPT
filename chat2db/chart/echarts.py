import json
from streamlit_echarts import st_echarts
from streamlit_echarts import JsCode

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

def render_chart(data, chart_type, multi_series):

    y_list = data.iloc[: , -1].to_list()
    columes_num = data.shape[1]

    if (chart_type=='pie'):
        render_piechart(data)
    elif (chart_type=="line"):
        print('------ line chart')
        if (multi_series=='yes'):
            render_linechart(data)
        else:
            x_list = data.iloc[:, -2].to_list()
            print(f"x_list is {x_list}")
            print(f"y_list is {y_list}")
            print(f"columes number is {columes_num}")
            render_linechart(x_list, y_list)
    elif (chart_type=='bar'):
        if (multi_series=='yes'):
            render_multi_barchart(data)
        else:
            render_barchart(data)