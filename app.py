import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf


# ==========================
# PAGE SETTINGS
# ==========================

st.set_page_config(
    page_title="AI Portfolio Analyzer",
    page_icon="📈",
    layout="wide"
)


st.title("🤖 AI Portfolio Analyzer")


# ==========================
# TABS
# ==========================

portfolio_tab, yahoo_tab = st.tabs(
    [
        "📊 Portfolio Analyzer",
        "📈 Yahoo Finance"
    ]
)


# ==========================
# SESSION STORAGE
# ==========================

if "clean_data" not in st.session_state:
    st.session_state.clean_data = None


if "raw_data" not in st.session_state:
    st.session_state.raw_data = None
# PART 2 - EXCEL UPLOAD + AI HEADER SCANNER
# ==========================

with portfolio_tab:

    st.header("📊 Portfolio Analyzer")

    uploaded_file = st.file_uploader(
        "Upload Portfolio Excel",
        type=["xlsx"]
    )


    if uploaded_file:

        df = pd.read_excel(uploaded_file)


        st.session_state.raw_data = df


        # ==========================
        # AI HEADER ALIASES
        # ==========================

        header_aliases = {

            "client": [
                "client",
                "customer",
                "account",
                "owner",
                "investor",
                "name"
            ],

            "stock": [
                "stock",
                "ticker",
                "symbol",
                "company",
                "security"
            ],

            "buy_date": [
                "buy date",
                "purchase date",
                "entry date",
                "open date"
            ],

            "sell_date": [
                "sell date",
                "sale date",
                "exit date",
                "close date"
            ],

            "shares": [
                "shares",
                "quantity",
                "qty",
                "units"
            ],

            "buy_price": [
                "buy price",
                "purchase price",
                "entry price",
                "cost"
            ],

            "sell_price": [
                "sell price",
                "sale price",
                "exit price"
            ],

            "profit": [
                "profit",
                "gain",
                "loss",
                "return",
                "p/l"
            ]

        }



        def find_column(columns, options):

            for col in columns:

                clean_col = (
                    str(col)
                    .lower()
                    .strip()
                )

                for option in options:

                    if option in clean_col:

                        return col

            return None



        detected = {}


        for key, options in header_aliases.items():

            detected[key] = find_column(
                df.columns,
                options
            )


        st.session_state.detected = detected


        st.success(
            "✅ Portfolio detected and scanned"
        )# ==========================
# PART 3 - CLEAN DATA ENGINE
# ==========================

if st.session_state.raw_data is not None:


    df = st.session_state.raw_data

    detected = st.session_state.detected


    clean = pd.DataFrame()



    # ==========================
    # CREATE STANDARD COLUMNS
    # ==========================

    for new_name, old_name in detected.items():

        if old_name is not None:

            clean[new_name] = df[old_name]



    # ==========================
    # CLEAN STOCK NAMES
    # ==========================

    if "stock" in clean.columns:

        clean["stock"] = (

            clean["stock"]
            .astype(str)
            .str.upper()
            .str.strip()

        )



    # ==========================
    # CLEAN NUMBERS
    # ==========================

    number_columns = [

        "shares",
        "buy_price",
        "sell_price",
        "profit"

    ]


    for col in number_columns:


        if col in clean.columns:


            clean[col] = (

                clean[col]
                .astype(str)
                .str.replace("$","", regex=False)
                .str.replace(",","", regex=False)

            )


            clean[col] = pd.to_numeric(

                clean[col],

                errors="coerce"

            )



    # ==========================
    # CALCULATE PROFIT IF MISSING
    # ==========================

    if (

        "profit" not in clean.columns

        and

        "buy_price" in clean.columns

        and

        "sell_price" in clean.columns

        and

        "shares" in clean.columns

    ):


        clean["profit"] = (

            (

                clean["sell_price"]

                -

                clean["buy_price"]

            )

            *

            clean["shares"]

        )



    # ==========================
    # RETURN %
    # ==========================

    if (

        "buy_price" in clean.columns

        and

        "shares" in clean.columns

        and

        "profit" in clean.columns

    ):


        clean["investment"] = (

            clean["buy_price"]

            *

            clean["shares"]

        )


        clean["return_percent"] = (

            clean["profit"]

            /

            clean["investment"]

            *

            100

        )



    # ==========================
    # CLEAN DATES
    # ==========================

    for col in [

        "buy_date",
        "sell_date"

    ]:


        if col in clean.columns:


            clean[col] = pd.to_datetime(

                clean[col],

                errors="coerce"

            )



    st.session_state.clean_data = clean# ==========================
# PART 4 - PORTFOLIO DASHBOARD
# ==========================

