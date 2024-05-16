import time  # to simulate a real time data, time loop
import numpy as np  # np mean, np random
import pandas as pd  # read csv, df manipulation
import plotly.express as px  # interactive charts
import streamlit as st  # 🎈 data web app development
from sqlalchemy import create_engine
import warnings
# Set display options to show all columns
pd.set_option('display.max_columns', None)
# Disable pandas warnings
warnings.filterwarnings('ignore', category=pd.errors.PerformanceWarning)
# Ignore specific warning
warnings.filterwarnings("ignore", message="The behavior of DatetimeProperties.to_pydatetime is deprecated")


st.set_page_config(
    page_title="Real-Time USDT/MMK Exchange Rate Dashboard",
    page_icon="📶",
    layout="wide",
)

############################################ EXTRACT DATA ################################################
username = st.secrets.db_credentials.username
password = st.secrets.db_credentials.password

# Database connection parameters
db_params = {
    'dbname': 'exchange_data',
    'user': username,
    'password': password,
    'host': '13.213.132.179',
    'port': '5432'
}
# Database connection
# Create the database URL
db_url = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['dbname']}"
conn = create_engine(db_url)

sql_query = """SELECT 
	    "DateTime",
		MAX("Top 4 Avg Buy Price") AS "AVG Buy Price", 
		MAX("Top 4 Avg Sell Price") AS "AVG Sell Price",
		MAX("Top 4 Total Buy Volume") AS "Top 4 Buy Volume",
		MAX("Top 4 Total Sell Volume") AS "Top 4 Sell Volume",
		MAX("Best Buy Price") AS "Best Buy Price",
		MAX("Best Sell Price") AS "Best Sell Price",
		MAX("Best Buy Volume") AS "Best Buy Volume MMK",
		MAX("Best Sell Volume") AS "Best Sell Volume MMK",
		SUM("Buy USDT") AS "Top 10 Total Buy Vol USDT",
		SUM("Sell USDT") AS "Top 10 Total Sell Vol USDT"
FROM exchange_data.exchange_data
WHERE DATE("DateTime") = CURRENT_DATE
GROUP BY "DateTime"
ORDER BY "DateTime";"""

# dashboard title
st.markdown("<h1 style='color:green; font-size:30px;'>USDT/MMK Exchange Rate Live Dashboard</h1>", unsafe_allow_html=True)

# creating a single-element container
placeholder = st.empty()


def fetch_data():
    return pd.read_sql(sql_query, conn)

# Get Live Data
old_avg_buy_price = 0
old_avg_sell_price = 0
old_best_buy_price = 0
old_best_sell_price = 0
old_best_buy_vol_mmk = 0
old_best_sell_vol_mmk = 0
old_best_buy_vol_usdt = 0
old_best_sell_vol_usdt = 0

