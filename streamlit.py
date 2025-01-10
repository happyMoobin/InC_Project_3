from collections import defaultdict
import boto3
import streamlit as st
from streamlit_echarts import st_echarts


# 데이터 가져오기 및 처리
def fetch_and_process_data():
    # DynamoDB 클라이언트 생성
    dynamodb = boto3.client("dynamodb", region_name="ap-northeast-3")  # 리전에 맞게 변경
    table_name = "orders"

    # 테이블 스캔
    response = dynamodb.scan(TableName=table_name)
    items = response["Items"]

    # 데이터를 합산하고 분석할 구조 초기화
    aggregated_num_item = defaultdict(int)
    aggregated_total_price = defaultdict(int)
    aggregated_num_item_month = defaultdict(int)
    aggregated_total_price_month = defaultdict(int)
    user_data = defaultdict(lambda: {"num_item": defaultdict(int), "total_price": defaultdict(int)})
    product_data = defaultdict(lambda: {"num_item": defaultdict(int), "total_price": defaultdict(int)})

    for item in items:
        timestamp = item["timestamp"]["S"]
        total_price = int(item["total_price"]["N"])
        user_id = item["user_id"]["S"]
        cart_items = item.get("cart_items", {}).get("L", [])

        # 월별 데이터용 키 생성
        month = timestamp[0:2] + "-" + timestamp[3:5]  # 'YY-MM' 형식으로 변경

        # `cart_items`에서 상품별 데이터 추출
        for cart_item in cart_items:
            if "L" in cart_item and len(cart_item["L"]) >= 2:
                product_id = cart_item["L"][0]["S"]  # 상품 ID
                num_item = int(cart_item["L"][1]["N"])  # 상품 수량

                # 일별 데이터 집계
                aggregated_num_item[timestamp] += num_item
                aggregated_total_price[timestamp] += total_price
                user_data[user_id]["num_item"][timestamp] += num_item
                user_data[user_id]["total_price"][timestamp] += total_price
                product_data[product_id]["num_item"][timestamp] += num_item 
                product_data[product_id]["total_price"][timestamp] += total_price

                # 월별 데이터 집계
                aggregated_num_item_month[month] += num_item
                aggregated_total_price_month[month] += total_price
                user_data[user_id]["num_item"][month] += num_item
                user_data[user_id]["total_price"][month] += total_price
                product_data[product_id]["num_item"][month] += num_item
                product_data[product_id]["total_price"][month] += total_price

    # x축 데이터 생성
    x_data = sorted(aggregated_num_item.keys())
    x_data_month = sorted(aggregated_num_item_month.keys())

    # y축 데이터 생성
    y_data_num_item = [aggregated_num_item[timestamp] for timestamp in x_data]
    y_data_total_price = [aggregated_total_price[timestamp] for timestamp in x_data]
    y_data_num_item_month = [aggregated_num_item_month[month] for month in x_data_month]
    y_data_total_price_month = [aggregated_total_price_month[month] for month in x_data_month]

    # 사용자별 시리즈 데이터 생성
    user_series_num_item = {
        user_id: [data["num_item"].get(timestamp, 0) for timestamp in x_data]
        for user_id, data in user_data.items()
    }
    user_series_total_price = {
        user_id: [data["total_price"].get(timestamp, 0) for timestamp in x_data]
        for user_id, data in user_data.items()
    }
    user_series_num_item_month = {
        user_id: [data["num_item"].get(month, 0) for month in x_data_month]
        for user_id, data in user_data.items()
    }
    user_series_total_price_month = {
        user_id: [data["total_price"].get(month, 0) for month in x_data_month]
        for user_id, data in user_data.items()
    }

    # 상품별 시리즈 데이터 생성
    product_series_num_item = {
        product_id: [data["num_item"].get(timestamp, 0) for timestamp in x_data]
        for product_id, data in product_data.items()
    }
    product_series_total_price = {
        product_id: [data["total_price"].get(timestamp, 0) for timestamp in x_data]
        for product_id, data in product_data.items()
    }
    product_series_num_item_month = {
        product_id: [data["num_item"].get(month, 0) for month in x_data_month]
        for product_id, data in product_data.items()
    }
    product_series_total_price_month = {
        product_id: [data["total_price"].get(month, 0) for month in x_data_month]
        for product_id, data in product_data.items()
    }

    return (x_data, y_data_num_item, y_data_total_price, x_data_month, y_data_num_item_month, y_data_total_price_month,
            user_series_num_item, user_series_total_price, user_series_num_item_month, user_series_total_price_month,
            product_series_num_item, product_series_total_price, product_series_num_item_month, product_series_total_price_month)

