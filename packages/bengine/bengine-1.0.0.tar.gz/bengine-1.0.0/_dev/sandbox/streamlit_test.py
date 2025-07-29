import streamlit as st
import pandas as pd

st.title("My First Streamlit App")

number = st.slider("Pick a number", 0, 100)
st.write("Square of your number is", number ** 2)

df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
st.line_chart(df)