while True:
    try:        
        # get values
        df = fetch_data()
        print(df.head())
        
        latest_row = df.iloc[-1]
        #print(latest_row)
        avg_buy_price = latest_row.iloc[1]
        avg_sell_price = latest_row.iloc[2]
        best_buy_price = latest_row.iloc[5]
        best_sell_price = latest_row.iloc[6]
        best_buy_vol_mmk = latest_row.iloc[7]
        best_sell_vol_mmk = latest_row.iloc[8]
        best_buy_vol_usdt = latest_row.iloc[9]
        best_sell_vol_usdt = latest_row.iloc[10]
        
        print(avg_buy_price)
        print(latest_row.iloc[0])
        
        # create container
        with placeholder.container():
            st.markdown("This dashboard can be used to monitor the price of USD in MMK. <span style='color:red;'>Warning: Prices on this site may be up to 100 MMK lower than USD bank notes.</span>", unsafe_allow_html=True)
        
            # create kpi columns
            kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
            
            st.markdown(
                        """
                    <style>
                    [data-testid="stMetricValue"] {
                        font-size: 20px;
                    }
                    </style>
                    """,
                        unsafe_allow_html=True,
                    )
            
            # Fill in those three columns with respective metrics or KPIs
            kpi1.metric(
                label="AVG Buy Price (MMK) 💸",
                value=f'{round(avg_buy_price):,}',
                delta=f"{round(avg_buy_price - old_avg_buy_price):,}",
            )

            kpi2.metric(
                label="AVG Sell Price (MMK) 💰",
                value=f"{round(avg_sell_price):,}",
                delta=f"{round(avg_sell_price - old_avg_sell_price):,}",
            )

            kpi3.metric(
                label="Best Buy Price (MMK) 🤩💸",
                value=f"{round(best_buy_price):,}",
                delta=f"{round(best_buy_price - old_best_buy_price):,}",
            )

            kpi4.metric(
                label="Best Sell Price (MMK) 🤩💰",
                value=f"{round(best_sell_price):,}",
                delta=f"{round(best_sell_price - old_best_sell_price):,}",
            )

            kpi5.metric(
                label="SUM of Top 10 Buy Vol - USDT 📉💸",
                value=f"{round(best_buy_vol_usdt):,}",
                delta=f"{round(best_buy_vol_usdt - old_best_buy_vol_usdt):,}",
            )

            kpi6.metric(
                label="SUM of Top 10 Sell Vol - USDT 📉💰",
                value=f"{round(best_sell_vol_usdt):,}",
                delta=f"{round(best_sell_vol_usdt - old_best_sell_vol_usdt):,}",
            )
            
         
            #st.markdown("----")
            
            # Create two columns for charts
            fig_col1, fig_col2 = st.columns(2)

            # Displaying Today USDT Price Trend with data labels
            with fig_col1:
                fig1 = px.line(data_frame=df, y=["Best Buy Price", "Best Sell Price"], x="DateTime")
                fig1.update_traces(text=df["Best Sell Price"], textposition='top center')  # Add data labels for Best Sell Price
                fig1.update_yaxes(range=(df["Best Sell Price"].min() - 30, df["AVG Buy Price"].max() + 30))
                fig1.update_layout( title={
                                        'text': "Today USDT Price Trend",
                                        'y':0.9,
                                        'x':0.5,
                                        'xanchor': 'center',
                                        'yanchor': 'top'})
                st.write(fig1)

            # Displaying Top 10 Buy & Sell Volume Trend (USDT) with data labels
            with fig_col2:
                fig2 = px.line(data_frame=df, y=["Top 10 Total Buy Vol USDT", "Top 10 Total Sell Vol USDT"], x="DateTime", color_discrete_sequence=["#26A17B", "#F94449"])
                fig2.update_traces(text=df["Top 10 Total Sell Vol USDT"], textposition='top center')  # Add data labels for Top 10 Total Sell Vol USDT
                fig2.update_yaxes(range=(df["Top 10 Total Sell Vol USDT"].min() - 30000, df["Top 10 Total Sell Vol USDT"].max() + 30000))
                fig2.update_layout( title={
                                        'text': "(Top 10) Buy & Sell Volume Trend in USDT",
                                        'y':0.9,
                                        'x':0.5,
                                        'xanchor': 'center',
                                        'yanchor': 'top'})                
                st.write(fig2)

                
            st.markdown("### Detailed Data View")
            st.dataframe(df[["DateTime", "AVG Buy Price", "AVG Sell Price", "Best Buy Price", "Best Sell Price", "Top 10 Total Buy Vol USDT", "Top 10 Total Sell Vol USDT"]].tail(10))

        old_avg_buy_price = avg_buy_price
        old_avg_sell_price = avg_sell_price
        old_best_buy_price = best_buy_price
        old_best_sell_price = best_sell_price
        old_best_buy_vol_mmk = best_buy_vol_mmk
        old_best_sell_vol_mmk = best_sell_vol_mmk
        old_best_buy_vol_usdt = best_buy_vol_usdt
        old_best_sell_vol_usdt = best_sell_vol_usdt
        
        time.sleep(20)
    except Exception as e:
        # Print the error message
        print(f"An error occurred: {e}")
    except Exception as e:
        st.error(f"An error is occurred: {e}")
    finally:
        continue