def fetch_sales_data():
    dynamodb = boto3.client("dynamodb", region_name="ap-northeast-3")  # 리전에 맞게 변경
    table_name = "sales_data"

    # 테이블 스캔
    response = dynamodb.scan(TableName=table_name)
    items = response["Items"]

    # `product_id`별 `quantity` 합산
    product_quantity = defaultdict(int)
    for item in items:
        product_id = item["product_id"]["S"]
        quantity = int(item["quantity"]["N"])
        product_quantity[product_id] += quantity

    # x축과 y축 데이터 반환
    x_data = list(product_quantity.keys())
    y_data = list(product_quantity.values())

    return x_data, y_data


# 시각화 함수
def render_chart(x_data, total_data, series_data, data_label):
    st.subheader(f"{data_label}")
    if series_data:
        ids = list(series_data.keys())
        available_options = ["전체"] + ids
        selected_options = st.multiselect(
            f"{data_label} 데이터 선택", available_options, default=["전체"]
        )

        series_list = []
        legend_data = []

        if "전체" in selected_options or not selected_options:
            series_list.append({"name": "전체", "type": "line", "data": total_data})
            legend_data.append("전체")

        for _id in selected_options:
            if _id in series_data:
                series_list.append(
                    {"name": _id, "type": "line", "data": series_data[_id]}
                )
                legend_data.append(_id)

        chart_options = {
            "tooltip": {"trigger": "axis"},
            "legend": {"data": legend_data},
            "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
            "toolbox": {"feature": {"saveAsImage": {}} },
            "xAxis": {"type": "category", "boundaryGap": False, "data": x_data},
            "yAxis": {"type": "value"},
            "series": series_list,
        }

        st_echarts(options=chart_options, height="500px")
    else:
        st.warning(f"{data_label} 데이터가 없습니다.")
        

# render_chart2 함수: 간단한 막대 그래프
def render_chart2(x_data, y_data, data_label):
    st.subheader(f"{data_label}")
    
    # 막대 그래프 옵션 설정
    chart_options = {
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "xAxis": {
            "type": "category",
            "data": x_data
        },
        "yAxis": {"type": "value"},
        "series": [
            {
                "name": data_label,
                "type": "bar",
                "data": y_data,
                "itemStyle": {"color": "#72A0C1"}  # 막대 색상 설정
            }
        ]
    }
    
    # 그래프 표시
    st_echarts(options=chart_options, height="500px")



# Streamlit 앱
st.title("데이터 분석")

try:
    (x_data, y_data_num_item, y_data_total_price, x_data_month, y_data_num_item_month,
     y_data_total_price_month, user_series_num_item, user_series_total_price,
     user_series_num_item_month, user_series_total_price_month, product_series_num_item,
     product_series_total_price, product_series_num_item_month, product_series_total_price_month) = fetch_and_process_data()
except Exception as e:
    st.error(f"데이터를 처리하는 중 오류 발생: {e}")
    x_data, y_data_num_item, y_data_total_price = [], [], []
    x_data_month, y_data_num_item_month, y_data_total_price_month = [], [], []
    user_series_num_item, user_series_total_price = {}, {}
    product_series_num_item, product_series_total_price = {}, {}

# x축 선택 UI
axis_type = st.selectbox("축 유형 선택", ["일별", "월별", "전체기간"])

# 데이터 유형 선택

# 데이터 시각화
if axis_type == "일별":
    selected_data_type = st.radio("데이터 유형을 선택하세요", ["사용자", "상품"])  
    if selected_data_type == "사용자":
        tab1, tab2 = st.tabs(["주문수", "금액"])
        with tab1:
            render_chart(x_data, y_data_num_item, user_series_num_item, "사용자별 주문수")
        with tab2:
            render_chart(x_data, y_data_total_price, user_series_total_price, "사용자별 금액")
    else:
        tab1, tab2 = st.tabs(["주문수", "금액"])
        with tab1:
            render_chart(x_data, y_data_num_item, product_series_num_item, "상품별 주문수")
        with tab2:
            render_chart(x_data, y_data_total_price, product_series_total_price, "상품별 금액")
elif axis_type == "월별":
    selected_data_type = st.radio("데이터 유형을 선택하세요", ["사용자", "상품"])  
    if selected_data_type == "사용자":
        tab1, tab2 = st.tabs(["주문수", "금액"])
        with tab1:
            render_chart(x_data_month, y_data_num_item_month, user_series_num_item_month, "사용자별 주문수")
        with tab2:
            render_chart(x_data_month, y_data_total_price_month, user_series_total_price_month, "사용자별 금액")
    else:
        tab1, tab2 = st.tabs(["주문수", "금액"])
        with tab1:
            render_chart(x_data_month, y_data_num_item_month, product_series_num_item_month, "상품별 주문수")
        with tab2:
            render_chart(x_data_month, y_data_total_price_month, product_series_total_price_month, "상품별 금액")
else:
    try:
        # `sales_data` 데이터 가져오기
        x_data_sales, y_data_sales = fetch_sales_data()

        # 막대 그래프 렌더링
        render_chart2(x_data_sales, y_data_sales, "상품별 총 판매량")
    except Exception as e:
        st.error(f"데이터를 처리하는 중 오류 발생: {e}")