if st.session_state.clean_data is not None:


    with portfolio_tab:


        clean = st.session_state.clean_data.copy()


        st.divider()


        st.header(
            "📈 Portfolio Performance"
        )


        filtered = clean.copy()



        # ==========================
        # CLIENT FILTER
        # ==========================

        if "client" in filtered.columns:


            clients = [

                "All"

            ] + sorted(

                filtered["client"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()

            )


            selected_client = st.selectbox(

                "Select Client",

                clients

            )


            if selected_client != "All":

                filtered = filtered[

                    filtered["client"].astype(str)

                    ==

                    selected_client

                ]



        # ==========================
        # STOCK FILTER
        # ==========================

        if "stock" in filtered.columns:


            stocks = [

                "All"

            ] + sorted(

                filtered["stock"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()

            )


            selected_stock = st.selectbox(

                "Select Stock",

                stocks

            )


            if selected_stock != "All":


                filtered = filtered[

                    filtered["stock"]

                    ==

                    selected_stock

                ]



        # ==========================
        # METRICS
        # ==========================

        total_profit = filtered["profit"].sum()


        total_trades = len(filtered)


        winners = (

            filtered["profit"] > 0

        ).sum()


        if total_trades > 0:

            win_rate = (

                winners

                /

                total_trades

                *

                100

            )

        else:

            win_rate = 0



        avg_return = filtered[

            "return_percent"

        ].mean()



        col1,col2,col3,col4 = st.columns(4)



        col1.metric(

            "Total Profit",

            f"${total_profit:,.2f}"

        )


        col2.metric(

            "Trades",

            total_trades

        )


        col3.metric(

            "Win Rate",

            f"{win_rate:.1f}%"

        )


        col4.metric(

            "Average Return",

            f"{avg_return:.2f}%"

        )



        # ==========================
        # LINE GRAPH
        # ==========================

        if "sell_date" in filtered.columns:


            graph = filtered.dropna(

                subset=["sell_date"]

            ).sort_values(

                "sell_date"

            )


            if len(graph) > 0:


                graph["portfolio_growth"] = (

                    graph["profit"]

                    .cumsum()

                )


                st.subheader(

                    "📈 Portfolio Growth"

                )


                fig = px.line(

                    graph,

                    x="sell_date",

                    y="portfolio_growth",

                    markers=True

                )


                st.plotly_chart(

                    fig,

                    use_container_width=True

                )



        # ==========================
        # TRADE TABLE
        # ==========================

        st.subheader(

            "Trade History"

        )


        st.dataframe(

            filtered,

            use_container_width=True

        )# ==========================
# PART 5 - YAHOO FINANCE TAB
# ==========================

with yahoo_tab:


    st.header(
        "📈 Yahoo Finance Analyzer"
    )


    ticker_input = st.text_input(

        "Enter Stock Ticker",

        "AAPL"

    )


    timeframe = st.selectbox(

        "Chart Time Range",

        [

            "1 Month",

            "3 Months",

            "6 Months",

            "1 Year",

            "5 Years",

            "10 Years",

            "All Time"

        ]

    )



    period_map = {

        "1 Month": "1mo",

        "3 Months": "3mo",

        "6 Months": "6mo",

        "1 Year": "1y",

        "5 Years": "5y",

        "10 Years": "10y",

        "All Time": "max"

    }



    if ticker_input:


        ticker = (

            ticker_input

            .upper()

            .strip()

        )


        try:


            stock = yf.Ticker(

                ticker

            )


            info = stock.info



            # ==========================
            # COMPANY INFO
            # ==========================

            st.subheader(

                "🏢 Company Information"

            )


            c1,c2 = st.columns(2)



            with c1:


                st.write(

                    "Company:",

                    info.get(

                        "longName",

                        "N/A"

                    )

                )


                st.write(

                    "Sector:",

                    info.get(

                        "sector",

                        "N/A"

                    )

                )


                st.write(

                    "Industry:",

                    info.get(

                        "industry",

                        "N/A"

                    )

                )



            with c2:


                st.write(

                    "Country:",

                    info.get(

                        "country",

                        "N/A"

                    )

                )


                st.write(

                    "Market Cap:",

                    info.get(

                        "marketCap",

                        "N/A"

                    )

                )



            # ==========================
            # MARKET DATA
            # ==========================

            st.subheader(

                "📊 Market Statistics"

            )


            a,b,c,d = st.columns(4)


            a.metric(

                "Current Price",

                info.get(

                    "currentPrice",

                    "N/A"

                )

            )


            b.metric(

                "P/E Ratio",

                info.get(

                    "trailingPE",

                    "N/A"

                )

            )


            c.metric(

                "52 Week High",

                info.get(

                    "fiftyTwoWeekHigh",

                    "N/A"

                )

            )


            d.metric(

                "52 Week Low",

                info.get(

                    "fiftyTwoWeekLow",

                    "N/A"

                )

            )



            # ==========================
            # PRICE GRAPH
            # ==========================

            history = stock.history(

                period=period_map[timeframe]

            )



            if len(history) > 0:


                st.subheader(

                    f"{ticker} Price History"

                )


                chart = px.line(

                    history,

                    x=history.index,

                    y="Close",

                    title=f"{ticker} Closing Price"

                )


                st.plotly_chart(

                    chart,

                    use_container_width=True

                )


                start_price = history["Close"].iloc[0]

                end_price = history["Close"].iloc[-1]


                change = (

                    (

                        end_price

                        -

                        start_price

                    )

                    /

                    start_price

                    *

                    100

                )


                st.info(

                    f"{ticker} performance: {change:.2f}%"

                )


        except:


            st.error(

                "Could not find stock. Check ticker symbol."

            )