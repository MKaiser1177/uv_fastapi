import streamlit as st
import httpx
import pandas as pd
import os


def get_backend_url() -> str:
    backend_url = os.getenv("BACKEND_URL")
    if not backend_url:
        try:
            backend_url = st.secrets["BACKEND_URL"]
        except (FileNotFoundError, KeyError):
            backend_url = None

    if not backend_url:
        st.error(
            "The backend URL is not configured. Add BACKEND_URL to Streamlit secrets "
            "using the public URL of your deployed FastAPI service."
        )
        st.stop()

    return backend_url.rstrip("/")


def main():
    base_url = get_backend_url()
    st.markdown("# PokeHub")

    st.write(base_url)

    stats = httpx.get(f"{base_url}/pokemon/stats").json()

    st.markdown("All cool stuff you'll need to know about these cute little monsters!!!")

    st.markdown("## PokeTypes")
    pokemons_per_type = httpx.get(f"{base_url}/pokemon/number_types").json()

    pokemons_per_type = pd.DataFrame(
        list(pokemons_per_type.items()), columns=["type", "number"],
    )
    st.bar_chart(pokemons_per_type.head(8), x="type", y="number")

    st.dataframe(stats)

    df = pd.DataFrame(stats)
    types = df["Type 1"].unique()
    poke_type = st.selectbox(label="Choose pokemon type", options=types)

    poke_types = httpx.get(f"{base_url}/pokemons/type", params={"poke_type": poke_type}).json()

    st.dataframe(poke_types)

    st.markdown("Pokemon stats")

if __name__ == "__main__":
    main()