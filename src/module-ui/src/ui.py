import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from snowflake.snowpark.session import Session
from snowflake.snowpark.functions import col
from snowflake.snowpark.types import StringType, DecimalType


def get_active_session() -> Session:
    """Create or get new Snowflake Session.
    When running locally it uses the SNOWFLAKE_DEFAULT_CONNECTION_NAME environment variable to get the connection name and when running in SiS it uses the context connection.
    """
    conn = st.connection("snowflake")
    return conn.session()


TABLE_NAME = "<% [ctx.entities.pkg.identifier,'PUBLIC','PENGUINS_V'] | join('.') %>"
session = get_active_session()

st.title("🤖 Machine Learning App")

st.write("Welcome to world of Machine Learning with Streamlit.")

with st.expander("Data"):
    st.write("**Raw Data**")
    # read the data from table
    # cast the columns to right data types with right precision
    df = session.table(TABLE_NAME).select(
        col("island").cast(StringType()).alias("island"),
        col("species").cast(StringType()).alias("species"),
        col("bill_length_mm").cast(DecimalType(5, 2)).alias("bill_length_mm"),
        col("bill_depth_mm").cast(DecimalType(5, 2)).alias("bill_depth_mm"),
        col("flipper_length_mm").cast(DecimalType(5, 2)).alias("flipper_length_mm"),
        col("body_mass_g").cast(DecimalType()).alias("body_mass_g"),
        col("sex").cast(StringType()).alias("sex"),
    )
    df = df.to_pandas()
    # make the column names lower to reuse the rest of the code as is
    df.columns = df.columns.str.lower()
    # define and display
    st.write("**X**")
    X_raw = df.drop("species", axis=1)
    X_raw

    st.write("**y**")
    y_raw = df.species
    y_raw

with st.expander("Data Visualization"):
    st.scatter_chart(
        df,
        x="bill_length_mm",
        y="body_mass_g",
        color="species",
    )

# Interactivity
# Columns:
# 'species', 'island', 'bill_length_mm', 'bill_depth_mm',
# 'flipper_length_mm', 'body_mass_g', 'sex'
with st.sidebar:
    st.header("Input Features")
    # Islands
    islands = df.island.unique().astype(str)
    island = st.selectbox(
        "Island",
        islands,
    )
    # Bill Length
    min, max, mean = (
        df.bill_length_mm.min(),
        df.bill_length_mm.max(),
        df.bill_length_mm.mean().round(2),
    )
    bill_length_mm = st.slider(
        "Bill Length(mm)",
        min_value=min,
        max_value=max,
        value=mean,
    )
    # Bill Depth
    min, max, mean = (
        df.bill_depth_mm.min(),
        df.bill_depth_mm.max(),
        df.bill_depth_mm.mean().round(2),
    )
    bill_depth_mm = st.slider(
        "Bill Depth(mm)",
        min_value=min,
        max_value=max,
        value=mean,
    )
    # Flipper Length
    min, max, mean = (
        df.flipper_length_mm.min(),
        df.flipper_length_mm.max(),
        df.flipper_length_mm.mean().round(2),
    )
    flipper_length_mm = st.slider(
        "Flipper Length(mm)",
        min_value=min,
        max_value=max,
        value=mean,
    )
    # Body Mass
    min, max, mean = (
        df.body_mass_g.min().astype(float),
        df.body_mass_g.max().astype(float),
        df.body_mass_g.mean().round(2),
    )
    body_mass_g = st.slider(
        "Body Mass(g)",
        min_value=min,
        max_value=max,
        value=mean,
    )
    # Gender
    gender = st.radio(
        "Gender",
        ("male", "female"),
    )

# Dataframes for Input features
data = {
    "island": island,
    "bill_length_mm": bill_length_mm,
    "bill_depth_mm": bill_depth_mm,
    "flipper_length_mm": flipper_length_mm,
    "body_mass_g": body_mass_g,
    "sex": gender,
}
input_df = pd.DataFrame(data, index=[0])
input_penguins = pd.concat([input_df, X_raw], axis=0)

with st.expander("Input Features"):
    st.write("**Input Penguins**")
    input_df
    st.write("**Combined Penguins Data**")
    input_penguins

# Data Preparation

# Encode X
X_encode = ["island", "sex"]
df_penguins = pd.get_dummies(input_penguins, prefix=X_encode)
X = df_penguins[1:]
input_row = df_penguins[:1]

# Encode Y
target_mapper = {
    "Adelie": 0,
    "Chinstrap": 1,
    "Gentoo": 2,
}


def target_encoder(val_y: str) -> int:
    return target_mapper[val_y]


y = y_raw.apply(target_encoder)

with st.expander("Data Preparation"):
    st.write("**Encoded X (input penguins)**")
    input_row
    st.write("**Encoded y**")
    y


with st.container():
    st.subheader("**Prediction Probability**")
    # Model Training
    rf_classifier = RandomForestClassifier()
    # Fit the model
    rf_classifier.fit(X, y)
    # predict using the model
    prediction = rf_classifier.predict(input_row)
    prediction_prob = rf_classifier.predict_proba(input_row)

    # reverse the target_mapper
    p_cols = dict((v, k) for k, v in target_mapper.items())
    df_prediction_prob = pd.DataFrame(prediction_prob)
    # set the column names
    df_prediction_prob.columns = p_cols.values()
    # set the Penguin name
    df_prediction_prob.rename(columns=p_cols)

    st.dataframe(
        df_prediction_prob,
        column_config={
            "Adelie": st.column_config.ProgressColumn(
                "Adelie",
                help="Adelie",
                format="%f",
                width="medium",
                min_value=0,
                max_value=1,
            ),
            "Chinstrap": st.column_config.ProgressColumn(
                "Chinstrap",
                help="Chinstrap",
                format="%f",
                width="medium",
                min_value=0,
                max_value=1,
            ),
            "Gentoo": st.column_config.ProgressColumn(
                "Gentoo",
                help="Gentoo",
                format="%f",
                width="medium",
                min_value=0,
                max_value=1,
            ),
        },
        hide_index=True,
    )

# display the prediction
st.subheader("Predicted Species")
st.success(p_cols[prediction[0]])
